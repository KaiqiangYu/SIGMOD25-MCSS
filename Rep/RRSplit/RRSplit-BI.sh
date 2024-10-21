#!/bin/bash
dataset="../dataset/newSIPbenchmarks/biochemicalReactions"
for num in {1..196}
do
	for ((num2=$num+1;num2<=196;num2++))
	do
		DataID1=$num
		DataID2=$num2
		if [[ $num -lt 10 ]]
		then
			DataID1=00$num
		elif [[ $num -lt 100 ]]
		then
			DataID1=0$num
		fi
		if [[ $num2 -lt 10 ]]
		then
			DataID2=00$num2
		elif [[ $num2 -lt 100 ]]
		then
			DataID2=0$num2
		fi
		./mcsp -l -q -t 3600 min_max $dataset/$DataID1.txt $dataset/$DataID2.txt >> BI_RR.txt
		
	done
done
