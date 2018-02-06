using namespace std;

namespace {

} //  end namespace

int main(int argc, char** argv) {
  // expect filename, and support and confidence thresholds passed in
  // parse file, each line is a new 'transaction'
  // can count support of each item (need a standardized delimter)
  // continue getting frequent itemsets until no more larger (support pruning)
  // (confidence pruning)
  string delim = " ";
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

  // items, counts, 'transactions'
  unordered_map<string, int> oneset_count;
  vector<string> transactions;
  {
    ifstream in(filename);

    if (in.good()) {
        fprintf(stderr, "Can't open transactions file\n");
        return -1;
    }

    string transaction;
    while (getLine(in, transaction)) {
      transactions.push_back(transaction);
      int start = 0, end = transaction.find(delim);
      unordered_set<string> items_curr;

      while (end != string::npos) { // each individual word
        // Note if element exists, this increments, if it does not it is init
        // to 0 then incremented to 1.
        string item = transaction.substr(start, end - start);
        // Ensure uniqueness per transaction
        if (items_curr.find(item) == items_curr.end()) {
          oneset_count[item]++;
          start = end + 1;
          end = transaction.find(delim, start);

          items_curr.push_back(item);
        }
      }
      if (items_curr.find(item) == items_curr.end()) {
        oneset_count[push_back(transaction.substr(start, end - start))]++;
      }
    }
    fclose(in);
  }

  unordered_set<string> frequent_items;
  for (string item, int count: oneset_count) {
    if (count > minsup*transactions) {
      frequent_items.push_back(item);
    }
  }
  return 0;
}
