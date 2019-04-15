import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("all_data/data-500games-200rounds.csv")
if 'Unnamed: 0' in data.columns:
    data.drop('Unnamed: 0', inplace=True, axis=1)
data.rename({"ME": "Revised MWU", "no_mwu": "No MWU"}, axis=1, inplace=True)
data = data/500
data -= 1000000
ax = data.plot(style=["r-", "b-"])
ax.set_xlabel("Rounds")
ax.set_ylabel("Difference from Original Pot Size")
plt.show()
