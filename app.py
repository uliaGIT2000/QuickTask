import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_FILE = "tasks.json"

# Read tasks from our local file
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save tasks to our local file
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# RESTful API Endpoint 1: Fetch and filter tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    energy = request.args.get('energy', 'high')
    all_tasks = load_tasks()
    filtered = [t for t in all_tasks if t.get('energy') == energy]
    # Restrict the view to a maximum of 3 items
    return jsonify(filtered[:3])

# RESTful API Endpoint 2: Add a new task
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Missing title"}), 400
        
    all_tasks = load_tasks()
    new_task = {
        "id": len(all_tasks) + 1,
        "title": data['title'],
        "energy": data.get('energy', 'high')
    }
    all_tasks.append(new_task)
    save_tasks(all_tasks)
    return jsonify(new_task), 201

# Serve our user interface front-end file
@app.route('/')
def home():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == '__main__':
    # Read the environment port dynamically for cloud hosting compatibility
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

