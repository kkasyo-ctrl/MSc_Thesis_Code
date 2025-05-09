# llm_llm descriptive analysis/ visualization
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import shapiro, wilcoxon, ttest_rel

# load data
df = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/LLM_LLM_results.xlsx", sheet_name="Results")

# profit differences
df["profit_diff"] = df["profit_b1"] - df["profit_b2"]
profit_counts = df["profit_diff"].value_counts().sort_index()
df["profit_sup"] = np.where(df["role_b1"] == "supplier", df["profit_b1"], df["profit_b2"])
df["profit_buy"] = np.where(df["role_b1"] == "buyer", df["profit_b1"], df["profit_b2"])

df["profit_diff_roles"] = df["profit_sup"] - df["profit_buy"]

# colors
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)




# visualize profit differences between configurations
profit_counts = df["profit_diff"].value_counts().sort_index()
profit_range = np.arange(df["profit_diff"].min(), df["profit_diff"].max() + 1)
profit_counts = df["profit_diff"].value_counts().sort_index()
profit_counts = profit_counts.reindex(profit_range, fill_value=0)

# colors
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)

# profit difference
plt.figure(figsize=(6, 5))
plt.bar(profit_counts.index, profit_counts.values, edgecolor="black", color=sky_blue, width=0.6)
plt.title("Profit Difference Distribution (RB - LLM)", fontsize=12, weight="bold")
plt.xlabel("Profit Difference", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.xticks(profit_range)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# profit agreement rate
msg_range = np.arange(df["message_count"].min(), df["message_count"].max() + 1)
msg_counts = df["message_count"].value_counts().sort_index()
msg_counts = msg_counts.reindex(msg_range, fill_value=0)

# offer count histogram
offer_range = np.arange(df["offer_count"].min(), df["offer_count"].max() + 1)
offer_counts = df["offer_count"].value_counts().sort_index()
offer_counts = offer_counts.reindex(offer_range, fill_value=0)

# plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

# plot message count
axes[0].bar(msg_counts.index, msg_counts.values, edgecolor="black", color=navy_blue, width=0.6)
axes[0].set_title("Frequency of Message Count", fontsize=12, weight="bold")
axes[0].set_xlabel("Message Count", fontsize=12)
axes[0].set_ylabel("Frequency", fontsize=12)
axes[0].grid(axis='y', linestyle=':', alpha=0.6)
axes[0].set_xticks(msg_range)

# plot offer count
axes[1].bar(offer_counts.index, offer_counts.values, edgecolor="black", color=sky_blue, width=0.6)
axes[1].set_title("Frequency of Offer Count", fontsize=12, weight="bold")
axes[1].set_xlabel("Offer Count", fontsize=12)
axes[1].grid(axis='y', linestyle=':', alpha=0.6)
axes[1].set_xticks(offer_range)

# one figure
plt.tight_layout()
plt.show()

# build a common set of bins spanning both distributions
all_profits = np.concatenate([df['profit_sup'], df['profit_buy']])
bins = np.linspace(all_profits.min(), all_profits.max(), 20)
plt.figure(figsize=(9, 6))

# plot step histograms
sns.histplot(df['profit_sup'], bins=20, kde=False, stat="count", color=sky_blue, element="step", linewidth=1, label='Supplier Profit')
sns.histplot(df['profit_buy'], bins=20, kde=False, stat="count", color=navy_blue, element="step", linewidth=1, label='Buyer Profit')

# mean lines
plt.axvline(df['profit_sup'].mean(), color=sky_blue, linestyle='--', linewidth=2, label='Supplier Mean')
plt.axvline(df['profit_buy'].mean(), color=navy_blue, linestyle='--', linewidth=2, label='Buyer Mean')

# plot style
plt.title("Distribution of Supplier vs. Buyer Profit", fontsize=14, weight='bold')
plt.xlabel("Profit", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend(frameon=False, fontsize=10, loc='upper right')
plt.tight_layout()
plt.show()

# normality test on profit differences based on roles
stat, p_normality = shapiro(df["profit_diff"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

t_stat, p_value = ttest_rel(df["profit_b1"], df["profit_b2"])
print(f"Paired t-test: t = {t_stat:.3f}, p = {p_value:.5f}")

# normality test on profit differences based on roles
stat, p_normality = shapiro(df["profit_diff_roles"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

t_stat, p_value = ttest_rel(df["profit_sup"], df["profit_buy"])
print(f"Paired t-test: t = {t_stat:.3f}, p = {p_value:.5f}")

print("\nSummary Statistics:")

df.groupby("role_b1")[["profit_b1", "profit_b2"]].describe()

df[["profit_b1", "profit_b2"]].describe()
df[["profit_sup", "profit_buy"]].describe()

# number of negotiations won
df["won"].value_counts()

# negotiations outcome statistics
df['pareto_efficient'].value_counts()
df['euclidean_deviation'].value_counts()
df['euclidean_deviation'].mean()
