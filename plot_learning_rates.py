import pandas as pd
import matplotlib.pyplot as plt
lrs = ["01", "001", "005"]
ax = None
for lr in lrs:
    data = pd.read_csv("all_data/data_learning_rate_%s.csv"%(lr))
    if 'Unnamed: 0' in data.columns:
        data.drop('Unnamed: 0', inplace=True, axis=1)
    data.rename({"ME": "MWU 0."+lr[1:], "no_mwu": "No MWU 0." + lr[1:]}, axis=1, inplace=True)
    data = data/1000
    if not ax:
        ax = data.plot(style=["r-", "b-"])
    else:
        data.plot(style=["r-", "b-"], ax=ax)
ax.set_xlabel("Rounds")
ax.set_ylabel("Average Pot")
plt.show()
