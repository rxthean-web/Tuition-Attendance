from flask import Flask, render_template_string, request
import sqlite3
import datetime
import requests

app = Flask(__name__)

teachers = ["林老师", "洪老师", "郑老师", "陈老师", "邓茹昕", "刘老师", "邓宇迅"]

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
conn = sqlite3.connect("../school.db", check_same_thread=False)
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

# ===== HTML 页面 =====
html = """
<!DOCTYPE html>
<html>
<head>
<title>精明培育中心打卡系统</title>
</head>
<body style="font-family:Arial; text-align:center; background:#f2f2f2;">

<h2>📋 打卡系统</h2>

<form method="POST" style="background:white; padding:20px; width:300px; margin:auto; border-radius:10px;">

    <label>选择老师</label><br>
    <select name="teacher" style="width:100%; padding:8px;">
        <option value="">请选择</option>
        {% for t in teachers %}
        <option value="{{t}}">{{t}}</option>
        {% endfor %}
    </select>

    <br><br>

    <input name="subject" placeholder="科目 (Part Time)" style="width:100%; padding:8px;"><br><br>
    <input name="level" placeholder="年级 (Part Time)" style="width:100%; padding:8px;"><br><br>

    <button name="action" value="in" style="width:100%; padding:10px; margin:5px;">上班打卡</button>
    <button name="action" value="out" style="width:100%; padding:10px; margin:5px;">下班打卡</button>
    <button name="action" value="class" style="width:100%; padding:10px; margin:5px;">上课打卡</button>

</form>

</body>
</html>
"""

# ================= Route =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        teacher = request.form.get("teacher")
        action = request.form.get("action")
        subject = request.form.get("subject", "")
        level = request.form.get("level", "")

        if not teacher:
            return "请选择老师"

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
        INSERT INTO Attendance (teacher, time, type, subject, level)
        VALUES (?, ?, ?, ?, ?)
        """, (teacher, now, action, subject, level))

        conn.commit()

        # Telegram message
        if action == "class":
            msg = f"📢 上课通知\n{teacher}\n{level} {subject}\n{now}"
        else:
            msg = f"📢 打卡通知\n{teacher}\n{action}\n{now}"

        send_telegram(msg)

    return render_template_string(html, teachers=teachers)

# ================= Run =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
