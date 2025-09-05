# File name: login_with_session.py
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import json
import os

cl = Client()

SESSION_FILE = "session.json"

if not os.path.exists(SESSION_FILE):
    print("❌ session.json file missing! Pehle login karke session save karo.")
    exit()

try:
    # Load session
    cl.load_settings(SESSION_FILE)
    cl.get_timeline_feed()  # Check if session valid

    me = cl.account_info()
    username = me.username

    # Followers & following info lete hain
    user_info = cl.user_info_by_username(username)

    print("✅ Login via session successful!")
    print(f"👤 Username: {username}")
    print(f"📝 Bio: {user_info.biography}")
    print(f"👥 Followers: {user_info.follower_count}")
    print(f"📌 Following: {user_info.following_count}")

except LoginRequired:
    print("❌ Session invalid! Please login again with username/password.")
except json.JSONDecodeError:
    print("❌ session.json file corrupted! Please create a new one.")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
