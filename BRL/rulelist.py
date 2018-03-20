import numpy as np

class RuleList:
    # TODO(iamabel): Remove antecedents and make it work with only unused and rules.
    '''
    Should contain an antecedent list and capture vector per rule.
    Instance Variables:
        label:
        dataset: List of lists corresponding to the data entries (includes label).
        rules: subset of antecedents, representing true rule list. Starts random.
        antecedents: Lists of lists corresponding to premined antecedents for rules.
        unused: List of lists of unused antecedents.
        captures: List of lists of counts captured per label for a specific rule. An entry is
                  captured by the first rule in which antecedents are a subset of the data entry.
    '''
    # # TODO(iamabel): how do we want to start this? Random size and then random antecedents?
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

    # Run through dataset, find corresponding rule and update corresponding capture vector.
    # Updates self.captures
    def run_data(self):
        self.captures = np.zeros(len(self.rules), 2)
        for transaction in self.dataset:
            for i, rule in enumerate(self.rules):
                if rule in transaction:
                    self.captures[i][label in transaction] += 1
                    break

    # Swap rules in positions i and j, updating corresponding capture vectors.
    # Naive: just runData again.
    def swap(self, i, j):
        self.rules[i], self.rules[j] = self.rules[j], self.rules[i]

        self.runData()

    # Delete rule i, updating corresponding capture vectors. Naive: just runData again.
    def delete(self, i):
        np.insert(self.unused, self.rules[i])
        self.rules = np.delete(self.rules, i)

        self.runData()

    # Add the antecedent to position i, updating corresponding capture vectors.
    # Naive: just runData again.
    def add(self, antecedent, i, unused_i):
        self.unused = np.delete(self.unused, unused_i)
        np.insert(self.rules, antecedent, i)

        self.runData()

    def __init__(self, dataset=[], label=""):
        self.label = label

        self.dataset = dataset
        # TODO(iamabel): integrate antecedent miner, want frequent itemsets without label.
        # self.antecedents = mined_antecedents(dataset, label)
        self.antecedents = []

        self.rules = []
        self.unused = []
        self.captures = []
