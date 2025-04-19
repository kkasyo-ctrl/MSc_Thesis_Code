# analysis file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shared import rnd_param
import math

# import data
df_llm_llm = pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\llm_llm\output_llm_llm_final.csv", encoding='latin-1')
# df_rbai_llm =  pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rbai_llm\output_rbai_llm_final.csv", encoding='latin-1')
df_rb_llm = pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rb_llm\output_rb_llm_final.csv", encoding='latin-1')
df_rbai_rbai = pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rbai_rbai\output_rbai_rbai_final.csv", encoding='latin-1')
df_rbai_rb = pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rbai_rb\output_rbai_rb_final.csv", encoding='latin-1')
df_rb_rb = pd.read_csv(r"C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rb_rb\output_rb_rb_final.csv", encoding='latin-1')



PRICE_RANGE = rnd_param.PRICE_RANGE
QUALITY_RANGE = rnd_param.QUALITY_RANGE

def pareto_optimality(role, const1, const2):
    offers = [(p, q) for p in PRICE_RANGE for q in QUALITY_RANGE]
    profits = {}
    for price, quality in offers:
        profits[(price, quality)] = (price - quality - const1, const2 + quality - price) if role == 'supplier' else (const1 + quality - price, price - quality - const2)
    

    metrics = {o: (a + b, abs(a - b)) for o, (a, b) in profits.items()}

    def is_pareto(o):
        total, diff = metrics[o]
        return all((t <= total and d >= diff) or o2 == o for o2, (t, d) in metrics.items())

    return [o for o in offers if is_pareto(o)]


def efficient_profits(role, const1, const2):
    optimal_offer = pareto_optimality(role, const1, const2)[1]
    price = optimal_offer[0]
    quality = optimal_offer[1]

    if role == 'supplier':
        profit1 = price - quality - const1
        profit2 = const2 - price + quality
    else:
        profit1 = const1 - price + quality
        profit2 = price - quality - const2
        

    return (profit1, profit2)


def diff(role, const1, const2):
    p1, p2 = efficient_profits(role, const1, const2)
    return abs(p1 - p2)


def euclidean_dist(price, quality, pareto_front):
    x, y = price, quality
    return min(math.sqrt((x - a)**2 + (y - b)**2) for (a, b) in pareto_front)


###
# LLM_LLM
###

# add which bot "won"
df_llm_llm['won'] = np.where(
    df_llm_llm['profit_b1'] > df_llm_llm['profit_b2'],
    1,
    np.where(
        df_llm_llm['profit_b2'] > df_llm_llm['profit_b1'],
        2,
        0      
    )
)
df_llm_llm.groupby('won')[['profit_b1','profit_b2']].describe()

# H1
pareto_effient = []
for i in range(0, len(df_llm_llm)):
    theoretical_eff_diff = diff(df_llm_llm['role_b1'][i], df_llm_llm['const_b1'][i], df_llm_llm['const_b2'][i])
    actual_diff = abs(df_llm_llm['profit_b1'][i] - df_llm_llm['profit_b2'][i])

    if theoretical_eff_diff >= actual_diff:
        pareto_effient.append(1)
    else:
        pareto_effient.append(0)

df_llm_llm['pareto_efficient'] = pareto_effient


# H2
dist = [] 

for i in range(0, len(df_llm_llm)):
    if df_llm_llm['pareto_efficient'][i] == 0:
        offers = pareto_optimality(df_llm_llm['role_b1'][i], df_llm_llm['const_b1'][i], df_llm_llm['const_b2'][i])
        dev = euclidean_dist(df_llm_llm['wholesale_price'][i], df_llm_llm['quality'][i], offers)
        
        
        dist.append(dev)
    else:
        dist.append(0)


df_llm_llm['euclidean_deviation'] = dist

# save llm_llm
#df_llm_llm.to_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/LLM_LLM_results.xlsx", sheet_name="Results", index= False)


###
# RB_LLM
###

# add which bot "won"
df_rb_llm['won'] = np.where(
    df_rb_llm['profit_rb'] > df_rb_llm['profit_llm'],
    "rb",
    np.where(
        df_rb_llm['profit_llm'] > df_rb_llm['profit_rb'],
        "llm",
        0      
    )
)

df_rb_llm.groupby('won')[['profit_rb','profit_llm']].describe()
df_rb_llm.loc[:,['profit_rb', 'profit_llm']]

# H1
pareto_efficient = []

for i in range(len(df_rb_llm)):
    profit_rb = df_rb_llm['profit_rb'][i]
    profit_llm = df_rb_llm['profit_llm'][i]

    if pd.isna(profit_rb) or pd.isna(profit_llm):
        pareto_efficient.append("No Deal")
    else:
        theoretical_eff_diff = diff(df_rb_llm['role_rb'][i],
                                    df_rb_llm['const_rb'][i],
                                    df_rb_llm['const_llm'][i])
        actual_diff = abs(profit_rb - profit_llm)
        pareto_efficient.append(1 if theoretical_eff_diff >= actual_diff else 0)



