#!/bin/bash
dataset="../dataset/newSIPbenchmarks/images-PR15"
for num in {1..24}
do
	./mcspDAL -l -q -t 1800 min_max $dataset/pattern$num $dataset/target >> PR_DAL.txt
		
done
