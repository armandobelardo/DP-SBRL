#!/usr/bin/env python

import scipy as sp
import numpy as np
import math
from rulelist import *

LOOP_ITERATIONS = 10000

# Score outcome y with capture vector N and preference vector alpha.
# Ensure alpha reflects the multinomial representing the potential labels.
def likelihood(N, alpha=[1,1]):
    fit = 1
    for capture in N:
        numerator = 1
        for i in range(len(capture)): # Binary for our use, expect 2 iterations.
            numerator *= sp.special.gamma(capture[i] + alpha[i])
        fit *= numerator / sp.special.gamma(sum(capture) + sum(alpha))
    return fit

# TODO(iamabel): Exists for continuity with the paper. Serves almost no purpose, consider removal.
def which_antecedents():
    return 1

def rules_list_length(m, len_A, lam):
    denominator = 0
    for j in range(len_A+1):
        denominator += lam**j/math.factorial(j)

    return (lam**m/math.factorial(m))/denominator

def antecedent_length(len_j, A_after_j, eta):
    denominator = 0
    for k in A_after_j:
        # TODO(iamabel): The paper is unclear here with what exactly R_{j-1} is
        denominator += eta**len(k)/math.factorial(len(k))

    return (eta**len_j/math.factorial(len_j))/denominator

# Score rule list d with antecedent list d.antecedents, and hyperparameters lam(bda) (desired rule
# list length) and eta (desired number of conditions per rule).
def prior(d, lam, eta):
    antecedent_product = 1
    for j in range(len(d.rules)):
        antecedent_product *= antecedent_length(len(d.rules[j]), d.rules[j:], eta)*which_antecedents()
    return antecedent_product * rules_list_length(len(d.rules), len(d.antecedents), lam)

def score(d, lam, eta):
    return prior(d, lam, eta)*likelihood(d.captures)

# Uniformly at random select the rule list mutation. Then uniformly at random select the antecedents
# to move around and their new locations.
def proposal(d):
    alteration = np.random.randint(3)
    d_c = d.copy()

    if alteration == 0 and len(d.unused) > 0:  # add
        # Get antecedent at random and get a random spot to insert it into.
        i = np.random.randint(len(d.rules))
        j = np.random.randint(len(d.unused))
        d_c.add(d.unused[j], i, j)

    elif alteration == 1 and len(d.rules) > 0: # delete
        # Get rule to delete at random.
        i = np.random.randint(len(d.rules))
        d_c.delete(i)

    elif alteration == 2 and len(d.rules) > 0: # swap
        # Get two locations to swap at random.
        i, j = np.random.randint(len(d.rules), size=2)
        d_c.swap(i, j)

    return d_c, alteration

def Q(given, alteration):
    if alteration == 0:
        return 1/((len(given.antecedents)-len(given.rules))*(len(given.rules)+1))
    elif alteration == 1:
        return 1/len(given.rules)
    elif alteration == 2:
        return 1/(len(given.rules)*(len(given.rules)-1))

# Run Metropolis-Hastings MCMC, get new rule list, score, keep or reject based on random alpha.
def mcmc_mh(d, lam, eta):
    new_rule_list, alteration = proposal(d)
    Q_factor = Q(d, alteration)  / Q(new_rule_list, alteration)
    alpha = (score(new_rule_list, lam, eta)/score(d, lam, eta)) * Q_factor

    # Always accept the new rule list if it scores higher. Otherwise, accept it with probability alpha.
    if alpha >= 1 or np.random.uniform() <= alpha:
        d = new_rule_list

    return d

# Note lam(bda) and eta are hyperparameters dictating length of rule list and number of conditions
# per rule, respectively.
def run(antecedents, dataset, label, lam, eta):
    d = RuleList(antecedents, dataset, label)
    for _ in range(LOOP_ITERATIONS):
        if len(d.rules) > 0:
            d = mcmc_mh(d, lam, eta);
    return d

def runDefault(label, lam, eta):
    d = RuleList(label)
    for _ in range(LOOP_ITERATIONS):
        if len(d.rules) > 0:
            d = mcmc_mh(d, lam, eta);
    return d

def main():
    runDefault("diapers", 5, 4)

main()
