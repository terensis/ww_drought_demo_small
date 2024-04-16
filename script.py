
import geopandas as gpd
import folium

from folium.plugins import DualMap


def prepare_data(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[gdf['trait_name'] == 'Grain Yield [t/ha]']
    gdf = gdf.rename(columns={'trait_value': 'Grain Yield [t/ha]'})
    gdf['Grain Yield [t/ha]'] = gdf['Grain Yield [t/ha]'].clip(2, 9).round(2)
    return gdf


m = DualMap(
    location=(46.16, 6.02),
    zoom_start=15,
    attr='© Terensis GmbH (2024). Basemap data © CartoDB'
)

folium.TileLayer("cartodbpositron").add_to(m.m1)
folium.TileLayer("cartodbpositron").add_to(m.m2)

# add a custom pane to both maps
pane1 = folium.map.CustomPane('2019', z_index=625)
m.m1.get_root().add_child(pane1)

pane2 = folium.map.CustomPane('2022', z_index=625)
m.m2.get_root().add_child(pane2)

# on the left, we dislay the 2019 data from the cool, wet year
gdf = gpd.read_file("data/grain_yield_2019.geojson")
gdf = prepare_data(gdf)

fill_color = 'Spectral'

# display the grain yield as colorphlet on the map
yield2019 = folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['_uid0_', 'Grain Yield [t/ha]'],
    key_on='feature.properties._uid0_',
    fill_color=fill_color,
    fill_opacity=0.9,
    line_opacity=0.2,
    legend_name='Grain Yield [t/ha]'
)

# add a tooltip to display the value of the grain yield
folium.GeoJsonTooltip(['Grain Yield [t/ha]']).add_to(
    yield2019.geojson)

m.m1.add_child(yield2019)

# on the right, we display the 2022 data from the hot, dry year
gdf = gpd.read_file("data/grain_yield_2022.geojson")
gdf = prepare_data(gdf)

# display the grain yield as colorphlet on the map
yield2022 = folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['_uid0_', 'Grain Yield [t/ha]'],
    key_on='feature.properties._uid0_',
    fill_color=fill_color,
    fill_opacity=0.9,
    line_opacity=0.2,
    legend_name='Grain Yield [t/ha]'
)

# add a tooltip to display the value of the grain yield
folium.GeoJsonTooltip(['Grain Yield [t/ha]']).add_to(
    yield2022.geojson)

# remove the colorbar from the right map
for key in yield2022._children:
    if key.startswith('color_map'):
        branca_color_map = yield2022._children[key]
        del (yield2022._children[key])

m.m2.add_child(yield2022)


fpath = "index.html"
m.save(fpath)

# open the HTML file and add the title box
with open(fpath, 'a') as f:
    f.write("""
    <style>
        .title {
            position: fixed;
            bottom: 40px;
            left: 280px;
            background-color: white;
            padding: 5px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 25px;
            font-weight: bold;
            color: #5a7247;
        }
    </style>
    <div class="title">Grain Yield 2019</div>
    <div class="title" style="left: 60%;">Grain Yield 2022</div>
    """)
