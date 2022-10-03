import altair as alt
from vega_datasets import data


cars = data.cars()

alt.renderers.enable('altair_viewer')
# chart = alt.Chart(cars).mark_point().encode(
#     x="Miles_per_Gallon",
#     y="Horsepower",
#     color="Cylinders:O"
# ).interactive()

interval = alt.selection_interval()

chart = alt.Chart()
areas = alt.Chart(cars).mark_area(opacity=0.3).encode(
    x=alt.X("Year", timeUnit="year"),
    y=alt.Y("ci0(Miles_per_Gallon)", axis=alt.Axis(title="Miles per Gallon")),
    y2="ci1(Miles_per_Gallon)",
    color=alt.condition(interval, "Origin", alt.value("lightgray"))
).properties(
    width=800
).add_selection(
    interval
)

lines = alt.Chart(cars).mark_line().encode(
    x=alt.X("Year", timeUnit="year"),
    y="mean(Miles_per_Gallon)",
    color="Origin"
).properties(
    width=800
)

chart = areas + lines

chart.show()
