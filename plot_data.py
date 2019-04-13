import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("all_data/data_for_alternative_mwu_final.csv")
if 'Unnamed: 0' in data.columns:
    data.drop('Unnamed: 0', inplace=True, axis=1)
data.rename({"ME": "Initial MWU", "no_mwu": "No MWU"}, axis=1, inplace=True)
data = data/100
ax = data.plot(style=["r-", "b-"])
ax.set_xlabel("Rounds")
ax.set_ylabel("Average Pot")
plt.show()
