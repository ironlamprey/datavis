import altair as alt
from vega_datasets import data
import pandas as pd



countries = alt.topo_feature(data.world_110m.url, "countries")
codes = pd.read_json("country_codes.json")
# Add country ID's to the covid dataset to match a country to each geoshape
deaths_simple = pd.read_csv("deaths_simple.csv")
deaths_simple  = deaths_simple.merge(codes, left_on="Code", right_on="code")
deaths_simple.drop(["name", "code"], axis=1, inplace=True)

background = alt.Chart(countries).mark_geoshape(
    fill="lightgray",
    stroke="white"
).project(
    "mercator"
).properties(
    width=800,
    height=600
)

map = alt.Chart(countries).mark_geoshape(
    stroke = "white"
).project(
    "mercator"
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(deaths_simple, "id", list(deaths_simple.columns))
).encode(
    color="Deaths:Q",
    # color = alt.condition(alt.Predicate(equal="0", field="Deaths:Q"), alt.value("lightgray"), "Deaths:Q"),
    tooltip=[alt.Tooltip("Country", type="nominal"), alt.Tooltip("Deaths", type="quantitative")]
)

chart = background + map
chart.show()