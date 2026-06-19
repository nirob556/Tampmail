import os
import random
import string
import json
from threading import Thread
import requests
from flask import Flask, render_template_string, jsonify, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ================= CONFIGURATION =================
BOT_TOKEN = "8446272435:AAGpS9p7fTs7IlCcAuGdO8vWJd44oB0NPy8"      # আপনার বট টোকেন দিন
ADMIN_ID = 7224513731                  # আপনার নিজের টেলিগ্রাম আইডি (숫자) দিন
CHANNEL_USERNAME = "SPEED_X_OFFICIAL1"     # '@' ছাড়া আপনার চ্যানেলের ইউজারনেম দিন

# Branding & Credits
CREDIT_NAME = "SPEED_X"
DEV_NAME = "NIROB BBZ"

# Simple Database to track users (In-Memory for easy deployment)
USER_DB = {}

app = Flask(__name__)

# ================= TELEGRAM BOT LOGIC =================

# Channel Join Checker
async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False
    return False

# Start Handler
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Track user info
    USER_DB[user_id] = {
        "name": user.full_name,
        "username": user.username or "No_Username",
        "mails_generated": USER_DB.get(user_id, {}).get("mails_generated", 0),
        "web_visits": USER_DB.get(user_id, {}).get("web_visits", 0)
    }
    
    # Notify Admin about new/active user activity (VIP Admin Alert)
    try:
        admin_alert = (
            f"👑 **[VIP ADMIN ALERT]** 👑\n\n"
            f"👤 **User:** {user.full_name}\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"🌐 **Username:** @{user.username or 'None'}\n"
            f"⚡ **Action:** Started the Bot!"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="Markdown")
    except Exception:
        pass

    joined = await is_user_joined(context, user_id)
    
    # Dynamic WebApp URL detection for Render/Localhost
    web_app_url = request.host_url if request else "http://localhost:5000/"
    # Appending user metadata to URL safely for WebApp Preview
    web_app_final_url = f"{web_app_url}?user_id={user_id}&name={requests.utils.quote(user.full_name)}&username={user.username or 'None'}"

    if not joined:
        text = (
            f"⚡ **WELCOME TO PREMIUM TEMP MAIL BOT** ⚡\n\n"
            f"🛑 `You must join our channel to use this VIP bot!`\n\n"
            f"📢 **Channel:** @{CHANNEL_USERNAME}\n\n"
            f"👤 **Developer:** {DEV_NAME}\n"
            f"🔥 **Powered by:** {CREDIT_NAME}"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("🔄 Verify / Start Again", url=f"https://t.me/{(await context.bot.get_me()).username}?start=true")]
        ])
        await update.message.reply_text(text, reply_markup=buttons, parse_mode="Markdown")
    else:
        text = (
            f"🔴 ✨ **WELCOME TO VIP TEMP MAIL HUB** ✨ 🔴\n\n"
            f"Your access has been **Verified** successfully! ✅\n"
            f"You can now generate premium temp mails directly inside Telegram WebApp.\n\n"
            f"👑 **Created by:** {CREDIT_NAME}\n"
            f"💻 **Developer:** {DEV_NAME}"
        )
        
        # Bottom corner / persistent Keyboard WebApp Menu Button
        reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton("🌐 Open VIP WebApp", web_app_info=WebAppInfo(url=web_app_final_url))]
        ], resize_keyboard=True)
        
        # Inline Button under the message
        inline_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Launch WebApp Now", web_app_info=WebAppInfo(url=web_app_final_url))],
            [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ])
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        await update.message.reply_text("👇 Click the button below to start generating mails!", reply_markup=inline_markup)

# Admin Panel Command
async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
        
    total_users = len(USER_DB)
    text = f"⚙️ 👑 **VIP ADMIN PANEL ({CREDIT_NAME})** 👑 ⚙️\n\n"
    text += f"📊 **Total Active Users Tracked:** {total_users}\n\n"
    
    for uid, data in USER_DB.items():
        text += f"👤 **Name:** {data['name']}\n🆔 **ID:** `{uid}`\n🌐 **User:** @{data['username']}\n📧 **Mails Gen:** {data['mails_generated']} | 🕸️ **Web Visits:** {data['web_visits']}\n──────────────────\n"
        
    await update.message.reply_text(text, parse_mode="Markdown")


