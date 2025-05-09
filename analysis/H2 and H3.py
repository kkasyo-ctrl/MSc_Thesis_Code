####
#H2
####
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, kruskal, shapiro
import matplotlib.pyplot as plt

# load datasets
df_ll = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/LLM_LLM_results.xlsx", sheet_name="Results")
df_hh = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RBAI_results.xlsx", sheet_name="Results")
df_lrb = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RB_LLM_results.xlsx", sheet_name="Results")
df_hrb = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RB_results.xlsx", sheet_name="Results")
df_hl = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_LLM_results.xlsx", sheet_name="Results")

# preprocess data
df_lrb = df_lrb[df_lrb['wholesale_price'].notna()]

# adjust deviation 
def adjust_deviation(df, profit_col1, profit_col2, deviation_col):
    adjusted = df.copy()
    adjusted['adjusted_deviation'] = np.where(
        (adjusted['pareto_efficient'] == 0) & (adjusted[profit_col1] < adjusted[profit_col2]),
        adjusted[deviation_col],
        0
    )
    return adjusted['adjusted_deviation']


hybrid_dev = df_hh['euclidean_deviation']
hybrid_dev = pd.concat([hybrid_dev, adjust_deviation(df_hrb, 'profit_hybrid', 'profit_rb', 'euclidean_deviation')], axis=0).reset_index(drop=True)
hybrid_dev = pd.concat([hybrid_dev, adjust_deviation(df_hl, 'profit_hybrid', 'profit_llm', 'euclidean_deviation')], axis=0).reset_index(drop=True)


llm_dev = df_ll['euclidean_deviation']
llm_dev = pd.concat([llm_dev, adjust_deviation(df_lrb, 'profit_llm', 'profit_rb', 'euclidean_deviation')], axis=0).reset_index(drop=True)
llm_dev = pd.concat([llm_dev, adjust_deviation(df_hl, 'profit_llm', 'profit_hybrid', 'euclidean_deviation')], axis=0).reset_index(drop=True)

rule_dev = adjust_deviation(df_lrb, 'profit_rb', 'profit_llm', 'euclidean_deviation')
rule_dev = pd.concat([rule_dev, adjust_deviation(df_hrb, 'profit_rb', 'profit_hybrid', 'euclidean_deviation')], axis=0).reset_index(drop=True)

hybrid_dev.describe()

# check for nan
hybrid_dev[hybrid_dev.isna()]
llm_dev[llm_dev.isna()]
rule_dev[rule_dev.isna()]
len(hybrid_dev)+ len(llm_dev) + len(rule_dev)

# normal dist
stat, p_normality = shapiro(hybrid_dev)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")
stat, p_normality = shapiro(llm_dev)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")
stat, p_normality = shapiro(rule_dev)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")


# Kruskal-Wallis
stat, p = kruskal(llm_dev, hybrid_dev, rule_dev)
print(f"Kruskal-Wallis test: statistic = {stat:.4f}, p = {p:.4g}")


# pairwise Wilcoxon Signed-Rank tests (two sided for general difference)
u_hybrid_llm = mannwhitneyu(hybrid_dev, llm_dev, alternative='two-sided') 
u_rule_llm = mannwhitneyu(rule_dev, llm_dev, alternative='two-sided')
u_hybrid_rule = mannwhitneyu(hybrid_dev, rule_dev, alternative='two-sided')

print("Mann-Whitney U Test:")
print("Hybrid vs LLM:", u_hybrid_llm)
print("Rule-based vs LLM:", u_rule_llm)
print("Hybrid vs Rule-Based:", u_hybrid_rule)



####
#H3
####

# hybrid and LLM conditions
hybrid_offs = pd.concat([df_hh['offer_count'], df_hrb['offer_count'], df_hl['offer_count']], axis=0).reset_index(drop= True)
llm_offs = pd.concat([df_ll['offer_count'], df_lrb['offer_count'], df_hl['offer_count']], axis=0).reset_index(drop= True)
rule_offs = pd.concat([df_lrb['offer_count'], df_hrb['offer_count']], axis=0).reset_index(drop= True)
llm_offs.describe()

# check for nan
hybrid_offs[hybrid_offs.isna()]
llm_offs[llm_offs.isna()]
rule_offs[rule_offs.isna()]

# normal dist
stat, p_normality = shapiro(hybrid_offs)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")
stat, p_normality = shapiro(llm_offs)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")
stat, p_normality = shapiro(rule_offs)
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")


# Kruskal-Wallis
stat_offs, p_offs = kruskal(hybrid_offs, llm_offs, rule_offs)
print(f"Kruskal-Wallis test: statistic = {stat_offs:.4f}, p = {p_offs:.4g}")

# pairwise Mann-Whitney U tests
o_hybrid_llm = mannwhitneyu(hybrid_offs, llm_offs, alternative='less')
o_rule_llm = mannwhitneyu(rule_offs, llm_offs, alternative='less')
o_hybrid_rule = mannwhitneyu(hybrid_offs, rule_offs, alternative='less')

print("Hybrid vs LLM (Mann-Whitney U):", o_hybrid_llm)
print("Rule-based vs LLM (Mann-Whitney U):", o_rule_llm)
print("Hybrid vs Rule-Based (Mann-Whitney U):", o_hybrid_rule)

conditions = ['Rule-based', 'Hybrid', 'LLM']
means = [rule_offs.mean(), hybrid_offs.mean(), llm_offs.mean()]
stds = [rule_offs.std(), hybrid_offs.std(), llm_offs.std()]
n_obs = [len(rule_offs), len(hybrid_offs), len(llm_offs)]

sems = [std / np.sqrt(n) for std, n in zip(stds, n_obs)]

# plot differences
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)
soft_coral = (255/255, 153/255, 153/255)

fig, ax = plt.subplots(figsize=(8, 6))

bars = ax.bar(conditions, means, yerr=sems, capsize=8, width=0.6,
              color=[sky_blue, navy_blue, soft_coral], edgecolor='black')

ax.set_xlabel('Agent Type', fontsize=12)
ax.set_ylabel('Mean Number of Offers', fontsize=12)
ax.set_title('Mean Offers to Reach Agreement by Agent Configuration', fontsize=12, fontweight='bold')

ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)  

ax.set_ylim(bottom=0)

# put values on bars
for i, (bar, mean) in enumerate(zip(bars, means)):
    height = bar.get_height()
    offset = 14 if i == 0 else 8 
    ax.annotate(f'{mean:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height + 0.05),
                xytext=(0, offset),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=12)
plt.tight_layout()
plt.show()
