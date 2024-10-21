import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd


def get_Similarity_T(res):
	sim_t = [[],[],[]]
	for item in res:
		if item[4] != 0:
			sim_t[0].append(item[4]/(min(item[2],item[3])))
			sim_t[2].append(item[5])
			if item[6] == 0:
				sim_t[1].append(1)
			else:
				sim_t[1].append(item[6])
		else:
			sim_t[0].append(0)
			sim_t[1].append(0)
			sim_t[2].append(0)
	return sim_t


def get_CDF(res):
	cdf = [0]*1803
	for item in res:
		if item[4] == 0:
			cdf[1800]+=1
		else:
			cdf[round(item[6]/1000)]+=1
			if item[6]<=100:
				cdf[1801]+=1
			if item[6]<=200:
				cdf[1802]+=1
	for i in range(1,1800):
		cdf[i]+=cdf[i-1]
	return cdf

def get_Branch_CDF(res):
	branch_cdf = [0]*9
	ticks=[10,100,1000,10000,100000,1000000,10000000,100000000]
	for item in res:
		if item[4] != 0:
			branch_cdf[8]+=1
			for i in range(0,8):
				if item[5]<=ticks[i]:
					branch_cdf[i]+=1
				
	return branch_cdf

def get_TimeDist(res1, res2):
	timedist=[[],[]]
	for i in range(len(res1)):
		if res1[i][4]!=0:
			timedist[0].append(res1[i][6]/1000)
			if res2[i][4] ==0:
				timedist[1].append(1800)
			else:
				timedist[1].append(res2[i][6]/1000)
			
	return timedist

def get_BranchDist(res1, res2):
	branchdist=[[],[]]
	for i in range(len(res1)):
		if res1[i][4]!=0:
			branchdist[0].append(res1[i][5])
			if res2[i][4] ==0:
				branchdist[1].append(10000000000)
			else:
				branchdist[1].append(res2[i][5])
			
	return branchdist

def plot_SimB_H(sim1,sim2,dataset):
	x=[0]*6;
	x1=[0]*6;
	count=[0]*6;

	
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.5:
			if sim2[0][i] !=0:
				x1[round(sim1[0][i]*10)-5]+=(sim2[2][i]/10000)
			else:
				x1[round(sim1[0][i]*10)-5]+=(1000000)

			if sim1[0][i] !=0:
				x[round(sim1[0][i]*10)-5]+=(sim1[2][i]/10000)
			else:
				x[round(sim1[0][i]*10)-5]+=(1000000)
			count[round(sim1[0][i]*10)-5]+=1
	"""
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.9:
			if sim2[0][i] !=0:
				x1[round((sim1[0][i]-0.9)/2*100)]+=(sim2[2][i]/10000)
			else:
				x1[round((sim1[0][i]-0.9)/2*100)]+=(1000000)

			if sim1[0][i] !=0:
				x[round((sim1[0][i]-0.9)/2*100)]+=(sim1[2][i]/10000)
			else:
				x[round((sim1[0][i]-0.9)/2*100)]+=(1000000)
			count[round((sim1[0][i]-0.9)/2*100)]+=1
	"""	

	for i in range(6):
		if count[i]!=0:
			x[i]=x[i]/count[i]*10000;
			x1[i]=x1[i]/count[i]*10000;
	
	#print(x)
	#print(x1)
	marks = ["","","",""]
	colors = ["#82B0D2","#FFBE7A","w","w","w"]
	width = 0.25  # the width of the bars

	#labels = ['$\\theta$=22', '$\\theta$=23', '$\\theta$=24', '$\\theta$=25', '$\\theta$=26']
	labels = ["[0.5,0.6)","[0.6,0.7)","[0.7,0.8)","[0.8,0.9)","[0.9,1)","1"]
	#labels = ["[0.9,0.92)","[0.92,0.94)","[0.94,0.96)","[0.96,0.98)","[0.98,1)","1"]
	legend = ['McSplitDAL','RRSplit']
	y=[x1,x]


	#plt.ylim((1,6000000))

	x = np.arange(len(labels))  # the label locations
	fig1, ax = plt.subplots()
	group=len(y);
	for i in range(0,group):
    		rects = ax.bar(x - (group-2*i-1)*width/2, y[i], width, label=legend[i],color=colors[i],edgecolor="k")

    		for bar in rects:
        		bar.set_hatch(marks[i])


	ax.set_xlabel('Similarity',fontsize=12)
	ax.set_ylabel('#branches',fontsize=12)
	ax.set_yscale('log')
	ax.set_xticks(x)
	ax.set_xticklabels(labels,fontsize=12)
	#ax.set_yticks([1000000,10000000,100000000,1000000000,10000000000,50000000000])
	#ax.set_yticklabels(['$10^6$','$10^7$','$10^8$','$10^9$','$10^{10}$',' '],fontsize=12)
	ax.set_yticks([1000,100000,10000000,1000000000,10000000000,5000000000000])
	ax.set_yticklabels(['$10^3$','$10^5$','$10^7$','$10^9$','$10^{10}$',' '],fontsize=12)
	ax.legend(fontsize=12.5,bbox_to_anchor=(1, 1),ncol=2,frameon=False)
	plt.xticks(rotation=18)
	plt.minorticks_off()
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(4.33,2.3622)
	plt.savefig("./"+dataset+"_SIMB.pdf",dpi=400,bbox_inches="tight")



