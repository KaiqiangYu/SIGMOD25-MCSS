# Readme for Availability&Reproducibility of SIGMOD Submission 1077

 Our code, data and additional materials are avaliable here. We also provide the scripts needed for reproducing and visualizing the main results in our submission. 


## 1. Algorithms
### Our proposed algorithm: RRSplit
The source code of RRSplit can be found in `./RRSplit`

### Baseline method: McSplitDAL
The source code of McSplitDAL is avaiable from the authors of "Hybrid learning
with new value function for the maximum common induced subgraph problem, In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 37. 4044–4051".


## 2. Hardware info
Programming Language: `C++`
 
Compiler Info: `gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0 `

Memory: `128GB` & CPU: `Intel(R) Xeon(R) Gold 6230R CPU @ 2.10GH`

Packages/Libraries Needed: `makefile` and `Python3` (including `numpy` and `matplotlib` for ploting figures)

## 3. Datasets info
All datasets used in our experiments are from the [benchmark]("http://liris.cnrs.fr/csolnon/SIP.html").


## 4. Compile and Usage
### 4.1 Compile RRSplit under folder `./RRSplit/`
```shell
make
```


### 4.2 Usage of RRSplit
  ./mcsp {OPTIONS}

    mcsp, an efficient algorithm for finding MCS

  OPTIONS:

      [--help]                          Display this help menu
      [-l]                              Format of datasets (list of edges)
      [-q]                              Quiet
      [-t XX]                           Time limit (seconds)
      HEURISTIC                         Strategy of selecting the branching vertex pair
      FILENAME1                         Path to the first given graph Q
      FILENAME2                         Path to the second given graph G                         

### 4.3 Running example under folder `./RRSplit/`
Command:
```shell
./mcsp -l -q -t 3600 min_max pattern target
```

Outputs:
```shell
#1: pattern target 5 6
#2: 4 9 0
```
 ### Format of the outputs
 ```shell
#1 pattern target [number of vertices in Q] [number of vertices in G]
#2 [number of vertices in the found MCS] [number of formed branches] [running time]
 ```

## 5.  Scripts for reproducing and visualizing the key results
We provide the scripts for reproducing and visualizing Figure 5, Figure 6, Figure 7, Figure 8 and Figure 9 in the folder `./Rep`. We remark that **before conducting this step, you need to ensure that** 

- **both RRSplit and McSplitDAL have been complied successfully**, and
- **the datasets have been downloaded.**

### 5.1. Preparation under `./Rep`

**STEP 1**: Put the complied RRSplit (i.e., mcsp) and McSplitDAL in the folder `./Rep/RRSplit/` and `./Rep/McSplitDAL/`, respectively.

**STEP 2**: Download the datasets and put the folder `newSIPbenchmarks` under `./Rep/dataset/`.

### 5.2. Reproducing the key results under `./Rep`

Below, we provide the instructions for reproducing the results in the graph collection ``BI``. For other graph collections (i.e., ``CV``, ``PR`` and ``LV``), the flow is similar. **We remark that reproducing the whole results would take several days, but we can terminate the programs mutually at any time and visualize the current results (the resulting figures could be different with those provided in the submission but indicate the similar trend that our method RRSplit performs better).**


**STEP 1**: Reproduce the results of RRSplit on ``BI`` under folder `./Rep/RRSplit` (Estimated time: **24+ hours**)
```shell
chmod +x RRSplit-BI.sh
./RRSplit-BI.sh
```

**STEP 2**: Reproduce the results of McSplitDAL on ``BI`` under folder `./Rep/McSplitDAL` (Estimated time: **24+ hours**)
```shell
chmod +x McSplitDAL-BI.sh
./McSplitDAL-BI.sh
```

Note that we can reproduce the results on other graph collections similary by running `*-CV.sh`, `*-PR.sh` and `*-LV.sh`.


### 5.2. Visualizing the key results under `./Rep/Vis/`

We remark that the provided scripts suppot the *online* visualization. That means we can visualize the current result without terminating the programs. To do this, we need to copy all output files (e.g., `*_RR.txt` and `*_DAL.txt` under `./Rep/RRSplit` and `./Rep/McSplitDAL`, respectively) to `./Rep/Vis/`.


**STEP 1**: Copy all output files (e.g., `*_RR.txt` and `*_DAL.txt` under `./Rep/RRSplit` and `./Rep/McSplitDAL`, respectively) to `./Rep/Vis/`.


**STEP 2**: Visualize the results of Figure 5 (a-d)
```shell
python vis.py -f "BI" -c 2
python vis.py -f "CV" -c 2
python vis.py -f "PR" -c 2
python vis.py -f "LV" -c 2
```
You can find 4 PDF files `*_TDS.pdf` under the current folder.

**STEP 3**: Visualize the results of Figure 6 (a-d)
```shell
python vis.py -f "BI" -c 4
python vis.py -f "CV" -c 4
python vis.py -f "PR" -c 4
python vis.py -f "LV" -c 4
```

You can find 4 PDF files `*_Branch_TDS.pdf` under the current folder.

**STEP 4**: Visualize the results of Figure 7 (a-d)
```shell
python vis.py -f "BI" -c 1
python vis.py -f "CV" -c 1
python vis.py -f "PR" -c 1
python vis.py -f "LV" -c 1
```

You can find 4 PDF files `*_CDS.pdf` under the current folder.

**STEP 5**: Visualize the results of Figure 8 (a-d)
```shell
python vis.py -f "BI" -c 3
python vis.py -f "CV" -c 3
python vis.py -f "PR" -c 3
python vis.py -f "LV" -c 3
```

You can find 4 PDF files `*_Branch_CDS.pdf` under the current folder.

**STEP 6**: Visualize the results of Figure 9 (a-d)
```shell
python vis.py -f "BI" -c 5
python vis.py -f "LV" -c 5
python vis.py -f "BI" -c 6
python vis.py -f "LV" -c 6
```
You can find 4 PDF files `*_SIM.pdf` and `*_SIMB.pdf` under the current folder.

## 6. Remark

We do not reproduce Figures 10-12 since they correspond to the ablation study of our proposed algorithm. We remark that the reproduced results, i.e., Figures 5-9, demonstrate the superiority of our algorithm RRSplit against the state-of-the-art McSplitDAL.
