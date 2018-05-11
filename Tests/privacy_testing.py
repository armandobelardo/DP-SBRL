#!/usr/bin/env python
import sys
sys.path.append("../BRL")
from mcmc import *
from rulelist import *
from data import *
from sklearn import metrics
sys.path.append("../Data/Graphs")
from figurer import *
import time

TABLE = "__________________________________________________________________________________________________________________________________________________________________________________________________________"
SEP = "\n............................................................................................................................................................................................................\n"

MCMC_REPS = 1500
ACC_REPS = 5

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

def trueLabel1(ds, label):
    labels = []
    for transaction in ds:
        if label in transaction:
            labels.append(1)
        else:
            labels.append(0)
    return labels

def confidenceOfLabel1(ds, rl):
    conf_scores = []
    for transaction in ds:
        added = False
        for i, rule in enumerate(rl.rules):
            if set(rule).issubset(transaction):
                added = True
                conf_scores.append(rl.pointEstimates[i])
                break
        # Default rule, transaction is not captured by any other rule.
        if not added:
            conf_scores.append(rl.pointEstimates[-1])
    return conf_scores

def auc(ds, rl):
    return metrics.roc_auc_score(trueLabel1(ds, rl.label), confidenceOfLabel1(ds, rl))

def MCMC_conv():
    MCMC_iters = 2000
    burn_in = [170, 70]     # Burn in
    window = 250    # Window of runs
    eps = ['_',.9, .5, .1, .01]
    hyperparams = [[7.0, 1.0], [3.0, 1.0]]
    multipliers = [2.5,1]
    datasets = ["../Data/UCI_shroom_clean.txt", "../Data/kaggle_titanic_clean_train.txt"]
    fims = ["../Data/shroom_fim.txt", "../Data/titanic_fim.txt"]
    labels = ["edible", "Survived"]

    for i, ds in enumerate(datasets):
        all_scores = []
        all_true_scores = []
        for j, ep in enumerate(eps):
            true_start_scores = []
            rl = RuleList(fims[i], ds, labels[i])
            for b in range(burn_in[i]):
                if ep == '_':
                    rl, _ = mcmc_mh(rl, hyperparams[i][0], hyperparams[i][1])
                    true_start_scores.append(score(rl, hyperparams[i][0], hyperparams[i][1]))
                else:
                    rl, _ = mcmc_mh(rl, hyperparams[i][0], hyperparams[i][1], ep, True)
                    true_start_scores.append(dp_score(rl, hyperparams[i][0], hyperparams[i][1], ep))

            trial_scores = []
            avg_lg_score_prev = -len(rl.dataset)   # Will make this run at least twice
            avg_lg_score = 0
            # Run until "close enough".
            # NOPE: For now, to graph, we need them all to run the same amount.
            # while fabs(avg_lg_score_prev - avg_lg_score) > (.05 * len_ds):
            for _ in range(int(MCMC_iters/window*multipliers[i])):
                avg_lg_score_prev = avg_lg_score
                avg_lg_score = 0
                for _ in range(window):
                    if j == 0:
                        rl, _ = mcmc_mh(rl, hyperparams[i][0], hyperparams[i][1])
                        true_curr_score = score(rl, hyperparams[i][0], hyperparams[i][1])
                        curr_score = true_curr_score
                    else:
                        rl, _ = mcmc_mh(rl, hyperparams[i][0], hyperparams[i][1], ep, True)
                        true_curr_score = dp_score(rl, hyperparams[i][0], hyperparams[i][1], ep)
                        curr_score = score(rl, hyperparams[i][0], hyperparams[i][1])
                    avg_lg_score += curr_score
                    # Accumulate all log scores for a specific run through
                    trial_scores.append(curr_score)
                    true_start_scores.append(true_curr_score)
                avg_lg_score /= window

            if math.fabs(avg_lg_score_prev - avg_lg_score) < (.05 * len(rl.dataset)):
                print("CONVERGENCE FOR ep:" + str(ep))
            else:
                print("!NO! CONVERGENCE FOR ep:" + str(ep))
            all_scores.append(trial_scores)
            all_true_scores.append(true_start_scores)
        MCMC_plot(all_scores, eps, burn_in[i], labels[i])
        # Graph plots using the corresponding scoring function (DP or Regular)
        MCMC_plot(all_true_scores, eps, 0, "true_scores_"+labels[i])


