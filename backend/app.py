from flask import Flask, request, jsonify
import subprocess
import os
import yaml
from dotenv import load_dotenv
import uuid
import socket
import glob

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "supersecret")

used_ports = set() 
def find_free_port(start=5001, end=6000):
    for port in range(start, end):
        if port in used_ports:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                used_ports.add(port)
                return port
    raise RuntimeError("No free port available in range")

def get_compose_path(user_id):
    """Compose filename for this session/user"""
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base_dir, f"../docker-compose.generated.{user_id}.yml"))

# Auth decorator
def require_auth(f):
    def wrapper(*args, **kwargs):
        if request.headers.get("x-api-key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/generate_compose", methods=["POST"])
@require_auth
def generate_compose():
    user_id = uuid.uuid4().hex
    body = request.json
    services = {}
    port_map = {}

    # === API Microservice ===
    if body.get("include_api"):
        api_port = find_free_port()
        services["api"] = {
            "build": os.path.abspath(os.path.join(os.path.dirname(__file__), "../api")),
            "ports": [f"{api_port}:5000"]
        }
        port_map["api"] = api_port

    # === PostgreSQL Database ===
    if body.get("include_db"):
        db_port = find_free_port(5433, 6000)
        services["db"] = {
            "image": "postgres",
            "environment": {"POSTGRES_PASSWORD": "example"},
            "ports": [f"{db_port}:5432"]
        }
        port_map["db"] = db_port

    # === Redis ===
    if body.get("include_redis"):
        redis_port = find_free_port(6380, 7000)
        services["redis"] = {
            "image": "redis",
            "ports": [f"{redis_port}:6379"]
        }
        port_map["redis"] = redis_port

    # === RAG Chatbot Microservice ===
    if body.get("include_ragchatbot"):
        rag_port = find_free_port()
        services["ragchatbot"] = {
            "build": os.path.abspath(os.path.join(os.path.dirname(__file__), "../rag-chatbot")),  
            "ports": [f"{rag_port}:8000"],
            "env_file": os.path.abspath(os.path.join(os.path.dirname(__file__), "../rag-chatbot/.env")),  
            "restart": "unless-stopped"
        }
        port_map["ragchatbot"] = rag_port

    # === If nothing was selected ===
    if not services:
        return jsonify({"error": "No services selected"}), 400

    # === Save compose file ===
    compose = {"version": "3", "services": services}
    compose_path = get_compose_path(user_id)
    with open(compose_path, "w") as f:
        yaml.dump(compose, f)

    return jsonify({
        "compose": yaml.dump(compose),
        "compose_path": compose_path,
        "ports": port_map,
        "user_id": user_id
    })


# Route to deploy services
@app.route("/deploy", methods=["POST"])
@require_auth
def deploy():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    compose_path = get_compose_path(user_id)
    if not os.path.exists(compose_path):
        return jsonify({"error": "Compose file does not exist"}), 400

    try:
        subprocess.run(
            ["docker", "compose","-p", user_id, "-f", compose_path, "up", "-d"],
            cwd=os.path.dirname(compose_path),
            check=True
        )
        return jsonify({"status": "Deployment started", "compose_path": compose_path})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

# Route to terminate containers
@app.route("/terminate", methods=["POST"])
@require_auth
def terminate():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    compose_path = get_compose_path(user_id)
    if not os.path.exists(compose_path):
        return jsonify({"error": "Compose file does not exist"}), 400

    try:
        subprocess.run(
            ["docker", "compose","-p", user_id, "-f", compose_path, "down"],
            cwd=os.path.dirname(compose_path),
            check=True
        )
        return jsonify({"status": "Containers terminated"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status", methods=["GET"])
@require_auth
def status():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    compose_path = get_compose_path(user_id)
    try:
        # Show only containers for this user's project
        if os.path.exists(compose_path):
            ps = subprocess.check_output([
                "docker", "compose", "-p", user_id, "-f", compose_path, "ps"
            ]).decode("utf-8")
            with open(compose_path) as f:
                cfg = yaml.safe_load(f)
            api_port = None
            if "api" in cfg.get("services", {}):
                api_port = int(cfg["services"]["api"]["ports"][0].split(":")[0])
        else:
            ps = "No compose file found."
            api_port = 5051

        try:
            res = subprocess.check_output([
                "curl", "-s", f"http://localhost:{api_port}/hello?name=Test"
            ]).decode("utf-8")
        except subprocess.CalledProcessError:
            res = "API not reachable"

        return jsonify({
            "docker_ps": ps,
            "api_health": res,
            "compose_path": compose_path
        })
    except Exception as e:
        return str(e), 500
import docker
client = docker.from_env()

@app.route("/admin/containers", methods=["GET"]) 
@require_auth
def list_all_containers():
    try:
        output = subprocess.check_output([
            "docker", "ps", "-a", "--format", "{{.ID}}::{{.Image}}::{{.Status}}::{{.Names}}"
        ]).decode("utf-8")
        
        containers = []
        for line in output.strip().splitlines():
            container_id, image, status, name = line.split("::")
            containers.append({
                "id": container_id,
                "image": image,
                "status": status,
                "name": name
            })
        return jsonify({"containers": containers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/terminate", methods=["POST"])
@require_auth
def terminate_selected_containers():
    data = request.get_json()
    container_ids = data.get("container_ids", [])
    if not container_ids:
        return jsonify({"error": "No container IDs provided"}), 400
    try:
        subprocess.run(["docker", "rm", "-f"] + container_ids, check=True)
        return jsonify({"status": "terminated", "containers": container_ids})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
