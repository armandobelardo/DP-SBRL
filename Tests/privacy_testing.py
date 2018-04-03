#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from mcmc import *
from rulelist import *

# NEED: Create two rule lists, one private, one not. Compare scores using the score function.
# Compare length of rule list and average length of the antecedents, compare to lambda and eta.
# Compare the accuracy of the private Rule List on it's classification on a reserved DS, vs non-private.
# Compare the accuracy of the private Rule List on it's classification on the non-noisey DS.
# See the above using different epsilon values.
def avgAntecedentLen(rl):
    count = 0
    for rule in rl.rules:
        count += len(rule)
    return float(count)/len(rl.rules)

def stats(d, pd, lam, eta):
    avgAntD = avgAntecedentLen(d)
    avgAntPD = avgAntecedentLen(pd)
    d_closer_lam = math.fabs(len(d.rules)-lam) < math.fabs(len(pd.rules)-lam)
    d_closer_eta = math.fabs(avgAntD - eta) < math.fabs(avgAntPD - eta)

    print(("d" if d_closer_lam else "pd") + " is more 'readable' WRT lambda with a length " +
          (len(d.rules) if d_closer_lam else len(pd.rules)) + ", closer to our lambda: "+ str(lam))
    print(("d" if d_closer_eta else "pd") + " is more 'readable' WRT eta with an average antecedent length (" +
          (avgAntD if d_closer_eta else avgAntPD) + ", closer to our eta: "+ str(eta))


def compShroom():
    d = run("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 7.0, 4.0, 10000)
    print("Regular Shroom Rule List:")
    d.printNeat()

    # stats(d, pd, 7.0, 4.0)


def compTitanic():
    d = run("../Data/titanic_fim.txt", "../Data/kaggle_titanic_clean_train.txt", "Survived", 5.0, 3.0, 10000)
    print("Regular Titanic Rule List:")
    d.printNeat()

    # stats(d, pd, 5.0, 3.0)

# compShroom()
compTitanic()
