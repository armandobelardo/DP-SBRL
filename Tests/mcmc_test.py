#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from data import *
from mcmc import *

# If we do not run any MCMC iterations we should get a rule list consisting of all possible rules with
# the corresponding information correct (ie. label, rules, captures, unused)
def initRLTest():
    all_rules_and_captures = run("../Data/fim_1.txt", "../Data/dat2_test.txt", "diapers", 5.0, 3.0, 0)
    rules = [["beer"], ["cola"], ["bread","milk"], ["beer","milk"], ["milk"], ["cola","milk"], ["beer","bread"], ["bread"]]
    captures = [[0,3],[0,1],[1,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
    all_passed = True

    all_passed = all_passed and (all_rules_and_captures.rules == rules)
    all_passed = all_passed and (all_rules_and_captures.label == "diapers")
    all_passed = all_passed and (all_rules_and_captures.captures == captures)
    all_passed = all_passed and (all_rules_and_captures.unused == [])

    return all_passed
def mathmaticalTests():
    all_passed = True       # Allows us to run all tests without quitting at a failure.
    # Test likelihood
    N = [[1,1], [2,3], [0,0], [4,9]]
    output_likelihood = likelihood(N)
    ex_likelihood = ((1.0/6.0) * (12.0/720.0) * 1.0 * (8709120.0/87178291200.0))
    if output_likelihood != ex_likelihood:
        all_passed = False
        print("likelihood function failed, expect: " + str(ex_likelihood) + " got: " + str(output_likelihood))

    # Test rules_list_length
    output_list_length = rules_list_length(4, 2, 3)
    ex_list_length = ((81.0)/24.0) / 8.5
    if output_list_length != ex_list_length:
        all_passed = False
        print("rules_list_length function failed, expect: " + str(ex_list_length) + " got: " + str(output_list_length))

    # Test antecedent_length
    output_antecedent_length = antecedent_length(3, [['hi', 'there'],['i', 'am', 'here'], ['this', 'has', 'five', 'words', 'now']], 2)
    ex_antecedent_length = ((8.0)/6.0) / (2.0 + 8.0/6.0 + 32.0/120.0)
    if output_antecedent_length != ex_antecedent_length:
        all_passed = False
        print("antecedent_length function failed, expect: " + str(ex_antecedent_length) + " got: " + str(output_antecedent_length))

    # Test prior
    output_prior = prior(run("../Data/dummy_fim.txt", "../Data/dummy_data.txt", "x", 3.0, 2.0, 0), 3, 2)
    ex_prior = (4.5 / 13.0) * (2.0 / (2.0 + 8.0/6.0 + 128.0/5040.0)) * ((8.0/6.0) / (8.0/6.0 + 128.0/5040.0))
    if output_prior != ex_prior:
        all_passed = False
        print("prior function failed, expect: " + str(ex_prior) + " got: " + str(output_prior))

    return all_passed

def main():
    print("init Rule List built correctly? " + str(initRLTest()))
    print("All Mathematical Tests Passed? " + str(mathmaticalTests()))
main()
