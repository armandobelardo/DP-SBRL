#include <algorithm>
#include <fstream>
#include <iterator>
#include <iostream>
#include <set>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

namespace {
  // Join set with spaces.
  string sjoin(const set<string> &s) {
    stringstream ss;
    int i = 0;
    for(string str : s) {
      if(i != 0) {
        ss << " ";
      }
      ss << str;
      i++;
    }
    return ss.str();
  }

  // Join vector with spaces.
  string vjoin(const vector<string> &v) {
    stringstream ss;
    for(int i = 0; i < v.size(); ++i) {
      if(i != 0) {
        ss << " ";
      }
      ss << v[i];
    }
    return ss.str();
  }

  // Split string on spaces.
  vector<string> split(string str) {
    stringstream ss(str);
    istream_iterator<string> begin(ss);
    istream_iterator<string> end;
    vector<string> str_v(begin, end);

    return str_v;
  }

  unordered_map<string, vector<int>> getFrequent(int num_transactions, float minsup,
                                                 unordered_map<string, vector<int>> &set_supports) {
    unordered_map<string, vector<int>> frequent_items;
    for (auto item_count: set_supports) {
      if (item_count.second.size() >= minsup*num_transactions) {
        frequent_items[item_count.first] = vector<int>(item_count.second.begin(), item_count.second.end());
      }
    }
    return frequent_items;
  }

  unordered_map<string, vector<int>> getLargerItemsets(const unordered_map<string, vector<int>>
                                                       &frequent_items) {

  }

  unordered_map<string, vector<int>> largerFrequentItemsets(const unordered_map<string, vector<int>>
                                                            &frequent_items,
                                                            const vector<unordered_set<string>>
                                                            &transactions,
                                                            float minsup,
                                                            vector<string> *maximal_items) {
    vector<vector<string>> frequent_sets;
    vector<vector<int>> frequent_supp;
    for (auto itemset_support : frequent_items) {
      frequent_sets.push_back(split(itemset_support.first));
      frequent_supp.push_back(itemset_support.second);
    }
    vector<bool> maximal(frequent_sets.size(), true);
    int k = frequent_sets[0].size();

    unordered_map<string, vector<int>> true_larger_sets;
    for (int i = 0; i < frequent_sets.size(); ++i) {      // Get all set unions.
      for (int j = i+1; j < frequent_sets.size(); ++j) {
        set<string> itemset(frequent_sets[i].begin(), frequent_sets[i].end());
        vector<int>::iterator it;
        for (int z = 0; z < k; ++z) {
          itemset.insert(frequent_sets[j][z]);
        }

        // Note the support of a joined set is the intersection of their supports
        if (itemset.size() == k+1) {
          vector<int> support(frequent_supp[i].size() + frequent_supp[j].size());
          sort(frequent_supp[i].begin(), frequent_supp[i].end());
          sort(frequent_supp[j].begin(), frequent_supp[j].end());
          it = set_intersection(frequent_supp[i].begin(), frequent_supp[i].end(),
                                frequent_supp[j].begin(), frequent_supp[j].end(),
                                support.begin());
          support.resize(it-support.begin());

          if (support.size() >= minsup*transactions.size()) {
            true_larger_sets[sjoin(itemset)] = support;
            maximal[i] = false;
            maximal[j] = false;
          }
        }
      }
    }

    for (int i = 0; i < maximal.size(); ++i) {
      if (maximal[i]) {
        maximal_items->push_back(vjoin(frequent_sets[i]));
      }
    }

    return true_larger_sets;
  }


} //  end namespace

int main(int argc, char** argv) {
  // (confidence pruning)
  char *filename = (char *)"../Testing/dat1.txt";
  float minsup = 0.375f;
  float minconf = 0.5f;
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
  unordered_map<string, vector<int>> oneset_supports;
  vector<unordered_set<string>> transactions;
  // Need a standardized delimiter that distinguishes 'items'.
  string delim = " ";
  {
    ifstream in(filename);

    if (!in.good()) {
        fprintf(stderr, "Can't open transactions file\n");
        return -1;
    }

    string transaction;
    int line = 1;
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
          oneset_supports[item].push_back(line);
          items_curr.insert(item);
        }

        start = end + 1;
        end = transaction.find(delim, start);
      }

      item = transaction.substr(start);
      if (items_curr.find(item) == items_curr.end()) {
        oneset_supports[item].push_back(line);
        items_curr.insert(item);
      }

      transactions.push_back(items_curr);
      line++;
    }
    in.close();
  }
  vector<string> maximal_items;

  unordered_map<string, vector<int>> frequent_onesets = getFrequent(transactions.size(), minsup, oneset_supports);
  unordered_map<string, vector<int>> next_sets = largerFrequentItemsets(frequent_onesets, transactions,
                                                                        minsup, &maximal_items);
  unordered_map<string, vector<int>> frequent_itemsets(frequent_onesets.begin(), frequent_onesets.end());

  while (next_sets.size() > 1) {
    frequent_itemsets.insert(next_sets.begin(), next_sets.end());
    next_sets = largerFrequentItemsets(next_sets, transactions, minsup, &maximal_items);
  }
  frequent_itemsets.insert(next_sets.begin(), next_sets.end());

  printf("-------------Frequent Itemsets------------\n");
  for (auto itemset_support : frequent_itemsets) {
    printf("%s\n", itemset_support.first.c_str());
  }
  printf("---------Maximal Frequent Itemsets--------\n");
  for (string itemset : maximal_items) {
    printf("%s\n", itemset.c_str());
  }

  return 0;
}
