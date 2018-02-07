#include <fstream>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

namespace {
  string sjoin(unordered_set<string> s) {
    stringstream ss;
    for(int i = 0; i < s.size(); ++i) {
      if(i != 0) {
        ss << " ";
      }
      ss << s[i];
    }
    return ss.str();
  }

  string vjoin(vector<string> v) {
    stringstream ss;
    for(int i = 0; i < v.size(); ++i) {
      if(i != 0) {
        ss << " ";
      }
      ss << v[i];
    }
    return ss.str();
  }

  // Split string on spaces
  vector<string> split(string str) {
    stringstream ss(str);
    istream_iterator<string> begin(ss);
    istream_iterator<string> end;
    vector<string> str_v(begin, end);

    return str_v;
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
    // Turn string itemsets into their sets.
    unordered_set<vector<string>> frequent_sets;
    for (string itemset : frequent_items) {
      frequent_sets.insert(split(itemset));
    }
    int k = frequent_sets[0].size();

    unordered_set<unordered_set<string>> larger_sets;
    for (int i = 0; i < frequent_sets.size(); ++i) {      // Get all set unions.
      for (int j = i+1; j < frequent_sets.size(); ++j) {
        unordered_set<string> itemset(frequent_sets[i]);
        for (int z = 0; z < k; ++z) {
          itemset.insert(frequent_sets[j][z]);
        }
        larger_sets.insert(itemset);
      }
    }

    unordered_set<string> true_larger_sets;
    for (unordered_set<string> larger_set: larger_sets) {
      if (larger_set.size() == k+1) {
        true_larger_sets.insert(sjoin(larger_set));
      }
    }

    return true_larger_sets;
  }

  unordered_set<string> largerFrequentItemsets(unordered_set<string> frequent_items,
                                               vector<unordered_set<string>> transactions,
                                               float minsup) {
    unordered_map<string, int> counts;
    unordered_set<string> potential_freq = getLargerItemsets(frequent_items);

    // Count occurences of potential frequent itemsets, size k+1.
    unordered_set<vector<string>> potential_freq_s;
    for (string itemset : potential_freq) {
      potential_freq_s.insert(split(itemset));
    }
    int k = potential_freq[0].size();

    bool subset = true;
    for (int i = 0; i < potential_freq.size(); ++i) {      // FIX: FOR EACH LOOP OVER MAP
      for (int j = 0; j < transactions.size(); ++j) {
        for (int z = 0; z < k; ++z) {
          if (transactions[j].find(first) == transactions[j].end()) {
            subset = false;
          }
        }
        if (subset) counts[potential_freq[i]]++;
        subset = true;
      }
    }

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
