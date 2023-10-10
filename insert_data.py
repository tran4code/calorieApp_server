from apps import App
import csv

app = App()
mongo = app.mongo

f = open("food_data/calories.csv", "r", encoding="ISO-8859-1")
lines = f.readlines()

for i in range(1, len(lines)):
    lines[i] = lines[i][1 : len(lines[i]) - 2]

for i in range(1, len(lines)):
    temp = lines[i].split(",")
    mongo.db.food.insert_one({"food": temp[0], "calories": temp[1]})

with open("food_data/exercise_dataset.csv", "r", encoding="utf-8") as exercise_data:
    reader = csv.reader(exercise_data, delimiter=",", quotechar='"')

    next(reader, None)

    for row in reader:
        activity = row[0].strip('"')
        calories_per_kg_per_hour = float(row[1])
        mongo.db.activities.insert_one(
            {"activity": activity, "burn_rate": calories_per_kg_per_hour}
        )
