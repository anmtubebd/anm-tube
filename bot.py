import telebot
import requests
import json
import base64

# আপনার দেওয়া তথ্য
BOT_TOKEN = "8575654947:AAGQqiIN88CPS65r5mAvifmJMnCP8HDlPxk"
GITHUB_TOKEN = "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" # আপনার দেওয়া গিটহাব টোকেন
REPO_OWNER = "anmtubebd"
REPO_NAME = "anm-tube"
FILE_PATH = "data.json"

bot = telebot.TeleBot(BOT_TOKEN)

# ইউজার ডেটা সাময়িকভাবে রাখার জন্য
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "স্বাগতম! নতুন এনিমে অ্যাড করতে /add কমান্ডটি দিন।")

@bot.message_handler(commands=['add'])
def add_anime(message):
    bot.reply_to(message, "এনিমেটির নাম (Title) দিন:")
    bot.register_next_step_handler(message, get_title)

def get_title(message):
    user_data['title'] = message.text
    bot.reply_to(message, "পোস্টার ইমেজের লিঙ্ক (Image URL) দিন:")
    bot.register_next_step_handler(message, get_image)

def get_image(message):
    user_data['img'] = message.text
    bot.reply_to(message, "জনরা বা ক্যাটাগরি (Genre) দিন: (যেমন: Action)")
    bot.register_next_step_handler(message, get_genre)

def get_genre(message):
    user_data['genre'] = message.text
    bot.reply_to(message, "ভিডিওর টেলিগ্রাম লিঙ্ক (Video Link) দিন:")
    bot.register_next_step_handler(message, get_link)

def get_link(message):
    user_data['link'] = message.text
    bot.reply_to(message, "গিটহাবে আপডেট করা হচ্ছে... দয়া করে অপেক্ষা করুন।")
    
    update_github(message)

def update_github(message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # বর্তমান ডেটা নিয়ে আসা
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json()
        sha = content['sha']
        # ফাইলটি ডিকোড করা
        existing_data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
        
        # নতুন এনিমে যোগ করা
        new_entry = {
            "title": user_data['title'],
            "img": user_data['img'],
            "genre": user_data['genre'],
            "link": user_data['link']
        }
        existing_data.append(new_entry)
        
        # নতুন ডেটা এনকোড করা
        updated_content = base64.b64encode(json.dumps(existing_data, indent=4).encode('utf-8')).decode('utf-8')
        
        # গিটহাবে পুশ করা
        payload = {
            "message": f"Added {user_data['title']} via Admin Bot",
            "content": updated_content,
            "sha": sha
        }
        
        put_response = requests.put(url, headers=headers, json=payload)
        
        if put_response.status_code == 200:
            bot.send_message(message.chat.id, f"✅ সফলভাবে '{user_data['title']}' অ্যাড করা হয়েছে! ১-২ মিনিট পর অ্যাপে দেখা যাবে।")
        else:
            bot.send_message(message.chat.id, "❌ আপডেট করতে সমস্যা হয়েছে।")
    else:
        bot.send_message(message.chat.id, "❌ গিটহাব থেকে ফাইল পাওয়া যায়নি।")

print("বটটি চলছে...")
bot.polling()
