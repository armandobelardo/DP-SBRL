#!/usr/bin/env python

import scipy as sp
from scipy.special import gamma
import numpy as np
import math
from rulelist import *

LOOP_ITERATIONS = 10000

# Score outcome y with capture vector N and preference vector alpha.
# Ensure alpha reflects the multinomial representing the potential labels.
def likelihood(N, alpha=[1,1]):
    fit = 1.0
    for capture in N:
        numerator = 1.0
        for i in range(len(capture)): # Binary for our use, expect 2 iterations.
            numerator *= gamma(capture[i] + alpha[i])
        fit *= numerator/ gamma(sum(capture) + sum(alpha))
    return fit

# TODO(iamabel): Exists for continuity with the paper. Serves almost no purpose, consider removal.
def which_antecedents():
    return 1

def rules_list_length(m, len_A, lam):
    denominator = 0.0
    for j in range(len_A+1):
        denominator += lam**j/math.factorial(j)

    return (lam**m/math.factorial(m))/denominator

def antecedent_length(len_j, A_after_j, eta):
    denominator = 0.0
    for k in A_after_j:
        # TODO(iamabel): The paper is unclear here with what exactly R_{j-1} is
        denominator += eta**len(k)/math.factorial(len(k))

    return (eta**len_j/math.factorial(len_j))/denominator

# Score rule list d with antecedent list d.antecedents, and hyperparameters lam(bda) (desired rule
# list length) and eta (desired number of conditions per rule).
def prior(d, lam, eta):
    antecedent_product = 1.0
    for j in range(len(d.rules)):
        antecedent_product *= antecedent_length(len(d.rules[j]), d.rules[j:], eta)*which_antecedents()
    return antecedent_product * rules_list_length(len(d.rules), len(d.antecedents), lam)

def score(d, lam, eta):
    return prior(d, lam, eta)*likelihood(d.captures)

# Uniformly at random select the rule list mutation. Then uniformly at random select the antecedents
# to move around and their new locations.
def proposal(d):
    alteration = np.random.randint(3)

    if alteration == 0 and len(d.unused) > 1:  # add
        d_c = d.copy()

        # Get antecedent at random and get a random spot to insert it into.
        i = np.random.randint(len(d.rules))
        j = np.random.randint(len(d.unused))
        d_c.add(i, j)
        return d_c, alteration
    elif alteration == 0: # unsuccessful add.
        return d, -1

    if alteration == 1 and len(d.rules) > 1: # delete, no point in trying a rule list of length 0.
        d_c = d.copy()

        # Get rule to delete at random.
        i = np.random.randint(len(d.rules))
        d_c.delete(i)
        return d_c, alteration
    elif alteration == 1: # unsuccessful delete.
        return d, -1

    if alteration == 2 and len(d.rules) > 1: # swap, no point in swapping one element with itself.
        d_c = d.copy()

        # Get two locations to swap at random.
        i, j = np.random.randint(len(d.rules), size=2)
        d_c.swap(i, j)
        return d_c, alteration
    elif alteration == 2: # unsuccessful swap.
        return d, -1


def Q(given, alteration):
    # TODO(iamabel): This makes us not be able to add to make a list of full size, we'd div by 0.
    if alteration == 0:
        return 1.0/((len(given.antecedents)-len(given.rules))*(len(given.rules)+1))
    elif alteration == 1:
        return 1.0/len(given.rules)
    elif alteration == 2:
        return 1.0/(len(given.rules)*(len(given.rules)-1))

# Run Metropolis-Hastings MCMC, get new rule list, score, keep or reject based on random alpha.
def mcmc_mh(d, lam, eta):
    new_rule_list, alteration = proposal(d)
    if (alteration == -1): # Unsuccessful proposal, d is unchanged.
        return d

    Q_factor = Q(d, alteration) / Q(new_rule_list, alteration)
    alpha = (score(new_rule_list, lam, eta)/score(d, lam, eta)) * Q_factor
    # Always accept the new rule list if it scores higher. Otherwise, accept it with probability alpha.
    if alpha >= 1 or np.random.uniform() <= alpha:
        d = new_rule_list

    return d

# Note lam(bda) and eta are hyperparameters dictating length of rule list and number of conditions
# per rule, respectively.
def run(antecedents, dataset, label, lam, eta):
    d = RuleList(antecedents, dataset, label)
    best = d
    for _ in range(LOOP_ITERATIONS):
        d = mcmc_mh(d, lam, eta)
        # Note that we will check every new rule list produced that has a better score than the
        # original d by the condition in mcmc_mh. Ocassionally, we get a rule list isn't better,
        # with probability alpha, so we cache the best rule list.
        best = d if score(d, lam, eta) > score(best, lam, eta) else best
    return best

def runDefault(lam, eta):
    d = RuleList()
    best = d
    for _ in range(LOOP_ITERATIONS):
        d = mcmc_mh(d, lam, eta)
        best = d if score(d, lam, eta) > score(best, lam, eta) else best
    return best

def main():
    d = runDefault(5.0, 3.0)
    d.printNeat()

main()
