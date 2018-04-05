#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from mcmc import *
from rulelist import *
from data import *
from sklearn import metrics

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

def proximity(d, pd, lam, eta):
    avgAntD = avgAntecedentLen(d)
    avgAntPD = avgAntecedentLen(pd)
    d_closer_lam = math.fabs(len(d.rules)-lam) < math.fabs(len(pd.rules)-lam)
    d_closer_eta = math.fabs(avgAntD - eta) < math.fabs(avgAntPD - eta)

    print(("d" if d_closer_lam else "pd") + " is more 'readable' WRT lambda with a length " +
          (len(d.rules) if d_closer_lam else len(pd.rules)) + ", closer to our lambda: "+ str(lam))
    print(("d" if d_closer_eta else "pd") + " is more 'readable' WRT eta with an average antecedent length (" +
          (avgAntD if d_closer_eta else avgAntPD) + ", closer to our eta: "+ str(eta) + '\n')

def scoring(d, pd, lam, eta):
    d_score = score(d, lam, eta)
    pd_score = score(pd, lam, eta)

    print("Rule list "+("d" if d_score > pd_score else "pd")+" scores higher with a score of " +
         (str(d_score) if d_score > pd_score else str(pd_score)) + " vs. " +
         (str(pd_score) if d_score > pd_score else str(d_score)) + '\n')

def compShroom():
    d = run("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 7.0, 4.0, 10000)
    print("Regular Shroom Rule List:")
    d.printNeat()
    print("\n----------------- SHROOM TESTING ------------------\n")

    # proximity(d, pd, 7.0, 4.0)
    # scoring(d, pd, 7.0, 4.0)
    # return d, pd

def compTitanic():
    d = run("../Data/titanic_fim.txt", "../Data/kaggle_titanic_clean_train.txt", "Survived", 5.0, 3.0, 10000)
    print("Regular Titanic Rule List:")
    d.printNeat()
    print("\n----------------- TITANIC TESTING ------------------\n")

    # proximity(d, pd, 5.0, 3.0)
    # scoring(d, pd, 5.0, 3.0)
    # return d, pd

def trueLabel1(ds, label):
    labels = []
    for transaction in ds:
        if label in transaction:
            labels.append(1)
        else:
            labels.append(0)
    return labels

def confidenceOfLabel1(ds, rl):
    rule_conf = []
    conf_scores = []
    for capture in rl.captures:
        probability = 0.0 if sum(capture) == 0 else float(capture[1])/sum(capture)
        rule_conf.append(probability)

    for transaction in ds:
        added = False
        for i, rule in enumerate(rl.rules):
            if set(rule).issubset(transaction):
                added = True
                conf_scores.append(rule_conf[i])
                break
        # Default rule, transaction is not captured by any other rule.
        if not added:
            conf_scores.append(rule_conf[-1])
    return conf_scores

def accuracy(ds, rl):
    fpr, tpr, _ = metrics.roc_curve(trueLabel1(ds, rl.label), confidenceOfLabel1(ds, rl))
    roc_auc = metrics.auc(fpr, tpr)
    return roc_auc

def runTitanicReserve(titanic_rl, priv_titanic_rl):
    titanic_res_DS = readData("../Data/kaggle_titanic_clean_res.txt")
    d_ac = accuracy(titanic_res_DS, titanic_rl)
    pd_ac = accuracy(titanic_res_DS, priv_titanic_rl)
    print("Rule list "+("d" if d_ac > pd_ac else "pd")+ " is more accurate with " +
         (str(d_ac) if d_ac > pd_ac else str(pd_ac)) + " correctly classified vs. " +
         (str(pd_ac) if d_ac > pd_ac else str(d_ac)) + " within the Titanic reserve DS.\n")

def runNoNoise(ds, priv_rl):
    pd_ac = accuracy(ds, priv_rl)
    print("The privatized rule list has an accuracy of " + str(pd_ac) + " on the original, untouched DS.\n")

def regSysTest():
    d = run("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 5.0, 1.0, 30000)
    print("Rule list for Shrooms:\n")
    d.printNeat()
    print("\n_____TESTING______\n")
    print(accuracy(d.dataset, d))


# def main():
    # shroom_rl, priv_shroom_rl = compShroom()
    # titanic_rl, priv_titanic_rl = compTitanic()
    #
    # runTitanicReserve(titanic_rl, priv_titanic_rl)
    # runNoNoise(shroom_rl.dataset, priv_shroom_rl)
    # TODO(iamabel): need a test for different epsilon values, also need the DP solution (hahaha).
regSysTest()
