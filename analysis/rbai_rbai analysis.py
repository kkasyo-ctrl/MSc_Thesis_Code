# rbai_rb descriptive analysis/ visualization
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import shapiro, wilcoxon

# load data
df = pd.read_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RBAI_results.xlsx", sheet_name="Results")

# profit differences
df["profit_diff"] = df["profit_b1"] - df["profit_b2"]
profit_counts = df["profit_diff"].value_counts().sort_index()
df["profit_sup"] = np.where(df["role_b1"] == "supplier", df["profit_b1"], df["profit_b2"])
df["profit_buy"] = np.where(df["role_b1"] == "buyer", df["profit_b1"], df["profit_b2"])

df["profit_diff_roles"] = df["profit_sup"] - df["profit_buy"]

# colors
sky_blue = (162/255, 213/255, 242/255)
navy_blue = (27/255, 38/255, 59/255)


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

# message count
axes[0].bar(msg_counts.index, msg_counts.values, edgecolor="black", color=navy_blue, width=0.6)
axes[0].set_title("Frequency of Message Count", fontsize=12, weight="bold")
axes[0].set_xlabel("Message Count", fontsize=12)
axes[0].set_ylabel("Frequency", fontsize=12)
axes[0].grid(axis='y', linestyle=':', alpha=0.6)
axes[0].set_xticks(msg_range)

# offer count
axes[1].bar(offer_counts.index, offer_counts.values, edgecolor="black", color=sky_blue, width=0.6)
axes[1].set_title("Frequency of Offer Count", fontsize=12, weight="bold")
axes[1].set_xlabel("Offer Count", fontsize=12)
axes[1].grid(axis='y', linestyle=':', alpha=0.6)
axes[1].set_xticks(offer_range)

# layout
plt.tight_layout()
plt.show()

# get number of interpreted correctly
tmp = df["const_b1"] == df["b1_const_thought_b2"]
tmp.value_counts()

tmp1 = df["const_b2"] == df["b2_const_thought_b1"]
tmp1.value_counts()


# normality test on profit differences based on roles
stat, p_normality = shapiro(df["profit_diff"])
print(f"Shapiro-Wilk Test: W = {stat:.3f}, p = {p_normality:.5f}")

wilcoxon_stat, wilcoxon_p = wilcoxon(df["profit_b1"], df["profit_b2"])
print(f"Wilcoxon Signed-Rank Test: Statistic = {wilcoxon_stat}, p = {wilcoxon_p:.5f}")


print("\nSummary Statistics:")

df.groupby("role_b1")[["profit_b1", "profit_b2"]].describe()

df[["profit_b1", "profit_b2"]].describe()

# number of negotiations won
df["won"].value_counts()

# negotiations outcome statistics
df['pareto_efficient'].value_counts()
df['euclidean_deviation'].value_counts()
df['euclidean_deviation'].mean()


df['profit_b1'].median()
df['profit_b1'].median()
