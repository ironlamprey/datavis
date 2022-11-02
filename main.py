import altair as alt
from vega_datasets import data
from altair import datum
import pandas as pd
from preprocess import group_covid_by_date_cum
from plotting import *
import sys


###  ---------- Main  ---------- ###

args = ' '.join(sys.argv[1:])
#group_covid_by_date_cum(covid)
countries = alt.topo_feature(data.world_110m.url, "countries")
covid_total = pd.read_csv("covid_grouped2.csv")

#Allow small dataset for testing
if args == "-small":
    covid_total = covid_total.head(10000)

select_date = create_select_date(covid_total)
select_measure = create_select_measure()
chart = make_background(countries)
chart += covid_map(countries, covid_total, select_date, select_measure)
chart = alt.hconcat(chart, barchart(covid_total, select_date, select_measure))
chart.show()
