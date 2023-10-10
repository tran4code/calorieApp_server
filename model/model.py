#  calculating a diet plan and generating a weight loss/gain projection chart
import pandas as pd
import pymongo
import collections
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_data.csv")
index_list = df.index.tolist()

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test"]
p_details = db["profile"]  # profile details
records = p_details.find()  # retrieves all documents
list_record = list(records)  # converts the cursor object to a list

df_profile = pd.DataFrame(list_record)
cur_wt_list = df_profile["weight"].tolist()
goal_wt_list = df_profile["target_weight"].tolist()

food = df["Food"].tolist()
calories = df["Calories"].tolist()


# Sum of Subsets problem, Trying to find a subset of food that satisfy its daily gold
# but the variable name as weight it's really confused really not helpful
def find_subset(weight: list, req_sum: int):
    # ROWS : array, # COL : range(sum)
    row = len(weight)
    col = req_sum + 1

    # 2d array storing Sum
    dp_array = [[0] * col for i in range(row)]

    for i in range(row):
        for j in range(1, col):
            # Row 0
            if i == 0:
                if j >= weight[i]:
                    dp_array[i][j] = weight[i]
                else:
                    continue
            else:
                if j - weight[i] >= 0:
                    dp_array[i][j] = max(
                        dp_array[i - 1][j], (weight[i] + dp_array[i - 1][j - weight[i]])
                    )
                elif j >= weight[i]:
                    # take from row above it
                    dp_array[i][j] = max(dp_array[i - 1][j], weight[i])
                else:
                    dp_array[i][j] = dp_array[i - 1][j]

    # Find out which Numbers should be in the subset
    # give from index 0
    row -= 1
    col -= 1
    sum_subset = []

    # check if the Subset is possible : if not, return None
    if dp_array[row][col] != req_sum:
        return None

    # get the subset
    while col >= 0 and row >= 0 and req_sum > 0:
        # First Row
        if row == 0:
            sum_subset.append(weight[row])
            break

        # Bottom-Right most ele
        if dp_array[row][col] != dp_array[row - 1][col]:
            # print(req_sum,' : ',dp_array[row][col],dp_array[row-1][col],' : ',
            # weight[row])
            sum_subset.append(weight[row])
            req_sum -= weight[row]
            col -= weight[row]
            row -= 1
        else:
            row -= 1

    return sum_subset


cur_wt_track = []
# cur_wt = int(input('Enter current weight: '))
cur_wt = int(cur_wt_list[0])
goal_wt = int(goal_wt_list[0])
cur_wt_track.append(cur_wt)
# goal_wt = int(input('Enter goal weight: '))
# set_goal = int(input('In how many days? '))

cal_to_burn = (cur_wt - goal_wt) * 7700
if goal_wt < cur_wt:  # diet
    daily_target = int((cur_wt - goal_wt) * 7700 / 30) - int(
        (cur_wt - goal_wt) * 7700 * 0.8 / 30
    )  # -2000 #1 kg = 7700 cal
else:
    daily_target = int((goal_wt - cur_wt) * 7700 / 30) - int(
        (goal_wt - cur_wt) * 7700 * 0.8 / 30
    )
# print(daily_target)
r = round((cur_wt - goal_wt) / 30, 2)

for i in range(30):
    cur_wt = round(cur_wt - r, 2)
    cur_wt_track.append(cur_wt)
# print(cur_wt_track)                #shows weight trend if diet is followed for 30 days

# calories.sort(reverse = True)
food_sort = [x for _, x in sorted(zip(calories, food))]
# print(food_sort)
calories.sort()

sum_subset = find_subset(calories, daily_target)
# print(sum_subset)


# if sum_subset is None:
# print("Sum :", daily_target, "is not possible")
# else:
# print("Subset for sum", daily_target, ' :', sum_subset)

occurrences = collections.Counter(sum_subset)
# print(occurrences)
dict_occ = dict(occurrences)
# print(dict_occ)

list_occ = []
for i in dict_occ:
    t = []
    t.append(i)
    t.append(dict_occ[i])
    list_occ.append(t)
# print(list_occ)

u_cal = list(set(sum_subset))
u_cal_food = []

for i in range(len(u_cal)):
    t = []
    for j in range(len(food)):
        if u_cal[i] == calories[j]:
            t.append(food_sort[j])
    u_cal_food.append(t)
# print(u_cal_food)

"""
for i in range(len(u_cal)):
    print('Consume one of these items', u_cal_food[i],'*',list_occ[i][1], 'times')
"""
# "diet_guide.txt"
diet_report = open(
    "C:\\Users\\Shivam\\Desktop\\calorieApp_server\\model\\diet_guide.txt", "wt"
)  # path

for i in range(len(u_cal)):
    fl = "Consume one of these items", u_cal_food[i], "*", list_occ[i][1], "times"
    fl = list(fl)
    string = " ".join([str(item) for item in fl])
    diet_report.writelines(string)
    diet_report.writelines("\n")

diet_report.close()

plt.plot(cur_wt_track, marker="o", color="green")
plt.xlabel("Days")
plt.ylabel("Weight")
plt.title("30 day weight gain/loss projections")
plt.show()
