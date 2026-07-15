import os
import threading
import time
import requests
import telebot
import html
import re
from datetime import datetime
import pytz

# ──────────────────────────────────────────────────────────
# কনফিগারেশন
# ──────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "-1003732171846"
API_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api/console"

HEADERS = {
    "mauthapi": "MINQWI3C03A",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

bot = telebot.TeleBot(BOT_TOKEN)

# ওটিপি ট্র্যাক রাখার জন্য আমরা শুধু কারেন্ট এপিআই রেসপন্সের আইডিগুলো মনে রাখব
processed_timestamps = set()

COUNTRY_CODES = {
    "93": "🇦🇫 Afghanistan", "355": "🇦🇱 Albania", "213": "🇩🇿 Algeria", "376": "🇦🇩 Andorra",
    "244": "🇦🇴 Angola", "1268": "🇦🇬 Antigua and Barbuda", "54": "🇦🇷 Argentina", "374": "🇦🇲 Armenia",
    "61": "🇦🇺 Australia", "43": "🇦🇹 Austria", "994": "🇦🇿 Azerbaijan", "1242": "🇧🇸 Bahamas",
    "973": "🇧🇭 Bahrain", "880": "🇧🇩 Bangladesh", "1246": "🇧🇧 Barbados", "375": "🇧🇾 Belarus",
    "32": "🇧🇪 Belgium", "501": "🇧🇿 Belize", "229": "🇧🇯 Benin", "975": "🇧🇹 Bhutan",
    "591": "🇧🇴 Bolivia", "387": "🇧🇦 Bosnia and Herzegovina", "267": "🇧🇼 Botswana", "55": "🇧🇷 Brazil",
    "673": "🇧🇳 Brunei", "359": "🇧🇬 Bulgaria", "226": "🇧🇫 Burkina Faso", "257": "🇧🇮 Burundi",
    "238": "🇨🇻 Cabo Verde", "855": "🇰🇭 Cambodia", "237": "🇨🇲 Cameroon", "236": "🇨🇫 Central African Republic",
    "235": "🇹🇩 Chad", "56": "🇨🇱 Chile", "86": "🇨🇳 China", "57": "🇨🇴 Colombia",
    "269": "🇰🇲 Comoros", "242": "🇨🇬 Congo", "243": "🇨🇩 DR Congo", "506": "🇨🇷 Costa Rica",
    "225": "🇨🇮 Côte d'Ivoire", "385": "🇭🇷 Croatia", "53": "🇨🇺 Cuba", "357": "🇨🇾 Cyprus",
    "420": "🇨🇿 Czechia", "45": "🇩🇰 Denmark", "253": "🇩🇯 Djibouti", "1767": "🇩🇲 Dominica",
    "1809": "🇩🇴 Dominican Republic", "593": "🇪🇨 Ecuador", "20": "🇪🇬 Egypt", "503": "🇸🇻 El Salvador",
    "240": "🇬🇶 Equatorial Guinea", "291": "🇪🇷 Eritrea", "372": "🇪🇪 Estonia", "268": "🇸🇿 Eswatini",
    "251": "🇪🇹 Ethiopia", "679": "🇫🇯 Fiji", "358": "🇫🇮 Finland", "33": "🇫🇷 France",
    "241": "🇬🇦 Gabon", "220": "🇬🇲 Gambia", "995": "🇬🇪 Georgia", "49": "🇩🇪 Germany",
    "233": "🇬🇭 Ghana", "30": "🇬🇷 Greece", "1473": "🇬🇩 Grenada", "502": "🇬🇹 Guatemala",
    "224": "🇬🇳 Guinea", "245": "🇬🇼 Guinea-Bissau", "592": "🇬🇾 Guyana", "509": "🇭🇹 Haiti",
    "504": "🇭🇳 Honduras", "36": "🇭🇺 Hungary", "354": "🇮🇸 Iceland", "91": "🇮🇳 India",
    "62": "🇮🇩 Indonesia", "98": "🇮🇷 Iran", "964": "🇮🇶 Iraq", "353": "🇮🇪 Ireland",
    "972": "🇮🇱 Israel", "39": "🇮🇹 Italy", "1876": "🇯🇲 Jamaica", "81": "🇯🇵 Japan",
    "962": "🇯🇴 Jordan", "77": "🇰🇿 Kazakhstan", "254": "🇰🇪 Kenya", "686": "🇰🇮 Kiribati",
    "965": "🇰🇼 Kuwait", "996": "🇰🇬 Kyrgyzstan", "856": "🇱🇦 Laos", "371": "🇱🇻 Latvia",
    "961": "🇱🇧 Lebanon", "266": "🇱🇸 Lesotho", "231": "🇱🇷 Liberia", "218": "🇱🇾 Libya",
    "423": "🇱🇮 Liechtenstein", "370": "🇱🇹 Lithuania", "352": "🇱🇺 Luxembourg", "261": "🇲🇬 Madagascar",
    "265": "🇲🇼 Malawi", "60": "🇲🇾 Malaysia", "960": "🇲🇻 Maldives", "223": "🇲🇱 Mali",
    "356": "🇲🇹 Malta", "692": "🇲🇭 Marshall Islands", "222": "🇲🇷 Mauritania", "230": "🇲🇺 Mauritius",
    "52": "🇲🇽 Mexico", "691": "🇫🇲 Micronesia", "373": "🇲🇩 Moldova", "377": "🇲🇨 Monaco",
    "976": "🇲🇳 Mongolia", "382": "🇲🇪 Montenegro", "212": "🇲🇦 Morocco", "258": "🇲🇿 Mozambique",
    "95": "🇲🇲 Myanmar", "264": "🇳🇦 Namibia", "674": "🇳🇷 Nauru", "977": "🇳🇵 Nepal",
    "31": "🇳🇱 Netherlands", "64": "🇳🇿 New Zealand", "505": "🇳🇮 Nicaragua", "227": "🇳🇪 Niger",
    "234": "🇳🇬 Nigeria", "850": "🇰🇵 North Korea", "389": "🇲🇰 North Macedonia", "47": "🇳🇴 Norway",
    "968": "🇴🇲 Oman", "92": "🇵🇰 Pakistan", "680": "🇵🇼 Palau", "970": "🇵🇸 Palestine",
    "507": "🇵🇦 Panama", "675": "🇵🇬 Papua New Guinea", "595": "🇵🇾 Paraguay", "51": "🇵🇪 Peru",
    "63": "🇵🇭 Philippines", "48": "🇵🇱 Poland", "351": "🇵🇹 Portugal", "974": "🇶🇦 Qatar",
    "40": "🇷🇴 Romania", "7": "🇷🇺 Russia", "250": "🇷🇼 Rwanda", "1869": "🇰🇳 Saint Kitts and Nevis",
    "1758": "🇱🇨 Saint Lucia", "1784": "🇻🇨 Saint Vincent and the Grenadines", "685": "🇼🇸 Samoa",
    "378": "🇸🇲 San Marino", "239": "🇸🇹 Sao Tome and Principe", "966": "🇸🇦 Saudi Arabia",
    "221": "🇸🇳 Senegal", "381": "🇷🇸 Serbia", "248": "🇸🇨 Seychelles", "232": "🇸🇱 Sierra Leone",
    "65": "🇸🇬 Singapore", "421": "🇸🇰 Slovakia", "386": "🇸🇮 Slovenia", "677": "🇸🇧 Solomon Islands",
    "252": "🇸🇴 Somalia", "27": "🇿🇦 South Africa", "82": "🇰🇷 South Korea", "211": "🇸🇸 South Sudan",
    "34": "🇪🇸 Spain", "94": "🇱🇰 Sri Lanka", "249": "🇸🇩 Sudan", "597": "🇸🇷 Suriname",
    "46": "🇸🇪 Sweden", "41": "🇨🇭 Switzerland", "963": "🇸🇾 Syria", "992": "🇹🇯 Tajikistan",
    "255": "🇹🇿 Tanzania", "66": "🇹🇭 Thailand", "670": "🇹🇱 Timor-Leste", "228": "🇹🇬 Togo",
    "676": "🇹🇴 Tonga", "1868": "🇹🇹 Trinidad and Tobago", "216": "🇹🇳 Tunisia", "90": "🇹🇷 Türkiye",
    "993": "🇹🇲 Turkmenistan", "688": "🇹🇻 Tuvalu", "256": "🇺🇬 Uganda", "380": "🇺🇦 Ukraine",
    "971": "🇦🇪 United Arab Emirates", "44": "🇬🇧 United Kingdom", "1": "🇺🇸 United States",
    "598": "🇺🇾 Uruguay", "998": "🇺🇿 Uzbekistan", "678": "🇻🇺 Vanuatu", "379": "🇻🇦 Vatican City",
    "58": "🇻🇪 Venezuela", "84": "🇻🇳 Vietnam", "967": "🇾🇪 Yemen", "260": "🇿🇲 Zambia",
    "263": "🇿🇼 Zimbabwe",
}

def get_country_info(sms_range):
    clean_digits = re.sub(r'[^0-9]', '', sms_range)
    if clean_digits[:4] in COUNTRY_CODES: return COUNTRY_CODES[clean_digits[:4]]
    elif clean_digits[:3] in COUNTRY_CODES: return COUNTRY_CODES[clean_digits[:3]]
    elif clean_digits[:2] in COUNTRY_CODES: return COUNTRY_CODES[clean_digits[:2]]
    elif clean_digits[:1] in COUNTRY_CODES: return COUNTRY_CODES[clean_digits[:1]]
    return "🌐 Unknown Country"

def extract_code(message):
    # ১. মেসেজ থেকে সব HTML ট্যাগ বা <#> এর মতো অপ্রয়োজনীয় চিহ্ন পরিষ্কার করি
    clean_msg = re.sub(r'<[^>]+>', '', message)
    clean_msg = clean_msg.replace('<#>', '').strip()

    # ২. স্পেশাল কেস: হোয়াটসঅ্যাপ বা ড্যাশ/স্পেস যুক্ত ৩-৩ বা ৩-৪ ডিজিটের কোড (যেমন: 347 682 বা 451-935)
    # এটি শব্দের আগে বা পরে যেখানেই থাকুক, সবার আগে ধরবে
    whatsapp_match = re.search(r'\b\d{3}[- ]\d{3,4}\b', clean_msg)
    if whatsapp_match:
        return whatsapp_match.group(0).strip()

    # ৩. ২-২-২ ফরম্যাটের কোড (যেমন: 12-34-56)
    split_match = re.search(r'\b\d{2}[- ]\d{2}[- ]\d{2}\b', clean_msg)
    if split_match:
        return split_match.group(0).strip()

    # ৪. যদি ওটিপি/কোড শব্দের আশেপাশে কোনো নির্দিষ্ট সংখ্যা থাকে (৪ থেকে ৮ ডিজিট)
    # এটা শব্দের আগেও চেক করবে, পরেও চেক করবে
    keyword_match = re.search(
        r'(?i)(\d{4,8})\s*(?:is your)?\s*(?:otp|code|passcode|pin|verification|security|login)', 
        clean_msg
    )
    if keyword_match:
        return keyword_match.group(1).strip()

    keyword_match_after = re.search(
        r'(?i)(?:otp|code|passcode|pin|verification|security|login)[^\d]*(\d{4,8})', 
        clean_msg
    )
    if keyword_match_after:
        return keyword_match_after.group(1).strip()

    # ৫. কোনো কি-ওয়ার্ড না মিললে, মেসেজে থাকা যেকোনো ৪ থেকে ৮ ডিজিটের টানা স্বাধীন সংখ্যা (ব্যাকআপ)
    generic_match = re.search(r'\b\d{4,8}\b', clean_msg)
    if generic_match:
        return generic_match.group(0).strip()

    # ৬. আলফানিউমেরিক মিক্সড কোড (যেমন: FB1234 বা ABC12) - শুধু তখনই নেবে যদি মেসেজে ওটিপি শব্দ থাকে
    if any(k in clean_msg.lower() for k in ['code', 'otp', 'pin', 'verification', 'passcode']):
        mix_match = re.search(r'\b[A-Z0-9]{4,8}\b', clean_msg, re.I)
        if mix_match:
            # নিশ্চিত হওয়া যে এটা শুধু কোনো ইংরেজি শব্দ নয় (কমপক্ষে ১টা সংখ্যা আছে)
            if any(char.isdigit() for char in mix_match.group(0)):
                return mix_match.group(0).strip()

    return "N/A"


def run_keep_alive_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class PingHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")

        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, format, *args):
            pass

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


