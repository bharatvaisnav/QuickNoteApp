
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "notes.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/notes", methods=["GET"])
def get_notes():
    conn = get_db_connection()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(note) for note in notes])


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json()

    if not data or not data.get("content", "").strip():
        return jsonify({"error": "Note cannot be empty"}), 400

    content = data["content"].strip()

    conn = get_db_connection()

    cursor = conn.execute(
        "INSERT INTO notes (content) VALUES (?)",
        (content,)
    )

    conn.commit()

    note_id = cursor.lastrowid

    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(note)), 201


init_db()


if __name__ == "__main__":
    app.run(debug=True)