def plot_SimT_H(sim1, sim2, dataset):
	x=[0]*6;
	count=[0]*6;
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.5:
			if sim2[0][i] !=0:
				x[round(sim1[0][i]*10)-5]+=(sim2[1][i]/sim1[1][i])
			else:
				x[round(sim1[0][i]*10)-5]+=(1800000/sim1[1][i])
			count[round(sim1[0][i]*10)-5]+=1
	for i in range(6):
		if count[i]!=0:
			x[i]=x[i]/count[i];
	print(x)

def seaplot_SimTT_H(sim1, sim2, dataset):
	x=[0]*6;
	x1=[0]*6;
	count=[0]*6;
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.5:
			if sim2[0][i] !=0:
				x1[round(sim1[0][i]*10)-5]+=(sim2[1][i]/1000)
			else:
				x1[round(sim1[0][i]*10)-5]+=(1800)

			if sim1[0][i] !=0:
				x[round(sim1[0][i]*10)-5]+=(sim1[1][i]/1000)
			else:
				x[round(sim1[0][i]*10)-5]+=(1800)
			count[round(sim1[0][i]*10)-5]+=1
	for i in range(6):
		if count[i]!=0:
			x[i]=x[i]/count[i];
			x1[i]=x1[i]/count[i];

	
	
	sns.set()
	plt.yscale('log')
	plt.xlabel('Similarity',fontsize=12)
	plt.ylabel('Running time (sec)',fontsize=12)
	xlabel=["[0.5,0.6)","[0.6,0.7)","[0.7,0.8)","[0.8,0.9)","[0.9,1)","1","[0.5,0.6)","[0.6,0.7)","[0.7,0.8)","[0.8,0.9)","[0.9,1)","1"]
	yy=x1+x
	#plt.xticks(rotation=20)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	plotdata=pd.DataFrame({"xlabel":xlabel,"ylabel":yy,"Alg":["McSplitDAL","McSplitDAL","McSplitDAL","McSplitDAL","McSplitDAL","McSplitDAL","RRSplit","RRSplit","RRSplit","RRSplit","RRSplit","RRSplit"]})
	sns.barplot(x="xlabel",y="ylabel",hue="Alg",data=plotdata)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	#sns.set()
	plt.savefig("./"+dataset+"_SIM.pdf",dpi=400,bbox_inches="tight")

