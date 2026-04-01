import asyncio
import aiohttp
import json
import os
import random
import string
import time
import re
from datetime import datetime, timedelta
from collections import deque
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8631613205:AAGcS_OUKWRQodQGoXID43V3z4wdrXwUfSs")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@TAMIL_VIP_1")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "8171102858").split(",")]

HISTORY_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ================= GLOBALS =================
history_cache = deque(maxlen=20)
consecutive_losses = 0
recovery_mode = False
recovery_counter = 0
maintenance_mode = False
auto_predict_enabled = True

# ================= LOGIC PERFORMANCE =================
logic_performance = {
    "S1": {"wins": 0, "losses": 0, "total": 0},
    "S2": {"wins": 0, "losses": 0, "total": 0},
    "S3": {"wins": 0, "losses": 0, "total": 0},
    "S4": {"wins": 0, "losses": 0, "total": 0},
    "TREND": {"wins": 0, "losses": 0, "total": 0},
    "STREAK": {"wins": 0, "losses": 0, "total": 0},
    "PRO_REX": {"wins": 0, "losses": 0, "total": 0},
    "ULTRA": {"wins": 0, "losses": 0, "total": 0},
}

# ================= FILE FUNCTIONS =================
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

def load_keys():
    if os.path.exists("keys.json"):
        with open("keys.json", "r") as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open("keys.json", "w") as f:
        json.dump(keys, f, indent=2)

def load_stats():
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open("stats.json", "w") as f:
        json.dump(stats, f, indent=2)

def load_user_settings():
    if os.path.exists("user_settings.json"):
        with open("user_settings.json", "r") as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open("user_settings.json", "w") as f:
        json.dump(settings, f, indent=2)

def load_logic_stats():
    global logic_performance
    if os.path.exists("logic_stats.json"):
        with open("logic_stats.json", "r") as f:
            logic_performance = json.load(f)
    return logic_performance

def save_logic_stats():
    with open("logic_stats.json", "w") as f:
        json.dump(logic_performance, f, indent=2)

def init_user_stats(user_id):
    stats = load_stats()
    uid = str(user_id)
    if uid not in stats:
        stats[uid] = {
            "total_pred": 0,
            "wins": 0,
            "losses": 0,
            "current_win_streak": 0,
            "current_loss_streak": 0,
            "max_win_streak": 0,
            "max_loss_streak": 0
        }
        save_stats(stats)
    return stats[uid]

def update_user_stats(user_id, won):
    stats = load_stats()
    uid = str(user_id)
    if uid not in stats:
        init_user_stats(user_id)
        stats = load_stats()
    
    stats[uid]["total_pred"] += 1
    if won:
        stats[uid]["wins"] += 1
        stats[uid]["current_win_streak"] += 1
        stats[uid]["current_loss_streak"] = 0
        if stats[uid]["current_win_streak"] > stats[uid]["max_win_streak"]:
            stats[uid]["max_win_streak"] = stats[uid]["current_win_streak"]
    else:
        stats[uid]["losses"] += 1
        stats[uid]["current_loss_streak"] += 1
        stats[uid]["current_win_streak"] = 0
        if stats[uid]["current_loss_streak"] > stats[uid]["max_loss_streak"]:
            stats[uid]["max_loss_streak"] = stats[uid]["current_loss_streak"]
    
    save_stats(stats)

def reset_user_stats(user_id):
    stats = load_stats()
    uid = str(user_id)
    stats[uid] = {
        "total_pred": 0,
        "wins": 0,
        "losses": 0,
        "current_win_streak": 0,
        "current_loss_streak": 0,
        "max_win_streak": 0,
        "max_loss_streak": 0
    }
    save_stats(stats)
    return True

# ================= HELPER FUNCTIONS =================
def getBigSmall(num):
    return "BIG" if num >= 5 else "SMALL"

def getColour(num):
    return "GREEN" if num % 2 == 1 else "RED"

