import pandas as pd
import matplotlib.pyplot as plt
for i in range(3):
    data = pd.read_csv("data_binary_loss_%d.csv"%(i))
    if 'Unnamed: 0' in data.columns:
        data.drop('Unnamed: 0', inplace=True, axis=1)
    data.rename({"ME": "mwu"+str(i), "no_mwu"+str(i): "no mwu"}, axis=1, inplace=True)
    data = data/100
    ax = data.plot(style=["r-", "b-"])
    ax.set_xlabel("Rounds")
    ax.set_ylabel("Average Pot")
plt.show()