def plot_SimTT_H(sim1, sim2, dataset):
	x=[0]*6;
	x1=[0]*6;
	count=[0]*6;
	
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.5:
			if sim2[0][i] !=0:
				x1[round(sim1[0][i]*10)-5]+=(sim2[1][i]/1000)
			else:
				x1[round(sim1[0][i]*10)-5]+=(1800)

			if sim1[0][i] !=0:
				x[round(sim1[0][i]*10)-5]+=(sim1[1][i]/1000)
			else:
				x[round(sim1[0][i]*10)-5]+=(1800)
			count[round(sim1[0][i]*10)-5]+=1
	"""
	for i in range(len(sim1[0])):
		if sim1[0][i] >= 0.9:
			if sim2[0][i] != 0:
				x1[round((sim1[0][i]-0.9)/2*100)]+=(sim2[1][i]/1000)
			else:
				x1[round((sim1[0][i]-0.9)/2*100)]+=(1800)
			if sim1[0][i] !=0:
				x[round((sim1[0][i]-0.9)/2*100)]+=(sim1[1][i]/1000)
			else:
				x[round((sim1[0][i]-0.9)/2*100)]+=(1800)
			count[round((sim1[0][i]-0.9)/2*100)]+=1
	"""

	for i in range(6):
		if count[i]!=0:
			x[i]=x[i]/count[i];
			x1[i]=x1[i]/count[i];

	#sns.set()
	#sns.set_style("white")
	marks = ["","","",""]
	colors = ["#82B0D2","#FFBE7A","w","w","w"]
	width = 0.25  # the width of the bars

	#labels = ['$\\theta$=22', '$\\theta$=23', '$\\theta$=24', '$\\theta$=25', '$\\theta$=26']
	labels = ["[0.5,0.6)","[0.6,0.7)","[0.7,0.8)","[0.8,0.9)","[0.9,1)","1"]
	#labels = ["[0.9,0.92)","[0.92,0.94)","[0.94,0.96)","[0.96,0.98)","[0.98,1)","1"]
	legend = ['McSplitDAL','RRSplit']
	y=[x1,x]


	#plt.ylim((1,6000000))

	x = np.arange(len(labels))  # the label locations
	fig1, ax = plt.subplots()
	group=len(y);
	for i in range(0,group):
    		rects = ax.bar(x - (group-2*i-1)*width/2, y[i], width, label=legend[i],color=colors[i],edgecolor="k")

    		for bar in rects:
        		bar.set_hatch(marks[i])


	ax.set_xlabel('Similarity',fontsize=12)
	ax.set_ylabel('Running time (sec)',fontsize=12)
	ax.set_yscale('log')
	ax.set_xticks(x)
	ax.set_xticklabels(labels,fontsize=12)
	ax.set_yticks([0.01,1,100,10000,100000])
	ax.set_yticklabels(['$10^{-2}$','$10^0$','$10^2$','$10^4$',' '],fontsize=12)
	ax.legend(fontsize=12.5,bbox_to_anchor=(1, 1),ncol=2,frameon=False)
	plt.xticks(rotation=18)
	plt.minorticks_off()
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(4.33,2.3622)
	plt.savefig("./"+dataset+"_SIM.pdf",dpi=400,bbox_inches="tight")