def getSingleNumber(side, period_num, last_num):
    idx = (period_num + last_num) % 5
    if side == "BIG":
        return [5, 6, 7, 8, 9][idx]
    else:
        return [0, 1, 2, 3, 4][idx]

def sum_digits(n):
    return sum(int(d) for d in str(n))

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_user_active(user_id):
    if is_admin(user_id):
        return True
    users = load_users()
    data = users.get(str(user_id))
    if not data or data.get("blocked"):
        return False
    expiry = data.get("expiry")
    if expiry and datetime.strptime(expiry, "%Y-%m-%d") < datetime.now():
        return False
    return True

def generate_formatted_key(days):
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"TamilVip-{random_part}-{days}D"

def extract_number_from_text(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None

def login_info(username, key, expiry, days):
    return (
        f"✅️ LOGIN INFO\n\n"
        f"👤 NAME: {username}\n"
        f"🔑 KEY: {key}\n"
        f"📅 EXPIRY: {expiry}\n"
        f"⏳ DAYS: {days}\n\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )

# ================= KEYBOARDS =================
def get_user_keyboard():
    return ReplyKeyboardMarkup([["👑 Login"]], resize_keyboard=True)

def get_authenticated_user_keyboard():
    return ReplyKeyboardMarkup([["📊 Status", "🚪 Logout"]], resize_keyboard=True)

def get_admin_main_keyboard():
    return ReplyKeyboardMarkup(
        [["⚙️ Admin Panel", "🔑 Key Creat", "📋 User Login"], 
         ["📊 Stats", "Status"]],
        resize_keyboard=True
    )

def get_admin_panel_keyboard():
    return ReplyKeyboardMarkup(
        [["🔄 Key Reset", "🚫 Block User"], 
         ["📢 Broadcast", "🔧 Maintenance", "🔙 Back"]],
        resize_keyboard=True
    )

def get_back_keyboard():
    return ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True)

def get_user_keyboard_by_id(user_id):
    if is_admin(user_id):
        return get_admin_main_keyboard()
    elif is_user_active(user_id):
        return get_authenticated_user_keyboard()
    else:
        return get_user_keyboard()

# ================= PREDICTION LOGICS =================
def server_s1(period_num, last_num):
    return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"

def server_s2(period_num, last_num):
    return "BIG" if (period_num + last_num) % 2 != 0 else "SMALL"

def server_s3(period_num, last_num):
    digit_sum = sum_digits(period_num)
    return "BIG" if (digit_sum + last_num) % 2 == 0 else "SMALL"

def server_s4(period_num, last_num):
    return "BIG" if (period_num * last_num) % 2 == 0 else "SMALL"

def server_pro_rex(period_num, last_num):
    return "BIG" if ((period_num * 3) + last_num) % 2 != 0 else "SMALL"

def server_trend(history_list):
    if len(history_list) < 5:
        return None
    last_5 = [getBigSmall(int(h["number"])) for h in list(history_list)[:5]]
    big_count = last_5.count("BIG")
    if big_count >= 4:
        return "SMALL"
    elif big_count <= 1:
        return "BIG"
    alternating = all(last_5[i] != last_5[i+1] for i in range(len(last_5)-1))
    if alternating:
        return "SMALL" if last_5[0] == "BIG" else "BIG"
    return "BIG" if big_count >= 3 else "SMALL"

def server_streak(history_list):
    if len(history_list) < 3:
        return None
    last_3 = [getBigSmall(int(h["number"])) for h in list(history_list)[:3]]
    if last_3[0] == last_3[1] == last_3[2]:
        return "SMALL" if last_3[0] == "BIG" else "BIG"
    return None

def server_ultra(period_num, last_num, history_list, recovery=False):
    predictions = {
        "S1": server_s1(period_num, last_num),
        "S2": server_s2(period_num, last_num),
        "S3": server_s3(period_num, last_num),
        "S4": server_s4(period_num, last_num),
        "PRO_REX": server_pro_rex(period_num, last_num),
    }
    
    trend = server_trend(history_list)
    if trend:
        predictions["TREND"] = trend
    
    streak = server_streak(history_list)
    if streak:
        predictions["STREAK"] = streak
    
    weights = {}
    for name in predictions:
        stats = logic_performance.get(name, {"wins": 1, "total": 1})
        if stats["total"] > 0:
            weights[name] = 1 + (stats["wins"] / stats["total"])
        else:
            weights[name] = 1
    
    if recovery:
        weights["PRO_REX"] = weights.get("PRO_REX", 1) * 2
    
    big_score = 0
    small_score = 0
    for name, pred in predictions.items():
        w = weights.get(name, 1)
        if pred == "BIG":
            big_score += w
        else:
            small_score += w
    
    return "BIG" if big_score >= small_score else "SMALL"

# ================= LOSS PROTECTION (5 LEVELS) =================
def update_logic_performance(logic_name, won):
    global logic_performance
    if logic_name not in logic_performance:
        logic_performance[logic_name] = {"wins": 0, "losses": 0, "total": 0}
    logic_performance[logic_name]["total"] += 1
    if won:
        logic_performance[logic_name]["wins"] += 1
    else:
        logic_performance[logic_name]["losses"] += 1
    save_logic_stats()

def get_best_logic():
    best = "ULTRA"
    best_rate = 0
    for name, stats in logic_performance.items():
        if stats["total"] > 5:
            rate = stats["wins"] / stats["total"]
            if rate > best_rate:
                best_rate = rate
                best = name
    return best, best_rate

def activate_recovery_mode():
    global recovery_mode, recovery_counter, consecutive_losses
    consecutive_losses += 1
    recovery_mode = True
    recovery_counter = min(consecutive_losses, 5)
    return recovery_counter

def deactivate_recovery_mode(won):
    global recovery_mode, recovery_counter, consecutive_losses
    if won:
        consecutive_losses = 0
        recovery_counter = 0
        recovery_mode = False
    else:
        activate_recovery_mode()

def get_recovery_status():
    if not recovery_mode:
        return "🟢 Normal Mode"
    levels = {
        1: "🟡 Level 1 - Light Recovery",
        2: "🟠 Level 2 - Streak Breaker",
        3: "🔴 Level 3 - MAX PROTECTION",
        4: "🔴🔴 Level 4 - EXTREME PROTECTION",
        5: "🔴🔴🔴 Level 5 - ULTIMATE PROTECTION"
    }
    return f"{levels.get(recovery_counter, '🔴 Level 5')} ({consecutive_losses} losses)"

# ================= PREDICTION ENGINE =================
def get_side_prediction(period_num, last_num, history_list):
    global recovery_mode, recovery_counter
    
    if recovery_mode:
        if recovery_counter == 1:
            side = server_ultra(period_num, last_num, history_list, True)
            trend = server_trend(history_list)
            if trend and trend == side:
                logic_name = "ULTRA+TREND"
            else:
                logic_name = "ULTRA"
        elif recovery_counter == 2:
            streak = server_streak(history_list)
            if streak:
                side = streak
                logic_name = "STREAK_BREAKER"
            else:
                side = server_ultra(period_num, last_num, history_list, True)
                logic_name = "ADAPTIVE"
        elif recovery_counter == 3:
            if history_list and len(history_list) >= 3:
                last_3 = [getBigSmall(int(h["number"])) for h in list(history_list)[:3]]
                if last_3[0] == last_3[1] == last_3[2]:
                    side = "SMALL" if last_3[0] == "BIG" else "BIG"
                    logic_name = "MAX_PROTECTION"
                else:
                    side = server_ultra(period_num, last_num, history_list, True)
                    logic_name = "ULTRA"
            else:
                side = server_ultra(period_num, last_num, history_list, True)
                logic_name = "ULTRA"
        elif recovery_counter == 4:
            if history_list and len(history_list) >= 5:
                last_5 = [getBigSmall(int(h["number"])) for h in list(history_list)[:5]]
                big_count = last_5.count("BIG")
                if big_count >= 4:
                    side = "SMALL"
                elif big_count <= 1:
                    side = "BIG"
                else:
                    side = server_ultra(period_num, last_num, history_list, True)
                logic_name = "EXTREME_PROTECTION"
            else:
                side = server_ultra(period_num, last_num, history_list, True)
                logic_name = "EXTREME_PROTECTION"
        else:
            if history_list and len(history_list) >= 3:
                last_3 = [getBigSmall(int(h["number"])) for h in list(history_list)[:3]]
                side = "SMALL" if last_3[0] == "BIG" else "BIG"
                logic_name = "ULTIMATE_PROTECTION"
            else:
                side = "BIG" if random.random() > 0.5 else "SMALL"
                logic_name = "ULTIMATE_PROTECTION"
    else:
        best_logic, best_rate = get_best_logic()
        if best_rate > 0.6 and best_logic != "ULTRA":
            if best_logic == "S1":
                side = server_s1(period_num, last_num)
            elif best_logic == "S2":
                side = server_s2(period_num, last_num)
            elif best_logic == "S3":
                side = server_s3(period_num, last_num)
            elif best_logic == "S4":
                side = server_s4(period_num, last_num)
            elif best_logic == "PRO_REX":
                side = server_pro_rex(period_num, last_num)
            elif best_logic == "TREND":
                side = server_trend(history_list)
            elif best_logic == "STREAK":
                side = server_streak(history_list)
            else:
                side = server_ultra(period_num, last_num, history_list, False)
            logic_name = best_logic
        else:
            side = server_ultra(period_num, last_num, history_list, False)
            logic_name = "ULTRA"
    
    number = getSingleNumber(side, period_num, last_num)
    if recovery_counter >= 2:
        alt = (period_num + last_num) % 10
        if getBigSmall(alt) == side:
            number = alt
    return side, number, logic_name

def get_color_prediction(period_num, last_num, history_list):
    side, number, logic_name = get_side_prediction(period_num, last_num, history_list)
    color = "GREEN" if side == "BIG" else "RED"
    return color, number, logic_name

# ================= API =================
async def fetch_history(session):
    try:
        async with session.get(HISTORY_API) as r:
            if r.status == 200:
                return json.loads(await r.text())
    except:
        pass
    return None

# ================= BACKGROUND JOB =================
async def prediction_job(context: ContextTypes.DEFAULT_TYPE):
    global auto_predict_enabled, maintenance_mode
    
    if not auto_predict_enabled or maintenance_mode:
        return
    
    async with aiohttp.ClientSession() as session:
        data = await fetch_history(session)
        if not data:
            return
        
        history = data["data"]["list"]
        global history_cache
        history_cache.clear()
        for item in history[:10]:
            history_cache.append(item)
        
        next_period = str(int(history[0]["issueNumber"]) + 1)
        period_num = int(next_period)
        last_num = int(history[0]["number"])
        
        period_short = next_period[-5:]
        side, number, logic_name = get_side_prediction(period_num, last_num, list(history_cache))
        msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period: {period_short}\n🛡 Predict: {side} {number}\n🎯 Logic: {logic_name}"
        
        users = load_users()
        all_users = list(users.keys())
        all_users.extend([str(aid) for aid in ADMIN_IDS])
        
        for uid in all_users:
            if maintenance_mode and not is_admin(int(uid)):
                continue
            try:
                keyboard = get_user_keyboard_by_id(int(uid))
                await context.bot.send_message(int(uid), msg, reply_markup=keyboard)
            except:
                pass

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "User"
    load_logic_stats()
    
    if is_admin(user_id):
        await update.message.reply_text(f"👋 Hi {username}! You are Admin.", reply_markup=get_admin_main_keyboard())
    elif is_user_active(user_id):
        await update.message.reply_text(
            f"✨ Welcome back {username}! ✨\n\n"
            "✅ You are logged in.\n"
            "🛡️ 5-Level Loss Protection Active\n"
            "💡 /predict - Get prediction\n"
            "📊 /status - View stats\n"
            "🔄 /reset - Reset stats\n"
            "⏸️ /stop - Toggle auto predictions\n\n"
            "🍀 Good luck!",
            reply_markup=get_authenticated_user_keyboard()
        )
    else:
        await update.message.reply_text(
            f"🎯 Hello {username}! 🎯\n\n"
            "🔥 12 Server Logics\n"
            "🛡️ 5-Level Loss Protection\n"
            "🔑 Press Login button\n\n"
            f"👑 Owner: {OWNER_USERNAME}",
            reply_markup=get_user_keyboard()
        )

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Maintenance mode. Try later.", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ Login first.", reply_markup=get_user_keyboard())
        return
    
    async with aiohttp.ClientSession() as session:
        data = await fetch_history(session)
        if not data:
            await update.message.reply_text("⚠️ Failed to fetch data.")
            return
        
        history = data["data"]["list"]
        next_period = str(int(history[0]["issueNumber"]) + 1)
        period_num = int(next_period)
        last_num = int(history[0]["number"])
        
        global history_cache
        history_cache.clear()
        for item in history[:10]:
            history_cache.append(item)
        
        period_short = next_period[-5:]
        pred_type = random.choice(["side", "color"])
        
        if pred_type == "side":
            side, number, logic_name = get_side_prediction(period_num, last_num, list(history_cache))
            msg = f"🎁 PREDICTION 🎉\n\n🆔 Period: {period_short}\n🛡 Predict: {side} {number}\n🎯 Logic: {logic_name}"
        else:
            color, number, logic_name = get_color_prediction(period_num, last_num, list(history_cache))
            msg = f"🎁 PREDICTION 🎉\n\n🆔 Period: {period_short}\n🛡 Predict: {color} {number}\n🎯 Logic: {logic_name}"
        
        await update.message.reply_text(msg, reply_markup=get_user_keyboard_by_id(user_id))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Maintenance mode.", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ Login first.", reply_markup=get_user_keyboard())
        return
    
    stats = load_stats()
    uid = str(user_id)
    if uid not in stats:
        init_user_stats(user_id)
        stats = load_stats()
    
    data = stats[uid]
    total = data["total_pred"]
    wins = data["wins"]
    losses = data["losses"]
    win_rate = (wins / total * 100) if total > 0 else 0
    
    msg = (
        f"📊 Your Statistics\n\n"
        f"🔮 Total: {total}\n"
        f"✅ Wins: {wins}\n"
        f"❌ Losses: {losses}\n"
        f"📈 Win Rate: {win_rate:.1f}%\n"
        f"🔥 Current Win Streak: {data['current_win_streak']}\n"
        f"📉 Current Loss Streak: {data['current_loss_streak']}\n"
        f"🏆 Max Win Streak: {data['max_win_streak']}\n"
        f"💀 Max Loss Streak: {data['max_loss_streak']}\n"
        f"🛡️ Protection: {get_recovery_status()}\n\n"
        f"©️ Powered by {OWNER_USERNAME}"
    )
    await update.message.reply_text(msg, reply_markup=get_user_keyboard_by_id(user_id))

