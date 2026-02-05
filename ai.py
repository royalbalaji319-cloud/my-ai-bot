from flask import Flask, render_template, request, jsonify
import subprocess
import sqlite3

app = Flask(__name__)

OLLAMA_PATH = r"C:\Users\akula\AppData\Local\Programs\Ollama\ollama.exe"
MODEL = "gemma3:1b"

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


def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")


def ask_ollama(msg):
    system_prompt = (
        "You are My AI Chatbot.\n"
        "Your name is My AI.\n"
        "You are friendly and helpful.\n"
        "Do NOT mention Google, Gemma, or DeepMind.\n"
    )

    prompt = system_prompt + "\nUser: " + msg + "\nAI:"

    result = subprocess.run(
        [OLLAMA_PATH, "run", MODEL],
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="ignore",
        capture_output=True
    )

    return clean_text(result.stdout.strip())


@app.route("/")
def home():
    cur.execute("SELECT user, ai FROM chat")
    chats = cur.fetchall()
    return render_template("index.html", chats=chats)


@app.route("/chat", methods=["POST"])
def chat():
    user = request.json["message"]
    ai = ask_ollama(user)

    cur.execute("INSERT INTO chat (user, ai) VALUES (?, ?)", (user, ai))
    conn.commit()

    return jsonify({"user": user, "ai": ai})


if __name__ == "__main__":
    app.run(debug=True)
