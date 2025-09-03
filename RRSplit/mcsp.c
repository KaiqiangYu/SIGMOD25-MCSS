#include "graph.h"

#include <algorithm>
#include <numeric>
#include <chrono>
#include <iostream>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <mutex>
#include <thread>
#include <condition_variable>
#include <atomic>

#include <argp.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

using std::vector;
using std::cout;
using std::endl;

static void fail(std::string msg) {
    std::cerr << msg << std::endl;
    exit(1);
}

vector<int> degInC1;
vector<int> degInC2;
ui *EqClass;
vector<int> index_right;

enum Heuristic { min_max, min_product };

/*******************************************************************************
                             Command-line arguments
*******************************************************************************/

static char doc[] = "Find a maximum clique in a graph in DIMACS format\vHEURISTIC can be min_max or min_product";
static char args_doc[] = "HEURISTIC FILENAME1 FILENAME2";
static struct argp_option options[] = {
    {"quiet", 'q', 0, 0, "Quiet output"},
    {"verbose", 'v', 0, 0, "Verbose output"},
    {"dimacs", 'd', 0, 0, "Read DIMACS format"},
    {"lad", 'l', 0, 0, "Read LAD format"},
    {"connected", 'c', 0, 0, "Solve max common CONNECTED subgraph problem"},
    {"directed", 'i', 0, 0, "Use directed graphs"},
    {"labelled", 'a', 0, 0, "Use edge and vertex labels"},
    {"vertex-labelled-only", 'x', 0, 0, "Use vertex labels, but not edge labels"},
    {"big-first", 'b', 0, 0, "First try to find an induced subgraph isomorphism, then decrement the target size"},
    {"timeout", 't', "timeout", 0, "Specify a timeout (seconds)"},
    { 0 }
};

static struct {
    bool quiet;
    bool verbose;
    bool dimacs;
    bool lad;
    bool connected;
    bool directed;
    bool edge_labelled;
    bool vertex_labelled;
    bool big_first;
    Heuristic heuristic;
    char *filename1;
    char *filename2;
    int timeout;
    int arg_num;
} arguments;

static std::atomic<bool> abort_due_to_timeout;

void set_default_arguments() {
    arguments.quiet = false;
    arguments.verbose = false;
    arguments.dimacs = false;
    arguments.lad = false;
    arguments.connected = false;
    arguments.directed = false;
    arguments.edge_labelled = false;
    arguments.vertex_labelled = false;
    arguments.big_first = false;
    arguments.filename1 = NULL;
    arguments.filename2 = NULL;
    arguments.timeout = 0;
    arguments.arg_num = 0;
}

static error_t parse_opt (int key, char *arg, struct argp_state *state) {
    switch (key) {
        case 'd':
            if (arguments.lad)
                fail("The -d and -l options cannot be used together.\n");
            arguments.dimacs = true;
            break;
        case 'l':
            if (arguments.dimacs)
                fail("The -d and -l options cannot be used together.\n");
            arguments.lad = true;
            break;
        case 'q':
            arguments.quiet = true;
            break;
        case 'v':
            arguments.verbose = true;
            break;
        case 'c':
            if (arguments.directed)
                fail("The connected and directed options can't be used together.");
            arguments.connected = true;
            break;
        case 'i':
            if (arguments.connected)
                fail("The connected and directed options can't be used together.");
            arguments.directed = true;
            break;
        case 'a':
            if (arguments.vertex_labelled)
                fail("The -a and -x options can't be used together.");
            arguments.edge_labelled = true;
            arguments.vertex_labelled = true;
            break;
        case 'x':
            if (arguments.edge_labelled)
                fail("The -a and -x options can't be used together.");
            arguments.vertex_labelled = true;
            break;
        case 'b':
            arguments.big_first = true;
            break;
        case 't':
            arguments.timeout = std::stoi(arg);
            break;
        case ARGP_KEY_ARG:
            if (arguments.arg_num == 0) {
                if (std::string(arg) == "min_max")
                    arguments.heuristic = min_max;
                else if (std::string(arg) == "min_product")
                    arguments.heuristic = min_product;
                else
                    fail("Unknown heuristic (try min_max or min_product)");
            } else if (arguments.arg_num == 1) {
                arguments.filename1 = arg;
            } else if (arguments.arg_num == 2) {
                arguments.filename2 = arg;
            } else {
                argp_usage(state);
            }
            arguments.arg_num++;
            break;
        case ARGP_KEY_END:
            if (arguments.arg_num == 0)
                argp_usage(state);
            break;
        default: return ARGP_ERR_UNKNOWN;
    }
    return 0;
}

