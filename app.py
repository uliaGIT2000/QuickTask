import json
import os
import sqlite3
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "quicktask.db"
JSON_DATA_FILE = "external_tasks.json"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# SYSTEM DATABASE SETUP & SCHEMA MIGRATION
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            energy TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# RESTful API Endpoint 1: Fetch and filter tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    energy = request.args.get('energy', 'high')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, energy FROM tasks WHERE energy = ? ORDER BY id DESC LIMIT 3", (energy,))
    rows = cur.fetchall()
    
    tasks = [{"id": row["id"], "title": row["title"], "energy": row["energy"]} for row in rows]
    
    cur.close()
    conn.close()
    return jsonify(tasks)

# RESTful API Endpoint 2: Add your own custom task manually
@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({"error": "Missing title"}), 400
            
        title = data['title']
        energy = data.get('energy', 'high')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", (title, energy))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Task added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RESTful API Endpoint 3: Read classified tasks from our external task data file
@app.route('/api/fetch-external', methods=['POST'])
def fetch_external_task():
    try:
        # Open and parse our structured local JSON file
        if os.path.exists(JSON_DATA_FILE):
            with open(JSON_DATA_FILE, "r") as f:
                dynamic_activities = json.load(f)
        else:
            raise FileNotFoundError("JSON Data file missing")
            
        # Pick an item randomly from the dataset array
        selected = random.choice(dynamic_activities)
        fetched_title = selected["activity"]
        activity_type = selected["type"]
        
        # Classify the task energy layout matching requirements
        fetched_energy = "low" if activity_type in ["relaxation", "music", "busywork"] else "high"
        
        # Persist the newly generated task directly into the SQL Database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", (fetched_title, fetched_energy))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Successfully generated classified task!", "task": fetched_title}), 201
        
    except Exception as e:
        # Fail-secure fallback route execution
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", ("Review application architecture layouts", "high"))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Saved fallback task", "task": "Review application architecture layouts"}), 201

# RESTful API Endpoint 4: Remove a task from the Database by ID
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        row_count = cur.rowcount
        cur.close()
        conn.close()
        
        if row_count == 0:
            return jsonify({"error": "Task not found"}), 404
            
        return jsonify({"message": "Task successfully removed!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
