import altair as alt
from vega_datasets import data
import pandas as pd

covid = pd.read_csv("deaths_simple.csv")
countries = alt.topo_feature(data.world_110m.url, "countries")
ids = pd.read_csv("world-110m-country-names.tsv", sep="\t")

# Add country ID's to the covid dataset to match a country to each geoshape
covid  = covid.merge(ids, left_on="Country", right_on="name")
covid.drop("name", axis=1, inplace=True)
print(covid.shape)
map = alt.Chart(countries).mark_geoshape(
    stroke = "white"
).project(
    "mercator"
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(covid, "id", ["Deaths"])
).encode(
    color="Deaths:Q",
    # color = alt.condition("Deaths:Q", alt.value("lightgray")),
    tooltip="Deaths:Q"
).properties(
    width=800,
    height=600
)

map.show()