import altair as alt
from vega_datasets import data
import pandas as pd
import math

# Let Altair use the whole dataframe
alt.data_transformers.disable_max_rows()

###  ---------- Data import and cleaning ----------  ###

countries = alt.topo_feature(data.world_110m.url, "countries")
codes = pd.read_json("country_codes.json")

#clean up the covid dataset
covid = pd.read_csv("covid2.csv")
covid = covid.merge(codes, left_on="Code", right_on="code")
covid.drop(["name", "code"], axis=1, inplace=True)


#Make dataframe for countries in the covid dataset
covid_countries = covid[["Country", "Code", "id"]].drop_duplicates()

#Date is date
covid["Date"] = pd.to_datetime(covid["Date"], dayfirst=True)

#Remove TOT from age for easier binning
covid = covid[covid["Age"] != "TOT"]

#Group by date for heatmap
#TODO: The cases, deaths etc are commulated, if we want separate days this is doable
def group_covid_by_date_cum(covid):
    last_seen_deaths = {}
    last_seen_cases = {}
    last_seen_tests = {}

    covid_total = pd.DataFrame()
    for date_df in covid.groupby("Date"):
        date = date_df[0] 
        print("Date: #" + str(date) + "#")
        #print(date)
        for index, row in covid_countries.iterrows():
            #if (pd.isna(code)):
            #    continue
            id = row["id"]
            country = row["Country"]
            code = row["Code"]
            country_df = date_df[1].loc[date_df[1]["Code"]==code]
            
            if (country_df.shape[0] != 0): #TODO: fix USA's holes in the data where its 0
                # total = country_df[["Deaths", "Cases", "Tests"]].sum()
                deaths = country_df["Deaths"].sum()
                cases = country_df["Cases"].sum()
                tests = country_df["Tests"].sum()

                last_seen_deaths = update_last_seen_dictionary(last_seen_deaths, code, deaths)
                last_seen_cases = update_last_seen_dictionary(last_seen_cases, code, cases)
                last_seen_tests = update_last_seen_dictionary(last_seen_tests, code, tests)

            covid_total = pd.concat([covid_total, pd.DataFrame({"Date": [date], 
                                            "Code": [code], 
                                            "Country": [country], 
                                            "Deaths": get_element_from_last_seen_dictionary(last_seen_deaths, code),
                                            "Cases": get_element_from_last_seen_dictionary(last_seen_cases, code),
                                            "Tests": get_element_from_last_seen_dictionary(last_seen_tests, code),
                                            "id": [id]
                                            })], ignore_index=True)
    covid_total.to_csv("covid_grouped.csv")

def update_last_seen_dictionary(dict, key, value):
    if(not math.isnan(value)):
        dict[key] = value
         
    return dict

def get_element_from_last_seen_dictionary(dict, key):
    if (not key in dict):
        #print(value)
        return 0
    else:
        return dict[key]

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

def covid_map(countries, covid, arg="Deaths"):

    #Time conversion
    covid["Date"] = covid["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    #remove when not testing
    #covid = covid.head(5000)

    first_date = covid["Date"].min()
    last_date = covid["Date"].max()

    #Make slider
    #TODO: see if we can label with dates, not timestamp
    slider = alt.binding_range(
        step=24*60*60*1000, #step-size 1 day
        min=first_date, 
        max=last_date
    )

    #Selection by slider
    select_date=alt.selection_single(
        name="slider",
        fields=["Date"],
        bind=slider
    )
    
    # Select parameter
    params = ["Deaths", "Cases"]
    param_radio = alt.binding_radio(options=params, name="Measurement: ")
    column_select = alt.selection_single(fields=["Measurement: "],
                                     bind=param_radio,
                                     init={"Measurement: ": 'Deaths'})
    #alt.binding_select(options=params, name='column')
    #color = alt.condition(select_params, )
    
    #Make map
    map = alt.Chart(covid).mark_geoshape(
        stroke = "white"
    ).add_selection(
        select_date
    ).transform_filter(
        select_date
    ).project(
        "mercator"
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(countries, "id", fields=["type", "properties", "geometry"])
    ).transform_fold(
        fold=params,
        as_=["Measurement: ", 'value']
    ).transform_filter(
        column_select
    ).encode(
        color="value:Q",
        tooltip=[alt.Tooltip("Country", type="nominal"), alt.Tooltip("value:N", type="quantitative")]
    ).add_selection(
        column_select
    )
    return map

###  ---------- Main  ---------- ###
#group_covid_by_date_cum(covid)
covid_total = pd.read_csv("covid_grouped.csv")

#covid_total = covid_total.tail(1000) #Comment out when not testing.

chart = make_background(countries)
chart += covid_map(countries, covid_total, arg="Deaths")
chart.show()