static struct argp argp = { options, parse_opt, args_doc, doc };

/*******************************************************************************
                                     Stats
*******************************************************************************/

unsigned long long nodes{ 0 };

/*******************************************************************************
                                 MCS functions
*******************************************************************************/

struct VtxPair {
    int v;
    int w;
    VtxPair(int v, int w): v(v), w(w) {}
};

struct Bidomain {
    int l,        r;        // start indices of left and right sets
    int left_len, right_len;
    bool is_adjacent;
    Bidomain(int l, int r, int left_len, int right_len, bool is_adjacent):
            l(l),
            r(r),
            left_len (left_len),
            right_len (right_len),
            is_adjacent (is_adjacent) { };
};

void show(const vector<VtxPair>& current, const vector<Bidomain> &domains,
        const vector<int>& left, const vector<int>& right)
{
    cout << "Nodes: " << nodes << std::endl;
    cout << "Length of current assignment: " << current.size() << std::endl;
    cout << "Current assignment:";
    for (unsigned int i=0; i<current.size(); i++) {
        cout << "  (" << current[i].v << " -> " << current[i].w << ")";
    }
    cout << std::endl;
    for (unsigned int i=0; i<domains.size(); i++) {
        struct Bidomain bd = domains[i];
        cout << "Left  ";
        for (int j=0; j<bd.left_len; j++)
            cout << left[bd.l + j] << " ";
        cout << std::endl;
        cout << "Right  ";
        for (int j=0; j<bd.right_len; j++)
            cout << right[bd.r + j] << " ";
        cout << std::endl;
    }
    cout << "\n" << std::endl;
}

bool check_sol(const Graph & g0, const Graph & g1 , const vector<VtxPair> & solution) {
    //return true;
    vector<bool> used_left(g0.n, false);
    vector<bool> used_right(g1.n, false);
    for (unsigned int i=0; i<solution.size(); i++) {
        struct VtxPair p0 = solution[i];
        if (used_left[p0.v] || used_right[p0.w]){
            cout<<"Vertex repeated in the solution"<<endl;
            return false;
        }
        used_left[p0.v] = true;
        used_right[p0.w] = true;
        if (g0.label[p0.v] != g1.label[p0.w]){
            cout<<"Label mistaching"<<endl;
            return false;
        }
        for (unsigned int j=i+1; j<solution.size(); j++) {
            struct VtxPair p1 = solution[j];
            if (g0.adjmat[p0.v][p1.v] != g1.adjmat[p0.w][p1.w]){
                cout<<"Topological mistaching: "<<p0.v<<" ("<<g0.adjmat[p0.v][p1.v]<<") "<<p1.v<<" ***** "<<
                p0.w<<" ("<<g1.adjmat[p0.w][p1.w]<<") "<<p1.w<<endl;
                return false;
            }
                
        }
    }
    return true;
}

int calc_bound(const vector<Bidomain>& domains) {
    int bound = 0;
    for (const Bidomain &bd : domains) {
        bound += std::min(bd.left_len, bd.right_len);
    }
    return bound;
}

int find_min_value(const vector<int>& arr, int start_idx, int len) {
    int min_v = INT_MAX;
    for (int i=0; i<len; i++)
        if (arr[start_idx + i] < min_v)
            min_v = arr[start_idx + i];
    return min_v;
}

