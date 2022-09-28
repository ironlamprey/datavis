// import {addExtendedProjections, extendedProjections} from "@vega/vega-utilities"
// import {legend} from "@d3/color-legend"
// import {concious_analytics} from "ff90685a875a43ac"
import {vl as api} from "@vega/vega-lite-api"
// import {slider} from "@jashkenas/inputs"

async function choroplethData() {
    const [worldTopo, lifeExpectancies, countryCodes] = await Promise.all([
        // we load a topojson file of the world
        d3.json('https://unpkg.com/world-atlas@1/world/110m.json'),
        // and a file containing the life expectancies of all countries
        d3.csv(
            "https://gist.githubusercontent.com/jashkenas/59c7c820265537b941251dabe33a8413/raw/e5dd92dad888a75045fcab80d0077e824d38b178/world-life-expectancy.csv"
        ),
        // as well as a file containing the countries ISO 3166 and alpha-3 codes.
        // We need this last file in order to match the life expectancy data obtained from 
        // the World Bank (using Alpha-3 country codes) with the ISO 3166 country codes
        // found in the world topojson country polygons.
        d3.csv(
            "https://gist.githubusercontent.com/jashkenas/59c7c820265537b941251dabe33a8413/raw/7ccd0d24ef50b3152ce848e7c3f9ce21a0d75af6/country-codes.csv"
        )
    ]);
    // we convert the topojson file to geojson
    const worldGeoJSON = topojson.feature(worldTopo, "countries");

    return worldGeoJSON.features.map(countryFeature => {
        const iso3166Code = countryFeature.id;
        // we try to look up the alpha3 code for the current country
        // in the countryCodes array, if it's not found, we simply ignore it
        const alpha3 = countryCodes.find(
            codes => codes['country-code'] == iso3166Code
        )?.['alpha-3'];
        // Each object in our 'lifeExpectancies' array contains the life expectancies for the different
        // years as properties. Also, it contains a property called 'Country Code', which represents
        // an Alpha-3 country code that we can use to match our GeoJSON country polygons
        // to the life expectancy data in the vega-lite map
        // In our world GeoJSON feature, the countries may only be referenced by their 3-letter
        // country code (this is not the Alpha-3 code!).
        const countryLifeExpData = lifeExpectancies.find(
            country => country['Country Code'] == alpha3
        );
        countryFeature.properties = countryLifeExpData;
        return countryFeature;
    });
}

function myFunction() {
    console.log("wallah i funktionen");
    map = vl
        .markGeoshape({ stroke: 'white' })
        .data(choroplethData())
        .encode(
            vl
                .color({
                    // here we may specify a color for missing data
                    condition: {
                        test: `!datum['properties.${year}']`,
                        value: "lightgrey"
                    }
                })
                .fieldQ(`properties.${year}`)
                // In the scale propery we may define an alternative color scheme (see
                // https://vega.github.io/vega/docs/schemes/ for possible options)
                // or a fixed domain for our variable
                .scale({
                    scheme: 'spectral',
                    domain: [30, 90]
                })
                // we hide the legend in this example,
                // as we produce it externally using the @d3/color-legend
                // plugin in the cell above this map
                .legend(null),
            vl.tooltip([
                {
                    field: 'properties["Country Name"]',
                    type: 'nominal',
                    title: 'Country'
                },
                {
                    field: `properties.${year}`,
                    type: 'quantitative',
                    title: 'Life expectancy'
                }
            ])
        )
        .project(
            vl
                .projection("naturalEarth1")
                .translate([450, 300])
                .rotate(0)
                .scale(200)
        )
        .width(width - 50)
        .height(500)
        .config({
            view: { stroke: null }
        })
        .render()
}