threading.Thread(target=run_keep_alive_server, daemon=True).start()

print("🤖 অল-হিট মনিটরিং বট চালু হয়েছে। প্রতি ৫ সেকেন্ড পর পর সব নতুন মেসেজ চেক করা হচ্ছে...")
first_run = True

while True:
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=5)

        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("meta", {}).get("code") == 200:
                hits = json_data.get("data", {}).get("hits", [])

                new_messages_to_send = []
                current_api_uids = set()
                seen_this_batch = set()  # এই ব্যাচের ভেতরেই uid রিপিট হলে ধরার জন্য

                for hit in hits:
                    current_hit_time = hit.get("time")
                    # রেঞ্জ একই হলেও যদি মেসেজ আলাদা হয় বা টাইম আলাদা হয়, তাহলেই নতুন আইডি তৈরি হবে
                    uid = f"{hit.get('range')}|{hit.get('sid')}|{hit.get('message')}|{current_hit_time}"
                    
                    if current_hit_time:
                        current_api_uids.add(uid)
                        # যদি এই মেসেজটি আমাদের লিস্টে না থাকে, তারমানে এটা একদম ফ্রেশ নতুন ওটিপি
                        if uid not in processed_timestamps and uid not in seen_this_batch:
                            new_messages_to_send.append((uid, hit))
                            seen_this_batch.add(uid)

                # ✨ আসল ট্রিক: প্রতি সেকেন্ডে মেমোরি অটো-আপডেট হয়ে যাবে। 
                # এপিআই-এর বাইরে চলে যাওয়া কোনো পুরানো ওটিপি নিয়ে মেমোরি জ্যাম করে বসে থাকবে না।
                processed_timestamps = current_api_uids

                if first_run:
                    print(f"⏭️ প্রথম রান — এপিআই-তে থাকা {len(new_messages_to_send)}টা পুরানো হিট স্কিপ করা হলো।")
                    first_run = False
                    new_messages_to_send = []

                # নতুন ওটিপি পাঠানোর লুপ
                for uid, hit in reversed(new_messages_to_send):
                    sid = hit.get("sid", "N/A")
                    sms_range = hit.get("range", "N/A")
                    message_text = hit.get("message", "N/A")
                    current_hit_time = hit.get("time")

                    country_str = get_country_info(sms_range)
                    extracted_code = extract_code(message_text)

                    try:
                        utc_dt = datetime.utcfromtimestamp(current_hit_time / 1000.0).replace(tzinfo=pytz.utc)
                        bd_tz = pytz.timezone('Asia/Dhaka')
                        bd_dt = utc_dt.astimezone(bd_tz)
                        formatted_time = bd_dt.strftime('%Y-%m-%d %I:%M:%S %p')
                    except Exception:
                        formatted_time = "Unknown"

                    safe_sid = html.escape(str(sid))
                    safe_range = html.escape(str(sms_range))
                    safe_message = html.escape(str(message_text))
                    safe_code = html.escape(str(extracted_code))

                    tg_message = (
                        f"<b>ACTIVE RANGE</b>\n"
                        f"╭───────────────╮\n"
                        f"📸✨ <b>{safe_sid.upper()} RANGE</b> ✨\n"
                        f"╰───────────────╯\n\n"
                        f"🌐 <b>Country</b>  ➔ {country_str}\n"
                        f"🗣️ <b>Service</b> ➔ {safe_sid}\n"
                        f"🔐 <b>Key</b> ➔ <code>{safe_code}</code>\n\n"
                        f"🎯 <b>Range</b>    ➔ <code>{safe_range}</code>\n\n"
                        f"🕒 <b>Time</b>     ➔ {formatted_time}\n\n"
                        f"✉️ <b>Message</b>\n"
                        f"<blockquote>{safe_message}</blockquote>"
                    )

                    markup = telebot.types.InlineKeyboardMarkup()
                    button1 = telebot.types.InlineKeyboardButton(text="🤖 Number Bot", url="https://t.me/SMSTOSMSBOT?start=start")
                    button2 = telebot.types.InlineKeyboardButton(text="📬 Main channel", url="https://t.me/+LZrutZRrpbRkNDVl")
                    markup.row(button1, button2)

                    # নতুন মেসেজ সরাসরি ১ বারেই চলে যাবে, কোনো বড় লুপ জ্যাম তৈরি করবে না
                    try:
                        bot.send_message(CHAT_ID, tg_message, parse_mode="HTML", reply_markup=markup)
                        print(f"✅ নতুন ওটিপি চ্যানেলে পাঠানো হয়েছে! রেঞ্জ: {sms_range}")
                    except Exception as send_err:
                        print(f"⚠️ মেসেজ সেন্ড এরর: {send_err}")

                    # প্রতিটা মেসেজের মাঝে ১ সেকেন্ড সেফটি বিরতি
                    time.sleep(1)

        else:
            print(f"⚠️ HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"❌ ব্যাকএন্ড এরর: {e}")

    # নতুন রেসপন্সের জন্য ৫ সেকেন্ড বিরতি (API cache-ও ৫ সেকেন্ড, তাই এর চেয়ে ঘন ঘন চেক করা অপ্রয়োজনীয়)
    time.sleep(5)
