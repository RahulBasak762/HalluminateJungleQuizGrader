import json

data = None
with open('cards_from_random_downvoted_cards_20250123_145929_without_understanding_ratings_for_card_by_user.json', 'r') as file:
    data = json.load(file)


with open("output1.json", "r") as file:
    dic1 = json.load(file)  # Fix: Use json.load instead of json.loads

with open("output2.json", "r") as file:
    dic2 = json.load(file)

combinedDict = {}
for i in range(1, 7, 1):
    key = f"[CATEGORY: {i}]"
    combinedDict[key] = dic1.get(key, []) + dic2.get(key, [])


finalDict = {}
for key in combinedDict.keys():
    finalDict[key] = []
    for cardNum in combinedDict[key]:
        finalDict[key].append(data[cardNum]["id"])

print(finalDict)


with open("ID_Map.json", "w") as file:
    json.dump(finalDict, file, indent=4)
