#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from mcmc import *
from rulelist import *
from data import *
from sklearn import metrics

TABLE = "__________________________________________________________________________________________________________________________________________________________________________________________________________"
SEP = "\n............................................................................................................................................................................................................\n"

MCMC_REPS = 1000

# NEED: Create two rule lists, one private, one not. Compare scores using the score function.
# Compare length of rule list and average length of the antecedents, compare to lambda and eta.
# Compare the auc of the private Rule List on it's classification on a reserved DS, vs non-private.
# Compare the auc of the private Rule List on it's classification on the non-noisey DS.
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

def auc(ds, rl):
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
    d_ac = auc(titanic_res_DS, titanic_rl)
    pd_ac = auc(titanic_res_DS, priv_titanic_rl)
    print("Rule list "+("d" if d_ac > pd_ac else "pd")+ " is more accurate with " +
         (str(d_ac) if d_ac > pd_ac else str(pd_ac)) + " correctly classified vs. " +
         (str(pd_ac) if d_ac > pd_ac else str(d_ac)) + " within the Titanic reserve DS.\n")

def runNoNoise(ds, priv_rl):
    pd_ac = auc(ds, priv_rl)
    print("The privatized rule list has an auc of " + str(pd_ac) + " on the original, untouched DS.\n")

def regSysTest():
    d = run("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 9.0, 1.0, 1000)
    print("Rule list for Shrooms:\n")
    d.printNeat()
    print("\n_____TESTING______\n")
    print(auc(d.dataset, d))
    print(score(d, 9.0, 1.0))

def DPSysTest():
    d = runDP("../Data/shroom_fim.txt", "../Data/UCI_shroom_clean.txt", "edible", 5.0, 1.0, .1, 1000)
    print("DP Rule list for Shrooms:\n")
    d.printNeat()
    print("\n_____TESTING______\n")
    print(auc(d.dataset, d))

def fullTest(rl_labels, epsilons):
    datasets = ["../Data/UCI_shroom_clean.txt", "../Data/kaggle_titanic_clean_train.txt"]
    reserve_ds = ["../Data/UCI_shroom_res.txt", "../Data/kaggle_titanic_clean_res.txt"]
    fims = ["../Data/shroom_fim.txt", "../Data/titanic_fim.txt"]
    labels = ["edible", "Survived"]
    rls = []
    print("Rule list\t|\t Dataset \t|\t Epsilon \t|\t Avg ant. len.: eta: 1.0 \t|\t Rule list len.: lam: 7.0 \t|\t Training auROC \t|\t Reserve auROC ")
    print(TABLE)
    for j in range(len(datasets)):
        for i in range(len(rl_labels)):
            if i == 0:
                rl = run(fims[j], datasets[j], labels[j], 7.0, 1.0, MCMC_REPS)
            else:
                rl = runDP(fims[j], datasets[j], labels[j], 7.0, 1.0, epsilons[i], MCMC_REPS)
            print("\t" + rl_labels[i] + "\t|\t" + datasets[j] + "\t|\t" + str(epsilons[i]) + "\t|\t" +
                  str(avgAntecedentLen(rl)) + "\t|\t" + str(len(rl.rules)) + "\t|\t" +
                  str(auc(rl.dataset, rl)) + "\t|\t" + str(auc(readData(reserve_ds[j]), rl)))
            rls.append(rl)
        print(SEP)

    for rl in rls:
        rl.printNeat()
def main():
    rl_labels = ["Regular RL", "DP ep:1.0", "DP ep:.5", "DP ep:.1"]
    eps = ['_',1.0, .5, .1]

    # Test: Run all rule lists on all dataset and compare lengths to hyperparameters, and auROC.
    fullTest(rl_labels, eps)
main()
