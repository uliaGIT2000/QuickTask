# QuickTask Planner

QuickTask is a minimalist, full-stack productivity web application designed to reduce task anxiety. Instead of overwhelming users with a long backlog, the app tracks and displays a maximum of three actionable tasks at a time, filtered by the user's current energy context (High or Low).

## Live Cloud Deployment
Live Deployment Link: https://onrender.com

## System Architecture and Stack
* **Frontend:** Plain HTML5 and Vanilla JavaScript using asynchronous fetch() API calls to handle instant UI updates without forcing full page reloads.
* **Backend:** Python Flask RESTful API engine managing system routing logic, file system reading, and relational table writes.
* **Data Storage:** A local relational SQLite3 Database (quicktask.db) that handles robust data persistence, alongside a structured catalog dataset file (external_tasks.json) acting as an internal repository for generating tasks.

## Core RESTful API Endpoints

### 1. Retrieve and Filter Tasks
* **Route:** GET /api/tasks
* **Query Parameter:** ?energy=high or ?energy=low (Defaults to high)
* **Behavior:** Queries the database table for rows matching the targeted energy context and restricts the return array to a maximum threshold of 3 items.

### 2. Manual Task Creation
* **Route:** POST /api/tasks
* **Payload Format:** JSON containing title and energy parameters.
* **Behavior:** Processes and appends custom, user-defined task data rows directly into the relational SQLite tracking schema table.

### 3. Classified External Task Generator
* **Route:** POST /api/fetch-external
* **Behavior:** Opens the internal catalog repository (external_tasks.json), randomly picks a task string, parses its required energy allocation metric, and commits it securely into the SQL database schema.

### 4. Record Purging Function
* **Route:** DELETE /api/tasks/<int:task_id>
* **Behavior:** Validates an exact record primary key parameter against the persistent database records and wipes that unique row entirely from memory storage.

## How to Run Locally

1. Ensure you have Python 3 installed on your computer.
2. Open your terminal window and navigate into your project folder directory:
   ```bash
   cd ~/Desktop/QuickTask
   ```
3. Initialize the application engine server:
   ```bash
   python app.py
   ```
4. Open your web browser and navigate directly to your local execution instance environment:
   http://localhost:8080

## Verification and Testability Parameters

* **Database Auto-Initialization:** Wiping quicktask.db locally and running the server forces init_db() to automatically generate a fresh SQLite tracking layout with proper structural schema parameters on boot.
* **Database Volume Restriction:** If you input or generate five tasks under the same context tier, the interface will only display the 3 most recent entries, validating the LIMIT 3 database filter.
* **Data Removal Validation:** Clicking the Delete action on a live task element maps its target index into the DELETE route, immediately cleaning out the database rows and refreshing your screen footprint.
