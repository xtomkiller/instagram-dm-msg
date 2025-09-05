# File name: instagram_dm_tool.py

from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import os
import json

SESSION_FILE = "session.json"

def get_username_from_id(user_id, users):
    for u in users:
        if u.pk == user_id:
            return u.username
    return "Unknown"

def dm_to_thread(cl, thread):
    print(f"\nParticipants: {', '.join([u.username for u in thread.users])}")
    print("\nMessages in this thread:")

    messages = getattr(thread, 'messages', None) or getattr(thread, 'items', [])
    
    for message in messages:
        sender_id = getattr(message, 'user_id', None) or getattr(message, 'sender_id', None)
        from_user = get_username_from_id(sender_id, thread.users)
        text = getattr(message, 'text', '') or getattr(message, 'message', '') or ''
        print(f"{from_user}: {text}")

    send_msg = input("\nIs thread me message bhejna hai? (yes/no): ").strip().lower()
    if send_msg == "yes":
        msg = input("Message likho: ").strip()
        if msg:
            recipients = [u.pk for u in thread.users if u.pk != cl.user_id]
            cl.direct_send(msg, recipients)
            print("✅ Message bheja gaya!")
        else:
            print("❌ Message blank tha, bheja nahi gaya.")
    else:
        print("Message bhejna cancel kar diya gaya.")

def dm_to_users(cl, users_list):
    for idx, user in enumerate(users_list, 1):
        print(f"{idx}. {user.username}")
    choice = input("Kisko message bhejna hai? Number daalo (ya 'exit' karne ke liye): ").strip()
    if choice.lower() == 'exit':
        return
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(users_list):
        print("❌ Galat input!")
        return
    user = users_list[int(choice) -1]
    print(f"\nUser selected: {user.username}")
    msg = input("Message likho: ").strip()
    if msg:
        cl.direct_send(msg, user.pk)
        print("✅ Message bheja gaya!")
    else:
        print("❌ Message blank tha, bheja nahi gaya.")

def dm_threads_menu(cl):
    threads = cl.direct_threads()
    if not threads:
        print("❌ Koi DM thread nahi mila.")
        return
    print("\nDM Threads List:")
    for i, thread in enumerate(threads, 1):
        participants = ', '.join([u.username for u in thread.users])
        print(f"{i}. Thread ID: {thread.id} | Participants: {participants}")

    while True:
        choice = input("Kis thread ka message history dekhna hai? Number daalo (ya 'exit' karne ke liye): ").strip()
        if choice.lower() == 'exit':
            break
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(threads):
            print("❌ Galat input! Dobara try karo.")
            continue

        thread = threads[int(choice) - 1]
        dm_to_thread(cl, thread)

def main():
    if not os.path.exists(SESSION_FILE):
        print(f"❌ {SESSION_FILE} file nahi mili! Pehle login karke session save karo.")
        return

    cl = Client()
    try:
        cl.load_settings(SESSION_FILE)
        cl.get_timeline_feed()  # Check if session valid
    except LoginRequired:
        print("❌ Session invalid hai! Dobara login karo username/password ke sath.")
        return
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return

    print("✅ Session se login successful!")

    while True:
        print("\nSelect karo option:")
        print("1. DM to Following list")
        print("2. DM to Followers list")
        print("3. DM to Threads list")
        print("4. Exit")

        choice = input("Number daalo: ").strip()

        if choice == "1":
            following = cl.user_following(cl.user_id)
            if not following:
                print("❌ Following list empty hai.")
                continue
            dm_to_users(cl, list(following.values()))
        elif choice == "2":
            followers = cl.user_followers(cl.user_id)
            if not followers:
                print("❌ Followers list empty hai.")
                continue
            dm_to_users(cl, list(followers.values()))
        elif choice == "3":
            dm_threads_menu(cl)
        elif choice == "4":
            print("Bye! Program close ho raha hai.")
            break
        else:
            print("❌ Galat input! Dobara try karo.")

if __name__ == "__main__":
    main()