int select_bidomain(const vector<Bidomain>& domains, const vector<int> & left,
        int current_matching_size)
{
    // Select the bidomain with the smallest max(leftsize, rightsize), breaking
    // ties on the smallest vertex index in the left set
    int min_size = INT_MAX;
    int min_tie_breaker = INT_MAX;
    int best = -1;
    for (unsigned int i=0; i<domains.size(); i++) {
        const Bidomain &bd = domains[i];
        if (arguments.connected && current_matching_size>0 && !bd.is_adjacent) continue;
        int len = arguments.heuristic == min_max ?
                std::max(bd.left_len, bd.right_len) :
                bd.left_len * bd.right_len;
        if (len < min_size) {
            min_size = len;
            min_tie_breaker = find_min_value(left, bd.l, bd.left_len);
            best = i;
        } else if (len == min_size) {
            int tie_breaker = find_min_value(left, bd.l, bd.left_len);
            if (tie_breaker < min_tie_breaker) {
                min_tie_breaker = tie_breaker;
                best = i;
            }
        }
    }
    return best;
}

// Returns length of left half of array
int partition(vector<int>& all_vv, int start, int len, const vector<unsigned int> & adjrow) {
    int i=0;
    for (int j=0; j<len; j++) {
        if (adjrow[all_vv[start+j]]) {
            std::swap(all_vv[start+i], all_vv[start+j]);
            i++;
        }
    }
    return i;
}

int partition_right(vector<int>& all_vv, int start, int len, const vector<unsigned int> & adjrow) {
    int i=0;
    for (int j=0; j<len; j++) {
        if (adjrow[all_vv[start+j]]) {
            std::swap(index_right[all_vv[start+i]],index_right[all_vv[start+j]]);
            std::swap(all_vv[start+i], all_vv[start+j]);
            i++;
        }
    }
    return i;
}

int partition_sparse(vector<int>& all_vv, int start, int len, int degree, const ui * adjlist){
    int pos; int j=0;
    for(int i=0;i<degree;++i){
        pos=index_right[adjlist[i]];
        if(pos>=start && pos<start+len){
            std::swap(index_right[all_vv[start+j]],index_right[all_vv[pos]]);
            std::swap(all_vv[start+j], all_vv[pos]);
            j++; 
        }
    }
    return j;
}

auto test_time=0;

// multiway is for directed and/or labelled graphs
vector<Bidomain> filter_domains(const vector<Bidomain> & d, vector<int> & left,
        vector<int> & right, const Graph & g0, const Graph & g1, int v, int w, bool &best_match)
{
    
    vector<Bidomain> new_d;
    new_d.reserve(d.size());
    unsigned int ccount=0; 
    int l=-1,r=-1,left_len=-1,right_len=-1,left_len_noedge=-1,right_len_noedge=-1;
    for (const Bidomain &old_bd : d) {
        l = old_bd.l;
        r = old_bd.r;

        left_len = partition(left, l, old_bd.left_len, g0.adjmat[v]);
        // right_len = partition_right(right, r, old_bd.right_len, g1.adjmat[w]);
        if(old_bd.right_len>(int)g1.degree[w]) 
           right_len = partition_sparse(right, r, old_bd.right_len, g1.degree[w], g1.adjlist[w]);
        else right_len = partition_right(right, r, old_bd.right_len, g1.adjmat[w]);
        left_len_noedge = old_bd.left_len - left_len;
        right_len_noedge = old_bd.right_len - right_len;

        if((left_len==0&&right_len==0)||(left_len_noedge==0&&right_len_noedge==0)||old_bd.left_len==0){
            ccount++;
        }

        if (left_len_noedge && right_len_noedge)
            new_d.push_back({l+left_len, r+right_len, left_len_noedge, right_len_noedge, old_bd.is_adjacent});
        if (left_len && right_len) {
            new_d.push_back({l, r, left_len, right_len, true});
        }
    }
    best_match = (ccount==d.size())? true : false;
    return new_d;
}





// returns the index of the smallest value in arr that is >w.
// Assumption: such a value exists
// Assumption: arr contains no duplicates
// Assumption: arr has no values==INT_MAX
int index_of_next_smallest(const vector<int>& arr, int start_idx, int len, int w) {
    int idx = -1;
    int smallest = INT_MAX;
    for (int i=0; i<len; i++) {
        if (arr[start_idx + i]>w && arr[start_idx + i]<smallest) {
            smallest = arr[start_idx + i];
            idx = i;
        }
    }
    return idx;
}

void remove_vtx_from_left_domain(vector<int>& left, Bidomain& bd, int v)
{
    int i = 0;
    while(left[bd.l + i] != v) i++;
    std::swap(left[bd.l+i], left[bd.l+bd.left_len-1]);
    bd.left_len--;
}

