# File name: login_save.py

from instagrapi import Client

# Client object banate hain
cl = Client()

# Login details
USERNAME = "edible9012@deshnetarchadacalculator.one"
PASSWORD = "YourName@@"

# Login karo
cl.login(USERNAME, PASSWORD)

# Session save karo file me
cl.dump_settings("session.json")

print("✅ Login success! Session save ho gaya 'session.json' me.")
