from scipy.stats.stats import pearsonr
import pandas as pd
from itertools import combinations
import glob

all_files = glob.glob("/Users/charlie/Desktop/Taipower/Archive/results_combined/*.csv")
df_pair1 = []
df_pair2 = []
corr = []
for combo in combinations(all_files, 2):  # 2 for pairs, 3 for triplets, etc
	print(combo)
	a = pd.read_csv(combo[0])
	b = pd.read_csv(combo[1])

	_a = list(a['0'].values)
	_b = list(b['0'].values)

	c = pearsonr(_a, _b)
	df_pair1.append(combo[0].split('/')[-1])
	df_pair2.append(combo[1].split('/')[-1])
	corr.append(c[0])
#	print(c)

df_cor = pd.DataFrame({'name_1':df_pair1,'nane_2':df_pair2,'corr':corr})

df_cor.to_csv('/Users/charlie/Desktop/Taipower/Archive/df_cor.csv',index=False)