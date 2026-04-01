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
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================= COLORFUL SLOW CONSOLE LOGGING =================
class Colors:
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def cprint(text, color=Colors.BRIGHT_WHITE, bold=False, end='\n', delay=0.1):
    prefix = Colors.BOLD if bold else ''
    print(f"{prefix}{color}{text}{Colors.RESET}", end=end, flush=True)
    time.sleep(delay)

def print_startup_banner():
    cprint("\n" + "="*50, Colors.BRIGHT_CYAN, bold=True, delay=0.03)
    cprint("     🐉 TAMIL VIP PREDICTION BOT v3.0 🎯", Colors.BRIGHT_YELLOW, bold=True, delay=0.03)
    cprint("="*50, Colors.BRIGHT_CYAN, bold=True, delay=0.03)
    cprint("\n📦 Loading modules...", Colors.BRIGHT_MAGENTA, bold=True, delay=0.1)
    
    modules = [
        ("User data system", 5),
        ("Key management system", 10),
        ("Admin panel", 20),
        ("Server Logic Engine", 35),
        ("Prediction Calculator", 50),
        ("AI Logic Loader", 65),
        ("Loss Protection System", 80),
        ("Trend Analysis Engine", 90),
        ("5-Level Recovery System", 100)
    ]
    for name, pct in modules:
        bar_length = pct // 5
        bar = "█" * bar_length + "░" * (20 - bar_length)
        cprint(f"  [{bar}] {pct:3}%   {name}", Colors.BRIGHT_GREEN, delay=0.05)
    
    cprint("  ✅ All modules loaded!", Colors.BRIGHT_GREEN, bold=True, delay=0.1)
    cprint("\n🔌 Testing API connection...", Colors.BRIGHT_YELLOW, bold=True, delay=0.1)
    cprint("  🔗 Connecting to https://draw.ar-lottery01.com/...", Colors.BRIGHT_BLUE, delay=0.05)
    time.sleep(0.5)
    cprint("  ✅ API Connection Successful!", Colors.BRIGHT_GREEN, bold=True, delay=0.1)
    
    cprint("\n🛡️ LOSS PROTECTION SYSTEM ACTIVE", Colors.BRIGHT_RED, bold=True, delay=0.05)
    cprint("  ✅ Consecutive Loss Tracker", Colors.BRIGHT_GREEN, delay=0.03)
    cprint("  ✅ 5-Level Smart Recovery Mode", Colors.BRIGHT_GREEN, delay=0.03)
    cprint("  ✅ Logic Performance Monitor", Colors.BRIGHT_GREEN, delay=0.03)
    cprint("  ✅ Trend Analysis Engine", Colors.BRIGHT_GREEN, delay=0.03)
    cprint("  ✅ Auto-Correction Algorithm", Colors.BRIGHT_GREEN, delay=0.03)
    cprint("  ✅ Extreme Protection (L4-L5)", Colors.BRIGHT_GREEN, delay=0.03)
    
    cprint("\n🧠 Server Logics Loaded: 12", Colors.BRIGHT_CYAN, bold=True, delay=0.05)
    logics = [
        "🖥️ S1: (periodNum + lastNum) % 2 == 0 → BIG",
        "🖥️ S2: (periodNum + lastNum) % 2 != 0 → BIG",
        "🖥️ S3: (sumDigits(periodNum) + lastNum) % 2 == 0 → BIG",
        "🖥️ S4: (periodNum * lastNum) % 2 == 0 → BIG",
        "🖥️ S5: Fibonacci sequence pattern",
        "🖥️ S6: Prime number based logic",
        "🖥️ S7: Wave pattern detection",
        "🖥️ S8: Adaptive learning from history",
        "🖥️ TREND: Pattern-based prediction",
        "🖥️ STREAK: Streak breaker logic",
        "🖥️ PRO REX: ((periodNum * 3) + lastNum) % 2 != 0 → BIG",
        "🖥️ ULTRA: Weighted AI decision from all 11"
    ]
    for logic in logics:
        cprint(f"  {logic}", Colors.BRIGHT_WHITE, delay=0.03)
    
    cprint("\n📜 RECOVERY LEVELS:", Colors.BRIGHT_YELLOW, bold=True, delay=0.05)
    cprint("  🟡 Level 1 - Light Recovery (ULTRA+TREND)", Colors.BRIGHT_YELLOW, delay=0.03)
    cprint("  🟠 Level 2 - Streak Breaker / Adaptive", Colors.BRIGHT_YELLOW, delay=0.03)
    cprint("  🔴 Level 3 - MAX PROTECTION", Colors.BRIGHT_YELLOW, delay=0.03)
    cprint("  🔴🔴 Level 4 - EXTREME PROTECTION (Reverse Pattern)", Colors.BRIGHT_RED, delay=0.03)
    cprint("  🔴🔴🔴 Level 5 - ULTIMATE PROTECTION (All Logics Reverse)", Colors.BRIGHT_RED, bold=True, delay=0.03)
    
    cprint("\n⚙️  Bot is starting...", Colors.BRIGHT_GREEN, bold=True, delay=0.1)
    cprint("✅ Bot Status: ACTIVE", Colors.BRIGHT_GREEN, bold=True, delay=0.05)
    cprint(f"👑 Owner: @TAMIL_VIP_1", Colors.BRIGHT_YELLOW, bold=True, delay=0.05)
    cprint(f"🤖 Bot Username: @NUMBERPREDICTION2_BOT", Colors.BRIGHT_CYAN, bold=True, delay=0.05)
    cprint("📡 Mode: PRIVATE DM ONLY", Colors.BRIGHT_BLUE, delay=0.05)
    cprint("👥 Authorized Users: 1", Colors.BRIGHT_WHITE, delay=0.05)
    cprint("\n✅ Bot ready! Auto prediction every 4 seconds.\n", Colors.BRIGHT_GREEN, bold=True, delay=0.1)

# ================= CONFIG =================
BOT_TOKEN = "8631613205:AAGcS_OUKWRQodQGoXID43V3z4wdrXwUfSs"
OWNER_USERNAME = "@TAMIL_VIP_1"
ADMIN_IDS = [8171102858]

