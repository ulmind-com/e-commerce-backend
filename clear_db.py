import asyncio
from pymongo import MongoClient

uri = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
client = MongoClient(uri)
db = client.ecommerce

def clear_collections():
    db.products.drop()
    db.categories.drop()
    print("Collections dropped")

if __name__ == "__main__":
    clear_collections()
