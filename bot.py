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
BOT_TOKEN_2 = os.environ["BOT_TOKEN_2"]
CHAT_ID = "-1003732171846"
API_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api/console"

HEADERS = {
    "mauthapi": "MINQWI3C03A",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# দুটো বট instance — একটাই দিয়ে সব পাঠানোর বদলে দুটো বটের মধ্যে পালাক্রমে ভাগ করে পাঠানো হবে,
# যাতে Telegram-এর প্রতি-বট rate-limit আলাদা আলাদা ব্যবহার হয়ে throughput বাড়ে
bot1 = telebot.TeleBot(BOT_TOKEN)
bot2 = telebot.TeleBot(BOT_TOKEN_2)

# ওটিপি ট্র্যাক রাখার জন্য আমরা শুধু কারেন্ট এপিআই রেসপন্সের আইডিগুলো মনে রাখব
processed_timestamps = set()

COUNTRY_CODES = {
    "93": ("🇦🇫 Afghanistan", "AF"), "355": ("🇦🇱 Albania", "AL"), "213": ("🇩🇿 Algeria", "DZ"), "376": ("🇦🇩 Andorra", "AD"),
    "244": ("🇦🇴 Angola", "AO"), "1268": ("🇦🇬 Antigua and Barbuda", "AG"), "54": ("🇦🇷 Argentina", "AR"), "374": ("🇦🇲 Armenia", "AM"),
    "61": ("🇦🇺 Australia", "AU"), "43": ("🇦🇹 Austria", "AT"), "994": ("🇦🇿 Azerbaijan", "AZ"), "1242": ("🇧🇸 Bahamas", "BS"),
    "973": ("🇧🇭 Bahrain", "BH"), "880": ("🇧🇩 Bangladesh", "BD"), "1246": ("🇧🇧 Barbados", "BB"), "375": ("🇧🇾 Belarus", "BY"),
    "32": ("🇧🇪 Belgium", "BE"), "501": ("🇧🇿 Belize", "BZ"), "229": ("🇧🇯 Benin", "BJ"), "975": ("🇧🇹 Bhutan", "BT"),
    "591": ("🇧🇴 Bolivia", "BO"), "387": ("🇧🇦 Bosnia and Herzegovina", "BA"), "267": ("🇧🇼 Botswana", "BW"), "55": ("🇧🇷 Brazil", "BR"),
    "673": ("🇧🇳 Brunei", "BN"), "359": ("🇧🇬 Bulgaria", "BG"), "226": ("🇧🇫 Burkina Faso", "BF"), "257": ("🇧🇮 Burundi", "BI"),
    "238": ("🇨🇻 Cabo Verde", "CV"), "855": ("🇰🇭 Cambodia", "KH"), "237": ("🇨🇲 Cameroon", "CM"), "236": ("🇨🇫 Central African Republic", "CF"),
    "235": ("🇹🇩 Chad", "TD"), "56": ("🇨🇱 Chile", "CL"), "86": ("🇨🇳 China", "CN"), "57": ("🇨🇴 Colombia", "CO"),
    "269": ("🇰🇲 Comoros", "KM"), "242": ("🇨🇬 Congo", "CG"), "243": ("🇨🇩 DR Congo", "CD"), "506": ("🇨🇷 Costa Rica", "CR"),
    "225": ("🇨🇮 Côte d'Ivoire", "CI"), "385": ("🇭🇷 Croatia", "HR"), "53": ("🇨🇺 Cuba", "CU"), "357": ("🇨🇾 Cyprus", "CY"),
    "420": ("🇨🇿 Czechia", "CZ"), "45": ("🇩🇰 Denmark", "DK"), "253": ("🇩🇯 Djibouti", "DJ"), "1767": ("🇩🇲 Dominica", "DM"),
    "1809": ("🇩🇴 Dominican Republic", "DO"), "593": ("🇪🇨 Ecuador", "EC"), "20": ("🇪🇬 Egypt", "EG"), "503": ("🇸🇻 El Salvador", "SV"),
    "240": ("🇬🇶 Equatorial Guinea", "GQ"), "291": ("🇪🇷 Eritrea", "ER"), "372": ("🇪🇪 Estonia", "EE"), "268": ("🇸🇿 Eswatini", "SZ"),
    "251": ("🇪🇹 Ethiopia", "ET"), "679": ("🇫🇯 Fiji", "FJ"), "358": ("🇫🇮 Finland", "FI"), "33": ("🇫🇷 France", "FR"),
    "241": ("🇬🇦 Gabon", "GA"), "220": ("🇬🇲 Gambia", "GM"), "995": ("🇬🇪 Georgia", "GE"), "49": ("🇩🇪 Germany", "DE"),
    "233": ("🇬🇭 Ghana", "GH"), "30": ("🇬🇷 Greece", "GR"), "1473": ("🇬🇩 Grenada", "GD"), "502": ("🇬🇹 Guatemala", "GT"),
    "224": ("🇬🇳 Guinea", "GN"), "245": ("🇬🇼 Guinea-Bissau", "GW"), "592": ("🇬🇾 Guyana", "GY"), "509": ("🇭🇹 Haiti", "HT"),
    "504": ("🇭🇳 Honduras", "HN"), "36": ("🇭🇺 Hungary", "HU"), "354": ("🇮🇸 Iceland", "IS"), "91": ("🇮🇳 India", "IN"),
    "62": ("🇮🇩 Indonesia", "ID"), "98": ("🇮🇷 Iran", "IR"), "964": ("🇮🇶 Iraq", "IQ"), "353": ("🇮🇪 Ireland", "IE"),
    "972": ("🇮🇱 Israel", "IL"), "39": ("🇮🇹 Italy", "IT"), "1876": ("🇯🇲 Jamaica", "JM"), "81": ("🇯🇵 Japan", "JP"),
    "962": ("🇯🇴 Jordan", "JO"), "77": ("🇰🇿 Kazakhstan", "KZ"), "254": ("🇰🇪 Kenya", "KE"), "686": ("🇰🇮 Kiribati", "KI"),
    "965": ("🇰🇼 Kuwait", "KW"), "996": ("🇰🇬 Kyrgyzstan", "KG"), "856": ("🇱🇦 Laos", "LA"), "371": ("🇱🇻 Latvia", "LV"),
    "961": ("🇱🇧 Lebanon", "LB"), "266": ("🇱🇸 Lesotho", "LS"), "231": ("🇱🇷 Liberia", "LR"), "218": ("🇱🇾 Libya", "LY"),
    "423": ("🇱🇮 Liechtenstein", "LI"), "370": ("🇱🇹 Lithuania", "LT"), "352": ("🇱🇺 Luxembourg", "LU"), "261": ("🇲🇬 Madagascar", "MG"),
    "265": ("🇲🇼 Malawi", "MW"), "60": ("🇲🇾 Malaysia", "MY"), "960": ("🇲🇻 Maldives", "MV"), "223": ("🇲🇱 Mali", "ML"),
    "356": ("🇲🇹 Malta", "MT"), "692": ("🇲🇭 Marshall Islands", "MH"), "222": ("🇲🇷 Mauritania", "MR"), "230": ("🇲🇺 Mauritius", "MU"),
    "52": ("🇲🇽 Mexico", "MX"), "691": ("🇫🇲 Micronesia", "FM"), "373": ("🇲🇩 Moldova", "MD"), "377": ("🇲🇨 Monaco", "MC"),
    "976": ("🇲🇳 Mongolia", "MN"), "382": ("🇲🇪 Montenegro", "ME"), "212": ("🇲🇦 Morocco", "MA"), "258": ("🇲🇿 Mozambique", "MZ"),
    "95": ("🇲🇲 Myanmar", "MM"), "264": ("🇳🇦 Namibia", "NA"), "674": ("🇳🇷 Nauru", "NR"), "977": ("🇳🇵 Nepal", "NP"),
    "31": ("🇳🇱 Netherlands", "NL"), "64": ("🇳🇿 New Zealand", "NZ"), "505": ("🇳🇮 Nicaragua", "NI"), "227": ("🇳🇪 Niger", "NE"),
    "234": ("🇳🇬 Nigeria", "NG"), "850": ("🇰🇵 North Korea", "KP"), "389": ("🇲🇰 North Macedonia", "MK"), "47": ("🇳🇴 Norway", "NO"),
    "968": ("🇴🇲 Oman", "OM"), "92": ("🇵🇰 Pakistan", "PK"), "680": ("🇵🇼 Palau", "PW"), "970": ("🇵🇸 Palestine", "PS"),
    "507": ("🇵🇦 Panama", "PA"), "675": ("🇵🇬 Papua New Guinea", "PG"), "595": ("🇵🇾 Paraguay", "PY"), "51": ("🇵🇪 Peru", "PE"),
    "63": ("🇵🇭 Philippines", "PH"), "48": ("🇵🇱 Poland", "PL"), "351": ("🇵🇹 Portugal", "PT"), "974": ("🇶🇦 Qatar", "QA"),
    "40": ("🇷🇴 Romania", "RO"), "7": ("🇷🇺 Russia", "RU"), "250": ("🇷🇼 Rwanda", "RW"), "1869": ("🇰🇳 Saint Kitts and Nevis", "KN"),
    "1758": ("🇱🇨 Saint Lucia", "LC"), "1784": ("🇻🇨 Saint Vincent and the Grenadines", "VC"), "685": ("🇼🇸 Samoa", "WS"),
    "378": ("🇸🇲 San Marino", "SM"), "239": ("🇸🇹 Sao Tome and Principe", "ST"), "966": ("🇸🇦 Saudi Arabia", "SA"),
    "221": ("🇸🇳 Senegal", "SN"), "381": ("🇷🇸 Serbia", "RS"), "248": ("🇸🇨 Seychelles", "SC"), "232": ("🇸🇱 Sierra Leone", "SL"),
    "65": ("🇸🇬 Singapore", "SG"), "421": ("🇸🇰 Slovakia", "SK"), "386": ("🇸🇮 Slovenia", "SI"), "677": ("🇸🇧 Solomon Islands", "SB"),
    "252": ("🇸🇴 Somalia", "SO"), "27": ("🇿🇦 South Africa", "ZA"), "82": ("🇰🇷 South Korea", "KR"), "211": ("🇸🇸 South Sudan", "SS"),
    "34": ("🇪🇸 Spain", "ES"), "94": ("🇱🇰 Sri Lanka", "LK"), "249": ("🇸🇩 Sudan", "SD"), "597": ("🇸🇷 Suriname", "SR"),
    "46": ("🇸🇪 Sweden", "SE"), "41": ("🇨🇭 Switzerland", "CH"), "963": ("🇸🇾 Syria", "SY"), "992": ("🇹🇯 Tajikistan", "TJ"),
    "255": ("🇹🇿 Tanzania", "TZ"), "66": ("🇹🇭 Thailand", "TH"), "670": ("🇹🇱 Timor-Leste", "TL"), "228": ("🇹🇬 Togo", "TG"),
    "676": ("🇹🇴 Tonga", "TO"), "1868": ("🇹🇹 Trinidad and Tobago", "TT"), "216": ("🇹🇳 Tunisia", "TN"), "90": ("🇹🇷 Türkiye", "TR"),
    "993": ("🇹🇲 Turkmenistan", "TM"), "688": ("🇹🇻 Tuvalu", "TV"), "256": ("🇺🇬 Uganda", "UG"), "380": ("🇺🇦 Ukraine", "UA"),
    "971": ("🇦🇪 United Arab Emirates", "AE"), "44": ("🇬🇧 United Kingdom", "GB"), "1": ("🇺🇸 United States", "US"),
    "598": ("🇺🇾 Uruguay", "UY"), "998": ("🇺🇿 Uzbekistan", "UZ"), "678": ("🇻🇺 Vanuatu", "VU"), "379": ("🇻🇦 Vatican City", "VA"),
    "58": ("🇻🇪 Venezuela", "VE"), "84": ("🇻🇳 Vietnam", "VN"), "967": ("🇾🇪 Yemen", "YE"), "260": ("🇿🇲 Zambia", "ZM"),
    "263": ("🇿🇼 Zimbabwe", "ZW"),
}

def mask_range(sms_range):
    clean = re.sub(r'[^0-9]', '', sms_range)
    if len(clean) > 10:
        return clean[:5] + "XXX"
    return sms_range

def get_country_info(sms_range):
    clean_digits = re.sub(r'[^0-9]', '', sms_range)
    if clean_digits[:4] in COUNTRY_CODES: name, code = COUNTRY_CODES[clean_digits[:4]]
    elif clean_digits[:3] in COUNTRY_CODES: name, code = COUNTRY_CODES[clean_digits[:3]]
    elif clean_digits[:2] in COUNTRY_CODES: name, code = COUNTRY_CODES[clean_digits[:2]]
    elif clean_digits[:1] in COUNTRY_CODES: name, code = COUNTRY_CODES[clean_digits[:1]]
    else: return "🌐 Unknown Country"
    return f"{name} ({code})"

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

                # নতুন ওটিপি পাঠানোর লুপ — এখন দুটো বটের মধ্যে পালাক্রমে ভাগ হয়ে পাঠানো হবে
                for i, (uid, hit) in enumerate(reversed(new_messages_to_send)):
                    sid = hit.get("sid", "N/A")
                    sms_range = hit.get("range", "N/A")
                    message_text = hit.get("message", "N/A")
                    current_hit_time = hit.get("time")

                    country_str = get_country_info(sms_range)
                    extracted_code = extract_code(message_text)

                    safe_sid = html.escape(str(sid))
                    safe_range = html.escape(mask_range(str(sms_range)))
                    safe_message = html.escape(str(message_text))
                    safe_code = html.escape(str(extracted_code))

                    tg_message = (
                        f"✨ <b>{safe_sid.upper()} RANGE</b> ✨\n\n"
                        f"🌐 <b>Country</b>  ➔ {country_str}\n"
                        f"🗣️ <b>Service</b> ➔ {safe_sid}\n"
                        f"🔐 <b>Code</b> ➔ <code>{safe_code}</code>\n\n"
                        f"🎯 <b>Range</b>    ➔ <code>{safe_range}</code>\n\n"
                        f"✉️ <b>Message</b>\n"
                        f"<blockquote><code>{safe_message}</code></blockquote>"
                    )

                    colors = ["primary", "success", "danger"]
                    color1 = colors[i % 3]
                    color2 = colors[(i + 1) % 3]
                    color3 = colors[(i + 2) % 3]

                    markup = telebot.types.InlineKeyboardMarkup()
                    button1 = telebot.types.InlineKeyboardButton(text="Get Number", url="https://t.me/SMSTOSMSBOT?start=start", style=color1)
                    button2 = telebot.types.InlineKeyboardButton(text="Join Channel", url="https://t.me/+LZrutZRrpbRkNDVl", style=color2)
                    button3 = telebot.types.InlineKeyboardButton(
                        text="Copy Range",
                        copy_text=telebot.types.CopyTextButton(text=str(sms_range)),
                        style=color3
                    )
                    markup.row(button3)
                    markup.row(button1, button2)

                    # জোড়-বেজোড় index অনুযায়ী পালাক্রমে বট বাছাই — প্রতিটা মেসেজ শুধু একটা বটই পাঠাবে
                    active_bot = bot1 if i % 2 == 0 else bot2
                    bot_label = "1" if i % 2 == 0 else "2"

                    # নতুন মেসেজ সরাসরি ১ বারেই চলে যাবে, কোনো বড় লুপ জ্যাম তৈরি করবে না
                    try:
                        active_bot.send_message(CHAT_ID, tg_message, parse_mode="HTML", reply_markup=markup)
                        print(f"✅ (Bot {bot_label}) নতুন ওটিপি চ্যানেলে পাঠানো হয়েছে! রেঞ্জ: {sms_range}")
                    except Exception as send_err:
                        print(f"⚠️ (Bot {bot_label}) মেসেজ সেন্ড এরর: {send_err}")

                    # প্রতিটা মেসেজের মাঝে ১ সেকেন্ড সেফটি বিরতি
                    time.sleep(1)

        else:
            print(f"⚠️ HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"❌ ব্যাকএন্ড এরর: {e}")

    # নতুন রেসপন্সের জন্য ৫ সেকেন্ড বিরতি (API cache-ও ৫ সেকেন্ড, তাই এর চেয়ে ঘন ঘন চেক করা অপ্রয়োজনীয়)
    time.sleep(2)