WIN_STICKER = "CAACAgUAAxkBAAEQ0YdpxAG9XxDr6CTvaAwki7WyW8Sh4AACyBsAAkQ0aFXCWdPVF2tZmjoE"
LOSS_STICKER = "CAACAgUAAxkBAAEQ0aBpxA8Ca1jqDrRxgeNroGQ6M34dtQAChBsAAqnymFb-nWVnvR760DoE"
NUMBER_WIN_STICKER = "CAACAgUAAxkBAAEQ2Otpy1jg4DchKSbW0J1MnVeLfdyBxAAC7R8AAsjTaVVOQWYGscwSCToE"

HISTORY_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ================= GLOBALS =================
job_lock = asyncio.Lock()
auto_predict_enabled = True
maintenance_mode = False
history_cache = deque(maxlen=20)
consecutive_losses = 0
recovery_mode = False
recovery_counter = 0

# ================= LOGIC PERFORMANCE (12 LOGICS) =================
logic_performance = {
    "S1": {"wins": 0, "losses": 0, "total": 0},
    "S2": {"wins": 0, "losses": 0, "total": 0},
    "S3": {"wins": 0, "losses": 0, "total": 0},
    "S4": {"wins": 0, "losses": 0, "total": 0},
    "S5": {"wins": 0, "losses": 0, "total": 0},
    "S6": {"wins": 0, "losses": 0, "total": 0},
    "S7": {"wins": 0, "losses": 0, "total": 0},
    "S8": {"wins": 0, "losses": 0, "total": 0},
    "TREND": {"wins": 0, "losses": 0, "total": 0},
    "STREAK": {"wins": 0, "losses": 0, "total": 0},
    "PRO_REX": {"wins": 0, "losses": 0, "total": 0},
    "ULTRA": {"wins": 0, "losses": 0, "total": 0}
}

# ================= FILE PATHS =================
USER_FILE = "users.json"
KEYS_FILE = "keys.json"
STATS_FILE = "user_stats.json"
USER_SETTINGS_FILE = "user_settings.json"
LOGIC_STATS_FILE = "logic_stats.json"

