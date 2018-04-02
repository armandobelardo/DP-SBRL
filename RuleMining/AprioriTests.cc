#include "Apriori.cc"

using namespace std;

bool getFrequentTest() {
  unordered_map<string, vector<int>> start = {{"hey there",{1,2,3,4}}, {"i am not frequent",{1}},
                                              {"i am frequent though",{1,2,3,4,5}}};
  unordered_map<string, vector<int>> ex_freq = {{"hey there",{1,2,3,4}}, {"i am frequent though",{1,2,3,4,5}}};

  unordered_map<string, vector<int>> end_freq = getFrequent(10, .4, start);

  return ex_freq == end_freq;
}

bool getLargerFreqItemsetsTest() {
  vector<unordered_set<string>> transactions = {{"hey", "there", "this"}, {"is", "hey", "there"},
                                                {"hey", "there", "this", "is"}, {"hey", "there", "is", "great"},
                                                {"there", "is", "this"}};
  vector<string> dontcare;

  unordered_map<string, vector<int>> frequent_onesets = {{"hey",{0,1,2,3}}, {"there",{0,1,2,3,4}},
                                                         {"this",{0,2,4}}, {"is",{1,2,3,4}}};
  unordered_map<string, vector<int>> ex_frequent_twosets =  {{"hey there",{0,1,2,3}}, {"hey is",{1,2,3}},
                                                             {"there this",{0,2,4}}, {"is there",{1,2,3,4}}};
  unordered_map<string, vector<int>> ex_frequent_threesets = {{"hey is there",{1,2,3}}};

  unordered_map<string, vector<int>> frequent_twosets = getLargerFreqItemsets(frequent_onesets,
                                                                  transactions, 3.0/5.0, &dontcare);
  if (ex_frequent_twosets != frequent_twosets)
    return false;

  unordered_map<string, vector<int>> frequent_threesets = getLargerFreqItemsets(frequent_twosets,
                                                                  transactions, 3.0/5.0, &dontcare);
  return ex_frequent_threesets == frequent_threesets;
}

int main() {
  printf("getFrequentTest output: %s\n", getFrequentTest()? "True": "False");
  printf("getLargerFreqItemsetsTest output: %s\n", getLargerFreqItemsetsTest()? "True": "False");
  return 0;
}