void remove_bidomain(vector<Bidomain>& domains, int idx) {
    domains[idx] = domains[domains.size()-1];
    domains.pop_back();
}

auto stop1 = std::chrono::steady_clock::now();
auto stop2 = std::chrono::steady_clock::now();

void solve(const Graph & g0, const Graph & g1, vector<VtxPair> & incumbent,
        vector<VtxPair> & current, vector<Bidomain> & domains,
        vector<int> & left, vector<int> & right, unsigned int matching_size_goal, unsigned int level)
{
    
    
    if (abort_due_to_timeout) return;

    //if (arguments.verbose) show(current, domains, left, right);
    

    if (current.size() > incumbent.size()) {
        incumbent = current;
        //if (!arguments.quiet) cout << "Incumbent size: " << incumbent.size() << endl;
    }

    unsigned int bound = current.size() + calc_bound(domains);
    if (bound <= incumbent.size() || bound < matching_size_goal) return;
    //if (arguments.big_first && incumbent.size()==matching_size_goal) return;
    int bd_idx = select_bidomain(domains, left, current.size());

    if (bd_idx == -1)   // In the MCCS case, there may be nothing we can branch on
        return;
    Bidomain &bd = domains[bd_idx];

    int v = find_min_value(left, bd.l, bd.left_len);
    remove_vtx_from_left_domain(left, domains[bd_idx], v);
    

    // Try assigning v to each vertex w in the colour class beginning at bd.r, in turn
    int w = -1, idx = -1;
    bd.right_len--;

    for (VtxPair & a:current){
        if(EqClass[a.v]==EqClass[v]&&w<a.w) w=a.w;
    }
    if(w>0){
        int count_left=0, count_right=0;
        for (int i=bd.left_len; i>=0; --i) if(EqClass[left[bd.l+i]]==EqClass[v]) count_left++;
        for (int i=bd.right_len; i>=0; --i) if(right[bd.r+i]>w) count_right++;
        if(bd.left_len<=bd.right_len && count_left>count_right){
            if(bound+count_right-count_left<=incumbent.size()){
                return;
            }
        }
        if(bd.left_len>bd.right_len && (bd.right_len-count_right)>(bd.left_len-count_left)){
            if(bound+(bd.left_len-count_left)-(bd.right_len-count_right)<=incumbent.size()){
                return;
            }
        }
    }
    //if(bd.left_len>=bd.right_len&&w>0){
    //    int ccount=0;
    //    for (int i=bd.right_len; i>=0; --i) if(right[bd.r+i]<w) ccount++;
        //if(bd.left_len<bd.right_len) ccount=(ccount-bd.right_len+bd.left_len)<0? 0:(ccount-bd.right_len+bd.left_len);
    //    if(bound-ccount<=incumbent.size()) w=INT_MAX;
    //}
    nodes++;
    bool best_match = false;
    for (int i=bd.right_len; i>=0; --i) {
        idx = index_of_next_smallest(right, bd.r, bd.right_len+1, w);
        if(idx==-1) break;
        w = right[bd.r + idx];

        std::swap(index_right[w],index_right[right[bd.r + bd.right_len]]);

        right[bd.r + idx] = right[bd.r + bd.right_len];
        right[bd.r + bd.right_len] = w;
        //auto stop1 = std::chrono::steady_clock::now();
        
        auto new_domains = filter_domains(domains, left, right, g0, g1, v, w,best_match);
        //auto stop2 = std::chrono::steady_clock::now();
        //test_time+=std::chrono::duration_cast<std::chrono::microseconds>(stop2-stop1).count();
        current.emplace_back(VtxPair(v, w));
        solve(g0, g1, incumbent, current, new_domains, left, right, matching_size_goal,level+1);
        current.pop_back();
        if(best_match||bound <= incumbent.size()) return;
    }
    
    bd.right_len++;
    //if (bd.left_len == 0) remove_bidomain(domains, bd_idx); // Fixed by Buddhi Kothalawala. Thank you, Buddhi Kothalawala, for the checking.

    
    
    //int ccount=0;
    for(int i = 0; i<bd.left_len; ++i){
        if(EqClass[left[bd.l+i]]==EqClass[v]){
            std::swap(left[bd.l+i], left[bd.l+bd.left_len-1]);
            --bd.left_len; --i;
        }
    }
    if (bd.left_len == 0) remove_bidomain(domains, bd_idx);
    solve(g0, g1, incumbent, current, domains, left, right, matching_size_goal,level+1);
    
   
}