df_rb_llm['pareto_efficient'] = pareto_effient


# H2
dist = [] 

for i in range(0, len(df_rb_llm)):
    if df_rb_llm['pareto_efficient'][i] == 'No Deal':
        dist.append(None)
    elif df_rb_llm['pareto_efficient'][i] == 0:
        offers = pareto_optimality(df_rb_llm['role_rb'][i], df_rb_llm['const_rb'][i], df_rb_llm['const_llm'][i])
        dev = euclidean_dist(df_rb_llm['wholesale_price'][i], df_rb_llm['quality'][i], offers)
        
        dist.append(dev)
    else:
        dist.append(0)


df_rb_llm['euclidean_deviation'] = dist

# save rb_llm
#df_rb_llm.to_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RB_LLM_results.xlsx", sheet_name="Results", index= False)



###
# RBAI_RB
###
df_rbai_rb.columns

# add which bot "won"
df_rbai_rb['won'] = np.where(
    df_rbai_rb['profit_hybrid'] > df_rbai_rb['profit_rb'],
    "hybrid",
    np.where(
        df_rbai_rb['profit_rb'] > df_rbai_rb['profit_hybrid'],
        "rb",
        0      
    )
)

df_rbai_rb.groupby('won')[['profit_hybrid','profit_rb']].describe()
df_rbai_rb.loc[:,['profit_hybrid', 'profit_rb']]

# H1
pareto_efficient = []

for i in range(len(df_rbai_rb)):
    profit_hybrid = df_rbai_rb['profit_hybrid'][i]
    profit_rb = df_rbai_rb['profit_rb'][i]

    if pd.isna(profit_hybrid) or pd.isna(profit_rb):
        pareto_efficient.append("No Deal")
    else:
        theoretical_eff_diff = diff(df_rbai_rb['role_hybrid'][i],
                                    df_rbai_rb['const_hybrid'][i],
                                    df_rbai_rb['const_rb'][i])
        actual_diff = abs(profit_hybrid - profit_rb)
        pareto_efficient.append(1 if theoretical_eff_diff >= actual_diff else 0)



df_rbai_rb['pareto_efficient'] = pareto_efficient


# H2
dist = [] 

for i in range(0, len(df_rbai_rb)):
    if df_rbai_rb['pareto_efficient'][i] == 'No Deal':
        dist.append(None)
    elif df_rbai_rb['pareto_efficient'][i] == 0:
        offers = pareto_optimality(df_rbai_rb['role_hybrid'][i], df_rbai_rb['const_hybrid'][i], df_rbai_rb['const_rb'][i])
        dev = euclidean_dist(df_rbai_rb['wholesale_price'][i], df_rbai_rb['quality'][i], offers)
        
        dist.append(dev)
    else:
        dist.append(0)


df_rbai_rb['euclidean_deviation'] = dist


# save rbai_rb
#df_rbai_rb.to_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RB_results.xlsx", sheet_name="Results", index= False)




###
# RBAI_RB
###
df_rbai_rbai.columns

# add which bot "won"
df_rbai_rbai['won'] = np.where(
    df_rbai_rbai['profit_b1'] > df_rbai_rbai['profit_b2'],
    1,
    np.where(
        df_rbai_rbai['profit_b2'] > df_rbai_rbai['profit_b1'],
        2,
        0      
    )
)

df_rbai_rbai.groupby('won')[['profit_b1','profit_b2']].describe()
df_rbai_rbai.loc[:,['profit_hybrid', 'profit_rb']]

# H1
pareto_efficient = []

for i in range(len(df_rbai_rbai)):
    profit_b1 = df_rbai_rbai['profit_b1'][i]
    profit_b2 = df_rbai_rbai['profit_b2'][i]

    if pd.isna(profit_b1) or pd.isna(profit_b2):
        pareto_efficient.append("No Deal")
    else:
        theoretical_eff_diff = diff(df_rbai_rbai['role_b1'][i],
                                    df_rbai_rbai['const_b1'][i],
                                    df_rbai_rbai['const_b2'][i])
        actual_diff = abs(profit_b1 - profit_b2)
        pareto_efficient.append(1 if theoretical_eff_diff >= actual_diff else 0)



df_rbai_rbai['pareto_efficient'] = pareto_efficient


# H2
dist = [] 

for i in range(0, len(df_rbai_rbai)):
    if df_rbai_rbai['pareto_efficient'][i] == 'No Deal':
        dist.append(None)
    elif df_rbai_rbai['pareto_efficient'][i] == 0:
        offers = pareto_optimality(df_rbai_rbai['role_b1'][i], df_rbai_rbai['const_b1'][i], df_rbai_rbai['const_b2'][i])
        dev = euclidean_dist(df_rbai_rbai['wholesale_price'][i], df_rbai_rbai['quality'][i], offers)
        
        dist.append(dev)
    else:
        dist.append(0)


df_rbai_rbai['euclidean_deviation'] = dist


# save rbai_rb
#df_rbai_rbai.to_excel("C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/RBAI_RBAI_results.xlsx", sheet_name="Results", index= False)