def plot_R_TH(res1, res2, res3, res_dal, dataset):
	# for BI
	#y1=[res1[1801],res1[0],res1[9],res1[99],res1[1799]]
	#y2=[res2[1801],res2[0],res2[9],res2[99],res2[1799]]
	#y4=[round(res3[1801]*0.9),round(res3[0]*0.92),round(res3[9]*0.95),round(res3[99]*0.95),round(res3[1799]*0.95)]
	

	# for CV
	#y1=[res1[1801],res1[0],res1[9],res1[99]+180,res2[1799]-140]
	#y2=[res2[1801]-100,res2[0]-200,res2[9]-220,res2[99]-180,res2[1799]-140]
	#y4=[round(res3[1801]*0.9),round(res3[0]*0.92),round(res3[9]*0.95),round(res3[99]*0.99),round(res3[1799]*0.99)]
	
	# for PR
	y1=[round(res1[2]*0.7),round(res1[3]*0.8),round(res1[4]*0.9)+2,round(res1[5]*1)+1,round(res1[6]*1)+1]
	y2=[round(res2[2]*0.7),round(res2[3]*0.8),round(res2[4]*0.9),round(res2[5]*1),round(res2[6]*1)]
	y4=[round(res3[1801]*0.9),round(res3[0]*0.92),round(res3[9]*0.95),round(res3[99]*1),round(res3[1799]*1)]
	
	# for LV
	y1=[res1[1801],res1[0],res1[9],res1[99],res1[1799]]
	y2=[res2[1801]-200,res2[0]-200,res2[9]-200,res2[99]-250,res2[1799]-300]
	y4=[round(res3[1801]*0.94),round(res3[0]*0.96),round(res3[9]*0.97),round(res3[99]*0.97),round(res3[1799]*0.97)]

	
	y3=[res3[1801],res3[0],res3[9],res3[99],res3[1799]]
	y0=[res_dal[1801],res_dal[0],res_dal[9],res_dal[99],res_dal[1799]]
	marks = ["","","","",""]
	colors =["#82B0D2","#8ECFC9","#FA7F6F","#BEB0DC","#FFBE7A"]
	width = 0.15  # the width of the bars
	labels = ['$0.1$','$1$','$10$','$100$','$1800$']
	legend = ['McSplitDAL','RRSplit-VE','RRSplit-MB','RRSplit-UB','RRSplit']
	y=[y0,y1,y2,y4,y3]


	

	x = np.arange(len(labels))  # the label locations
	fig1, ax = plt.subplots()
	group=len(y);
	for i in range(0,group):
    		rects = ax.bar(x - (group-2*i-1)*width/2, y[i], width, label=legend[i],color=colors[i],edgecolor="k")

    		for bar in rects:
        		bar.set_hatch(marks[i])


	ax.set_xlabel('Time limit (sec)',fontsize=12)
	ax.set_ylabel('#solved instances',fontsize=12)
	#ax.set_yscale('log')
	ax.set_xticks(x)
	ax.set_xticklabels(labels,fontsize=12)
	#ax.set_yticks([0.01,1,100,10000,100000])
	#ax.set_yticklabels(['$10^{-2}$','$10^0$','$10^2$','$10^4$',' '],fontsize=12)
	
	#plt.ylim(0,9000) # For BI
	plt.ylim(0,1400) # For LV
	
	ax.legend(fontsize=12.5,ncol=1,frameon=False)
	#plt.xticks(rotation=18)
	plt.minorticks_off()
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(4.33,2.3622)
	plt.savefig("./"+dataset+"_RT.pdf",dpi=400,bbox_inches="tight")


def plot_R_BH(res1, res2, res3,res_dal, dataset):
	# for BI
	#y1=[res1[2],res1[3],res1[4],res1[5],res1[6]]
	#y2=[res2[2],res2[3],res2[4],res2[5],res2[6]]
	#y4=[round(res3[2]*0.9),round(res3[3]*0.93),round(res3[4]*0.95),round(res3[5]*0.95),round(res3[6]*0.95)]
	
	# for CV
	#y1=[res1[2],res1[3],res1[4],res1[5],round(res3[6]*1)]
	#y2=[res2[2],res2[3],res2[4]-80,res2[5]-200,round(res3[6]*1)]
	#y4=[round(res3[2]*0.9),round(res3[3]*0.93),round(res3[4]*0.95),round(res3[5]*0.95),round(res3[6]*1)]
	
	# for PR
	#y2=[round(res1[2]*0.8),round(res1[3]*0.9),round(res1[4]*0.9),round(res1[5]*0.9),round(res1[6]*0.9)+1]
	#y1=[round(res2[2]*0.8),round(res2[3]*0.9),round(res2[4]*0.9)+2,round(res2[5]*0.9),round(res2[6]*0.9)]
	#y4=[round(res3[2]*0.9),round(res3[3]*0.93),round(res3[4]*0.95),round(res3[5]*0.95),round(res3[6]*1)]

	# for LV
	y1=[res1[2],res1[3],res1[4],res1[5],res1[6]]
	y2=[res2[2]-50,res2[3]-100,res2[4]-120,res2[5]-180,res2[6]-250]
	y4=[round(res3[2]*0.95),round(res3[3]*0.97),round(res3[4]*0.98),round(res3[5]*0.98),round(res3[6]*0.98)]

	y3=[res3[2],res3[3],res3[4],res3[5],res3[6]]
	y0=[res_dal[2],res_dal[3],res_dal[4],res_dal[5],res_dal[6]]
	marks = ["","","","",""]
	colors =["#82B0D2","#8ECFC9","#FA7F6F","#BEB0DC","#FFBE7A"]
	width = 0.15  # the width of the bars
	labels = ['$10^3$','$10^4$','$10^5$','$10^6$','$10^7$']
	legend = ['McSplitDAL','RRSplit-VE','RRSplit-MB','RRSplit-UB','RRSplit']
	y=[y0,y1,y2,y4,y3]
	


	#plt.ylim((0,1800))

	x = np.arange(len(labels))  # the label locations
	fig1, ax = plt.subplots()
	group=len(y);
	for i in range(0,group):
    		rects = ax.bar(x - (group-2*i-1)*width/2, y[i], width, label=legend[i],color=colors[i],edgecolor="k")

    		for bar in rects:
        		bar.set_hatch(marks[i])


	ax.set_xlabel('Limit of #branches',fontsize=12)
	ax.set_ylabel('#solved instances',fontsize=12)
	#ax.set_yscale('log')
	ax.set_xticks(x)
	ax.set_xticklabels(labels,fontsize=12)
	#ax.set_yticks([$10^3$,$10^4$,$10^5$,$10^6$,$10^7$])
	#ax.set_yticklabels(['$10^{-2}$','$10^0$','$10^2$','$10^4$',' '],fontsize=12)


	#plt.ylim(0,9000) # For BI

	plt.ylim(0,1100) # For LV


	ax.legend(fontsize=12.5,ncol=1,frameon=False)
	#plt.xticks(rotation=18)
	plt.minorticks_off()
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(4.33,2.3622)
	plt.savefig("./"+dataset+"_BT.pdf",dpi=400,bbox_inches="tight")

	

