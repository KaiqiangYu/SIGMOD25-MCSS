#!/bin/bash
dataset="../dataset/newSIPbenchmarks/LV"
for num in {2..112}
do
	for ((num2=$num+1;num2<=112;num2++))
	do
		./mcsp -l -q -t 1800 min_max $dataset/g$num $dataset/g$num2 >> LV_RR.txt
		
	done
done
