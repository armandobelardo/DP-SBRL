import scipy as sp
import numpy as np

LOOP_ITERATIONS = 10000

# Score outcome y with capture vector N and preference vector alpha.
# Ensure alpha reflects the multinomial representing the potential labels.
def likelihood(y, N, alpha=[1,1]):
    fit = 1
    for capture in N:
        numerator = 1
        for i in range(len(capture)): # Binary for our use, expect 2 iterations.
            numerator *= sp.special.gamma(capture[i] + alpha[i])
        fit *= numerator / sp.special.gamma(sum(capture) + sum(alpha))
    return fit

def antecedent_length(len_j, A_after_j, eta):
    return 1

def which_antecedents():
    return 1

def rules_in_list(m, len_A, lambda):
    return 1

# Score rule list d with antecedent list d.antecedents, and hyperparameters lam(bda) (desired rule
# list length) and eta (desired number of conditions per rule).
def prior(d, lam, eta):
    antecedent_product = 1
    for i in range(len(d.antecedents)):
        antecedent_product *= antecedent_length(len(d.antecedents[i]), d.antecedents[i:], eta)*which_antecedents()
    return antecedent_product * rules_in_list(len(d), len(d.antecedents), lam)

def score(d, N, lam, eta):
    # TODO(iamabel): Figure out what y is to score it.
    # return prior(d, lam, eta)*likelihood(y, N)
    return 1


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
