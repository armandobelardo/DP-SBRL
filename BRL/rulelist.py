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

        return d_c

    def printNeat(self):
        for i in range(len(self.rules)):
            probability = 0.0 if sum(self.captures[i]) == 0 else float(self.captures[i][1])/sum(self.captures[i])
            print("if " + ' '.join(self.rules[i]) + " then probability of " + self.label + " = " + str(probability))

    # Run through dataset, find corresponding rule and update corresponding capture vector.
    # Updates self.captures
    def run_data(self):
        self.captures = np.zeros((len(self.rules), 2)).tolist()
        for transaction in self.dataset:
            for i, rule in enumerate(self.rules):
                if set(rule).issubset(transaction):
                    self.captures[i][self.label in transaction] += 1
                    break

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

    def __init__(self, antecedents="../Data/fim_1.txt", dataset="../Data/dat2_test.txt", label="diapers"):
        self.label = label

        self.dataset = readData(dataset)
        self.antecedents = readFIM(antecedents)

        self.rules = self.antecedents[:]
        self.unused = []
        self.captures = []
        self.run_data()
