#!/usr/bin/env python
import re

def get_shroom_guide():
    shroom_schema = open("../Data/Schema/shroom_schema.txt", 'r')
    cats = []
    shroom_guide = []
    for att in shroom_schema:
        att = re.split('[0-9]+. |: |=|, |,', att.strip())
        cats.append(att[1])
        cat_deets = {}
        for i in range(2,len(att),2):
            cat_deets[att[i+1]] = att[i]
        shroom_guide.append(cat_deets)
    shroom_schema.close()
    return cats, shroom_guide

def mushrooms(fname):
    shroom_clean = open("../Data/shroom_clean.txt", "w+")
    shrooms = open(fname, 'r')
    cats, shroom_guide = get_shroom_guide()
    transactions = []
    for shroom in shrooms:
        transaction = []
        shroom_deets = shroom.strip().split(',')
        for i in range(len(cats)):
            if i == 0 or i == 4:
                transaction.append(cats[i])
            else:
                transaction.append(cats[i]+ "=" + shroom_guide[i][shroom_deets[i]])
        shroom_clean.write(" ".join(transaction)+"\n")

    shroom_clean.close()
    shrooms.close()

def sani_mushrooms():
    mushrooms("../Data/UCI-agaricus-lepiota.data")

sani_mushrooms()
