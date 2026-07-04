import sys
from pymongo import MongoClient

# Encode the password to handle the @ symbol
uri = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    sys.exit(0)
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)
