import altair as alt
from vega_datasets import data
from altair import datum
import pandas as pd
from preprocess import group_covid_by_date_cum
from plotting import *
import math

# Let Altair use the whole dataframe
alt.data_transformers.disable_max_rows()

def create_select_date(covid):
    #Time conversion
    covid_copy = covid.copy(deep=True)
    covid_copy["Date"] = covid_copy["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    #remove when not testing
    #covid = covid.head(5000)

    first_date = covid_copy["Date"].min()
    last_date = covid_copy["Date"].max()

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

    return select_date

def make_background(countries):
    background = alt.Chart(countries).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).project(
        "mercator"
    ).properties(
        width=800,
        height=600
    ).transform_filter(
        datum.id != 10
    )
    return background

def covid_map(countries, covid, select_date):

    #Time conversion
    covid_copy = covid.copy(deep=True)
    covid_copy["Date"] = covid_copy["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    # Select parameter
    params = ["Deaths", "Cases", "Tests"]
    param_radio = alt.binding_radio(options=params, name="Measurement: ")
    column_select = alt.selection_single(fields=["Measurement: "],
                                     bind=param_radio,
                                     init={"Measurement: ": 'Deaths'})
    #alt.binding_select(options=params, name='column')
    #color = alt.condition(select_params, )
    
    #Make map
    map = alt.Chart(covid_copy).mark_geoshape(
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

def barchart(covid, select_date):
    covid_copy = covid.copy(deep=True)
    by_date = covid_copy.groupby("Date")
    group = by_date.get_group("2021-08-31")
    return alt.Chart(group).mark_bar().encode(
        x="Deaths",
        y="Country"
    ).properties(
        width=100,
        height=800
    )