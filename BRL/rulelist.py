import numpy as np
from data import *


class RuleList:
    # TODO(iamabel): Remove antecedents and make it work with only unused and rules.
    '''
    Should contain an antecedent list and capture vector per rule.
    Instance Variables:
        label: The 'then' condition of the rules. The goal outcome.
        dataset: List of lists corresponding to the data entries (includes label).
        rules: subset of antecedents, representing true rule list. Starts random.
        antecedents: Lists of lists corresponding to premined antecedents for rules.
        unused: List of lists of unused antecedents.
        captures: List of lists of counts captured per label for a specific rule. An entry is
                  captured by the first rule in which antecedents are a subset of the data entry.
        pointEstimates: ...
    '''
    # TODO(iamabel): how do we want to start this? Random size and then random antecedents?
    # def random_rule_list(self):
    #     # Would set unused if it weren't all antecedents.
    #     return self.antecedents

    # TODO(iamabel): There's probably a better way to do this.
    def copy(self):
        d_c = RuleList()

        d_c.label = self.label
        d_c.dataset = self.dataset
        d_c.antecedents = self.antecedents

        d_c.rules = self.rules[:]
        d_c.unused = self.unused[:]
        d_c.captures = self.captures[:]

        d_c.pointEstimates = self.pointEstimates[:]

        return d_c

    def calcPointEstimates(self, alpha=[1,1]):
        estimates = self.pointEstimates
        for capture in self.captures:
            # Note there is no worry of dividing by 0, given a nonzero alpha
            estimates.append((capture[1] + alpha[1])/(sum(capture)+sum(alpha)))

    # NEED TO CALL calcPointEstimates BEFORE.
    def printNeat(self):
        for i in range(len(self.rules)):
            print("if " + ' '.join(self.rules[i]) + " then probability of " + self.label + " = " + str(self.pointEstimates[i]))
        # Default Rule.
        print("if (default rule) then probability of "+ self.label + " = " + str(self.pointEstimates[-1]))

    def strNeat(self):
        str_rl = ""
        for i in range(len(self.rules)):
            str_rl += "if " + ' '.join(self.rules[i]) + " then probability of " + self.label + " = " + str(self.pointEstimates[i])
        # Default Rule.
        str_rl += "if (default rule) then probability of "+ self.label + " = " + str(self.pointEstimates[-1])

        return str_rl

    # Run through dataset, find corresponding rule and update corresponding capture vector.
    # Updates self.captures.
    def run_data(self):
        self.captures = np.zeros((len(self.rules)+1, 2)).tolist()
        for transaction in self.dataset:
            added = False
            for i, rule in enumerate(self.rules):
                if set(rule).issubset(transaction):
                    added = True
                    self.captures[i][self.label in transaction] += 1
                    break
            # Default Rule, note that we will have the rule list be one shorter, given we have
            # no need to represent the default rule and we should not move or delete it.
            if not added:
                self.captures[-1][self.label in transaction] += 1

    # Swap rules in positions i and j, updating corresponding capture vectors.
    # Naive: just run_data again.
    def swap(self, i, j):
        self.rules[i], self.rules[j] = self.rules[j], self.rules[i]

        self.run_data()

    # Delete rule i, updating corresponding capture vectors. Naive: just run_data again.
    def delete(self, i):
        self.unused.append(self.rules[i])
        del self.rules[i]

        self.run_data()

    # Add the antecedent (at unused_i) to position i, updating corresponding capture vectors.
    # Naive: just run_data again.
    def add(self, i, unused_i):
        self.rules.insert(i, self.unused[unused_i])
        del self.unused[unused_i]

        self.run_data()

    # Add Laplace noise with a scale of epsilon. Note that according to Dwork, for privacy, we must
    # scale with m/epsilon for m queries.
    def noisifyCaptures(self, epsilon):
        for capture in self.captures:
            for i in range(len(capture)):
                capture[i] = max(0.0, capture[i]+np.random.laplace(0,1.0/epsilon))


    def __init__(self, antecedents="../Data/fim_1.txt", dataset="../Data/dat2_test.txt", label="diapers"):
        self.label = label

        self.dataset = readData(dataset)
        self.antecedents = readFIM(antecedents, label)

        self.rules = [self.antecedents[0]]
        self.unused = self.antecedents[1:]
        self.captures = []
        self.pointEstimates = []
        self.run_data()
