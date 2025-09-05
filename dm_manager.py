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

def select_option(prompt, options):
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        choice = input("Number daalo (ya 'exit' karne ke liye): ").strip()
        if choice.lower() == "exit":
            return None
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
            print("❌ Galat input! Dobara try karo.")
            continue
        return int(choice) - 1

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

        # 1. Followed users list
        following = cl.user_following(cl.user_id)
        if following:
            usernames = [user.username for user in following.values()]
            print("\nTum jo log follow karte ho (Following):")
            idx = select_option("Kisko DM bhejna hai? Select karo:", usernames)
            if idx is not None:
                selected_user = following[list(following.keys())[idx]]
                msg = input(f"Message likho {selected_user.username} ko: ").strip()
                if msg:
                    cl.direct_send(msg, [selected_user.pk])
                    print(f"✅ Message sent to {selected_user.username}!")
                else:
                    print("❌ Message blank tha. Koi message nahi bheja gaya.")
            else:
                print("Followed users se message bhejna chhoda gaya.")

        # 2. Pehle DM kiye users ki threads list
        threads = cl.direct_threads()
        if not threads:
            print("\n😶 Koi DM thread nahi mila.")
            return

        print("\nPehle DM kiye users ke threads:")
        thread_descriptions = []
        for thread in threads:
            names = ", ".join([u.username for u in thread.users])
            thread_descriptions.append(f"Thread ID: {thread.id} | Participants: {names}")

        idx = select_option("Kis thread ka message history dekhna hai?", thread_descriptions)
        if idx is None:
            print("Threads list se message history dekhna chhoda gaya.")
            return

        selected_thread = threads[idx]
        print(f"\nMessage history for thread with participants:")
        for user in selected_thread.users:
            print(f"- {user.username}")

        print("\nMessages in this thread:")
        for item in selected_thread.items:
            from_user = item.user.username if item.user else "Unknown"
            print(f"{from_user}: {item.text}")

        send_msg = input("\nIs thread me message bhejna chahte ho? (yes/no): ").strip().lower()
        if send_msg == "yes":
            msg = input("Message likho: ").strip()
            if msg:
                # Reply sabhi participants ko bhej rahe hain except khud
                recipients = [u.pk for u in selected_thread.users if u.pk != cl.user_id]
                cl.direct_send(msg, recipients)
                print("✅ Message sent successfully!")
            else:
                print("❌ Message blank tha, bheja nahi gaya.")
        else:
            print("Message bhejna cancel kar diya gaya.")

    except LoginRequired:
        print("❌ Session invalid hai! Dobara login karo.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    main()
