import streamlit as st
import requests
import os
<<<<<<< HEAD
st.title("Docker Automation Dashboard")

API_KEY = os.environ.get("API_KEY")  # Ensure you have your API key set in the environment
API_URL = "http://49.36.180.69:5050"

headers = {"x-api-key": API_KEY}

st.header("Select Microservices to Launch")

=======
from dotenv import load_dotenv

# === Load .env ===
load_dotenv()

st.title("Docker Automation Dashboard")

API_KEY = os.getenv("API_KEY", "DhanurAI@108")  # Fallback if env not set
API_URL = "http://localhost:5050"
HEADERS = {"x-api-key": API_KEY}

# === Service Selection UI ===
st.header("Select Microservices to Launch")
>>>>>>> c6f723d (final commit)
include_api = st.checkbox("API Service", value=True)
include_db = st.checkbox("Postgres DB")
include_redis = st.checkbox("Redis")
include_ragchatbot = st.checkbox("RAG Chatbot (Govt Schemes)")

<<<<<<< HEAD
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
            "include_ragchatbot": include_ragchatbot,
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
=======
# === Session State ===
for key in ["compose_yaml", "user_id", "ports", "deployed"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "ports" else None if key == "user_id" else False if key == "deployed" else ""

# === Generate Compose ===
if st.button("Generate Compose"):
    try:
        res = requests.post(
            f"{API_URL}/generate_compose",
            headers=HEADERS,
            json={
                "include_api": include_api,
                "include_db": include_db,
                "include_redis": include_redis,
                "include_ragchatbot": include_ragchatbot,
            }
        )
        if res.ok:
            data = res.json()
            st.session_state["compose_yaml"] = data["compose"]
            st.session_state["user_id"] = data["user_id"]
            st.session_state["ports"] = data["ports"]
            st.success(f"Compose YAML generated! Session ID: {data['user_id']}")
            st.info(f"Assigned ports: {data['ports']}")
        else:
            st.error(f"Failed: {res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"Request Error: {e}")

st.text_area("Generated docker-compose YAML", st.session_state["compose_yaml"], height=300)

# === Deploy ===
if st.button("Deploy"):
    uid = st.session_state.get("user_id")
    if uid:
        res = requests.post(f"{API_URL}/deploy", headers=HEADERS, json={"user_id": uid})
>>>>>>> c6f723d (final commit)
        if res.ok:
            st.success("Deployment started!")
            st.session_state["deployed"] = True
        else:
<<<<<<< HEAD
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
=======
            st.error(f"Deployment failed: {res.text}")
    else:
        st.warning("Please generate compose file first.")

# === Terminate ===
if st.button("Terminate"):
    uid = st.session_state.get("user_id")
    if uid:
        res = requests.post(f"{API_URL}/terminate", headers=HEADERS, json={"user_id": uid})
>>>>>>> c6f723d (final commit)
        if res.ok:
            st.success("Containers terminated!")
            st.session_state["deployed"] = False
        else:
<<<<<<< HEAD
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
=======
            st.error(f"Termination failed: {res.text}")
    else:
        st.warning("No compose file generated.")

# === Status ===
if st.session_state["deployed"] and st.button("Check Status"):
    uid = st.session_state.get("user_id")
    if uid:
        res = requests.get(f"{API_URL}/status?user_id={uid}", headers=HEADERS)
        if res.ok:
            st.json(res.json())
        else:
            st.error("Status check failed.")
    else:
        st.warning("No compose file generated.")

# === Port Mapping Display ===
if st.session_state["ports"]:
    st.subheader("Your Service Ports")
    for svc, port in st.session_state["ports"].items():
        st.write(f"{svc}: {port}")

# === Hello API Test ===
if st.session_state.get("deployed") and st.session_state["ports"].get("api"):
    st.subheader("Test Hello API")
    name = st.text_input("Enter name")
    if st.button("Call Hello API") and name:
        try:
            url = f"http://localhost:{st.session_state['ports']['api']}/hello?name={name}"
            api_res = requests.get(url, timeout=5)
            if api_res.ok:
                st.success(f"API Response: {api_res.text}")
>>>>>>> c6f723d (final commit)
            else:
                st.error(f"API call failed: {api_res.status_code}")
        except Exception as e:
            st.error(f"API call error: {e}")

if "ragchatbot" in st.session_state["ports"]:
<<<<<<< HEAD
    st.subheader("💬 Ask the Govt Scheme Chatbot")

    query = st.text_input("Ask a question (e.g., 'What is Ayushman Bharat?')")

    if query:
        rag_url = f"http://64.227.136.203:{st.session_state['ports']['ragchatbot']}/chat"
        try:
            res = requests.post(rag_url, json={"query": query})
            if res.ok:
                st.success("Answer:")
                st.write(res.json().get("answer", "No response"))
            else:
                st.error("Failed to get a response from chatbot")
        except Exception as e:
            st.error(f"Exception: {e}")

# Admin Control 

=======
    st.subheader("Ask Government Scheme Bot")
    query = st.text_input("Ask a question (e.g., 'Eligibility for PMAY')")

    # Add a button to trigger the query
    if st.button("Ask") and query:  # Make sure query is not empty
        rag_url = f"http://localhost:{st.session_state['ports']['ragchatbot']}/ask"
        
        try:
            res = requests.post(rag_url, json={"query": query}, timeout=30)
            
            # Log the response status and content
            if res.ok:
                st.success("Answer:")
                st.write(res.json().get("answer", "No answer returned"))
            else:
                st.error(f"Failed to get chatbot response. Status Code: {res.status_code}")
                st.write(f"Response: {res.text}")
        
        except requests.exceptions.Timeout:
            st.error("Request timed out. The backend took too long to respond.")
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Could not connect to the backend.")
        except Exception as e:
            st.error(f"Chatbot error: {e}")

# === Admin Sidebar ===
>>>>>>> c6f723d (final commit)
st.sidebar.subheader("Admin Access")

if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    with st.sidebar.form("admin_login"):
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
<<<<<<< HEAD
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if admin_user == "admin" and admin_pass == "admin":  
=======
        if st.form_submit_button("Login"):
            if admin_user == "admin" and admin_pass == "admin":
>>>>>>> c6f723d (final commit)
                st.session_state["admin_authenticated"] = True
                st.success("Logged in as Admin")
            else:
                st.error("Invalid credentials")
else:
    st.sidebar.success("Admin Mode Enabled")

<<<<<<< HEAD
    st.subheader(" Admin Container Control")

    
    admin_res = requests.get(f"{API_URL}/admin/containers", headers=headers)
    if admin_res.ok:
        containers = admin_res.json()["containers"]
=======
    st.subheader("Admin Container Control")
    admin_res = requests.get(f"{API_URL}/admin/containers", headers=HEADERS)
    if admin_res.ok:
        containers = admin_res.json().get("containers", [])
>>>>>>> c6f723d (final commit)
        selected = []
        for c in containers:
            label = f"{c['name']} | {c['image']} | {c['status']}"
            if st.checkbox(label, key=c["id"]):
                selected.append(c["id"])
<<<<<<< HEAD

=======
>>>>>>> c6f723d (final commit)
        if st.button("Terminate Selected Containers"):
            if selected:
                kill_res = requests.post(
                    f"{API_URL}/admin/terminate",
<<<<<<< HEAD
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
=======
                    headers=HEADERS,
                    json={"container_ids": selected}
                )
                if kill_res.ok:
                    st.success(f"Terminated: {selected}")
                else:
                    st.error("Termination failed")
            else:
                st.warning("No containers selected.")
    else:
        st.error("Failed to fetch containers.")
>>>>>>> c6f723d (final commit)