# ------------ FOR EXPERIMENTS ------------
def avgRuns(rl_labels, epsilons):
    datasets = ["../Data/UCI_adult_clean.txt", "../Data/UCI_shroom_clean.txt", "../Data/kaggle_titanic_clean_train.txt"]
    hyperparams = [[13.0,1.0], [7.0, 1.0], [3.0, 1.0]]
    reserve_ds = [readData("../Data/UCI_adult_res.txt"), readData("../Data/UCI_shroom_res.txt"), readData("../Data/kaggle_titanic_clean_res.txt")]
    fims = ["../Data/adult_fim.txt", "../Data/shroom_fim.txt", "../Data/titanic_fim.txt"]
    labels = [">50k", "edible", "Survived"]

    for j, ds in enumerate(datasets):
        if j != 1:
            continue
        print(ds)
        for i in range(len(rl_labels)):
            print("\t" + rl_labels[i])
            scores_in_sample = []
            scores_out_sample = []
            pos_score = []
            dp_pos_score = []
            pos_out = []
            dp_pos_out = []
            times = []
            lams = []
            etas = []
            for _ in range(ACC_REPS):
                start = time.time()
                if i == 0:
                    rl = run(fims[j], ds, labels[j], hyperparams[j][0], hyperparams[j][1], MCMC_REPS)
                    end = time.time()
                    pos_score.append(score(rl, hyperparams[j][0], hyperparams[j][1]))

                    # Change the DS to make use of the scoring function on the RL, then change it back.
                    tempDS = rl.dataset
                    rl.dataset = reserve_ds
                    pos_out.append(score(rl, hyperparams[j][0], hyperparams[j][1]))
                    rl.dataset = tempDS
                else:
                    rl = runDP(fims[j], ds, labels[j], hyperparams[j][0], hyperparams[j][1], epsilons[i], MCMC_REPS)
                    end = time.time()
                    pos_score.append(score(rl, hyperparams[j][0], hyperparams[j][1]))
                    dp_pos_score.append(dp_score(rl, hyperparams[j][0], hyperparams[j][1], epsilons[i]))

                    # Change the DS to make use of the scoring function on the RL, then change it back.
                    tempDS = rl.dataset
                    rl.dataset = reserve_ds
                    pos_out.append(score(rl, hyperparams[j][0], hyperparams[j][1]))
                    dp_pos_out.append(dp_score(rl, hyperparams[j][0], hyperparams[j][1], epsilons[i]))
                    rl.dataset = tempDS

                times.append(end-start)
                scores_in_sample.append(auc(rl.dataset, rl))
                scores_out_sample.append(auc(reserve_ds[j], rl))
                lams.append(len(rl.rules))
                etas.append(avgAntecedentLen(rl))
            print("\t\t AUC in -- SD: " + str(np.std(scores_in_sample)) + ", MEAN: " + str(np.mean(scores_in_sample)))
            print("\t\t AUC out -- SD: " + str(np.std(scores_out_sample)) + ", MEAN: " + str(np.mean(scores_out_sample)))
            print("\t\t LOG Pos IN -- SD: " + str(np.std(pos_score)) + ", MEAN: " + str(np.mean(pos_score)))
            print("\t\t LOG Pos OUT -- SD: " + str(np.std(pos_out)) + ", MEAN: " + str(np.mean(pos_out)))
            if i != 0:
                print("\t\t LOG DP Pos IN -- SD: " + str(np.std(dp_pos_score)) + ", MEAN: " + str(np.mean(dp_pos_score)))
                print("\t\t LOG DP Pos OUT -- SD: " + str(np.std(dp_pos_out)) + ", MEAN: " + str(np.mean(dp_pos_out)))
            print("\t\t HYPER -- LAM: " + str(hyperparams[j][0]) + " GOT " + str(np.mean(lams)) + " -- ETA: " + str(hyperparams[j][1]) + " GOT " + str(np.mean(etas)))
            print("\t\t AVG TIME: " + str(np.mean(times)))


def main():
    rl_labels = ["Regular RL", "DP ep:.9", "DP ep:.5", "DP ep:.1", "DP ep:.01"]
    eps = ['_',.9, .5, .1, .01]

    # Test: Run all rule lists on all dataset and compare lengths to hyperparameters, and auROC.
    avgRuns(rl_labels, eps)

main()
# MCMC_conv()
