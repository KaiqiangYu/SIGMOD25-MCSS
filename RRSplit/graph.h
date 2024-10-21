#include <limits.h>
#include <stdbool.h>

#include <vector>

using ui = unsigned int;
//using std::cout; using std::endl; using std::vector;

struct Graph {
    int n;
    std::vector<std::vector<unsigned int>> adjmat;
    std::vector<unsigned int> label;
    unsigned int *degree;
    unsigned int **adjlist;
    Graph(unsigned int n);
};

Graph induced_subgraph(struct Graph& g, std::vector<int> vv);

Graph readGraph(char* filename, char format, bool directed, bool edge_labelled, bool vertex_labelled);

void set_adjlist(struct Graph & g);

void GetEqClass(Graph & g, ui *&EqClass);

