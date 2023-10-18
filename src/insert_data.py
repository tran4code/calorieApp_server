from apps import App
import csv

app = App()
mongo = app.mongo

# f = open("datasets/calories.csv", "r", encoding="ISO-8859-1")
# lines = f.readlines()
#
# for i in range(1, len(lines)):
#     lines[i] = lines[i][1: len(lines[i]) - 2]
#
# for i in range(1, len(lines)):
#     temp = lines[i].split(",")
#     mongo.db.food.insert_one({"food": temp[0], "calories": temp[1]})

with open("../datasets/nutrition.csv", "r", encoding="utf-8") as food_data:
    food_reader = csv.reader(food_data, delimiter=",", quotechar='"')

    next(food_reader, None)

    food_list = []

    for row in food_reader:
        food = row[0].strip('"')
        cals = int(row[1])
        food_list.append((food, cals))

    sorted_food_list = sorted(food_list, key=lambda x: x[0])

    for item in sorted_food_list:
        mongo.db.food.insert_one({"food": item[0], "calories": item[1]})

with open("../datasets/exercise_dataset.csv", "r", encoding="utf-8") as exercise_data:
    activity_reader = csv.reader(exercise_data, delimiter=",", quotechar='"')

    next(activity_reader, None)

    activity_list = []

    for row in activity_reader:
        activity = row[0].strip('"')
        rate = float(row[1])
        activity_list.append((activity, rate))

    sorted_activity_list = sorted(activity_list, key=lambda x: x[0])

    for item in sorted_activity_list:
        mongo.db.activities.insert_one({"activity": item[0], "burn_rate": item[1]})
