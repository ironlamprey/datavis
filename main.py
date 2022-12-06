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
covid = pd.read_csv("covid_imputed.csv")
#covid = pd.read_csv("covid2.csv")
covid_total = pd.read_csv("covid_grouped2.csv")
covid_monthly = pd.read_csv("covid_monthly.csv")

#Allow small dataset for testing
if args == "-small":
    n = 25000
    covid_total = covid_total.head(n)
    covid = covid.head(n * 10)

select_date = create_select_date(covid_total)
select_measure = create_select_measure()
select_country = create_select_country()

chart = make_background(countries)
chart += covid_map(countries, covid_total, select_date, select_measure, select_country)
chart = alt.vconcat(chart, age_histogram(covid, select_date, select_measure, select_country))
chart = alt.hconcat(chart, barchart(covid_total, select_date, select_measure, select_country))

chart = alt.vconcat(chart, small_multiples(covid_monthly, countries, select_country, select_measure), padding={"left": 50, "top": 550, "right": 5, "bottom": 50})

chart.show()
