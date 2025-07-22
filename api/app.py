from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', 'World')
        return jsonify({"message": f"Hello, {name}"})
    return "Send a POST with JSON {'name': ...}"

@app.route('/hello')
def hello_query():
    name = request.args.get('name', 'World')
    return f"Hello {name}", 200

@app.route('/health')
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
