import altair as alt
from vega_datasets import data
import pandas as pd

###  ---------- Data import and cleaning ----------  ###

countries = alt.topo_feature(data.world_110m.url, "countries")
codes = pd.read_json("country_codes.json")

#clean up the covid dataset
covid = pd.read_csv("covid2.csv")
covid = covid.merge(codes, left_on="Code", right_on="code")
covid.drop(["name", "code"], axis=1, inplace=True)

#Date is date
covid["Date"] = pd.to_datetime(covid["Date"])

#Remove TOT from age for easier binning
covid = covid[covid["Age"] != "TOT"]

#Group by date for heatmap
#TODO: Not sure this is necessary right now
for date_df in covid.groupby("Date"):
    date = date_df[0] 
    #print(date)
    for country_df in date_df[1].groupby("Country"):
        country = country_df[0]
        #print(country_df[1].sum())


### ---------- Functions for plotting ---------- ###

def make_background(countries):
    background = alt.Chart(countries).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).project(
        "mercator"
    ).properties(
        width=800,
        height=600
    )
    return background


def map(countries, covid):
    map = alt.Chart(countries).mark_geoshape(
        stroke = "white"
    ).project(
        "mercator"
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(covid, "id", list(covid.columns))
    ).encode(
        color="Deaths:Q",
        tooltip=[alt.Tooltip("Country", type="nominal"), alt.Tooltip("Deaths", type="quantitative")]
    )
    return map


###  ---------- Main  ---------- ###
chart = make_background(countries) #+ map(countries, covid)
chart.show()