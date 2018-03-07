import scipy as sp
import numpy as np
import math

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

def antecedent_length(len_j, A_after_j, eta):
    denominator = 0
    for k in A_after_j:
        denominator += eta**len(k)/math.factorial(len(k))

    return (eta**len_j/math.factorial(len_j))/denominator

def which_antecedents():
    return 1

def rules_list_length(m, len_A, lam):
    denominator = 0
    for j in range(len_A):
        denominator += lam**j/math.factorial(j)

    return (lam**m/math.factorial(m))/denominator

# Score rule list d with antecedent list d.antecedents, and hyperparameters lam(bda) (desired rule
# list length) and eta (desired number of conditions per rule).
def prior(d, lam, eta):
    antecedent_product = 1
    for j in range(len(d.rules)):
        antecedent_product *=
            antecedent_length(len(d.rules[j]), d.rules[:j], eta)*which_antecedents()
    return antecedent_product * rules_list_length(len(d.rules), len(d.antecedents), lam)

def score(d, N, lam, eta):
    return prior(d, lam, eta)*likelihood(N)

# Uniformly at random select the rule list mutation. Then uniformly at random select the antecedents
# to move around and their new locations.
def proposal(d):
    alteration = np.random.randint(3)

    if alteration == 0:   # add
        # Get antecedent at random and get a random spot to insert it into.
        i = np.random.randint(len(d.rules))
        j = np.random.randint(len(d.unused))
        d.add(d.unused[j], i, j)

    elif alteration == 1: # delete
        # Get rule to delete at random.
        i = np.random.randint(len(d.rules))
        d.delete(i)

    else:                 # swap
        # Get two locations to swap at random.
        i, j = np.random.randint(len(d.rules), size=2)
        d.swap(i, j)


# Run Metropolis-Hastings MCMC, get new rule list, score, keep or reject based on random alpha.
def mcmc_mh(d, N, lam, eta):
    new_rule_list = proposal(d)
    alpha = np.random.uniform()

    if score(new_rule_list, N, lam, eta)/score(d , N, lam, eta) <= alpha: # Accept new rule list
        d = new_rule_list

    return d

def run(A, N, lam, eta):
    d = RuleList(dataset)
    for _ in range(LOOP_ITERATIONS):
        d = mcmc_mh(d, N, lam, eta);
    return d
