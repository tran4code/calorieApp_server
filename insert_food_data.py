from apps import App

app = App()
mongo = app.mongo

f = open("food_data/calories.csv", "r", encoding="ISO-8859-1")
lines = f.readlines()

for i in range(1, len(lines)):
    lines[i] = lines[i][1 : len(lines[i]) - 2]

for i in range(1, len(lines)):
    temp = lines[i].split(",")
    mongo.db.food.insert_one({"food": temp[0], "calories": temp[1]})
