import altair as alt
from vega_datasets import data

alt.renderers.enable('altair_viewer')

# cars = data.cars()

# # chart = alt.Chart(cars).mark_point().encode(
# #     x="Miles_per_Gallon",
# #     y="Horsepower",
# #     color="Cylinders:O"
# # ).interactive()

# interval = alt.selection_interval()
# multi = alt.selection_multi()

# chart = alt.Chart()
# areas = alt.Chart(cars).mark_area(opacity=0.3).encode(
#     x=alt.X("Year", timeUnit="year"),
#     y=alt.Y("ci0(Miles_per_Gallon)", axis=alt.Axis(title="Miles per Gallon")),
#     y2="ci1(Miles_per_Gallon)",
#     color=alt.condition(interval, "Origin", alt.value("lightgray"))
# ).properties(
#     width=800
# ).add_selection(
#     interval
# )

# lines = alt.Chart(cars).mark_line().encode(
#     x=alt.X("Year", timeUnit="year"),
#     y="mean(Miles_per_Gallon)",
#     color="Origin"
# ).properties(
#     width=800
# )

# chart = areas + lines
# chart.show()

hover = alt.selection_single(on="mouseover", empty="none")
airports = data.airports()

countries = alt.topo_feature(data.world_110m.url, "countries")
states = alt.topo_feature(data.us_10m.url, feature='states')
pop = data.population_engineers_hurricanes()

map = alt.Chart(states).mark_geoshape(
    stroke="white"
).project(
    "albersUsa"
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(pop, "id", list(pop.columns))
).encode(
    color=alt.condition(hover, alt.value("red"), "population:Q"),
    tooltip="state:N"
).properties(
    width=800,
    height=600
).add_selection(
    hover
)

airports = alt.Chart(airports).mark_circle(opacity=0.5).encode(
    longitude="longitude:Q",
    latitude="latitude:Q",
    size=alt.value(5),
    color=alt.value("black")
    # tooltip="name"
).project(
    "albersUsa"
)

chart = map + airports

chart.show()
