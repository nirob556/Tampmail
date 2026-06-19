import os
import random
import string
import requests
import asyncio
from flask import Flask, render_template_string, jsonify, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= CONFIGURATION =================
BOT_TOKEN = "8446272435:AAGpS9p7fTs7IlCcAuGdO8vWJd44oB0NPy8"      
ADMIN_ID = 7224513731                  
CHANNEL_USERNAME = "SPEED_X_OFFICIAL1"     

# Branding & Credits
CREDIT_NAME = "SPEED_X"
DEV_NAME = "NIROB BBZ"

USER_DB = {}

app = Flask(__name__)

# ================= TELEGRAM BOT LOGIC =================

async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False
    return False

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    USER_DB[user_id] = {
        "name": user.full_name,
        "username": user.username or "No_Username",
        "mails_generated": USER_DB.get(user_id, {}).get("mails_generated", 0),
        "web_visits": USER_DB.get(user_id, {}).get("web_visits", 0)
    }
    
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
    
    # Request checking inside bot context securely
    web_app_url = f"https://{request.host}" if (request and request.host) else "http://localhost:5000"
    web_app_final_url = f"{web_app_url}/?user_id={user_id}&name={requests.utils.quote(user.full_name)}&username={user.username or 'None'}"

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
        
        reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton("🌐 Open VIP WebApp", web_app_info=WebAppInfo(url=web_app_final_url))]
        ], resize_keyboard=True)
        
        inline_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Launch WebApp Now", web_app_info=WebAppInfo(url=web_app_final_url))],
            [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ])
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        await update.message.reply_text("👇 Click the button below to start generating mails!", reply_markup=inline_markup)

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
        
    total_users = len(USER_DB)
    text = f"⚙️ 👑 **VIP ADMIN PANEL ({CREDIT_NAME})** 👑 ⚙️\n\n"
    text += f"📊 **Total Active Users Tracked:** {total_users}\n\n"
    
    for uid, data in USER_DB.items():
        text += f"👤 **Name:** {data['name']}\n🆔 **ID:** `{uid}`\n🌐 **User:** @{data['username']}\n📧 **Mails Gen:** {data['mails_generated']} | 🕸️ **Web Visits:** {data['web_visits']}\n──────────────────\n"
        
    await update.message.reply_text(text, parse_mode="Markdown")


