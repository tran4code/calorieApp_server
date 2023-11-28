# MIT License
#
# Copyright 2023 BurnOut4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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