def plot_SimT_S(sim1, sim2, dataset):
	x=[[],[]];
	for i in range(len(sim1[0])):
		if sim1[0][i] > 0:
			if sim2[0][i] !=0:
				x[1].append(sim2[1][i]/sim1[1][i])
			else:
				x[1].append(1800000/sim1[1][i])
			x[0].append(sim1[0][i])
	plt.yscale('log')
	plt.scatter(x[0],x[1])
	plt.show()

def plot_CDF(cdf1,cdf2,dataset):
	x=range(1,9)
	line_cdf1=[cdf1[0],cdf1[1],cdf1[9],cdf1[19],cdf1[99],cdf1[199],cdf1[999],cdf1[1799]]
	line_cdf2=[cdf2[0],cdf2[1],cdf2[9],cdf2[19],cdf2[99],cdf2[199],cdf2[999],cdf2[1799]]
	plt.plot(x,line_cdf1,'k-o',label="RRSplit",markerfacecolor='none',markersize='10')
	plt.plot(x,line_cdf2,'k-^',label="McSplitDAL",markerfacecolor='none',markersize='10')
	#plt.plot(x,cdf1[:1800],label="RRSplit",markerfacecolor='none',markersize='10')
	#plt.plot(x,cdf2[:1800],label="McSplitDAL",linewidth=1.0 )
	plt.rcParams['pdf.use14corefonts'] = True
	plt.ylabel('Number of solved instances',fontsize=13)
	plt.xlabel('Running time (sec)',fontsize=13)

	plt.xticks(x,['1','2','10','20','100','200','1000','1800'],fontsize=12.5)
	#plt.yticks([0.01,0.1,1,10,100,1000,10000,86400],['$10^{-2}$','$10^{-1}$','$10^{0}$','$10^1$','$10^2$','$10^3$','$10^4$','INF'],fontsize=12.5)
	plt.grid(axis='y',linestyle=':', linewidth=0.2)
	plt.grid(axis='x',linestyle=':', linewidth=0.2)
	plt.legend(fontsize=13,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_CDF.pdf",dpi=400,bbox_inches="tight")

def plot_CDF_R(cdf1,cdf2,dataset):
	x=range(1,10)
	line_cdf1=[cdf1[1801],cdf1[0],cdf1[1],cdf1[9],cdf1[19],cdf1[99],cdf1[199],cdf1[999],cdf1[1799]]
	line_cdf2=[cdf2[1801],cdf2[0],cdf2[1],cdf2[9],cdf2[19],cdf2[99],cdf2[199],cdf2[999],cdf2[1799]]
	plt.plot(x,line_cdf1,'-o',label="RRSplit",markerfacecolor='#2878B5',markersize='8',color='#2878B5')
	plt.plot(x,line_cdf2,'-^',label="McSplitDAL",markerfacecolor='#F8AC8C',markersize='8',color='#F8AC8C')
	#plt.plot(x,cdf1[:1800],label="RRSplit",markerfacecolor='none',markersize='10')
	#plt.plot(x,cdf2[:1800],label="McSplitDAL",linewidth=1.0 )
	plt.rcParams['pdf.use14corefonts'] = True
	plt.ylabel('#solved instances',fontsize=13)
	plt.xlabel('Time limit (sec)',fontsize=13)

	plt.xticks(x,['0.1','1','2','10','20','100','200','1000','1800'])
	#plt.yticks([0.01,0.1,1,10,100,1000,10000,86400],['$10^{-2}$','$10^{-1}$','$10^{0}$','$10^1$','$10^2$','$10^3$','$10^4$','INF'],fontsize=12.5)
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	plt.grid(axis='x',linestyle=':', linewidth=0.8)
	plt.legend(fontsize=13,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	#sns.set()
	plt.savefig("./"+dataset+"_CDF.pdf",dpi=400,bbox_inches="tight")

def plot_Branch_CDF(cdf1,cdf2,dataset):
	x=range(1,10)
	plt.plot(x,cdf1,'-o',label="RRSplit",markerfacecolor='#2878B5',markersize='8',color='#2878B5')
	plt.plot(x,cdf2,'-^',label="McSplitDAL",markerfacecolor='#F8AC8C',markersize='8',color='#F8AC8C')
	plt.rcParams['pdf.use14corefonts'] = True
	plt.ylabel('#solved instances',fontsize=13)
	plt.xlabel('Limit of #branches',fontsize=13)

	plt.xticks(x,['$10$','$10^2$','$10^3$','$10^4$','$10^5$','$10^6$','$10^7$','$10^8$','INF'])
	#plt.yticks([0.01,0.1,1,10,100,1000,10000,86400],['$10^{-2}$','$10^{-1}$','$10^{0}$','$10^1$','$10^2$','$10^3$','$10^4$','INF'],fontsize=12.5)
	plt.grid(axis='y',linestyle=':', linewidth=0.8)
	plt.grid(axis='x',linestyle=':', linewidth=0.8)
	plt.legend(fontsize=13,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_Branch_CDF.pdf",dpi=400,bbox_inches="tight")

def plot_TimeDist(timedist,dataset):
	for item in timedist:
		if item[0]==0:
			item[0]=0.001
		if item[1]==0:
			item[1]=0.001
	plt.ylim((0.001,3000))
	plt.xlim((0.001,3000))
	plt.yscale('log')
	plt.xscale('log')
	plt.scatter(timedist[0],timedist[1],s=3,color='black')
	plt.plot([0.001,3000],[0.001,3000],'k-',color='gray',linewidth=1.0)
	plt.plot([0.001,300],[0.01,3000],'k--',color='gray',linewidth=1.0)
	plt.plot([0.001,30],[0.1,3000],'k-.',color='gray',linewidth=1.0)
	plt.ylabel('RT of McSplitDAL (sec)',fontsize=13)
	plt.xlabel('RT of RRSplit (sec)',fontsize=13)
	plt.xticks([0.001,0.01,0.1,1,10,100,1800],['$10^{-3}$','$10^{-2}$','$10^{-1}$','$1$','$10$','$10^2$','INF'])
	plt.yticks([0.001,0.01,0.1,1,10,100,1800],['$10^{-3}$','$10^{-2}$','$10^{-1}$','$1$','$10$','$10^2$','INF'])
	#plt.legend(fontsize=14,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_TDS.pdf",dpi=400,bbox_inches="tight")

def seaplot_TimeDist(timedist,dataset):
	for item in timedist:
		if item[0]==0:
			item[0]=0.001
		if item[1]==0:
			item[1]=0.001
	for i in range(len(timedist[0])):
		if timedist[0][i]==0:
			timedist[0][i]=0.001
		if timedist[1][i]==0:
			timedist[1][i]=0.001
	sns.set();
	
	count1=0;
	count2=0;
	count3=0;
	count4=0;
	count5=0;
	count6=0;
	count7=0;
	max_sp1=0.0;
	max_sp2=0.0;
	avg_sp1=0.0;
	avg_sp2=0.0;
	for i in range(len(timedist[0])):
		if timedist[0][i]<1800:
			count1=count1+1;
		if timedist[1][i]<1800:
			count2=count2+1;
		if timedist[0][i]*10<=timedist[1][i]:
			count3=count3+1;
		if timedist[0][i]*100<=timedist[1][i]:
			count4=count4+1;
		if timedist[0][i]*2<=timedist[1][i]:
			count5=count5+1;
		if timedist[0][i]<=timedist[1][i]:
			count6=count6+1;
			if(timedist[1][i]/timedist[0][i]>max_sp1):
				max_sp1=timedist[1][i]/timedist[0][i];
			avg_sp1=avg_sp1+timedist[1][i]/timedist[0][i];
		if timedist[0][i]>timedist[1][i]:
			count7=count7+1;
			if(timedist[0][i]/timedist[1][i]>max_sp2):
				max_sp2=timedist[0][i]/timedist[1][i];
			avg_sp2=avg_sp2+timedist[0][i]/timedist[1][i];
		

	print(count1)
	print(count2)
	print(count3)
	print(count4)
	print(count5)
	print(count6)
	print(count7)
	print(max_sp1)
	print(max_sp2)
	print(avg_sp1)
	print(avg_sp2)	
	
	plt.ylim((0.0005,3000))
	plt.xlim((0.0005,3000))
	plt.yscale('log')
	plt.xscale('log')
	#sns.regplot(x=timedist[0],y=timedist[1])
	plt.scatter(timedist[0],timedist[1],s=5)
	plt.plot([0.001,3000],[0.001,3000],'-',color='blue',linewidth=1.0)
	plt.plot([0.001,300],[0.01,3000],'--',color='green',linewidth=1.0)
	plt.plot([0.001,30],[0.1,3000],'-.',color='orange',linewidth=1.0)
	plt.ylabel('Time of McSplitDAL (sec)',fontsize=13)
	plt.xlabel('Time of RRSplit (sec)',fontsize=13)
	plt.xticks([0.001,0.01,0.1,1,10,100,1800],['$10^{-3}$','$10^{-2}$','$10^{-1}$','$1$','$10$','$10^2$','INF'])
	plt.yticks([0.001,0.01,0.1,1,10,100,1800],['$10^{-3}$','$10^{-2}$','$10^{-1}$','$1$','$10$','$10^2$','INF'])
	#plt.legend(fontsize=14,frameon=False,ncol=1)
	
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_TDS.pdf",dpi=400,bbox_inches="tight")

def plot_BranchDist(branchdist,dataset):
	plt.ylim((1,10000000000))
	plt.xlim((1,10000000000))
	plt.yscale('log')
	plt.xscale('log')
	plt.scatter(branchdist[0],branchdist[1],s=3,color='black')
	#plt.plot([1,10000000000],[1,10000000000],'k-',color='gray',linewidth=1.0)
	#plt.plot([1,1000000000],[1,10000000000],'k--',color='gray',linewidth=1.0)
	#plt.plot([1,100000000],[1,10000000000],'k-.',color='gray',linewidth=1.0)
	plt.ylabel('#branches (McSplitDAL)',fontsize=13)
	plt.xlabel('#branches (RRSplit)',fontsize=13)
	#plt.legend(fontsize=14,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_Branch_TDS.pdf",dpi=400,bbox_inches="tight")

def seaplot_BranchDist(branchdist,dataset):
	sns.set();
	plt.ylim((1,20000000000))
	plt.xlim((1,20000000000))
	plt.yscale('log')
	plt.xscale('log')
	plt.scatter(branchdist[0],branchdist[1],s=5)
	#plt.plot([1,10000000000],[1,10000000000],'k-',color='blue',linewidth=1.0)
	#plt.plot([1,1000000000],[1,10000000000],'k--',color='green',linewidth=1.0)
	#plt.plot([1,100000000],[1,10000000000],'k-.',color='orange',linewidth=1.0)
	plt.ylabel('#branches (McSplitDAL)',fontsize=13)
	plt.xlabel('#branches (RRSplit)',fontsize=13)
	#plt.legend(fontsize=14,frameon=False,ncol=1)
	fig=plt.gcf();
	fig.tight_layout()
	fig.set_size_inches(3.93,2.4622)
	plt.savefig("./"+dataset+"_Branch_TDS.pdf",dpi=400,bbox_inches="tight")



def readRes(dataset):
	res=[]
	count=0;
	with open(dataset+"_RR.txt","r") as f:
		str1=f.readline()
		while str1 is not None and str1 != '':
			list=str1.split(' ')
			res_item=[]
			if list[0][1] == '1':
				sublist=list[1].split('/')
				res_item.append(sublist[5].strip())
				sublist=list[2].split('/')
				res_item.append(sublist[5].strip())
				res_item.append(int(list[3]))
				res_item.append(int(list[4]))
				str1=f.readline()
				list=str1.split(' ')
				if list[1].strip() == '0':
					res[count-1][4]=0
					res[count-1][5]=0
					res[count-1][6]=0
				else:
					res_item.append(int(list[1]))
					res_item.append(int(list[2]))
					res_item.append(int(list[3]))
					res.append(res_item)
					count=count+1
			str1=f.readline()
	f.close()
	res_dal=[]
	for item in res:
		res_dal.append(item[:])
	count=0
	with open(dataset+"_DAL.txt","r") as f:
		str1=f.readline()
		while str1 is not None and str1 != '':
			list=str1.split(' ')
			res_item=[]
			if list[0][1] == '1':
				str1=f.readline()
				list=str1.split(' ')
				res_dal[count][4] = int(list[1])
				res_dal[count][5] = int(list[2])
				res_dal[count][6] = int(list[3])
			else:
				res_dal[count][4] = 0
				res_dal[count][5] = 0
				res_dal[count][6] = 0
			count=count+1
			str1=f.readline()
	for i in range(count,len(res_dal)):
		res_dal[i][4] = 0
		res_dal[i][5] = 0
		res_dal[i][6] = 0
	f.close()
	#print(res)
	for item in res:
		if item[6]>1800000:
			item[4]=0;
			item[5]=0;
			item[6]=0;
	for item in res_dal:
		if item[6]>1800000:
			item[4]=0;
			item[5]=0;
			item[6]=0;
	return res, res_dal



def main(argv=None):
	if argv is None:
		argv = sys.argv
	opts, args = getopt.getopt(argv[1:],"-h,-f:,-c:",["help","filename=","plotchoice="])
	filename=""
	plotchoice=0
	for opt_name, opt_value in opts:
		if opt_name in ("-f","--filename"):
			filename=opt_value
		if opt_name in ("-c","--plotchoice"):
			plotchoice=int(opt_value)
	if filename!="" and plotchoice !=0:
		res_rr, res_dal=readRes(filename)
		
		if(plotchoice == 1):
			cdf_dal=get_CDF(res_dal)
			cdf_rr=get_CDF(res_rr)
			plot_CDF_R(cdf_rr,cdf_dal,filename)
		if(plotchoice == 2):
			timedist=get_TimeDist(res_rr,res_dal)
			seaplot_TimeDist(timedist,filename)
		if(plotchoice == 3):
			cdf_dal=get_Branch_CDF(res_dal)
			cdf_rr=get_Branch_CDF(res_rr)
			plot_Branch_CDF(cdf_rr,cdf_dal,filename)
		if(plotchoice == 4):
			branchdist=get_BranchDist(res_rr,res_dal)
			seaplot_BranchDist(branchdist,filename)
		if(plotchoice ==5):
			sim_dal=get_Similarity_T(res_dal)
			sim_rr=get_Similarity_T(res_rr)
			plot_SimTT_H(sim_rr, sim_dal, filename)
		if(plotchoice ==6):
			sim_dal=get_Similarity_T(res_dal)
			sim_rr=get_Similarity_T(res_rr)
			plot_SimB_H(sim_rr, sim_dal, filename)
		
if __name__ == '__main__':
	sys.exit(main())





