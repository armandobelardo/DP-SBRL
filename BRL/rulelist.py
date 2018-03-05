import numpy as np

class RuleList:
    '''
    Should contain an antecedent list and capture vector per rule.
    Instance Variables:
        dataset: List of lists corresponding to the data entries.
        rules: subset of antecedents, representing true rule list. Starts random.
        antecedents: Lists of lists corresponding to premined antecedents for rules.
        captures: List of lists of counts captured per label for a specific rule. An entry is
                  captured by the first rule in which antecedents are a subset of the data entry.
    '''

    # Run through dataset, find corresponding rule and update corresponding capture vector.
    # Updates self.captures
    def runData(self):

    # Swap rules in positions i and j, updating corresponding capture vectors.
    # Naive: just runData again.
    def swap(self, i, j):
        self.rules[i], self.rules[j] = self.rules[j], self.rules[i]

        self.runData()

    # Delete rule i, updating corresponding capture vectors. Naive: just runData again.
    def delete(self, i):
        np.delete(self.rules, i)

        self.runData()

    # Add the antecedent to position i, updating corresponding capture vectors.
    # Naive: just runData again.
    def add(self, antecedent, i):
        np.insert(self.rules, antecedent, i)

        self.runData()

    def __init__(self, dataset):
        self.dataset = dataset
        self.antecedents = minedAntecedents(dataset)
        self.rules = random_rule_list(self.antecedents)
        self.captures = [[]]