vector<VtxPair> mcs(const Graph & g0, const Graph & g1) {
    vector<int> left;  // the buffer of vertex indices for the left partitions
    vector<int> right;  // the buffer of vertex indices for the right partitions

    auto domains = vector<Bidomain> {};

    std::set<unsigned int> left_labels;
    std::set<unsigned int> right_labels;
    for (unsigned int label : g0.label) left_labels.insert(label);
    for (unsigned int label : g1.label) right_labels.insert(label);
    std::set<unsigned int> labels;  // labels that appear in both graphs
    std::set_intersection(std::begin(left_labels),
                          std::end(left_labels),
                          std::begin(right_labels),
                          std::end(right_labels),
                          std::inserter(labels, std::begin(labels)));

    // Create a bidomain for each label that appears in both graphs
    //for (unsigned int label : labels) {
        int start_l = left.size();
        int start_r = right.size();

        for (int i=0; i<g0.n; i++)
            //if (g0.label[i]==label)
                left.push_back(i);
        for (int i=0; i<g1.n; i++)
            //if (g1.label[i]==label)
                right.push_back(i);
            
        //cout<<label<<endl;

        int left_len = left.size() - start_l;
        int right_len = right.size() - start_r;
        domains.push_back({start_l, start_r, left_len, right_len, false});
    //}
    
    vector<VtxPair> incumbent;

    if (arguments.big_first) {
        for (int k=0; k<g0.n; k++) {
            unsigned int goal = g0.n - k;
            auto left_copy = left;
            auto right_copy = right;
            auto domains_copy = domains;
            vector<VtxPair> current;
            solve(g0, g1, incumbent, current, domains_copy, left_copy, right_copy, goal,1);
            if (incumbent.size() == goal || abort_due_to_timeout) break;
            if (!arguments.quiet) cout << "Upper bound: " << goal-1 << std::endl;
        }

    } else {
        vector<VtxPair> current;
        solve(g0, g1, incumbent, current, domains, left, right, 1,1);
        
    }

    return incumbent;
}

vector<int> calculate_degrees(const Graph & g) {
    vector<int> degree(g.n, 0);
    for (int v=0; v<g.n; v++) {
        for (int w=0; w<g.n; w++) {
            unsigned int mask = 0xFFFFu;
            if (g.adjmat[v][w] & mask) degree[v]++;
            if (g.adjmat[v][w] & ~mask) degree[v]++;  // inward edge, in directed case
        }
    }
    return degree;
}

int sum(const vector<int> & vec) {
    return std::accumulate(std::begin(vec), std::end(vec), 0);
}