# ================= HIGH-END VIP GLOSSY WEBAPP UI =================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIP Premium Mail Hub</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
    <style>
        :root {
            --neon-pink: #ff0055;
            --neon-cyan: #00ffff;
            --glass-bg: rgba(10, 10, 15, 0.75);
            --border-glass: rgba(255, 255, 255, 0.08);
        }
        body {
            margin: 0; padding: 0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #050508 0%, #0c0d14 100%);
            color: #ffffff; overflow-x: hidden;
        }
        #particles-js { position: fixed; width: 100%; height: 100%; z-index: -1; }
        .container { max-width: 500px; margin: 0 auto; padding: 20px 15px; box-sizing: border-box; }
        
        /* Glassmorphism VIP Card */
        .vip-card {
            background: var(--glass-bg);
            border: 1px solid var(--border-glass);
            border-top: 2px solid var(--neon-pink);
            border-bottom: 2px solid var(--neon-cyan);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(255, 0, 85, 0.15);
            border-radius: 20px; padding: 30px 20px; text-align: center;
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            margin-bottom: 25px; position: relative;
        }
        .vip-title {
            font-size: 26px; font-weight: 900; letter-spacing: 3px;
            background: linear-gradient(to right, #fff, #ff80aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255, 0, 85, 0.6); margin-bottom: 5px;
        }
        .vip-subtitle { font-size: 11px; color: var(--neon-cyan); font-weight: bold; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 25px; }
        
        /* Profile Layout */
        .profile-sec {
            display: flex; align-items: center; gap: 15px;
            background: rgba(255, 255, 255, 0.03); padding: 12px 18px;
            border-radius: 14px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.05);
        }
        .profile-img { width: 48px; height: 48px; border-radius: 50%; border: 2px solid var(--neon-cyan); box-shadow: 0 0 10px rgba(0,255,255,0.2); }
        .profile-info { text-align: left; }
        .profile-info h4 { margin: 0; color: #fff; font-size: 15px; font-weight: 700; }
        .profile-info p { margin: 3px 0 0 0; font-size: 11px; color: #8a8d98; }
        
        .mail-box, .pass-box {
            background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 16px; border-radius: 12px; font-size: 15px; word-break: break-all;
            margin-top: 15px; display: flex; justify-content: space-between; align-items: center;
            transition: all 0.3s ease;
        }
        .mail-box:hover, .pass-box:hover { border-color: rgba(255, 255, 255, 0.15); background: rgba(255,255,255,0.02); }
        .mail-box { color: var(--neon-cyan); font-weight: 700; font-family: 'Courier New', monospace; font-size: 16px; }
        .pass-box { color: #ffcc00; font-size: 14px; margin-top: 12px; }
        .copy-badge { font-size: 10px; background: rgba(255,255,255,0.08); padding: 4px 8px; border-radius: 6px; color: #aaa; letter-spacing: 1px; }

        .btn-vip {
            background: linear-gradient(90deg, var(--neon-pink) 0%, #cc0044 100%); color: white;
            border: none; padding: 15px; font-size: 14px; font-weight: 800;
            text-transform: uppercase; border-radius: 12px; cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 0, 85, 0.3); transition: all 0.3s ease; width: 100%; margin-top: 10px;
        }
        .btn-vip:hover { box-shadow: 0 0 25px rgba(255, 0, 85, 0.6); transform: translateY(-1px); }
        
        /* Premium Inbox */
        .inbox-title { text-align: left; font-size: 16px; font-weight: 800; border-left: 4px solid var(--neon-pink); padding-left: 12px; margin: 30px 0 15px 0; text-transform: uppercase; letter-spacing: 1px; }
        .email-list { display: flex; flex-direction: column; gap: 12px; }
        .email-item {
            background: var(--glass-bg); border: 1px solid var(--border-glass); border-radius: 14px;
            padding: 16px; text-align: left; transition: all 0.2s ease; backdrop-filter: blur(10px);
        }
        .email-item:hover { border-color: var(--neon-cyan); box-shadow: 0 0 15px rgba(0, 255, 255, 0.08); }
        .email-meta { display: flex; justify-content: space-between; font-size: 11px; color: #71747c; margin-bottom: 6px; }
        .email-sender { font-weight: 700; color: var(--neon-cyan); }
        .email-subject { font-size: 14px; font-weight: 600; color: #f1f1f3; }
        .email-body {
            margin-top: 12px; padding: 12px; background: rgba(0, 0, 0, 0.5); border-radius: 8px;
            font-size: 13px; color: #d1d2d6; display: none; white-space: pre-wrap; line-height: 1.5;
            border: 1px solid rgba(255,255,255,0.04);
        }
        
        .tg-join-btn {
            background: linear-gradient(90deg, #1d93d2 0%, #24A1DE 100%); color: white; text-decoration: none;
            display: flex; align-items: center; justify-content: center; gap: 10px; padding: 14px;
            border-radius: 12px; font-weight: 700; margin-top: 35px; font-size: 14px;
        }
        .toast {
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); background: #fff;
            color: #000; padding: 10px 24px; border-radius: 30px; font-weight: 800; font-size: 12px;
            display: none; z-index: 1000; box-shadow: 0 10px 25px rgba(255,255,255,0.3); text-transform: uppercase;
        }
    </style>
</head>
<body>
<div id="particles-js"></div>
<div class="container">
    <div class="vip-card">
        <div class="vip-title">{{ credit_name }} MAIL HUB</div>
        <div class="vip-subtitle">VIP Premium Temp Mail UI</div>

        <div class="profile-sec">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed={{ user_id }}" class="profile-img">
            <div class="profile-info">
                <h4>{{ name }}</h4>
                <p>ID: {{ user_id }} | @{{ username }}</p>
            </div>
        </div>

        <button class="btn-vip" onclick="generateNewMail()">⚡ Generate New Mail</button>

        <div class="mail-box" onclick="copyText('currentMail')">
            <span id="currentMail">Click Generate Button</span>
            <span class="copy-badge">📋 COPY</span>
        </div>
        <div class="pass-box" onclick="copyText('currentPass')">
            <span id="currentPass">Password: speedx_******</span>
            <span class="copy-badge">📋 COPY</span>
        </div>
    </div>

    <div class="inbox-title">📥 Live Inbox (Auto Refreshing)</div>
    <div class="email-list" id="emailList">
        <p style="text-align: center; color: #51535b; font-size: 13px;">No mail active. Click generate to poll server.</p>
    </div>

    <a href="https://t.me/{{ channel_username }}" target="_blank" class="tg-join-btn">✈️ Join Official Telegram Channel</a>
</div>
<div class="toast" id="toast">Copied!</div>

<script>
    let currentEmailUser = "";
    let currentEmailDomain = "";
    const userId = "{{ user_id }}";

    if (userId !== "Unknown") {
        fetch(`/api/log-visit?user_id=${userId}`);
    }

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
                    list.innerHTML = '<p style="text-align: center; color: #51535b; font-size: 13px;">Inbox is empty. Awaiting verification messages...</p>';
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
                            <div style="text-align:right; margin-bottom:8px;"><button onclick="copyRawText(document.getElementById('text-${index}').innerText)" style="background:#111; color:var(--neon-cyan); border:1px solid var(--neon-cyan); border-radius:6px; padding:4px 10px; font-size:11px; cursor:pointer; font-weight:bold;">Copy OTP</button></div>
                            <span id="text-${index}">${email.textBody || email.htmlBody || 'No Content'}</span>
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
        navigator.clipboard.writeText(text).then(() => showToast("Copied! 📋"));
    }
    function showToast(msg) {
        const t = document.getElementById('toast'); t.innerText = msg; t.style.display = 'block';
        setTimeout(() => t.style.display = 'none', 1500);
    }

    setInterval(fetchInbox, 2500);

    particlesJS('particles-js', {
        "particles": {
            "number": {"value": 40}, "color": {"value": "#ff0055"},
            "shape": {"type": "circle"}, "opacity": {"value": 0.2}, "size": {"value": 2.5},
            "line_linked": {"enable": true, "distance": 130, "color": "#00ffff", "opacity": 0.1, "width": 1},
            "move": {"enable": true, "speed": 1.2}
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
    if uid and uid != "Unknown" and int(uid) in USER_DB:
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

# ================= ASYNC RUNNER FOR BOTH BOT & FLASK =================

async def main():
    # Build bot application natively inside async context
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("admin", admin_handler))

    # Initialize bot polling inside the event loop safely
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Configure and run Flask inside the exact same asyncio loop via custom background config
    import werkzeug.serving
    port = int(os.environ.get("PORT", 5000))
    
    # Run server task concurrently using the main loop without thread-interruption
    loop = asyncio.get_running_loop()
    server_task = loop.run_in_executor(None, lambda: werkzeug.serving.run_simple("0.0.0.0", port, app, use_reloader=False))

    print(f"🔥 VIP System Online! Web running on port {port}")
    
    # Keep checking and preventing the event loop from collapsing
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    # Launch with high priority pure asyncio core execution
    asyncio.run(main())
