using namespace std;

namespace {
  vector<unordered_set<string>> getFrequent(int num_transactions, unordered_map<unordered_set<string>, int> set_counts,
                                    float minsup) {
    vector<unordered_set<string>> frequent_items;
    for (unordered_set<string> item, int count: set_counts) {
      if (count > minsup*num_transactions) {
        frequent_items.push_back(item);
      }
    }
    return frequent_items;
  }

  unordered_set<string> larger_frequent_itemsets(unordered_set<string> frequent_items,
                                                 vector<string> transactions, float minsup) {
    unordered_map<string, int> counts;

    return getFrequent(transactions.size(), counts, minsup);
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
              trials = atoi(argv[++i]);
          } else { // Trial flag called but unspecified
                cerr << "--file option requires one argument." << endl;
              return 1;
          }
      } else if (string(argv[i]) == "--minsup") {
        if (i + 1 < argc) {
            filename = argv[++i];
        } else { // Graph flag called but unspecified
              cerr << "--minsup option requires one argument." << endl;
            return 1;
        }
      } else if (string(argv[i]) == "--minconf") {
        if (i + 1 < argc) {
            filename = argv[++i];
        } else { // Graph flag called but unspecified
              cerr << "--minconf option requires one argument." << endl;
            return 1;
        }
      }
  }

  // Items, counts, 'transactions'.
  unordered_map<unordered_set<string>, int> oneset_counts;
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
    while (getLine(in, transaction)) {
      int start = 0, end = transaction.find(delim);
      unordered_set<string> items_curr;

      while (end != string::npos) {
        // Note if element exists, this increments, if it does not it is init
        // to 0 then incremented to 1.
        string item = transaction.substr(start, end - start);
        // Ensure uniqueness per transaction
        // Sets maintain uniquesness, however we want to count elements as well, this allows us to
        // limit iterations (we won't have to iterate through the set after).
        if (items_curr.find(item) == items_curr.end()) {
          oneset_counts[unordered_set<string>(item)]++;
          items_curr.push_back(item);
        }

        start = end + 1;
        end = transaction.find(delim, start);
      }

      item = transaction.substr(start);
      if (items_curr.find(item) == items_curr.end()) {
        oneset_counts[unordered_set<string>(item)]++;
        items_curr.push_back(item);
      }

      transactions.push_back(items_curr);
    }
    fclose(in);
  }

  vector<unordered_set<string>> frequent_items = getFrequent(transactions.size(), oneset_counts, minsup);
  return 0;
}
