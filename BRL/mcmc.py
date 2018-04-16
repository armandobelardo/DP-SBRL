#!/usr/bin/env python
from __future__ import division

import scipy as sp
from scipy.special import gammaln
from scipy.misc import factorial
import numpy as np
import math
import warnings
from rulelist import *

LOOP_ITERATIONS = 10000

# Score outcome y with capture vector N and preference vector alpha.
# Ensure alpha reflects the multinomial representing the potential labels.
# To avoid integer over- or under-flow, we are getting the log of the likelihood.
def likelihood(N, alpha=[1,1]):
    fit = 0.0
    for capture in N:
        numerator = 0.0
        for i in range(len(capture)): # Binary for our use, expect 2 iterations.
            numerator += gammaln(capture[i] + alpha[i])
        fit += numerator - gammaln(sum(capture) + sum(alpha))

    return fit

# TODO(iamabel): Exists for continuity with the paper. Serves almost no purpose, consider removal.
def which_antecedents():
    return 1

# To avoid integer over- or under-flow, we are getting the log of the rules_list_length.
def rules_list_length(m, len_A, lam):
    lam = np.float128(lam)    # Ensure double when critical
    return (np.log(lam**m)-np.log(factorial(m)))

# To avoid integer over- or under-flow, we are getting the log of the antecedent_length.
def antecedent_length(len_j, A_after_j, eta):
    denominator = np.float128(0.0)
    eta = np.float128(eta)    # Ensure double when critical
    for k in A_after_j:
        # TODO(iamabel): The paper is unclear here with what exactly R_{j-1} is
        # Note the denominator is never that large, considering we heavily constrict antecedent mining.
        denominator += eta**len(k)/factorial(len(k))

    return (np.log(eta**len_j)-np.log(factorial(len_j))) - np.log(denominator)

# Score rule list d with antecedent list d.antecedents, and hyperparameters lam(bda) (desired rule
# list length) and eta (desired number of conditions per rule).
# To avoid integer over- or under-flow, we are getting the log of the prior.
def prior(d, lam, eta):
    antecedent_sum =  np.float128(0.0)
    for j in range(len(d.rules)):
        antecedent_sum += antecedent_length(len(d.rules[j]), d.rules[j:], eta)
    return antecedent_sum + rules_list_length(len(d.rules), len(d.antecedents), lam)

# To avoid integer over- or under-flow, we are using logs, hence the addition as opposed got multiplication.
def score(d, lam, eta):
    return prior(d, lam, eta)+likelihood(d.captures)

def dp_score(d, lam, eta, epsilon):
    return (epsilon*score(d, lam, eta)) - (2*np.log(len(d.dataset)))

def scoring(d, lam, eta, epsilon, dp):
    return dp_score(d, lam, eta, epsilon) if dp else score(d, lam, eta)

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
def mcmc_mh(d, lam, eta, epsilon=1, dp=False):
    new_rule_list, alteration = proposal(d)
    if (alteration == -1): # Unsuccessful proposal, d is unchanged.
        return d

    Q_factor = Q(d, alteration) / Q(new_rule_list, alteration)
    lg_alpha = (scoring(new_rule_list, lam, eta, epsilon, dp) - scoring(d, lam, eta, epsilon, dp)) + np.log(Q_factor)

    # Always accept the new rule list if it scores higher. Otherwise, accept it with probability alpha.
    # Given we are utilizing logs, we compare to 0 (basically 1 once exponentiated), additionally,
    # we must catch underflow here, hence the try catch. We assume low scores are yielded from a
    # much lower scoring new rule list, and so we reject it.
    if lg_alpha < 0:
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                alpha = np.exp(lg_alpha)
                if np.random.uniform() <= alpha:
                    return new_rule_list
                else:
                    return d
            except Warning:
                return d
    else:
        return new_rule_list


# Note lam(bda) and eta are hyperparameters dictating length of rule list and number of conditions
# per rule, respectively. These must be floats.
def run(antecedents, dataset, label, lam, eta, loops):
    d = RuleList(antecedents, dataset, label)
    best = d
    for _ in range(loops):
        d = mcmc_mh(d, lam, eta)
        better = (scoring(d, lam, eta, 1, False) - scoring(best, lam, eta, 1, False)) > 0
        # Note that we will check every new rule list produced that has a better score than the
        # original d by the condition in mcmc_mh. Ocassionally, we get a rule list isn't better,
        # with probability alpha, so we cache the best rule list.
        best = d if better else best
    d.calcPointEstimates()
    return best

def runDefault(lam, eta):
    d = RuleList()
    best = d
    for _ in range(LOOP_ITERATIONS):
        d = mcmc_mh(d, lam, eta)
        better = (scoring(d, lam, eta, 1, False) - scoring(best, lam, eta, 1, False)) > 0
        best = d if better else best
    d.calcPointEstimates()
    return best

def runDP(antecedents, dataset, label, lam, eta, epsilon, loops):
    d = RuleList(antecedents, dataset, label)
    for _ in range(loops):
        d = mcmc_mh(d, lam, eta, epsilon, True)
    d.noisifyCaptures(epsilon)
    d.calcPointEstimates()
    return d

def main():
    d = runDefault(5.0, 3.0)
    d.printNeat()
