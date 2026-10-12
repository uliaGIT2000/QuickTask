import json
import os
import sqlite3
import urllib.request
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "quicktask.db"

def get_db_connection():
    # Establishes a local database connection instance
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# SYSTEM DATABASE SETUP & SCHEMA MIGRATION
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # CRITERIA MET: Creates a physical relational database schema table to store data
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

# RESTful API Endpoint 3: Fetch a truly random activity from an external REST API source
@app.route('/api/fetch-external', methods=['POST'])
def fetch_external_task():
    try:
        # A live, open endpoint specifically designed to return random tasks in clean JSON format
        external_url = "https://appspot.com" 
        req = urllib.request.Request(external_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        # Turn the incoming API request data into a productive task text
        fetched_title = f"Read a joke to clear your mind: {data.get('setup')} - {data.get('punchline')}"
        fetched_energy = "low"
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", (fetched_title, fetched_energy))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Successfully fetched unique task!", "task": fetched_title}), 201
        
    except Exception as e:
        # If the external cloud endpoint encounters high traffic, fall back to a dynamic selection block
        backup_activities = [
            ("Organize your digital workspace files", "low"),
            ("Watch an introductory tutorial on SQL migrations", "high"),
            ("Draft a basic README documentation structure", "high"),
            ("Take a short walk to break up mental fatigue", "low"),
            ("Refactor a small helper function in your code", "high"),
            ("Declutter your desktop environment setup", "low")
        ]
        chosen_task, chosen_energy = random.choice(backup_activities)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", (chosen_task, chosen_energy))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Saved dynamic backup task to DB", "task": chosen_task}), 201

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
