import pandas as pd
import matplotlib.pyplot as plt
lrs = ["01", "03", "05"]
styles = [["r-", "b-"],["r--", "b--"], ["r:", "b:"] ]
ax = None
i = 0
for lr in lrs:
    data = pd.read_csv("all_data/data_binary_loss_%s.csv"%(lr))
    if 'Unnamed: 0' in data.columns:
        data.drop('Unnamed: 0', inplace=True, axis=1)
    data.rename({"ME": "MWU 0."+lr[1:], "no_mwu": "No MWU 0." + lr[1:]}, axis=1, inplace=True)
    data = data/1000
    data = data - 1000000
    if not ax:
        ax = data.plot(style=styles[i])
    else:
        data.plot(style=styles[i], ax=ax)
    i += 1

ax.set_xlabel("Rounds")
ax.set_ylabel("Average Pot")
plt.show()
