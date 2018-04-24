#!/usr/bin/env python
import re
import csv

def get_shroom_guide():
    shroom_schema = open("../Data/Schema/UCI_shroom_schema.txt", 'r')
    cats = []
    shroom_guide = []
    for att in shroom_schema:
        att = re.split('[0-9]+. |: |=|, |,', att.strip())
        # Note we begin with an empty string, so index one holds the category name
        cats.append(att[1])
        cat_deets = {}
        for i in range(2,len(att),2):
            # The format is type=abbrv, since the data contains abbrvs, we want to reverse map this
            # data (ie abbrv:type).
            cat_deets[att[i+1]] = att[i]
        shroom_guide.append(cat_deets)
    shroom_schema.close()
    return cats, shroom_guide

def sani_mushrooms():
    shroom_clean = open("../Data/UCI_shroom_clean.txt", "w+")
    shrooms = open("../Data/UCI-agaricus-lepiota.data", 'r')
    cats, shroom_guide = get_shroom_guide()
    for shroom in shrooms:
        transaction = []
        shroom_deets = shroom.strip().split(',')
        for i in range(len(cats)):
            if i == 0 or i == 4:
                if shroom_deets[i] == 'e' or shroom_deets[i] == 't':
                    transaction.append(cats[i])
            else:
                transaction.append(cats[i]+ "=" + shroom_guide[i][shroom_deets[i]])
        shroom_clean.write(" ".join(transaction)+"\n")

    shroom_clean.close()
    shrooms.close()

def sani_titanic():
    cats = ["Survived", "Pclass", "Sex", "Age", "Cabin"]
    passengers_clean = open("../Data/kaggle_titanic_clean_train.txt", "w+")
    with open('../Data/kaggle-titanic.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transaction = []
            # Not particularly useful to us if we can't get details on survival.
            if row["Survived"] == '':
                continue
            for cat in cats:
                if row[cat] == '':
                    continue
                if cat == "Age":
                    age = int(float(row[cat]))
                    # We'll arbitrarily choose 4 age buckets: -12, 13-21, 22-40, 41+
                    if age <= 12:
                        transaction.append("Age<13")
                    elif age <= 21:
                        transaction.append("Age=13-21")
                    elif age <= 40:
                        transaction.append("Age=22-40")
                    else:
                        transaction.append("Age>40")
                elif cat == "Survived":
                    if int(row[cat]):
                        transaction.append("Survived")
                elif cat == "Cabin":
                    transaction.append("Cabin="+row[cat][0])
                else:
                    transaction.append(cat+"="+row[cat])
            passengers_clean.write(" ".join(transaction)+"\n")
    passengers_clean.close()

def sani_adult():
    cats = {0:"Age", 1:"WorkClass", 3:"Edu.", 5:"Marital Stat.", 6:"Occ.", 8:"Race", 9:"Sex", 10:"Cap-Gain", 11:"Cap-Loss", 14:">50K"}
    adults_clean = open("../Data/UCI_adult_clean.txt", "w+")
    adults = open("../Data/UCI-adult.data", 'r')

    for adult in adults:
        row = adult.strip().split(', ')
        transaction = []
        for i in cats:
            # Not particularly useful to us if we can't get details on survival.
            if row[i] == '?':
                transaction = []
                break
            if cats[i] == "Age":
                age = int(float(row[i]))
                # We'll arbitrarily choose 4 age buckets: -12, 13-21, 22-40, 41+
                if age <= 29:
                    transaction.append("Age<30")
                elif age <= 40:
                    transaction.append("Age=30-40")
                elif age <= 50:
                    transaction.append("Age=41-50")
                else:
                    transaction.append("Age>50")
            elif cats[i] == "Cap-Gain":
                gain = int(float(row[i]))
                # We'll arbitrarily choose 4 age buckets: -12, 13-21, 22-40, 41+
                if gain == 0:
                    transaction.append("Cap-Gain=0")
                elif gain <= 3499:
                    transaction.append("Cap-Gain<3500")
                elif gain <= 7000:
                    transaction.append("Cap-Gain=3500-7000")
                else:
                    transaction.append("Cap-Gain>7000")
            elif cats[i] == "Cap-Loss":
                loss = int(float(row[i]))
                # We'll arbitrarily choose 4 age buckets: -12, 13-21, 22-40, 41+
                if loss == 0:
                    transaction.append("Cap-Loss=0")
                elif loss <= 499:
                    transaction.append("Cap-Loss<500")
                elif loss <= 1500:
                    transaction.append("Cap-Loss=500-1500")
                else:
                    transaction.append("Cap-Loss>1500")
            elif i == 14:
                if row[i] == ">50K":
                    transaction.append(">50k")
            else:
                transaction.append(cats[i]+"="+row[i])
        if len(transaction) > 0:
            adults_clean.write(" ".join(transaction)+"\n")
    adults.close()
    adults_clean.close()
sani_adult()
