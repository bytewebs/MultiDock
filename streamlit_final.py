import streamlit as st
import requests
import os
st.title("Docker Automation Dashboard")

API_KEY = os.environ.get("API_KEY")  # Ensure you have your API key set in the environment
API_URL = "http://64.227.136.203:5050"

headers = {"x-api-key": API_KEY}

st.header("Select Microservices to Launch")

include_api = st.checkbox("API Service", value=True)
include_db = st.checkbox("Postgres DB")
include_redis = st.checkbox("Redis")

if "compose_yaml" not in st.session_state:
    st.session_state["compose_yaml"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "ports" not in st.session_state:
    st.session_state["ports"] = {}
if "deployed" not in st.session_state:
    st.session_state["deployed"] = False

if st.button("Generate Compose"):
    res = requests.post(
        f"{API_URL}/generate_compose",
        headers=headers,
        json={
            "include_api": include_api,
            "include_db": include_db,
            "include_redis": include_redis,
        },
    )
    if res.ok:
        data = res.json()
        st.session_state["compose_yaml"] = data["compose"]
        st.session_state["user_id"] = data["user_id"]
        st.session_state["ports"] = data["ports"]
        st.success(f"Compose YAML generated! Your session ID: {data['user_id']}")
        st.info(f"Assigned ports: {data['ports']}")
    else:
        st.error("Failed to generate compose file.")

st.text_area("Generated docker-compose YAML", st.session_state["compose_yaml"], height=300)

if st.button("Deploy"):
    if st.session_state["user_id"] is not None:
        res = requests.post(
            f"{API_URL}/deploy",
            headers=headers,
            json={"user_id": st.session_state["user_id"]},
        )
        if res.ok:
            st.success("Deployment started!")
            st.session_state["deployed"] = True
        else:
            st.error("Failed to deploy containers.")
    else:
        st.warning("No compose file generated.")

if st.button("Terminate"):
    if st.session_state["user_id"] is not None:
        res = requests.post(
            f"{API_URL}/terminate",
            headers=headers,
            json={"user_id": st.session_state["user_id"]},
        )
        if res.ok:
            st.success("Containers terminated!")
            st.session_state["deployed"] = False
        else:
            st.error("Failed to terminate containers.")
    else:
        st.warning("No compose file generated.")

if st.session_state["deployed"]:
    if st.button("Check Status"):
        if st.session_state["user_id"] is not None:
            res = requests.get(
                f"{API_URL}/status?user_id={st.session_state['user_id']}",
                headers=headers,
            )
            if res.ok:
                st.json(res.json())
            else:
                st.error("Failed to check status.")
        else:
            st.warning("No compose file generated.")

if st.session_state["ports"]:
    st.subheader("Your Service Ports")
    for service, port in st.session_state["ports"].items():
        st.write(f"{service}: {port}")

if st.session_state.get("deployed") and st.session_state.get("ports", {}).get("api"):
    st.subheader("Call Your Deployed API")
    name = st.text_input("Enter your name")
    if st.button("Call Hello API") and name:
        api_port = st.session_state["ports"]["api"]
        try:
            # Use requests to call your own Docker-exposed API
            url = f"http://64.227.136.203:{api_port}/hello?name={name}"
            api_res = requests.get(url, timeout=5)
            if api_res.ok:
                st.success(f"API response: {api_res.text}")
            else:
                st.error(f"API call failed: {api_res.status_code}")
        except Exception as e:
            st.error(f"API call error: {e}")

# Admin Control 

st.sidebar.subheader("Admin Access")

if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    with st.sidebar.form("admin_login"):
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if admin_user == "admin" and admin_pass == "admin":  
                st.session_state["admin_authenticated"] = True
                st.success("Logged in as Admin")
            else:
                st.error("Invalid credentials")
else:
    st.sidebar.success("Admin Mode Enabled")

    st.subheader(" Admin Container Control")

    
    admin_res = requests.get(f"{API_URL}/admin/containers", headers=headers)
    if admin_res.ok:
        containers = admin_res.json()["containers"]
        selected = []
        for c in containers:
            label = f"{c['name']} | {c['image']} | {c['status']}"
            if st.checkbox(label, key=c["id"]):
                selected.append(c["id"])

        if st.button("Terminate Selected Containers"):
            if selected:
                kill_res = requests.post(
                    f"{API_URL}/admin/terminate",
                    headers=headers,
                    json={"container_ids": selected}
                )
                if kill_res.ok:
                    st.success(f"Terminated containers: {selected}")
                else:
                    st.error("Failed to terminate containers")
            else:
                st.warning("No containers selected")
    else:
        st.error("Failed to fetch container list")
