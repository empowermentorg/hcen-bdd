from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)

DB = "reports.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            alias TEXT,
            phone TEXT,
            vehicle_color TEXT,
            vehicle_type TEXT,
            vehicle_make_model TEXT,
            license_plate TEXT,
            appearance TEXT,
            features TEXT,
            location TEXT,
            incident TEXT,
            reported_to_police TEXT,
            wants_help_reporting TEXT,
            status TEXT,
            created_at TEXT
        )''')

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = { key: request.form.get(key, "") for key in request.form }
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO reports VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            str(uuid.uuid4()),
            data["alias"],
            data["phone"],
            data["vehicle_color"],
            data["vehicle_type"],
            data["vehicle_make_model"],
            data["license_plate"],
            data["appearance"],
            data["features"],
            data["location"],
            data["incident"],
            data.get("reported_to_police", "no"),
            data.get("wants_help_reporting", "no"),
            "pending",
            datetime.utcnow().isoformat()
        ))
    return redirect(url_for("form"))

@app.route("/admin")
def admin():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM reports WHERE status = 'pending'")
        pending = c.fetchall()
    return render_template("admin.html", reports=pending)

@app.route("/approve/<rid>")
def approve(rid):
    with sqlite3.connect(DB) as conn:
        conn.execute("UPDATE reports SET status='approved' WHERE id=?", (rid,))
    return redirect(url_for("admin"))

@app.route("/reject/<rid>")
def reject(rid):
    with sqlite3.connect(DB) as conn:
        conn.execute("UPDATE reports SET status='rejected' WHERE id=?", (rid,))
    return redirect(url_for("admin"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0")