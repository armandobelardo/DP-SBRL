#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from mcmc import *
from rulelist import *
from data import *
from sklearn import metrics

separator = "\n_______________________________________________________\n"

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

def accOOS(new_ds, rl):
    correct = 0.0
    rule_conf = []
    for capture in rl.captures:
        probability = 0.0 if sum(capture) == 0 else float(capture[1])/sum(capture)
        rule_conf.append(probability)

    for transaction in new_ds:
        for i, rule in enumerate(rl.rules):
            if set(rule).issubset(transaction):
                # Verify that the rule states the labels presence and it is there or the opposite.
                if (rule_conf[i] >= .5 and (rl.label in transaction)) or (rule_conf[i] < .5 and (rl.label not in transaction)):
                    correct += 1
                break
    return correct / len(new_ds)

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
    d = run("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 9.0, 1.0, 1000)
    print("Rule list for Shrooms:\n")
    d.printNeat()
    print("\n_____TESTING______\n")
    print(accuracy(d.dataset, d))
    print(score(d, 9.0, 1.0))


# def main():
#     rl_labels = ["Regular", "DP ep:.3"] # Just examples, fill in with the DP epsilons used
#
#     # Test: Run all rule lists on the shroom dataset and compare lengths to hyperparameters.
#     print("\tRule list\t|\tAvg ant. len.: Shroom - eta: 1.0\t|\tRule list length: Shroom - lam: 5.0")
#     for i,rl in enumerate(rlsShroom):
#         print(rl_labels[i] + "\t|\t" + str(avgAntecedentLen(rl)) + "\t|\t" + str(len(rl.rules)))
#     print(separator)
#
#     # Test: Run all rule lists on reserve data from the titanic dataset to test out of training acc.
#     titanic_res_DS = readData("../Data/kaggle_titanic_clean_res.txt")
#     print("\tRule list\t|\tTraining auROC\t|\tAccuracy OoS")
#     for i,rl in enumerate(rlsTitanic):
#         print(rl_labels[i] + "\t|\t" + str(accuracy(rl.dataset, rl)) + "\t|\t" + str(accOOS(titanic_res_DS, rl)))
#
#     # Test: Run all rule lists on reserve data from the titanic dataset to test out of training acc.
#     titanic_DS = readData("../Data/kaggle_titanic_clean_train.txt")
#     print("\tRule list\t|\tAccuracy on unNoisey DS")
#     for i,rl in enumerate(rlsTitanicDP_ONLY):
#         print(rl_labels[i+1] + "\t|\t" + str(accOOS(titanic_DS, rl)))
#     # TODO(iamabel): need a test for different epsilon values, also need the DP solution (hahaha).

regSysTest()
