from itertools import count
import pandas as pd
import matplotlib.pyplot as plt

cov = pd.read_csv("covid.csv")
#print(cov.head(20))
res = cov.loc[cov["Age"] == "TOT"]
res = res.loc[res["Measure"]=="Deaths"]
res = res[["Country", "Value", "Date"]]
#print(res.loc[res["Country"] == "Denmark"])
deaths = [[], []]
for country in res.groupby("Country"):
    deaths[0].append(country[0])
    deaths[1].append(country[1].iloc[-1, country[1].columns.get_loc("Value")])
df = pd.DataFrame({"Country": deaths[0], "Deaths": deaths[1]})
print(df.head())
df.to_csv("deaths_simple.csv")