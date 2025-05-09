# test hypothesis 1
import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt


# load datasets
df_ll = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/LLM_LLM_results.xlsx", sheet_name="Results")
df_hh = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RBAI_results.xlsx", sheet_name="Results")
df_lrb = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RB_LLM_results.xlsx", sheet_name="Results")
df_hrb = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RB_results.xlsx", sheet_name="Results")

# preprocess data
df_lrb = df_lrb[df_lrb['wholesale_price'].notna()]

# hybrid and LLM conditions
hybrid_data = pd.concat([df_hh, df_hrb], axis=0)
llm_data = pd.concat([df_ll, df_lrb], axis=0)

# pareto efficient offers
hybrid_pareto_c = hybrid_data['pareto_efficient'].sum()
llm_pareto_c = llm_data['pareto_efficient'].sum()

hybrid_total = len(hybrid_data)
llm_total = len(llm_data)

# proportion calculation 
hybrid_pareto_prop = hybrid_pareto_c / hybrid_total
llm_pareto_prop = llm_pareto_c / llm_total

# two-sample proportion test
count = np.array([hybrid_pareto_c, llm_pareto_c])  
nobs = np.array([hybrid_total, llm_total])  

# z-test
z_stat, p_value = proportions_ztest(count, nobs)

# results
print(f"Z-statistic: {z_stat}")
print(f"P-value: {p_value}")



# visualize results
conditions = ['Hybrid', 'LLM']
proportions = [hybrid_pareto_prop, llm_pareto_prop]
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)

# error bars 
hybrid_se = np.sqrt(hybrid_pareto_prop * (1 - hybrid_pareto_prop) / hybrid_total)
llm_se = np.sqrt(llm_pareto_prop * (1 - llm_pareto_prop) / llm_total)
errors = [hybrid_se, llm_se]

# plot
plt.figure(figsize=(4, 6))
bars = plt.bar(conditions, proportions, yerr=errors, capsize=10, color=[sky_blue, navy_blue], alpha=0.8, edgecolor='black')
plt.title('Proportion of Pareto Efficient Negotiations', fontsize=12, fontweight='bold')
plt.xlabel('Agent Type', fontsize=10)
plt.ylabel('Proportion of Pareto Efficient Outcomes', fontsize=10)
plt.ylim(0, 1.1)

for i, bar in enumerate(bars):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03, f'{proportions[i]:.2f}', 
             ha='center', va='bottom', fontsize=12, fontweight='bold', color='black')

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()