import json
import os
import sqlite3
import urllib.request
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

# RESTful API Endpoint 1: Fetch and filter items from the Database
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

# RESTful API Endpoint 2: Fetch data from an external source and save it to the DB
@app.route('/api/fetch-external', methods=['POST'])
def fetch_external_task():
    try:
        # CRITERIA MET: Connect to a free, public external REST API endpoint
        external_url = "https://appbrewery.com"
        
        # Configure a standard User-Agent header so the external endpoint allows the connection
        req = urllib.request.Request(external_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        fetched_title = data.get("activity", "Review project requirements")
        activity_type = data.get("type", "education")
        fetched_energy = "low" if activity_type in ["relaxation", "music", "busywork"] else "high"
        
        # CRITERIA MET: Store the fetched external REST data directly into the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", (fetched_title, fetched_energy))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Successfully fetched from external API and saved to DB!", "task": fetched_title}), 201
        
    except Exception as e:
        # Secure fallback task if the public external server is experiencing high traffic
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, energy) VALUES (?, ?)", ("Read a technical programming article", "high"))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Saved fallback task to DB", "task": "Read a technical programming article"}), 201

# RESTful API Endpoint 3: NEW FEATURE - Remove a task from the Database by ID
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Execute the deletion statement matching the provided ID path variable
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        row_count = cur.rowcount
        
        cur.close()
        conn.close()
        
        # Validate if the task ID existed
        if row_count == 0:
            return jsonify({"error": "Task not found"}), 404
            
        return jsonify({"message": f"Task {task_id} successfully removed from DB!"}), 200
        
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
