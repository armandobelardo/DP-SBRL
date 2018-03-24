#!/usr/bin/env python

# Read in frequent itemsets and return as a list of lists. FIM mined using C++ code in ../RuleMining
def readFIM(fname):
    return readGeneric(fname)

# Read in data and return as a list of lists, one list per transaction.
def readData(fname):
    return readGeneric(fname)

def readGeneric(fname):
    lol = []
    f = open(fname, 'r')
    for transaction in f:
        lol.append(transaction.split())
    f.close()
    return lol

# def main():
#     test = readGeneric("test.txt")
#     for list in test:
#         print list
# main()
