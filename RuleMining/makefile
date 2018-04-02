CXX=g++-7
CXXFLAGS=-g -std=c++11

SRC=$(wildcard *.cc)
OBJ=$(SRC:%.cc=%.o)

run: $(OBJ)
	$(CXX) $(CXXFLAGS) -o apriori $^

test: $(OBJ)
	$(CXX) $(CXXFLAGS) -o apriori_test $^

%.o: %.c
	$(CXX) $(CXXFLAGS) $@ -c $<

clean:
	rm -f *.o
	rm apriori_test
	rm apriori
