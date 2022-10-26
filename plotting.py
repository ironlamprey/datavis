import altair as alt
from vega_datasets import data
from altair import datum
import pandas as pd
from preprocess import group_covid_by_date_cum
from plotting import *
import math

PLOT_HEIGHT = 550
PLOT_WIDTH = 800

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

def create_select_measure():
    measure = ["Deaths", "Cases", "Tests"]
    measure_radio = alt.binding_radio(options=measure, name="Measurement: ")
    select_measure = alt.selection_single(fields=["Measurement: "],
                                     bind=measure_radio,
                                     init={"Measurement: ": 'Deaths'})
    return select_measure

def make_background(countries):
    background = alt.Chart(countries).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).project(
        "mercator"
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    ).transform_filter(
        datum.id != 10
    )
    return background

def covid_map(countries, covid, select_date, select_measure):

    #Time conversion
    covid_copy = covid.copy(deep=True)
    covid_copy["Date"] = covid_copy["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    # Select parameter
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
        fold=["Deaths", "Cases", "Tests"],
        as_=["Measurement: ", 'value']
    ).transform_filter(
        select_measure
    ).encode(
        color="value:Q",
        tooltip=[alt.Tooltip("Country", type="nominal"), alt.Tooltip("value:N", type="quantitative")]
    ).add_selection(
        select_measure
    )
    return map

def barchart(covid, select_date, select_measure):
    covid_copy = covid.copy(deep=True)
    covid_copy["Date"] = covid_copy["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    #Make radio button for sorting - couldnt fucking make it work
    #sort_radio = alt.binding_radio(options=["Country", "-x"], name="Barchart ordering: ")
    #select_sort = alt.selection_single(fields=["Barchart ordering: "], bind=sort_radio)
    #sort_param = alt.Parameter(name="Barchart ordering: ", bind=sort_radio, value="-x")
    #y = alt.Y("Country", sort=[select_sort.expr])
    # y = alt.condition(select_sort, "Country", alt.Y("Country", sort="-x"))
    y = alt.Y("Country", sort="-x")

    return alt.Chart(covid_copy).mark_bar().encode(
        x="value:Q",
        y=y,
        tooltip=[alt.Tooltip("value:Q", type="quantitative")]
    ).add_selection(
        select_date
    ).transform_filter(
        select_date
    ).transform_fold(
        fold=["Deaths", "Cases", "Tests"],
        as_=["Measurement: ", 'value']
    ).transform_filter(
        select_measure
    ).transform_filter(
        datum.value != 0
    ).properties(
        width=PLOT_WIDTH//8,
        height=PLOT_HEIGHT
    )