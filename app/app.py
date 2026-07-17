import sqlite3
import subprocess
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Intentional Vulnerability: Hardcoded Secrets / Credentials
SUPER_SECRET_API_KEY = "secret_token_abc123xyz789"
ADMIN_PASSWORD = "AdminSecurePassword2026!"

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # Insert some dummy users if not exists
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'adminpass')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('guest', 'guestpass')")
        conn.commit()
    conn.close()

@app.route("/")
def index():
    return "Vulnerable Flask API is running!"

# Intentional Vulnerability: SQL Injection (raw query string concatenation)
@app.route("/api/user", methods=["GET"])
def get_user():
    username = request.args.get("username", "")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # SQLi query: concatenating input directly into the query
    query = f"SELECT id, username FROM users WHERE username = '{username}'"
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        users = [{"id": row[0], "username": row[1]} for row in result]
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

# Intentional Vulnerability: Command Injection (shell=True, direct string formatting)
@app.route("/api/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "")
    if not host:
        return jsonify({"error": "Missing host parameter"}), 400
    
    # Vulnerable to command injection (e.g. host="127.0.0.1; whoami" or "127.0.0.1 & whoami")
    # For compatibility, we'll run ping command. On Windows/Linux ping args slightly differ but shell=True works.
    cmd = f"ping -n 1 {host}" if os.name == 'nt' else f"ping -c 1 {host}"
    
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return jsonify({"status": "success", "output": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "failed", "output": e.output}), 400

# Endpoint to test API Key validation (demonstrating secret usage)
@app.route("/api/admin", methods=["GET"])
def admin_panel():
    api_key = request.headers.get("X-API-Key", "")
    if api_key != SUPER_SECRET_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Welcome to the admin panel!"})

if __name__ == "__main__":
    init_db()
    # Running in debug mode (bad practice for production)
    # Listening on all interfaces (0.0.0.0)
    app.run(host="0.0.0.0", port=5000, debug=True)
