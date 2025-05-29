# rb_llm descriptive analysis/ visualization
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import shapiro, wilcoxon

# load data
df = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RB_LLM_results.xlsx", sheet_name="Results")

# profit differences
df["profit_diff"] = df["profit_rb"] - df["profit_llm"]
profit_counts = df["profit_diff"].value_counts().sort_index()
df["profit_sup"] = np.where(df["role_rb"] == "supplier", df["profit_rb"], df["profit_llm"])
df["profit_buy"] = np.where(df["role_rb"] == "buyer", df["profit_rb"], df["profit_llm"])

df["profit_diff_roles"] = df["profit_sup"] - df["profit_buy"]

df_deal = df[df["wholesale_price"].notna()]

df.shape[0] - df_deal.shape[0]

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
msg_counts = df_deal["message_count"].value_counts().sort_index()

offer_range = np.arange(df_deal["offer_count"].min(), df_deal["offer_count"].max() + 1)
offer_counts = df_deal["offer_count"].value_counts().sort_index()
offer_counts = offer_counts.reindex(offer_range, fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

# plot message count
axes[0].bar(msg_counts.index, msg_counts.values, edgecolor="black", color=navy_blue, width=0.6)
axes[0].set_title("Frequency of Message Count", fontsize=13, weight="bold")
axes[0].set_xlabel("Message Count", fontsize=12)
axes[0].set_ylabel("Frequency", fontsize=12)
axes[0].grid(axis='y', linestyle=':', alpha=0.6)
axes[0].set_xticks(msg_counts.index)

# plot offer count
axes[1].bar(offer_counts.index, offer_counts.values, edgecolor="black", color=sky_blue, width=0.6)
axes[1].set_title("Frequency of Offer Count", fontsize=13, weight="bold")
axes[1].set_xlabel("Offer Count", fontsize=12)
axes[1].grid(axis='y', linestyle=':', alpha=0.6)
axes[1].set_xticks(offer_range)

# layout
plt.tight_layout()
plt.show()


# distance from pareto optimal 
dist = df_deal["euclidean_deviation"].value_counts().sort_index()

plt.figure(figsize=(5, 5))
plt.bar(dist.index, dist.values, 
        edgecolor="black", color=sky_blue, width=0.6)

plt.title("Frequency of Message Count", fontsize=12, weight="bold")
plt.xlabel("Message Count", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.xticks(dist.index)  

plt.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()

df_deal[['profit_llm', 'profit_rb']].describe()
df_deal["euclidean_deviation"].value_counts().sort_index()



# normality test on profit differences based on configurations
stat, p_normality = shapiro(df_deal["profit_diff"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

wilcoxon_stat, wilcoxon_p = wilcoxon(df_deal["profit_llm"], df_deal["profit_rb"])
print(f"Wilcoxon Signed-Rank Test: Statistic = {wilcoxon_stat}, p = {wilcoxon_p:.5f}")


# normality test on profit differences based on roles
stat, p_normality = shapiro(df_deal["profit_diff_roles"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

wilcoxon_stat, wilcoxon_p = wilcoxon(df_deal["profit_buy"], df_deal["profit_sup"])
print(f"Wilcoxon Signed-Rank Test: Statistic = {wilcoxon_stat}, p = {wilcoxon_p:.5f}")

df_deal[['message_count', 'offer_count']].describe()

df['llm_const_thought_rb'] == df['const_llm']

tmp = df['llm_const_thought_rb'] == df['const_llm']
tmp.value_counts()

df_deal['profit_llm'].median()
df_deal['profit_rb'].median()