int main(int argc, char** argv) {
    set_default_arguments();
    argp_parse(&argp, argc, argv, 0, 0, 0);

    char format = arguments.dimacs ? 'D' : arguments.lad ? 'L' : 'B';
    struct Graph g0 = readGraph(arguments.filename1, format, arguments.directed,
            arguments.edge_labelled, arguments.vertex_labelled);
    struct Graph g1 = readGraph(arguments.filename2, format, arguments.directed,
            arguments.edge_labelled, arguments.vertex_labelled);

        
          if(g0.n>g1.n){
	struct Graph gg = g0;
	g0 = g1;
 	g1 = gg;
        }

    std::thread timeout_thread;
    std::mutex timeout_mutex;
    std::condition_variable timeout_cv;
    abort_due_to_timeout.store(false);
    bool aborted = false;

    if (0 != arguments.timeout) {
        timeout_thread = std::thread([&] {
                auto abort_time = std::chrono::steady_clock::now() + std::chrono::seconds(arguments.timeout);
                {
                    /* Sleep until either we've reached the time limit,
                     * or we've finished all the work. */
                    std::unique_lock<std::mutex> guard(timeout_mutex);
                    while (! abort_due_to_timeout.load()) {
                        if (std::cv_status::timeout == timeout_cv.wait_until(guard, abort_time)) {
                            /* We've woken up, and it's due to a timeout. */
                            aborted = true;
                            break;
                        }
                    }
                }
                abort_due_to_timeout.store(true);
                });
    }

    

    vector<int> g0_deg = calculate_degrees(g0);
    vector<int> g1_deg = calculate_degrees(g1);
    for(int i=0;i<g1.n;++i) index_right.push_back(i);
    
    // As implemented here, g1_dense and g0_dense are false for all instances
    // in the Experimental Evaluation section of the paper.  Thus,
    // we always sort the vertices in descending order of degree (or total degree,
    // in the case of directed graphs.  Improvements could be made here: it would
    // be nice if the program explored exactly the same search tree if both
    // input graphs were complemented.
    vector<int> vv0(g0.n);
    std::iota(std::begin(vv0), std::end(vv0), 0);
    bool g1_dense = sum(g1_deg) < g1.n*(g1.n-1);
    std::stable_sort(std::begin(vv0), std::end(vv0), [&](int a, int b) {
        return !g1_dense ? (g0_deg[a]<g0_deg[b]) : (g0_deg[a]>g0_deg[b]);
    });
    vector<int> vv1(g1.n);
    std::iota(std::begin(vv1), std::end(vv1), 0);
    bool g0_dense = sum(g0_deg) < g0.n*(g0.n-1);
    std::stable_sort(std::begin(vv1), std::end(vv1), [&](int a, int b) {
        return !g0_dense ? (g1_deg[a]<g1_deg[b]) : (g1_deg[a]>g1_deg[b]);
    });

      // struct Graph g0_sorted(0), g1_sorted(0);
   // if(g0.n<=g1.n){
        	struct Graph g0_sorted = induced_subgraph(g0, vv0);
    	struct Graph g1_sorted = induced_subgraph(g1, vv1);
        //}else{
//	g1_sorted = induced_subgraph(g0, vv0);
 //   	g0_sorted = induced_subgraph(g1, vv1);
   //      }
	//cout<<g0_sorted.n<<" "<<g1_sorted.n<<endl;
    
    set_adjlist(g0_sorted);
    set_adjlist(g1_sorted);
    EqClass = new ui[g0_sorted.n];
    GetEqClass(g0_sorted,EqClass);

    // for(int i=0;i<g0_sorted.n;++i){
    //     cout<<EqClass[i]<<" ";
    // }
    // cout<<endl;

    auto start = std::chrono::steady_clock::now();
        
    vector<VtxPair> solution = mcs(g0_sorted, g1_sorted);

    

    auto stop = std::chrono::steady_clock::now();
    auto time_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();

// Convert to indices from original, unsorted graphs
    for (auto& vtx_pair : solution) {
        vtx_pair.v = vv0[vtx_pair.v];
        vtx_pair.w = vv1[vtx_pair.w];
    }

    /* Clean up the timeout thread */
    if (timeout_thread.joinable()) {
        {
            std::unique_lock<std::mutex> guard(timeout_mutex);
            abort_due_to_timeout.store(true);
            timeout_cv.notify_all();
        }
        timeout_thread.join();
    }

    if (!check_sol(g0, g1, solution))
        fail("*** Error: Invalid solution\n");

    //cout << "Solution size " << solution.size() << std::endl;
    //for (int i=0; i<g0.n; i++)
    //    for (unsigned int j=0; j<solution.size(); j++)
    //        if (solution[j].v == i)
    //            cout << "(" << solution[j].v << " -> " << solution[j].w << ") ";
   // cout << std::endl;

   // cout << "Nodes:                      " << nodes << endl;
   // cout << "CPU time (ms):              " << time_elapsed << endl;
   // cout << "test_time (ms): "<<test_time<<endl;
  cout<<"#1: "<<arguments.filename1<<" "<<arguments.filename2<<" "<< g0.n<<" "<<g1.n << std::endl;
    cout<<"#2: "<<solution.size()<<" "<<nodes<<" "<<time_elapsed<<std::endl;   
 if (aborted){
	cout<<"#1: "<<arguments.filename1<<" "<<arguments.filename2<<" "<< g0.n<<" "<<g1.n << std::endl;
        cout<<"#2: "<<0<<std::endl;
 }
        //cout << "TIMEOUT" << endl;
    
}