# ================= FLASK WEBAPP & UI =================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIP Temp Mail Hub</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
    <style>
        :root {
            --neon-red: #ff0055;
            --neon-blue: #00ffff;
            --bg-dark: #0a0a0c;
            --card-bg: rgba(20, 20, 25, 0.85);
        }
        body {
            margin: 0; padding: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--bg-dark); color: #ffffff;
            overflow-x: hidden;
        }
        #particles-js { position: fixed; width: 100%; height: 100%; z-index: -1; }
        .container { max-width: 600px; margin: 20px auto; padding: 15px; box-sizing: border-box; }
        .vip-card {
            background: var(--card-bg); border: 2px solid var(--neon-red);
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.3); border-radius: 15px;
            padding: 25px; text-align: center; backdrop-filter: blur(10px); margin-bottom: 20px;
        }
        .vip-title {
            font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;
            text-shadow: 0 0 10px var(--neon-red), 0 0 20px var(--neon-red); margin-bottom: 5px;
        }
        .vip-subtitle { font-size: 11px; color: var(--neon-blue); text-transform: uppercase; letter-spacing: 3px; margin-bottom: 20px; }
        .profile-sec {
            display: flex; align-items: center; justify-content: center; gap: 15px;
            background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid var(--neon-blue);
        }
        .profile-img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid var(--neon-blue); }
        .profile-info { text-align: left; }
        .profile-info h4 { margin: 0; color: #fff; }
        .profile-info p { margin: 0; font-size: 12px; color: #aaa; }
        .mail-box, .pass-box {
            background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
            padding: 14px; border-radius: 8px; font-size: 15px; word-break: break-all;
            margin-top: 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer;
        }
        .mail-box { color: var(--neon-blue); font-weight: bold; }
        .pass-box { color: #ffcc00; font-size: 14px; margin-top: 10px; }
        .btn-vip {
            background: linear-gradient(45deg, var(--neon-red), #b3003b); color: white;
            border: none; padding: 12px 25px; font-size: 14px; font-weight: bold;
            text-transform: uppercase; border-radius: 8px; cursor: pointer;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.4); transition: 0.3s; width: 100%; margin-top: 15px;
        }
        .btn-vip:hover { box-shadow: 0 0 25px rgba(255, 0, 85, 0.8); transform: scale(1.01); }
        .inbox-title { text-align: left; font-size: 18px; border-left: 4px solid var(--neon-red); padding-left: 10px; margin: 25px 0 15px 0; text-transform: uppercase; }
        .email-list { display: flex; flex-direction: column; gap: 10px; }
        .email-item { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; text-align: left; cursor: pointer; }
        .email-item:hover { border-color: var(--neon-blue); background: rgba(0, 255, 255, 0.05); }
        .email-meta { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 5px; }
        .email-sender { font-weight: bold; color: var(--neon-blue); }
        .email-subject { font-size: 14px; font-weight: 500; }
        .email-body { margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.4); border-radius: 5px; font-size: 13px; color: #ddd; display: none; white-space: pre-wrap; border-top: 1px solid rgba(255,255,255,0.05); }
        .tg-join-btn { background: #24A1DE; color: white; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 10px; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 30px; box-shadow: 0 0 10px rgba(36, 161, 222, 0.4); }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--neon-blue); color: #000; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; display: none; z-index: 999; box-shadow: 0 0 15px var(--neon-blue); }
    </style>
</head>
<body>
<div id="particles-js"></div>
<div class="container">
    <div class="vip-card">
        <div class="vip-title">{{ credit_name }} MAIL HUB</div>
        <div class="vip-subtitle">VIP Premium Temp Mail UI</div>

        <div class="profile-sec">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=VIP" class="profile-img" id="userPhoto">
            <div class="profile-info">
                <h4 id="userName">{{ name }}</h4>
                <p id="userMeta">ID: {{ user_id }} | @{{ username }}</p>
            </div>
        </div>

        <button class="btn-vip" onclick="generateNewMail()">⚡ Generate New Mail</button>

        <div class="mail-box" onclick="copyText('currentMail')">
            <span id="currentMail">Click Generate Button</span>
            <span style="font-size: 11px; color: #888;">📋 COPY</span>
        </div>
        <div class="pass-box" onclick="copyText('currentPass')">
            <span id="currentPass">Password: speedx_******</span>
            <span style="font-size: 11px; color: #888;">📋 COPY</span>
        </div>
    </div>

    <div class="inbox-title">📥 Live Inbox (Auto Refreshing)</div>
    <div class="email-list" id="emailList">
        <p style="text-align: center; color: #555;">No mail active. Click generate to start receiving.</p>
    </div>

    <a href="https://t.me/{{ channel_username }}" target="_blank" class="tg-join-btn">✈️ Join Official Telegram Channel</a>
</div>
<div class="toast" id="toast">Copied!</div>

<script>
    const tg = window.Telegram.WebApp;
    tg.ready(); tg.expand();

    let currentEmailUser = "";
    let currentEmailDomain = "";
    const userId = "{{ user_id }}";

    // Inform backend of a web view log
    fetch(`/api/log-visit?user_id=${userId}`);

    function generateNewMail() {
        fetch(`/api/gen-mail?user_id=${userId}`)
            .then(res => res.json())
            .then(data => {
                currentEmailUser = data.user;
                currentEmailDomain = data.domain;
                document.getElementById('currentMail').innerText = data.email;
                document.getElementById('currentPass').innerText = data.password;
                showToast("VIP Mail Created!");
                fetchInbox();
            });
    }

    function fetchInbox() {
        if (!currentEmailUser || !currentEmailDomain) return;
        fetch(`/api/get-inbox?user=${currentEmailUser}&domain=${currentEmailDomain}`)
            .then(res => res.json())
            .then(emails => {
                const list = document.getElementById('emailList');
                if (emails.length === 0) {
                    list.innerHTML = '<p style="text-align: center; color: #666;">Inbox is empty. Awaiting verification messages...</p>';
                    return;
                }
                list.innerHTML = "";
                emails.forEach((email, index) => {
                    const item = document.createElement('div');
                    item.className = 'email-item';
                    item.onclick = () => {
                        const b = document.getElementById(`body-${index}`);
                        b.style.display = b.style.display === 'block' ? 'none' : 'block';
                    };
                    item.innerHTML = `
                        <div class="email-meta"><span class="email-sender">From: ${email.from}</span><span>${email.date}</span></div>
                        <div class="email-subject">📝 ${email.subject}</div>
                        <div class="email-body" id="body-${index}" onclick="event.stopPropagation();">
                            <div style="text-align:right;"><button onclick="copyRawText(document.getElementById('text-${index}').innerText)" style="background:#222; color:var(--neon-blue); border:1px solid var(--neon-blue); border-radius:4px; padding:2px 6px; font-size:11px; cursor:pointer;">Copy Content</button></div>
                            <span id="text-${index}">${email.textBody || email.htmlBody || 'No data'}</span>
                        </div>`;
                    list.appendChild(item);
                });
            });
    }

    function copyText(id) {
        const text = document.getElementById(id).innerText.replace("Password: ", "");
        if(text.includes("Click") || text.includes("speedx_***")) return;
        copyRawText(text);
    }
    function copyRawText(text) {
        navigator.clipboard.writeText(text).then(() => showToast("Copied to clipboard! 📋"));
    }
    function showToast(msg) {
        const t = document.getElementById('toast'); t.innerText = msg; t.style.display = 'block';
        setTimeout(() => t.style.display = 'none', 1800);
    }

    setInterval(fetchInbox, 2500); // Live high-frequency polling every 2.5s

    particlesJS('particles-js', {
        "particles": {
            "number": {"value": 45}, "color": {"value": "#ff0055"},
            "shape": {"type": "circle"}, "opacity": {"value": 0.25}, "size": {"value": 3},
            "line_linked": {"enable": true, "distance": 140, "color": "#00ffff", "opacity": 0.15, "width": 1},
            "move": {"enable": true, "speed": 1.5}
        }
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    user_id = request.args.get('user_id', 'Unknown')
    name = request.args.get('name', 'VIP User')
    username = request.args.get('username', 'None')
    return render_template_string(HTML_TEMPLATE, user_id=user_id, name=name, username=username, credit_name=CREDIT_NAME, channel_username=CHANNEL_USERNAME)

@app.route('/api/log-visit')
def log_visit():
    uid = request.args.get('user_id')
    if uid and int(uid) in USER_DB:
        USER_DB[int(uid)]["web_visits"] += 1
    return jsonify({"status": "ok"})

@app.route('/api/gen-mail')
def gen_mail():
    uid = request.args.get('user_id')
    if uid and int(uid) in USER_DB:
        USER_DB[int(uid)]["mails_generated"] += 1
        
    domains = ["1secmail.com", "1secmail.org", "1secmail.net"]
    domain = random.choice(domains)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    password = f"speedx_{random_suffix}"
    
    return jsonify({
        "user": username, "domain": domain, "email": f"{username}@{domain}", "password": password
    })

@app.route('/api/get-inbox')
def get_inbox():
    user = request.args.get('user')
    domain = request.args.get('domain')
    if not user or not domain: return jsonify([])
    
    try:
        res = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}").json()
        full_emails = []
        for msg in res[:4]:
            detail = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={user}&domain={domain}&id={msg['id']}").json()
            full_emails.append(detail)
        return jsonify(full_emails)
    except:
        return jsonify([])

# ================= RUNNER =================

def run_tg_bot():
    # Build bot application using only the Token safely
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("admin", admin_handler))
    
    application.run_polling()

if __name__ == "__main__":
    # Start Telegram Bot thread
    tg_thread = Thread(target=run_tg_bot)
    tg_thread.daemon = True
    tg_thread.start()

    # Start Flask Web app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
