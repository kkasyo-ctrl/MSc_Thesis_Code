# rbai_rb descriptive analysis/ visualization
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import shapiro, wilcoxon

# load data
df = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RB_results.xlsx", sheet_name="Results")

# profit differences
df["profit_diff"] = df["profit_hybrid"] - df["profit_rb"]
profit_counts = df["profit_diff"].value_counts().sort_index()
df["profit_sup"] = np.where(df["role_hybrid"] == "supplier", df["profit_hybrid"], df["profit_rb"])
df["profit_buy"] = np.where(df["role_hybrid"] == "buyer", df["profit_hybrid"], df["profit_rb"])

df["profit_diff_roles"] = df["profit_sup"] - df["profit_buy"]

# colors
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)


# visualize profit differences between configurations
plt.figure(figsize=(5, 5))
plt.bar(profit_counts.index, profit_counts.values, edgecolor="black", color=sky_blue, width=0.4)
plt.title("Profit Differences (Hybrid - Rule-based)", fontsize=12, weight = 'bold')
plt.xlabel("Profit Difference", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.xticks(profit_counts.index) 
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


# visualize profit differences between roles
sup_counts = df["profit_sup"].value_counts().sort_index()
buy_counts = df["profit_buy"].value_counts().sort_index()

all_profits = sorted(set(sup_counts.index).union(set(buy_counts.index)))
sup_counts = sup_counts.reindex(all_profits, fill_value=0)
buy_counts = buy_counts.reindex(all_profits, fill_value=0)

x = np.arange(len(all_profits))  
bar_width = 0.4

plt.figure(figsize=(8, 5))
plt.bar(x - bar_width/2, sup_counts, width=bar_width, label="Supplier Profit", color=sky_blue, edgecolor="black")
plt.bar(x + bar_width/2, buy_counts, width=bar_width, label="Buyer Profit", color=navy_blue, edgecolor="black")
plt.xticks(x, all_profits)
plt.xlabel("Profit", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.title("Profit Distribution by Role", fontsize=12, weight='bold')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# get number of interpreted correctly
tmp = df["const_rb"] == df["rb_const_thought_hybrid"]
tmp.value_counts()

df[df["const_rb"] != df["rb_const_thought_hybrid"]]

tmp1 = df["const_hybrid"] == df["hybrid_const_thought_rb"]
tmp1.value_counts()

# normality test on profit differences based on configurations
stat, p_normality = shapiro(df["profit_diff"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

wilcoxon_stat, wilcoxon_p = wilcoxon(df["profit_hybrid"], df["profit_rb"])
print(f"Wilcoxon Signed-Rank Test: Statistic = {wilcoxon_stat}, p = {wilcoxon_p:.5f}")


# normality test on profit differences based on roles
stat, p_normality = shapiro(df["profit_diff_roles"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

wilcoxon_stat, wilcoxon_p = wilcoxon(df["profit_hybrid"], df["profit_rb"])
print(f"Wilcoxon Signed-Rank Test: Statistic = {wilcoxon_stat}, p = {wilcoxon_p:.5f}")

print("\nSummary Statistics:")
df.loc[:,['profit_hybrid', 'profit_rb', 'offer_count', 'message_count', 'conversation_history', 'offer_list', 'won', 'pareto_efficient', 'euclidean_deviation', 'profit_diff', 'profit_sup','profit_buy', 'profit_diff_roles']].describe()
df.columns

df.groupby("role_hybrid")[["profit_hybrid", "profit_rb"]].mean()

df["won"].value_counts()

