from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import json
import os

SESSION_FILE = "session.json"

def get_sessionid_from_file():
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
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
        cl.set_settings({"cookies": {"sessionid": sessionid}})
        cl.login_by_sessionid(sessionid)

        print("✅ Sessionid se login successful!")

        # DM threads fetch karo (latest 20 threads)
        threads = cl.direct_threads()
        if not threads:
            print("😶 Koi DM thread nahi mila.")
            return

        print("\nDM Threads List:")
        for i, thread in enumerate(threads, 1):
            # Thread participants me se tumhare alawa dusra user dhundho
            usernames = [u.username for u in thread.users]
            thread_name = ", ".join(usernames)
            print(f"{i}. Thread ID: {thread.id} | Participants: {thread_name}")

        choice = int(input("\nKis thread ka message history dekhna hai? Number daalo: "))
        selected_thread = threads[choice - 1]

        print(f"\nMessage history for thread with participants:")
        for user in selected_thread.users:
            print(f"- {user.username}")

        print("\nMessages in this thread:")
        for item in selected_thread.items:
            from_user = item.user.username if item.user else "Unknown"
            print(f"{from_user}: {item.text}")

        # Message bhejne ka option
        send_msg = input("\nKya tum is thread me message bhejna chahte ho? (yes/no): ").lower()
        if send_msg == "yes":
            msg = input("Message likho: ")
            cl.direct_send(msg, [selected_thread.users[0].pk])  # Usually first user besides you
            print("✅ Message sent successfully!")

    except LoginRequired:
        print("❌ Session invalid hai! Dobara login karo.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    main()
