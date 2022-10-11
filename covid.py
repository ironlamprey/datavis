import datetime
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
#TODO: The cases, deaths etc are commulated, if we want separate days this is doable
#TODO: fill out missing dates for countries
def group_covid_by_date_cum(covid):
    covid_total = pd.DataFrame()
    for date_df in covid.groupby("Date"):
        date = date_df[0] 
        print("Date: #" + str(date) + "#")
        #print(date)
        for country_df in date_df[1].groupby("Country"):
            id = country_df[1]["id"].iloc[0]
            country = country_df[0]
            code = country_df[1]["Code"].iloc[0]
            total = country_df[1][["Deaths", "Cases", "Tests"]].sum()
            covid_total = pd.concat([covid_total, pd.DataFrame({"Date": [date], 
                                            "Code": [code], 
                                            "Country": [country], 
                                            "Deaths": total["Deaths"],
                                            "Cases": total["Cases"],
                                            "Tests": total["Tests"],
                                            "id": [id]
                                            })], ignore_index=True)
    covid_total.to_csv("covid_grouped.csv")

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

def map_deaths(countries, covid):

    #Time conversion
    covid["Date"] = covid["Date"].map(lambda x: pd.to_datetime(x).timestamp()*1000)
    #TODO: Altair only allows for smaller dataframes, figure out what to do (later)
    covid = covid.tail(5000)
    first_date = covid["Date"].min()
    last_date = covid["Date"].max()


    slider = alt.binding_range(
        step=24*60*60*1000, #step-size 1 day
        min=first_date, 
        max=last_date)

    #covid = covid.loc[covid["Date"] == covid["Date"].iloc[5000]]
    select_date=alt.selection_single(
        name="slider",
        fields=["Date"],
        bind=slider
    )

    map = alt.Chart(countries).mark_geoshape(
        stroke = "white"
    ).add_selection(
        select_date
    ).transform_filter(
        select_date
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
covid_total = pd.read_csv("covid_grouped.csv")

chart = make_background(countries)
chart += map_deaths(countries, covid_total)
chart.show()