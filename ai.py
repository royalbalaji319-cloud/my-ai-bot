from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from openai import OpenAI

# ------------------ CONFIG ------------------
app = Flask(__name__)

# OpenAI client (API key from Render ENV)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------ DATABASE ------------------
conn = sqlite3.connect("chat.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    ai TEXT
)
""")
conn.commit()

# ------------------ AI FUNCTION ------------------
def ask_ai(message):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=message
    )
    return response.output_text

# ------------------ ROUTES ------------------
@app.route("/")
def home():
    cur.execute("SELECT user, ai FROM chat")
    chats = cur.fetchall()
    return render_template("index.html", chats=chats)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json["message"]
    ai_msg = ask_ai(user_msg)

    cur.execute(
        "INSERT INTO chat (user, ai) VALUES (?, ?)",
        (user_msg, ai_msg)
    )
    conn.commit()

    return jsonify({"user": user_msg, "ai": ai_msg})

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run()