async def reset_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ Login first.", reply_markup=get_user_keyboard())
        return
    
    reset_user_stats(user_id)
    global consecutive_losses, recovery_mode, recovery_counter
    consecutive_losses = 0
    recovery_mode = False
    recovery_counter = 0
    
    await update.message.reply_text("✅ Stats reset!", reply_markup=get_user_keyboard_by_id(user_id))

async def stop_auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ Login first.", reply_markup=get_user_keyboard())
        return
    
    settings = load_user_settings()
    uid = str(user_id)
    if uid not in settings:
        settings[uid] = {}
    
    current = settings[uid].get('auto_predict', True)
    settings[uid]['auto_predict'] = not current
    save_user_settings(settings)
    
    status = "ON" if settings[uid]['auto_predict'] else "OFF"
    await update.message.reply_text(f"✅ Auto predictions: {status}", reply_markup=get_user_keyboard_by_id(user_id))

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Unauthorized.")
        return
    
    context.user_data['admin_action'] = 'broadcast'
    await update.message.reply_text("📢 Enter message to broadcast:", reply_markup=get_back_keyboard())

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Unauthorized.")
        return
    
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    status = "ON" if maintenance_mode else "OFF"
    await update.message.reply_text(f"🔧 Maintenance: {status}", reply_markup=get_admin_main_keyboard())

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🔙 Back":
        if context.user_data.get('admin_action'):
            context.user_data.pop('admin_action', None)
            context.user_data.pop('reset_user', None)
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_admin_main_keyboard())
        elif is_admin(user_id):
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_admin_main_keyboard())
        elif is_user_active(user_id):
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_authenticated_user_keyboard())
        else:
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_user_keyboard())
        return
    
    if text == "👑 Login":
        if is_user_active(user_id):
            await update.message.reply_text("✅ Already logged in.")
            return
        context.user_data['awaiting_key'] = True
        await update.message.reply_text("🔑 Enter key:", reply_markup=get_back_keyboard())
        return
    
    if text == "📊 Status" or text == "Status":
        await status_command(update, context)
        return
    
    if text == "🚪 Logout":
        users = load_users()
        if str(user_id) in users:
            del users[str(user_id)]
            save_users(users)
            await update.message.reply_text("👋 Logged out.", reply_markup=get_user_keyboard())
        return
    
    if text == "⚙️ Admin Panel" and is_admin(user_id):
        await update.message.reply_text("🛠️ Admin Panel:", reply_markup=get_admin_panel_keyboard())
        return
    
    if text == "🔑 Key Creat" and is_admin(user_id):
        context.user_data['admin_action'] = 'create_key'
        await update.message.reply_text("📅 Enter days:", reply_markup=get_back_keyboard())
        return
    
    if text == "🔄 Key Reset" and is_admin(user_id):
        context.user_data['admin_action'] = 'key_reset'
        await update.message.reply_text("🆔 Enter user ID:", reply_markup=get_back_keyboard())
        return
    
    if text == "🚫 Block User" and is_admin(user_id):
        context.user_data['admin_action'] = 'block_user'
        await update.message.reply_text("🆔 Enter user ID:", reply_markup=get_back_keyboard())
        return
    
    if text == "📋 User Login" and is_admin(user_id):
        users = load_users()
        if not users:
            await update.message.reply_text("📭 No users.")
            return
        msg = "📋 Users:\n\n"
        for uid, udata in users.items():
            status = "🚫" if udata.get('blocked') else "✅"
            expiry = udata.get('expiry', 'None')
            msg += f"ID: {uid} {status}\nExp: {expiry}\n\n"
        await update.message.reply_text(msg, reply_markup=get_admin_main_keyboard())
        return
    
    if text == "📊 Stats" and is_admin(user_id):
        users = load_users()
        active = sum(1 for uid, udata in users.items() if is_user_active(int(uid)))
        await update.message.reply_text(
            f"📊 Admin Stats\n\n"
            f"👥 Total: {len(users)}\n"
            f"✅ Active: {active}\n"
            f"🛡️ {get_recovery_status()}\n"
            f"🔧 Maintenance: {'ON' if maintenance_mode else 'OFF'}",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    if text == "📢 Broadcast" and is_admin(user_id):
        await broadcast_command(update, context)
        return
    
    if text == "🔧 Maintenance" and is_admin(user_id):
        await maintenance_command(update, context)
        return
    
    # Handle key entry
    if context.user_data.get('awaiting_key'):
        key = text
        keys = load_keys()
        if key in keys and not keys[key].get('used', False):
            days = keys[key]['days']
            expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            users = load_users()
            users[str(user_id)] = {"key": key, "expiry": expiry, "blocked": False}
            save_users(users)
            keys[key]['used'] = True
            save_keys(keys)
            init_user_stats(user_id)
            info = login_info(update.effective_user.first_name, key, expiry, str(days))
            await update.message.reply_text(info, reply_markup=get_authenticated_user_keyboard())
            context.user_data.pop('awaiting_key', None)
        else:
            await update.message.reply_text("❌ Invalid key.", reply_markup=get_user_keyboard())
        return
    
    # Handle admin actions
    if context.user_data.get('admin_action') == 'create_key':
        days = extract_number_from_text(text)
        if days and days > 0:
            key = generate_formatted_key(days)
            keys = load_keys()
            keys[key] = {"days": days, "used": False}
            save_keys(keys)
            await update.message.reply_text(f"✅ Key: {key}\n📅 {days} days", reply_markup=get_admin_main_keyboard())
            context.user_data.pop('admin_action', None)
        else:
            await update.message.reply_text("❌ Invalid days.", reply_markup=get_back_keyboard())
        return
    
    if context.user_data.get('admin_action') == 'key_reset':
        if 'reset_user' not in context.user_data:
            if text.isdigit():
                context.user_data['reset_user'] = text
                await update.message.reply_text("📅 Enter days to add:", reply_markup=get_back_keyboard())
            else:
                await update.message.reply_text("❌ Invalid ID.", reply_markup=get_back_keyboard())
        else:
            days = extract_number_from_text(text)
            if days and days > 0:
                users = load_users()
                target = context.user_data['reset_user']
                if target in users:
                    old = users[target].get('expiry')
                    if old:
                        new = datetime.strptime(old, "%Y-%m-%d") + timedelta(days=days)
                    else:
                        new = datetime.now() + timedelta(days=days)
                    users[target]['expiry'] = new.strftime("%Y-%m-%d")
                    save_users(users)
                    await update.message.reply_text(f"✅ Added {days} days to {target}", reply_markup=get_admin_main_keyboard())
                else:
                    await update.message.reply_text("❌ User not found.", reply_markup=get_admin_main_keyboard())
            else:
                await update.message.reply_text("❌ Invalid days.", reply_markup=get_back_keyboard())
            context.user_data.pop('reset_user', None)
            context.user_data.pop('admin_action', None)
        return
    
    if context.user_data.get('admin_action') == 'block_user':
        if text.isdigit():
            users = load_users()
            if text in users:
                users[text]['blocked'] = True
                save_users(users)
                await update.message.reply_text(f"✅ Blocked {text}", reply_markup=get_admin_main_keyboard())
            else:
                await update.message.reply_text("❌ User not found.", reply_markup=get_admin_main_keyboard())
        else:
            await update.message.reply_text("❌ Invalid ID.", reply_markup=get_back_keyboard())
        context.user_data.pop('admin_action', None)
        return
    
    if context.user_data.get('admin_action') == 'broadcast':
        broadcast_msg = text
        users = load_users()
        all_users = list(users.keys())
        all_users.extend([str(aid) for aid in ADMIN_IDS])
        all_users = list(set(all_users))
        
        sent = 0
        await update.message.reply_text(f"📢 Broadcasting to {len(all_users)} users...")
        
        for uid in all_users:
            try:
                await context.bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{broadcast_msg}\n\n👑 {OWNER_USERNAME}")
                sent += 1
                await asyncio.sleep(0.1)
            except:
                pass
        
        await update.message.reply_text(f"✅ Sent: {sent}", reply_markup=get_admin_main_keyboard())
        context.user_data.pop('admin_action', None)
        return
    
    await update.message.reply_text("❓ Use buttons.", reply_markup=get_user_keyboard_by_id(user_id))

# ================= MAIN =================
def main():
    load_logic_stats()
    
    print("=" * 50)
    print("     🐉 TAMIL VIP PREDICTION BOT v3.0 🎯")
    print("=" * 50)
    print(f"👑 Owner: {OWNER_USERNAME}")
    print("🧠 12 Server Logics Loaded")
    print("🛡️ 5-Level Loss Protection Active")
    print("✅ Bot Started Successfully!")
    print("=" * 50)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("reset", reset_stats_command))
    app.add_handler(CommandHandler("stop", stop_auto_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("maintenance", maintenance_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(prediction_job, interval=4, first=0)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
