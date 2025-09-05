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
        print("\n" + prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        choice = input("Number daalo (ya 'exit' karne ke liye): ").strip()
        if choice.lower() == "exit":
            return None
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
            print("❌ Galat input! Dobara try karo.")
            continue
        return int(choice) - 1

def dm_to_user(cl, user):
    print(f"Selected user: {user.username}")
    msg = input("Message likho: ").strip()
    if msg:
        cl.direct_send(msg, [user.pk])
        print(f"✅ Message sent to {user.username}!")
    else:
        print("❌ Message blank tha. Koi message nahi bheja gaya.")

def dm_to_thread(cl, thread):
    print(f"\nParticipants: {', '.join([u.username for u in thread.users])}")
    print("\nMessages in this thread:")

    # Try messages or items attribute for messages list
    messages = getattr(thread, 'messages', None) or getattr(thread, 'items', [])

    for message in messages:
        from_user = message.user.username if message.user else "Unknown"
        print(f"{from_user}: {message.text}")

    send_msg = input("\nIs thread me message bhejna hai? (yes/no): ").strip().lower()
    if send_msg == "yes":
        msg = input("Message likho: ").strip()
        if msg:
            recipients = [u.pk for u in thread.users if u.pk != cl.user_id]
            cl.direct_send(msg, recipients)
            print("✅ Message sent successfully!")
        else:
            print("❌ Message blank tha, bheja nahi gaya.")
    else:
        print("Message bhejna cancel kar diya gaya.")

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

        while True:
            choice = select_option(
                "Choose an option:",
                [
                    "DM to Following list",
                    "DM to Followers list",
                    "DM to Threads list",
                    "Exit program"
                ]
            )
            if choice is None or choice == 3:
                print("Program exit kar rahe hain.")
                break

            if choice == 0:
                # Following list
                following = cl.user_following(cl.user_id)
                if not following:
                    print("😶 Tum kisi ko follow nahi karte.")
                    continue
                users = list(following.values())
                usernames = [u.username for u in users]
                idx = select_option("Kisko DM bhejna hai? Select karo:", usernames)
                if idx is not None:
                    dm_to_user(cl, users[idx])

            elif choice == 1:
                # Followers list
                followers = cl.user_followers(cl.user_id)
                if not followers:
                    print("😶 Tumhare koi followers nahi hain.")
                    continue
                users = list(followers.values())
                usernames = [u.username for u in users]
                idx = select_option("Kisko DM bhejna hai? Select karo:", usernames)
                if idx is not None:
                    dm_to_user(cl, users[idx])

            elif choice == 2:
                # Threads list
                threads = cl.direct_threads()
                if not threads:
                    print("😶 Koi DM thread nahi mila.")
                    continue
                thread_descriptions = []
                for thread in threads:
                    names = ", ".join([u.username for u in thread.users])
                    thread_descriptions.append(f"Thread ID: {thread.id} | Participants: {names}")
                idx = select_option("Kis thread ka message history dekhna hai?", thread_descriptions)
                if idx is not None:
                    dm_to_thread(cl, threads[idx])

    except LoginRequired:
        print("❌ Session invalid hai! Dobara login karo.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    main()
