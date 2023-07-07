import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["legal_500"]

collection = "legal_500_ALL"


# mydb[collection].update_many({}, {"$set": {"complete": 0}})


all_data = list(mydb[collection].find())

for data in all_data:
    print(data)
    new_country = data["Country"].replace("-", " ").title()
    mydb[collection].update_one(
        {"_id": data["_id"]}, {"$set": {"Country": new_country}}
    )
