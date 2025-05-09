# process rb_llm data
import pandas as pd
from ast import literal_eval

# load data
df = pd.read_csv(r'C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rb_llm\output_processed_rb_llm.csv', encoding='latin1')
df_copy = df.copy()

df_copy = df.copy()

# helper function
def safe_parse(x):
    if isinstance(x, str):
        return literal_eval(x)
    return x

df_copy.iloc[:, 14] = df_copy.iloc[:, 14].apply(safe_parse)

# adjust the offers and offer count
for i in range(len(df_copy)):
    discts = df_copy.iloc[i, 14]

    if not isinstance(discts, list) or len(discts) < 2:
        continue

    last_off = discts[-1]
    llast_off = discts[-2]

    if (
        last_off['price'] == llast_off['price'] and
        last_off['quality'] == llast_off['quality'] and
        last_off['profit_bot1'] == llast_off['profit_bot1'] and
        last_off['profit_bot2'] == llast_off['profit_bot2']
    ):
        print(i)
        df_copy.at[i, df_copy.columns[14]] = discts[:-1]
        df_copy.at[i, df_copy.columns[11]] -= 1

df_copy.to_csv(r'C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rb_llm\output_rb_llm_offers_fixed.csv', index=False, encoding='latin1')