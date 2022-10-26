import altair as alt
from vega_datasets import data
from altair import datum
import pandas as pd
from preprocess import group_covid_by_date_cum
from plotting import *
import math


###  ---------- Main  ---------- ###
#group_covid_by_date_cum(covid)
countries = alt.topo_feature(data.world_110m.url, "countries")
covid_total = pd.read_csv("covid_grouped.csv")

covid_total = covid_total.tail(1000) #Comment out when not testing.
select_date = create_select_date(covid_total)
select_measure = create_select_measure()
chart = make_background(countries)
chart += covid_map(countries, covid_total, select_date, select_measure)
chart = alt.hconcat(chart, barchart(covid_total, select_date, select_measure))
chart.show()