# ================= FILE FUNCTIONS =================
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def load_user_settings():
    if os.path.exists(USER_SETTINGS_FILE):
        with open(USER_SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open(USER_SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def load_logic_stats():
    global logic_performance
    if os.path.exists(LOGIC_STATS_FILE):
        with open(LOGIC_STATS_FILE, "r") as f:
            logic_performance = json.load(f)
    return logic_performance

def save_logic_stats():
    with open(LOGIC_STATS_FILE, "w") as f:
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

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ================= KEYBOARDS =================
def get_user_keyboard():
    return ReplyKeyboardMarkup([["👑 Login"]], resize_keyboard=True)

def get_authenticated_user_keyboard():
    return ReplyKeyboardMarkup(
        [["📊 Status", "🚪 Logout"]], 
        resize_keyboard=True
    )

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

# ================= HELPER FUNCTIONS =================
def extract_number_from_text(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None

def generate_formatted_key(days: int) -> str:
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"TamilVip-{random_part}-{days}D"

def login_info(username: str, key: str, expiry_str: str, days_str: str) -> str:
    return (
        f"✅️ LOGIN INFO\n\n"
        f"👤 NAME           : -  {username}\n"
        f"🔑 LOGIN          : -  {key}\n"
        f"📅 EXPIRED        : -  {expiry_str}\n"
        f"⏳ DAYS           : -  {days_str}\n\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )

# ================= BASE PREDICTION FUNCTIONS =================
def sum_digits(n):
    return sum(int(d) for d in str(n))

def getBigSmall(num):
    return "BIG" if num >= 5 else "SMALL"

def getColour(num):
    return "GREEN" if num % 2 == 1 else "RED"

def getSingleNumber(side, period_num, last_num):
    pseudo_random_index = (period_num + last_num) % 5
    if side == "BIG":
        return [5, 6, 7, 8, 9][pseudo_random_index]
    else:
        return [0, 1, 2, 3, 4][pseudo_random_index]

# ================= 12 SERVER LOGICS =================
def server_s1(period_num, last_num):
    calc = (period_num + last_num) % 2
    return "BIG" if calc == 0 else "SMALL"

def server_s2(period_num, last_num):
    calc = (period_num + last_num) % 2
    return "BIG" if calc != 0 else "SMALL"

def server_s3(period_num, last_num):
    digit_sum = sum_digits(period_num)
    calc = (digit_sum + last_num) % 2
    return "BIG" if calc == 0 else "SMALL"

def server_s4(period_num, last_num):
    calc = (period_num * last_num) % 2
    return "BIG" if calc == 0 else "SMALL"

def server_s5(period_num, last_num, history_list):
    if len(history_list) < 3:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"
    
    last_3 = [int(h["number"]) for h in list(history_list)[:3]]
    fib_pattern = [last_3[0], last_3[1], last_3[0] + last_3[1]]
    
    if last_3[2] == fib_pattern[2] or abs(last_3[2] - fib_pattern[2]) <= 1:
        next_val = last_3[1] + last_3[2]
        return "BIG" if next_val >= 5 else "SMALL"
    else:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"

def server_s6(period_num, last_num, history_list):
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    prime_count = 0
    for h in list(history_list)[:5]:
        if is_prime(int(h["number"])):
            prime_count += 1
    
    if prime_count >= 3:
        return "SMALL"
    else:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"

def server_s7(period_num, last_num, history_list):
    if len(history_list) < 4:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"
    
    last_4 = [getBigSmall(int(h["number"])) for h in list(history_list)[:4]]
    
    wave_up = (last_4[0] == "BIG" and last_4[1] == "SMALL" and 
               last_4[2] == "BIG" and last_4[3] == "SMALL")
    wave_down = (last_4[0] == "SMALL" and last_4[1] == "BIG" and 
                 last_4[2] == "SMALL" and last_4[3] == "BIG")
    
    if wave_up:
        return "BIG"
    elif wave_down:
        return "SMALL"
    else:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"

def server_s8(period_num, last_num, history_list):
    if len(history_list) < 10:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"
    
    last_10 = [getBigSmall(int(h["number"])) for h in list(history_list)[:10]]
    big_count = last_10.count("BIG")
    
    if big_count >= 7:
        return "SMALL"
    elif big_count <= 3:
        return "BIG"
    else:
        return "BIG" if (period_num + last_num) % 2 == 0 else "SMALL"

def server_trend(history_list):
    if len(history_list) < 5:
        return None
    
    last_5 = list(history_list)[:5]
    sides = [getBigSmall(int(r["number"])) for r in last_5]
    
    big_count = sides.count("BIG")
    small_count = sides.count("SMALL")
    
    if big_count >= 4:
        return "SMALL"
    elif small_count >= 4:
        return "BIG"
    
    alternating = all(sides[i] != sides[i+1] for i in range(len(sides)-1))
    if alternating:
        return "SMALL" if sides[0] == "BIG" else "BIG"
    
    return "BIG" if big_count > small_count else "SMALL"

def server_streak(history_list):
    if len(history_list) < 3:
        return None
    
    last_3 = list(history_list)[:3]
    sides = [getBigSmall(int(r["number"])) for r in last_3]
    
    if sides[0] == sides[1] == sides[2]:
        return "SMALL" if sides[0] == "BIG" else "BIG"
    
    return None

def server_pro_rex(period_num, last_num):
    calc = ((period_num * 3) + last_num) % 2
    return "BIG" if calc != 0 else "SMALL"

def server_ultra(period_num, last_num, history_list, recovery_mode=False):
    predictions = {}
    
    predictions["S1"] = server_s1(period_num, last_num)
    predictions["S2"] = server_s2(period_num, last_num)
    predictions["S3"] = server_s3(period_num, last_num)
    predictions["S4"] = server_s4(period_num, last_num)
    predictions["S5"] = server_s5(period_num, last_num, history_list)
    predictions["S6"] = server_s6(period_num, last_num, history_list)
    predictions["S7"] = server_s7(period_num, last_num, history_list)
    predictions["S8"] = server_s8(period_num, last_num, history_list)
    predictions["PRO_REX"] = server_pro_rex(period_num, last_num)
    
    trend_pred = server_trend(history_list)
    if trend_pred:
        predictions["TREND"] = trend_pred
    
    streak_pred = server_streak(history_list)
    if streak_pred:
        predictions["STREAK"] = streak_pred
    
    weights = {}
    for logic_name in predictions:
        stats = logic_performance.get(logic_name, {"wins": 1, "total": 1})
        if stats["total"] > 0:
            win_rate = stats["wins"] / stats["total"]
            weights[logic_name] = 1 + (win_rate * 2)
        else:
            weights[logic_name] = 1
    
    if recovery_mode:
        weights["PRO_REX"] = weights.get("PRO_REX", 1) * 2
        weights["S8"] = weights.get("S8", 1) * 1.5
    
    big_score = 0
    small_score = 0
    
    for logic_name, prediction in predictions.items():
        weight = weights.get(logic_name, 1)
        if prediction == "BIG":
            big_score += weight
        else:
            small_score += weight
    
    if big_score > small_score:
        return "BIG", "ULTRA"
    else:
        return "SMALL", "ULTRA"

# ================= LOSS PROTECTION SYSTEM (5 LEVELS) =================
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
    best_logic = "ULTRA"
    best_rate = 0
    
    for logic_name, stats in logic_performance.items():
        if stats["total"] > 5:
            win_rate = stats["wins"] / stats["total"]
            if win_rate > best_rate:
                best_rate = win_rate
                best_logic = logic_name
    
    return best_logic, best_rate

def activate_recovery_mode():
    global recovery_mode, recovery_counter, consecutive_losses
    consecutive_losses += 1
    recovery_mode = True
    recovery_counter = min(consecutive_losses, 5)  # 5 levels now
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
    return f"{levels.get(recovery_counter, '🔴 Level 5')} (After {consecutive_losses} losses)"

# ================= PREDICTION ENGINE (5 LEVELS) =================
def get_side_prediction(period_num, last_num, history_list=None):
    global recovery_mode, recovery_counter
    
    if recovery_mode:
        # LEVEL 1: Light Recovery
        if recovery_counter == 1:
            side, logic_name = server_ultra(period_num, last_num, history_list, True)
            trend_pred = server_trend(history_list)
            if trend_pred and trend_pred == side:
                logic_name = "ULTRA+TREND"
        
        # LEVEL 2: Streak Breaker / Adaptive
        elif recovery_counter == 2:
            streak_pred = server_streak(history_list)
            if streak_pred:
                side = streak_pred
                logic_name = "STREAK_BREAKER"
            else:
                side = server_s8(period_num, last_num, history_list)
                logic_name = "ADAPTIVE"
        
        # LEVEL 3: MAX PROTECTION
        elif recovery_counter == 3:
            if history_list and len(history_list) >= 3:
                last_3_sides = [getBigSmall(int(history_list[i]["number"])) for i in range(3)]
                
                if last_3_sides[0] == last_3_sides[1] == last_3_sides[2]:
                    side = "SMALL" if last_3_sides[0] == "BIG" else "BIG"
                    logic_name = "MAX_PROTECTION"
                else:
                    s5_pred = server_s5(period_num, last_num, history_list)
                    s8_pred = server_s8(period_num, last_num, history_list)
                    
                    if s5_pred == s8_pred:
                        side = s5_pred
                        logic_name = "FIBONACCI+ADAPTIVE"
                    else:
                        side, logic_name = server_ultra(period_num, last_num, history_list, True)
            else:
                side, logic_name = server_ultra(period_num, last_num, history_list, True)
        
        # LEVEL 4: EXTREME PROTECTION - Reverse Pattern + Weighted
        elif recovery_counter == 4:
            if history_list and len(history_list) >= 5:
                last_5_sides = [getBigSmall(int(history_list[i]["number"])) for i in range(5)]
                big_count = last_5_sides.count("BIG")
                small_count = last_5_sides.count("SMALL")
                
                # Strong reversal based on last 5 pattern
                if big_count >= 4:
                    side = "SMALL"
                    logic_name = "EXTREME_REVERSE_BIG"
                elif small_count >= 4:
                    side = "BIG"
                    logic_name = "EXTREME_REVERSE_SMALL"
                else:
                    # Weighted average of last 10
                    last_10_sides = [getBigSmall(int(history_list[i]["number"])) for i in range(min(10, len(history_list)))]
                    big_pct = last_10_sides.count("BIG") / len(last_10_sides)
                    if big_pct > 0.6:
                        side = "SMALL"
                        logic_name = "EXTREME_WEIGHTED"
                    elif big_pct < 0.4:
                        side = "BIG"
                        logic_name = "EXTREME_WEIGHTED"
                    else:
                        side = "SMALL" if random.random() > 0.5 else "BIG"
                        logic_name = "EXTREME_RANDOM"
            else:
                side = "SMALL" if random.random() > 0.5 else "BIG"
                logic_name = "EXTREME_RANDOM"
        
        # LEVEL 5: ULTIMATE PROTECTION - All Logics Reverse + Boost
        else:
            if history_list and len(history_list) >= 3:
                # Get all 11 logics predictions
                all_predictions = []
                
                all_predictions.append(server_s1(period_num, last_num))
                all_predictions.append(server_s2(period_num, last_num))
                all_predictions.append(server_s3(period_num, last_num))
                all_predictions.append(server_s4(period_num, last_num))
                all_predictions.append(server_s5(period_num, last_num, history_list))
                all_predictions.append(server_s6(period_num, last_num, history_list))
                all_predictions.append(server_s7(period_num, last_num, history_list))
                all_predictions.append(server_s8(period_num, last_num, history_list))
                all_predictions.append(server_pro_rex(period_num, last_num))
                
                trend_pred = server_trend(history_list)
                if trend_pred:
                    all_predictions.append(trend_pred)
                
                streak_pred = server_streak(history_list)
                if streak_pred:
                    all_predictions.append(streak_pred)
                
                # Count majority
                big_count = all_predictions.count("BIG")
                small_count = all_predictions.count("SMALL")
                
                # Reverse the majority
                if big_count > small_count:
                    side = "SMALL"
                    logic_name = "ULTIMATE_REVERSE_BIG"
                elif small_count > big_count:
                    side = "BIG"
                    logic_name = "ULTIMATE_REVERSE_SMALL"
                else:
                    # If tie, use opposite of last result
                    last_result = getBigSmall(int(history_list[0]["number"]))
                    side = "SMALL" if last_result == "BIG" else "BIG"
                    logic_name = "ULTIMATE_TIE_BREAKER"
                
                # Boost number prediction
                alt_number = (period_num + last_num * 3) % 10
                number = getSingleNumber(side, period_num, last_num)
                if getBigSmall(alt_number) == side:
                    number = alt_number
            else:
                # Fallback to opposite of last result
                if history_list and len(history_list) >= 1:
                    last_result = getBigSmall(int(history_list[0]["number"]))
                    side = "SMALL" if last_result == "BIG" else "BIG"
                    logic_name = "ULTIMATE_FALLBACK"
                else:
                    side = "BIG" if random.random() > 0.5 else "SMALL"
                    logic_name = "ULTIMATE_RANDOM"
    else:
        # Normal mode - use best performing logic
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
            elif best_logic == "S5":
                side = server_s5(period_num, last_num, history_list)
            elif best_logic == "S6":
                side = server_s6(period_num, last_num, history_list)
            elif best_logic == "S7":
                side = server_s7(period_num, last_num, history_list)
            elif best_logic == "S8":
                side = server_s8(period_num, last_num, history_list)
            elif best_logic == "PRO_REX":
                side = server_pro_rex(period_num, last_num)
            elif best_logic == "TREND":
                side = server_trend(history_list)
            elif best_logic == "STREAK":
                side = server_streak(history_list)
            else:
                side, _ = server_ultra(period_num, last_num, history_list, False)
            logic_name = best_logic
        else:
            side, logic_name = server_ultra(period_num, last_num, history_list, False)
    
    number = getSingleNumber(side, period_num, last_num)
    
    # Boost number prediction in higher recovery levels
    if recovery_counter >= 4:
        alt_number = (period_num + last_num * 2) % 10
        if getBigSmall(alt_number) == side:
            number = alt_number
    elif recovery_counter >= 2:
        alt_number = (period_num + last_num) % 10
        if getBigSmall(alt_number) == side:
            number = alt_number
    
    return side, number, logic_name

def get_color_prediction(period_num, last_num, history_list=None):
    side, number, logic_name = get_side_prediction(period_num, last_num, history_list)
    color = "GREEN" if side == "BIG" else "RED"
    return color, number, logic_name

# ================= API =================
async def fetch_history(session):
    try:
        async with session.get(HISTORY_API) as r:
            if r.status != 200:
                return None
            return json.loads(await r.text())
    except:
        return None

# ================= PREDICTION JOB =================
async def prediction_job(context: ContextTypes.DEFAULT_TYPE):
    global auto_predict_enabled, maintenance_mode
    
    if not auto_predict_enabled:
        return
    
    async with job_lock:
        last_sent = context.bot_data.get('last_sent_period')
        waiting = context.bot_data.get('waiting_result', False)
        pred_data = context.bot_data.get('predicted_data', {})

        async with aiohttp.ClientSession() as session:
            if waiting and pred_data.get('period'):
                data = await fetch_history(session)
                if data:
                    history = data["data"]["list"]
                    latest = history[0]
                    if str(latest["issueNumber"]) == pred_data['period']:
                        actual_num = int(latest["number"])
                        actual_side = getBigSmall(actual_num)
                        actual_color = getColour(actual_num)
                        
                        pred_type = pred_data['type']
                        logic_used = pred_data.get('logic', 'UNKNOWN')
                        
                        if pred_type == "side":
                            predicted_side = pred_data['value']
                            predicted_number = pred_data['number']
                            side_correct = (actual_side == predicted_side)
                            number_hit = (actual_num == predicted_number)
                            
                            if number_hit:
                                sticker = NUMBER_WIN_STICKER
                                message = f"🎉 JACKPOT {actual_num}"
                                won = True
                            elif side_correct:
                                sticker = WIN_STICKER
                                message = f"✅ WIN  {predicted_side} {predicted_number}"
                                won = True
                            else:
                                sticker = LOSS_STICKER
                                message = f"❌ LOSS  {actual_side} {actual_num}"
                                won = False
                        else:
                            predicted_color = pred_data['value']
                            predicted_number = pred_data['number']
                            color_correct = (actual_color == predicted_color)
                            number_hit = (actual_num == predicted_number)
                            
                            if number_hit:
                                sticker = NUMBER_WIN_STICKER
                                message = f"🎉 JACKPOT {actual_num}"
                                won = True
                            elif color_correct:
                                sticker = WIN_STICKER
                                message = f"✅ WIN  {predicted_color} {predicted_number}"
                                won = True
                            else:
                                sticker = LOSS_STICKER
                                message = f"❌ LOSS  {actual_color} {actual_num}"
                                won = False
                        
                        update_logic_performance(logic_used, won)
                        
                        if won:
                            deactivate_recovery_mode(True)
                        else:
                            activate_recovery_mode()
                        
                        users = load_users()
                        admin_ids = ADMIN_IDS
                        all_active = set()
                        for uid, udata in users.items():
                            if is_user_active(int(uid)):
                                settings = load_user_settings()
                                if settings.get(uid, {}).get('auto_predict', True):
                                    all_active.add(int(uid))
                        for aid in admin_ids:
                            all_active.add(aid)
                        
                        for uid in all_active:
                            update_user_stats(uid, won)
                        
                        for uid in all_active:
                            try:
                                try:
                                    await context.bot.send_sticker(uid, sticker)
                                except:
                                    pass
                                keyboard = get_user_keyboard_by_id(uid)
                                await context.bot.send_message(uid, message, reply_markup=keyboard)
                            except:
                                pass
                        
                        context.bot_data['waiting_result'] = False
                        context.bot_data['predicted_data'] = {}
            
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
            
            if next_period != last_sent and not context.bot_data.get('waiting_result', False):
                skip_count = context.bot_data.get('skip_count', 0)
                skip_threshold = 0.3 if not recovery_mode else 0.05
                force_real = skip_count >= 2
                
                if not force_real and random.random() < skip_threshold:
                    users = load_users()
                    admin_ids = ADMIN_IDS
                    all_active = set()
                    for uid, udata in users.items():
                        if is_user_active(int(uid)):
                            settings = load_user_settings()
                            if settings.get(str(uid), {}).get('auto_predict', True):
                                all_active.add(int(uid))
                    for aid in admin_ids:
                        all_active.add(aid)
                    period_short = next_period[-5:] if len(next_period) >= 5 else next_period
                    skip_msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period    : {period_short}\n🛡 Predict    : Skip"
                    
                    for uid in all_active:
                        if maintenance_mode and not is_admin(uid):
                            continue
                        try:
                            keyboard = get_user_keyboard_by_id(uid)
                            await context.bot.send_message(uid, skip_msg, reply_markup=keyboard)
                        except:
                            pass
                    context.bot_data['last_sent_period'] = next_period
                    context.bot_data['skip_count'] = skip_count + 1
                    context.bot_data['waiting_result'] = False
                    return
                else:
                    context.bot_data['skip_count'] = 0
                    
                    pred_type = random.choice(["side", "color"])
                    period_short = next_period[-5:] if len(next_period) >= 5 else next_period
                    
                    if recovery_counter >= 2:
                        pred_type = "side"
                    
                    if pred_type == "side":
                        side, number, logic_name = get_side_prediction(period_num, last_num, list(history_cache))
                        msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period    : {period_short}\n🛡 Predict    : {side} {number}\n🎯 Logic     : {logic_name}"
                        context.bot_data['predicted_data'] = {
                            'period': next_period, 
                            'type': 'side', 
                            'value': side, 
                            'number': number,
                            'logic': logic_name
                        }
                    else:
                        color, number, logic_name = get_color_prediction(period_num, last_num, list(history_cache))
                        msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period    : {period_short}\n🛡 Predict    : {color} {number}\n🎯 Logic     : {logic_name}"
                        context.bot_data['predicted_data'] = {
                            'period': next_period, 
                            'type': 'color', 
                            'value': color, 
                            'number': number,
                            'logic': logic_name
                        }
                    
                    users = load_users()
                    admin_ids = ADMIN_IDS
                    all_active = set()
                    for uid, udata in users.items():
                        if is_user_active(int(uid)):
                            settings = load_user_settings()
                            if settings.get(str(uid), {}).get('auto_predict', True):
                                all_active.add(int(uid))
                    for aid in admin_ids:
                        all_active.add(aid)
                    
                    for uid in all_active:
                        if maintenance_mode and not is_admin(uid):
                            continue
                        try:
                            keyboard = get_user_keyboard_by_id(uid)
                            await context.bot.send_message(uid, msg, reply_markup=keyboard)
                        except:
                            pass
                    
                    context.bot_data['last_sent_period'] = next_period
                    context.bot_data['waiting_result'] = True

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "User"
    
    load_logic_stats()
    
    if is_admin(user_id):
        await update.message.reply_text(f"👋 Hi {username}! You are Admin.\nUse buttons below.", reply_markup=get_admin_main_keyboard())
    elif is_user_active(user_id):
        await update.message.reply_text(
            f"✨ Welcome back {username}! ✨\n\n"
            "✅ You are logged in.\n"
            "🛡️ Loss Protection System Active (5 Levels)\n"
            "🧠 12 Server Logics Loaded\n"
            "💡 Type /predict to get prediction.\n"
            "🖥️ Type /wingo to see server logics explained.\n"
            "📊 Type /status to see your stats.\n"
            "📈 Type /reset to reset your statistics.\n"
            "⏸️ Type /stop to turn off auto predictions.\n\n"
            "🍀 Good luck!",
            reply_markup=get_authenticated_user_keyboard()
        )
    else:
        await update.message.reply_text(
            f"🎯 Hello {username}! 🎯\n\n"
            "🔥 12 Server Logic predictions\n"
            "🛡️ Loss Protection System (5 Levels)\n"
            "🔑 Press Login button\n\n"
            f"👑 Owner: {OWNER_USERNAME}",
            reply_markup=get_user_keyboard()
        )

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.\n\n👑 Owner: @TAMIL_VIP_1", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ You are not logged in. Please login first.", reply_markup=get_user_keyboard())
        return
    
    async with aiohttp.ClientSession() as session:
        data = await fetch_history(session)
        if not data:
            await update.message.reply_text("⚠️ Failed to fetch data.", reply_markup=get_user_keyboard_by_id(user_id))
            return
        history = data["data"]["list"]
        next_period = str(int(history[0]["issueNumber"]) + 1)
        period_num = int(next_period)
        last_num = int(history[0]["number"])
        
        global history_cache
        history_cache.clear()
        for item in history[:10]:
            history_cache.append(item)
        
        pred_type = random.choice(["side", "color"])
        period_short = next_period[-5:] if len(next_period) >= 5 else next_period
        
        if pred_type == "side":
            side, number, logic_name = get_side_prediction(period_num, last_num, list(history_cache))
            msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period    : {period_short}\n🛡 Predict    : {side} {number}\n🎯 Logic     : {logic_name}"
        else:
            color, number, logic_name = get_color_prediction(period_num, last_num, list(history_cache))
            msg = f"🎁 TAMIL VIP PREDICTION 🎉\n\n🆔 Period    : {period_short}\n🛡 Predict    : {color} {number}\n🎯 Logic     : {logic_name}"
        
        await update.message.reply_text(msg, reply_markup=get_user_keyboard_by_id(user_id))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.\n\n👑 Owner: @TAMIL_VIP_1", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ You are not logged in. Please login first.", reply_markup=get_user_keyboard())
        return
    
    stats = load_stats()
    uid = str(user_id)
    if uid not in stats:
        init_user_stats(user_id)
        stats = load_stats()
    
    data = stats[uid]
    total_pred = data["total_pred"]
    wins = data["wins"]
    losses = data["losses"]
    win_rate = (wins / total_pred * 100) if total_pred > 0 else 0
    
    current_win_streak = data["current_win_streak"]
    current_loss_streak = data["current_loss_streak"]
    max_win_streak = data["max_win_streak"]
    max_loss_streak = data["max_loss_streak"]
    
    settings = load_user_settings()
    auto_enabled = settings.get(uid, {}).get('auto_predict', True)
    auto_status = "✅ ON" if auto_enabled else "⏸️ OFF"
    
    recovery_status = get_recovery_status()
    best_logic, best_rate = get_best_logic()
    
    msg = (
        f"📊 Your Statistics\n\n"
        f"🔮 Total Predictions: {total_pred}\n"
        f"✅ Wins: {wins}\n"
        f"❌ Losses: {losses}\n"
        f"📈 Win Rate: {win_rate:.1f}%\n"
        f"🔥 Current Win Streak: {current_win_streak}\n"
        f"📉 Current Loss Streak: {current_loss_streak}\n"
        f"🏆 Max Win Streak: {max_win_streak}\n"
        f"💀 Max Loss Streak: {max_loss_streak}\n"
        f"🤖 Auto Predictions: {auto_status}\n"
        f"🛡️ Protection Status: {recovery_status}\n"
        f"🎯 Best Logic: {best_logic} ({best_rate*100:.1f}%)\n\n"
        f"📝 Commands:\n"
        f"/predict - Get instant prediction\n"
        f"/status - View your stats\n"
        f"/reset - Reset your statistics\n"
        f"/stop - Turn off auto predictions\n"
        f"/wingo - View server logics\n\n"
        f"©️ Powered by {OWNER_USERNAME}"
    )
    await update.message.reply_text(msg, reply_markup=get_user_keyboard_by_id(user_id))

async def wingo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.\n\n👑 Owner: @TAMIL_VIP_1", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ You are not logged in. Please login first.", reply_markup=get_user_keyboard())
        return
    
    load_logic_stats()
    performance_text = "📊 LOGIC PERFORMANCE:\n"
    for logic_name, stats in logic_performance.items():
        if stats["total"] > 0:
            win_rate = (stats["wins"] / stats["total"]) * 100
            performance_text += f"  {logic_name}: {win_rate:.1f}% ({stats['wins']}/{stats['total']})\n"
    
    msg = (
        f"🖥️ SERVER LOGICS EXPLAINED (12 Logics) 🖥️\n\n"
        f"🔢 S1: (periodNum + lastNum) % 2 == 0 → BIG\n\n"
        f"🔢 S2: (periodNum + lastNum) % 2 != 0 → BIG\n\n"
        f"🔢 S3: (sumDigits(periodNum) + lastNum) % 2 == 0 → BIG\n\n"
        f"🔢 S4: (periodNum * lastNum) % 2 == 0 → BIG\n\n"
        f"🔢 S5 (NEW): Fibonacci sequence pattern detection\n\n"
        f"🔢 S6 (NEW): Prime number based logic\n\n"
        f"🔢 S7 (NEW): Wave pattern detection\n\n"
        f"🔢 S8 (NEW): Adaptive learning from history\n\n"
        f"🔢 TREND: Pattern analysis from last 5 results\n\n"
        f"🔢 STREAK: Streak breaker logic\n\n"
        f"🔢 PRO REX: ((periodNum * 3) + lastNum) % 2 != 0 → BIG\n\n"
        f"🔢 ULTRA: Weighted AI decision from all 11 logics\n\n"
        f"🛡️ LOSS PROTECTION (5 Levels):\n"
        f"  🟡 Level 1 - Light Recovery (ULTRA+TREND)\n"
        f"  🟠 Level 2 - Streak Breaker / Adaptive\n"
        f"  🔴 Level 3 - MAX PROTECTION\n"
        f"  🔴🔴 Level 4 - EXTREME PROTECTION (Reverse Pattern)\n"
        f"  🔴🔴🔴 Level 5 - ULTIMATE PROTECTION (All Logics Reverse)\n\n"
        f"{performance_text}\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )
    await update.message.reply_text(msg, reply_markup=get_user_keyboard_by_id(user_id))

async def reset_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.\n\n👑 Owner: @TAMIL_VIP_1", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ You are not logged in. Please login first.", reply_markup=get_user_keyboard())
        return
    
    reset_user_stats(user_id)
    
    global consecutive_losses, recovery_mode, recovery_counter
    consecutive_losses = 0
    recovery_mode = False
    recovery_counter = 0
    
    await update.message.reply_text("✅ Your statistics have been reset successfully!\n🛡️ Loss protection system also reset.", reply_markup=get_user_keyboard_by_id(user_id))

async def stop_auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    
    if maintenance_mode and not is_admin(user_id):
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.\n\n👑 Owner: @TAMIL_VIP_1", reply_markup=get_user_keyboard_by_id(user_id))
        return
    
    if not is_user_active(user_id):
        await update.message.reply_text("❌ You are not logged in. Please login first.", reply_markup=get_user_keyboard())
        return
    
    settings = load_user_settings()
    uid = str(user_id)
    if uid not in settings:
        settings[uid] = {}
    
    current_status = settings[uid].get('auto_predict', True)
    new_status = not current_status
    settings[uid]['auto_predict'] = new_status
    save_user_settings(settings)
    
    if new_status:
        await update.message.reply_text("✅ Auto predictions turned ON!", reply_markup=get_user_keyboard_by_id(user_id))
    else:
        await update.message.reply_text("⏸️ Auto predictions turned OFF! Use /predict for manual predictions.", reply_markup=get_user_keyboard_by_id(user_id))

# ================= BROADCAST & MAINTENANCE =================
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    context.user_data['admin_action'] = 'broadcast'
    await update.message.reply_text("📢 Enter message to broadcast to all users:\n\n(Type your message and send)", reply_markup=get_back_keyboard())

async def maintenance_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    
    status = "ON" if maintenance_mode else "OFF"
    msg = f"🔧 Maintenance mode turned {status}!\n\n"
    if maintenance_mode:
        msg += "⚠️ Auto predictions are paused for all users.\n"
        msg += "✅ Admins can still receive predictions.\n"
        msg += "💡 Use /maintenance again to turn OFF."
    else:
        msg += "✅ Auto predictions resumed for all users."
    
    await update.message.reply_text(msg, reply_markup=get_admin_main_keyboard())

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🔙 Back":
        if context.user_data.get('admin_action'):
            context.user_data.pop('admin_action', None)
            context.user_data.pop('reset_user', None)
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_admin_main_keyboard())
        elif is_admin(user_id):
            await update.message.reply_text("🏠 Main menu:", reply_markup=get_admin_main_keyboard())
        else:
            if is_user_active(user_id):
                await update.message.reply_text("🏠 Main menu:", reply_markup=get_authenticated_user_keyboard())
            else:
                await update.message.reply_text("🏠 Main menu:", reply_markup=get_user_keyboard())
        return
    
    if text == "👑 Login":
        if is_user_active(user_id):
            await update.message.reply_text("✅ You are already logged in.", reply_markup=get_user_keyboard_by_id(user_id))
            return
        context.user_data['awaiting_key'] = True
        await update.message.reply_text("🔑 Please enter your login key:", reply_markup=get_back_keyboard())
        return
    
    if text == "📊 Status" or text == "Status":
        await status_command(update, context)
        return
    
    if text == "🚪 Logout":
        users = load_users()
        if str(user_id) in users:
            del users[str(user_id)]
            save_users(users)
            await update.message.reply_text("👋 You have been logged out.", reply_markup=get_user_keyboard())
        else:
            await update.message.reply_text("❌ You are not logged in.", reply_markup=get_user_keyboard())
        return
    
    if text == "⚙️ Admin Panel":
        if is_admin(user_id):
            await update.message.reply_text("🛠️ Admin Panel:", reply_markup=get_admin_panel_keyboard())
        else:
            await update.message.reply_text("⛔ You are not authorized.")
        return
    
    if text == "🔑 Key Creat" and is_admin(user_id):
        context.user_data['admin_action'] = 'create_key'
        await update.message.reply_text("📅 Enter number of days for the key:", reply_markup=get_back_keyboard())
        return
    
    if text == "🔄 Key Reset" and is_admin(user_id):
        context.user_data['admin_action'] = 'key_reset'
        await update.message.reply_text("🆔 Enter user ID to reset key (add days):", reply_markup=get_back_keyboard())
        return
    
    if text == "🚫 Block User" and is_admin(user_id):
        context.user_data['admin_action'] = 'block_user'
        await update.message.reply_text("🆔 Enter user ID to block:", reply_markup=get_back_keyboard())
        return
    
    if text == "📋 User Login" and is_admin(user_id):
        users = load_users()
        if not users:
            await update.message.reply_text("📭 No users logged in.", reply_markup=get_admin_main_keyboard())
            return
        msg = "📋 Logged in users:\n\n"
        for uid, udata in users.items():
            status = "🚫 Blocked" if udata.get('blocked') else "✅ Active"
            expiry = udata.get('expiry', 'None')
            msg += f"🆔 ID: {uid}\n🔑 Key: {udata.get('key','')}\n📅 Expiry: {expiry} | {status}\n\n"
        await update.message.reply_text(msg, reply_markup=get_admin_main_keyboard())
        return
    
    if text == "📊 Stats" and is_admin(user_id):
        users = load_users()
        active = sum(1 for uid, udata in users.items() if is_user_active(int(uid)))
        total = len(users)
        
        recovery_status = get_recovery_status()
        best_logic, best_rate = get_best_logic()
        
        await update.message.reply_text(
            f"📊 Admin Statistics\n\n"
            f"🤖 Bot Status: {'ACTIVE' if auto_predict_enabled else 'STOPPED'}\n"
            f"🔧 Maintenance: {'ON' if maintenance_mode else 'OFF'}\n"
            f"🛡️ Protection: {recovery_status}\n"
            f"👥 Total Users: {total}\n"
            f"✅ Active Users: {active}\n"
            f"🎯 Best Logic: {best_logic} ({best_rate*100:.1f}%)\n"
            f"🧠 Total Logics: 12\n"
            f"📊 Recovery Levels: 5", 
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    if text == "📢 Broadcast" and is_admin(user_id):
        await broadcast_command(update, context)
        return
    
    if text == "🔧 Maintenance" and is_admin(user_id):
        await maintenance_mode_command(update, context)
        return
    
    # Handle broadcast message
    if context.user_data.get('admin_action') == 'broadcast':
        broadcast_msg = text
        users = load_users()
        all_users = list(users.keys())
        all_users.extend([str(aid) for aid in ADMIN_IDS])
        all_users = list(set(all_users))
        
        sent = 0
        failed = 0
        
        await update.message.reply_text(f"📢 Broadcasting message to {len(all_users)} users...\nPlease wait.")
        
        for uid in all_users:
            try:
                await context.bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{broadcast_msg}\n\n👑 {OWNER_USERNAME}")
                sent += 1
                await asyncio.sleep(0.1)
            except:
                failed += 1
        
        await update.message.reply_text(f"✅ Broadcast completed!\n📨 Sent: {sent}\n❌ Failed: {failed}", reply_markup=get_admin_main_keyboard())
        context.user_data.pop('admin_action', None)
        return
    
    if context.user_data.get('awaiting_key'):
        key = text
        keys = load_keys()
        if key in keys and not keys[key].get('used', False):
            days = keys[key]['days']
            expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            users = load_users()
            users[str(user_id)] = {"key": key, "expiry": expiry_date, "blocked": False}
            save_users(users)
            keys[key]['used'] = True
            save_keys(keys)
            init_user_stats(user_id)
            info = login_info(username=update.effective_user.first_name, key=key, expiry_str=expiry_date, days_str=str(days))
            await update.message.reply_text(info, reply_markup=get_authenticated_user_keyboard())
            context.user_data.pop('awaiting_key', None)
        else:
            await update.message.reply_text("❌ Invalid or already used key.", reply_markup=get_user_keyboard())
        return
    
    if context.user_data.get('admin_action') == 'create_key':
        days = extract_number_from_text(text)
        
        if days and days > 0:
            key_str = generate_formatted_key(days)
            keys = load_keys()
            keys[key_str] = {"days": days, "used": False}
            save_keys(keys)
            await update.message.reply_text(f"✅ Key created:\n{key_str}\n📅 Valid for {days} days", reply_markup=get_admin_main_keyboard())
            context.user_data.pop('admin_action', None)
        else:
            await update.message.reply_text("❌ Please enter a valid number of days (like 1, 7, 30, etc.).", reply_markup=get_back_keyboard())
        return
    
    if context.user_data.get('admin_action') == 'key_reset':
        if 'reset_user' not in context.user_data:
            target_id = text.strip()
            if target_id.isdigit():
                context.user_data['reset_user'] = target_id
                await update.message.reply_text("📅 Enter number of days to add:", reply_markup=get_back_keyboard())
            else:
                await update.message.reply_text("❌ Invalid user ID. Please enter a numeric ID.", reply_markup=get_back_keyboard())
        else:
            days = extract_number_from_text(text)
            if days and days > 0:
                users = load_users()
                target = context.user_data['reset_user']
                if target in users:
                    old_expiry = users[target].get('expiry')
                    if old_expiry:
                        new_expiry = datetime.strptime(old_expiry, "%Y-%m-%d") + timedelta(days=days)
                    else:
                        new_expiry = datetime.now() + timedelta(days=days)
                    users[target]['expiry'] = new_expiry.strftime("%Y-%m-%d")
                    save_users(users)
                    await update.message.reply_text(f"✅ Added {days} days to user {target}. New expiry: {users[target]['expiry']}", reply_markup=get_admin_main_keyboard())
                else:
                    await update.message.reply_text("❌ User not found.", reply_markup=get_admin_main_keyboard())
            else:
                await update.message.reply_text("❌ Please enter a valid number of days.", reply_markup=get_back_keyboard())
            context.user_data.pop('reset_user', None)
            context.user_data.pop('admin_action', None)
        return
    
    if context.user_data.get('admin_action') == 'remove_key':
        target_id = text.strip()
        if target_id.isdigit():
            users = load_users()
            if target_id in users:
                del users[target_id]
                save_users(users)
                await update.message.reply_text(f"✅ Removed key for user {target_id}.", reply_markup=get_admin_main_keyboard())
            else:
                await update.message.reply_text("❌ User not found.", reply_markup=get_admin_main_keyboard())
        else:
            await update.message.reply_text("❌ Invalid user ID.", reply_markup=get_admin_main_keyboard())
        context.user_data.pop('admin_action', None)
        return
    
    if context.user_data.get('admin_action') == 'block_user':
        target_id = text.strip()
        if target_id.isdigit():
            users = load_users()
            if target_id in users:
                users[target_id]['blocked'] = True
                save_users(users)
                await update.message.reply_text(f"✅ Blocked user {target_id}.", reply_markup=get_admin_main_keyboard())
            else:
                await update.message.reply_text("❌ User not found.", reply_markup=get_admin_main_keyboard())
        else:
            await update.message.reply_text("❌ Invalid user ID.", reply_markup=get_admin_main_keyboard())
        context.user_data.pop('admin_action', None)
        return
    
    await update.message.reply_text("❓ Please use the buttons.", reply_markup=get_user_keyboard_by_id(user_id))

# ================= MAIN =================
def main():
    global auto_predict_enabled
    auto_predict_enabled = True
    
    load_logic_stats()
    print_startup_banner()
    
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(60)
        .read_timeout(60)
        .write_timeout(60)
        .pool_timeout(60)
        .get_updates_read_timeout(60)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("predict", predict_command))
    application.add_handler(CommandHandler("wingo", wingo_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("reset", reset_stats_command))
    application.add_handler(CommandHandler("stop", stop_auto_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("maintenance", maintenance_mode_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(prediction_job, interval=4, first=0)
    
    application.run_polling(
        drop_pending_updates=True,
        stop_signals=None
    )

if __name__ == "__main__":
    main()
