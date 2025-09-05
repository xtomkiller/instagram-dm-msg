from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import json
import os

SESSION_FILE = "session.json"

def get_sessionid_from_file():
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
    # Recursive search function se sessionid nikalenge
    def find_sessionid(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "sessionid":
                    return v
                else:
                    result = find_sessionid(v)
                    if result:
                        return result
        elif isinstance(d, list):
            for item in d:
                result = find_sessionid(item)
                if result:
                    return result
        return None
    return find_sessionid(data)

def main():
    if not os.path.exists(SESSION_FILE):
        print("❌ session.json file missing! Pehle login karke session save karo.")
        return
    
    sessionid = get_sessionid_from_file()
    if not sessionid:
        print("❌ sessionid session.json me nahi mila!")
        return

    cl = Client()
    try:
        # Sessionid ko set karna
        cl.set_settings({"cookies": {"sessionid": sessionid}})
        cl.login_by_sessionid(sessionid)

        print("✅ Sessionid se login successful!")

        # Followers ya followings list lelo jisme DM karna hai
        users = cl.user_followers(cl.user_id)
        if not users:
            print("😶 Koi follower nahi mila.")
            return
        
        print("Followers List:")
        for i, user in enumerate(users.values(), 1):
            print(f"{i}. {user.username} ({user.pk})")

        # User select karo DM bhejne ke liye
        choice = int(input("Kis user ko DM bhejna hai? Number daalo: "))
        selected_user = list(users.values())[choice - 1]
        print(f"Selected: {selected_user.username}")

        msg = input("Message likho: ")
        cl.direct_send(msg, [selected_user.pk])

        print(f"✅ Message sent to {selected_user.username} successfully!")

    except LoginRequired:
        print("❌ Session invalid hai! Dobara login karo.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    main()
