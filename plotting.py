import altair as alt
from vega_datasets import data
from altair import datum
import pandas as pd
from preprocess import group_covid_by_date_cum
from plotting import *
from datetime import datetime
import math

PLOT_HEIGHT = 750
PLOT_WIDTH = 950

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
    slider = alt.binding_range(
        step=24*60*60*1000, #step-size 1 day
        min=first_date, 
        max=last_date
    )

    #Selection by slider
    select_date=alt.selection_single(
        name="slider",
        fields=["Date"],
        bind=slider,
        # Date Denmark closed down is init
        init={"Date": 1583884800000}
    )

    return select_date

def create_select_measure():
    measure = ["Deaths", "Cases"]
    measure_radio = alt.binding_radio(options=measure, name="Measurement: ")
    select_measure = alt.selection_single(fields=["Measurement: "],
                                     bind=measure_radio,
                                     init={"Measurement: ": 'Deaths'})
    return select_measure

def create_select_country():
    return alt.selection(type="multi", fields=["Country"], init = [{"Country": "Denmark"}], empty="none")

def make_background(countries, width=PLOT_WIDTH, height=PLOT_HEIGHT):
    background = alt.Chart(countries).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).project(
        "mercator"
    ).properties(
        width=width,
        height=height
    ).transform_filter(
        #Remove Antarctica
        datum.id != 10
    )
    return background

def covid_map(countries, covid, select_date, select_measure, select_country):

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
        color = alt.condition(select_country, alt.ColorValue("red"), "value:Q"),
        tooltip=[alt.Tooltip("Country", type="nominal"), 
                    alt.Tooltip("value:N", type="quantitative"),
                    alt.Tooltip("Date", type="temporal")]
        # text = alt.Text("Date", type="temporal")
    ).add_selection(
        select_measure
    ).add_selection(
        select_country
    )

    text = alt.Chart(covid_copy).mark_text(
        dx = 0, dy = 250
    ).transform_filter(
        select_date
    ).encode(
        text = alt.Text("Date", type="temporal")
    )


    return map + text

def barchart(covid, select_date, select_measure, select_country):
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
        #TODO: play around with logscale
        x=alt.X("value:Q", scale=alt.Scale(type="log")),
        #x="value:Q",
        y=y,
        # color = alt.condition(select_country, alt.ColorValue("red"), alt.ColorValue("steelblue")),
        color = alt.condition(select_country, alt.ColorValue("red"), alt.ColorValue("steelblue")),
        tooltip=[alt.Tooltip("value:Q", type="quantitative")]
    ).add_selection(
        select_date
    ).transform_filter(
        select_date
    ).transform_fold(
        fold=["Deaths", "Cases"],
        as_=["Measurement: ", 'value']
    ).transform_filter(
        select_measure
    ).transform_filter(
        datum.value != 0
    ).properties(
        width=PLOT_WIDTH//4,
        height=PLOT_HEIGHT
    ).add_selection(
        select_country
    )

def age_histogram(covid, select_date, select_measure, select_country):
    covid_copy = covid.copy(deep=True)
    covid_copy["Date"] = covid_copy["Date"].map(lambda x: pd.to_datetime(x, dayfirst=True).timestamp()*1000)

    return alt.Chart(covid_copy).mark_bar().encode(
        x=alt.X("Country:N", title=""),
        y="value:Q",
        color="Country:N",
        column=alt.Column("Age:O", spacing=0, title="Age"),
        tooltip=[alt.Tooltip("Country:N", type="nominal"), 
                    alt.Tooltip("value:N", type="quantitative"),
                    alt.Tooltip("Date", type="temporal")]
    ).add_selection(
        select_date
    ).transform_filter(
        select_date
    ).transform_fold(
        fold=["Deaths", "Cases"],
        as_=["Measurement: ", 'value']
    ).transform_filter(
        select_measure
    ).transform_filter(
        select_country
    ).properties(
        width=50,
        height = 200
    )

def small_multiples(covid_monthly, countries, select_country, select_measure):
    background = make_background(countries, height=150, width=150)
    chart = alt.concat(*(background + alt.Chart(covid_monthly.loc[covid_monthly["Date"] == month]).mark_geoshape(
                stroke = "white"
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
                color = alt.condition(select_country, alt.ColorValue("red"), "value:Q")#, scale=alt.Scale(domain=[0, covid_monthly.loc[covid_monthly["Date"] == month]["Cases"].max()])))
            ).add_selection(
                select_measure
            ).add_selection(
                select_country
            ).properties(
                height=150,
                width=150,
                title=month
            )
        for month in covid_monthly["Date"].unique()
        ), columns=12
    ).resolve_scale(color='independent')

    return chart