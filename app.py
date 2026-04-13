from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime
import requests

app = Flask(__name__)

# ===== Telegram =====
BOT_TOKEN = "8724884045:AAFuDkAHDwHcQccnttQ1dl1OPyLNXnXNnLk"
CHAT_ID = "8791380535"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ===== DB =====
conn = sqlite3.connect("tuition.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher TEXT,
    time TEXT,
    type TEXT,
    subject TEXT,
    level TEXT
)
""")
conn.commit()

# ===== 首页（选择入口）=====
@app.route("/")
def home():
    return """
    <h2>打卡系统</h2>
    <a href='/fulltime'><button>Full Time</button></a>
    <a href='/parttime'><button>Part Time</button></a>
    """

# ===== Full Time =====
@app.route("/fulltime", methods=["GET", "POST"])
def fulltime():
    if request.method == "POST":
        teacher = request.form["teacher"]
        action = request.form["action"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
        INSERT INTO Attendance (teacher, time, type, subject, level)
        VALUES (?, ?, ?, '', '')
        """, (teacher, now, action))
        conn.commit()

        msg = f"📢 Full Time\n{teacher}\n{action}\n{now}"
        send_telegram(msg)

        return redirect(url_for("fulltime"))

    return render_template("fulltime.html")

# ===== Part Time =====
@app.route("/parttime", methods=["GET", "POST"])
def parttime():
    if request.method == "POST":
        teacher = request.form["teacher"]
        subject = request.form["subject"]
        level = request.form["level"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
        INSERT INTO Attendance (teacher, time, type, subject, level)
        VALUES (?, ?, 'class', ?, ?)
        """, (teacher, now, subject, level))
        conn.commit()

        msg = f"📢 Part Time\n{teacher}\n{level} {subject}\n{now}"
        send_telegram(msg)

        return redirect(url_for("parttime"))

    return render_template("parttime.html")

# ===== Run =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
