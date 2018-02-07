#include <fstream>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

namespace {
  vector<string> split(string str) {

  }

  unordered_set<string> getFrequent(int num_transactions, float minsup,
                                    unordered_map<string, int> set_counts) {
    unordered_set<string> frequent_items;
    for (const auto& item_count: set_counts) {
      if (item_count.second > minsup*num_transactions) {
        frequent_items.insert(item_count.first);
      }
    }
    return frequent_items;
  }

  unordered_set<string> getLargerItemsets(unordered_set<string> frequent_items) {
    // vector set union

    return unordered_set<string>();
  }

  unordered_set<string> largerFrequentItemsets(unordered_set<string> frequent_items,
                                               vector<unordered_set<string>> transactions,
                                               float minsup) {
    unordered_map<string, int> counts;
    unordered_set<string> potential_freq = getLargerItemsets(frequent_items);

    // count occurences

    return getFrequent(transactions.size(), minsup, counts);
  }
} //  end namespace

int main(int argc, char** argv) {
  // continue getting frequent itemsets until no more larger (support pruning)
  // (confidence pruning)
  char *filename = (char *)"Testing/dat1.txt";
  float minsup = 0.75f;
  float minconf = 0.8f;
  for (int i = 1; i < argc; ++i) {
      if (string(argv[i]) == "--file") {
          if (i + 1 < argc) {
              filename = argv[++i];
          } else { // Trial flag called but unspecified
                cerr << "--file option requires one argument." << endl;
              return 1;
          }
      } else if (string(argv[i]) == "--minsup") {
        if (i + 1 < argc) {
            minsup = atof(argv[++i]);
        } else { // Graph flag called but unspecified
              cerr << "--minsup option requires one argument." << endl;
            return 1;
        }
      } else if (string(argv[i]) == "--minconf") {
        if (i + 1 < argc) {
            minconf = atof(argv[++i]);
        } else { // Graph flag called but unspecified
              cerr << "--minconf option requires one argument." << endl;
            return 1;
        }
      }
  }

  // Items, counts, 'transactions'.
  unordered_map<string, int> oneset_counts;
  vector<unordered_set<string>> transactions;
  // Need a standardized delimiter that distinguishes 'items'.
  string delim = " ";
  {
    ifstream in(filename);

    if (in.good()) {
        fprintf(stderr, "Can't open transactions file\n");
        return -1;
    }

    string transaction;
    while (getline(in, transaction)) {
      int start = 0, end = transaction.find(delim);
      unordered_set<string> items_curr;
      string item;

      while (end != string::npos) {
        // Note if element exists, this increments, if it does not it is init
        // to 0 then incremented to 1.
        item = transaction.substr(start, end - start);
        // Ensure uniqueness per transaction
        // Sets maintain uniquesness, however we want to count elements as well, this allows us to
        // limit iterations (we won't have to iterate through the set after).
        if (items_curr.find(item) == items_curr.end()) {
          oneset_counts[item]++;
          items_curr.insert(item);
        }

        start = end + 1;
        end = transaction.find(delim, start);
      }

      item = transaction.substr(start);
      if (items_curr.find(item) == items_curr.end()) {
        oneset_counts[item]++;
        items_curr.insert(item);
      }

      transactions.push_back(items_curr);
    }
    in.close();
  }

  unordered_set<string> frequent_items = getFrequent(transactions.size(), minsup, oneset_counts);
  return 0;
}
