import pymongo

myclient = pymongo.MongoClient(
    f"mongodb://zara:zara*2009@192.168.100.37:27017/?authMechanism=DEFAULT"
)

mydb = myclient["europages"]

collection = "Construction"


# mydb[collection].update_many({}, {"$set": {"complete": 0}})


mydb[collection].delete_many({'Country': "Germany"})


# all_data = list(mydb[collection].find())

# for data in all_data:
#     print(data)
#     new_country = data["Country"].replace("-", " ").title()
#     mydb[collection].update_one(
#         {"_id": data["_id"]}, {"$set": {"Country": new_country}}
#     )
