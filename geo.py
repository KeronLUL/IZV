#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np


def get_year(gdf: geopandas.GeoDataFrame, year):
    """
    Get data for specified year

    Arugments:
        gdf - dataframe with data
        year - year for data extraction
    """
    gdf = gdf[(gdf['p2a'] >= pd.to_datetime(f'{year}-1-1'))
              & (gdf['p2a'] <= pd.to_datetime(f'{year}-12-31'))]
    return gdf


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """
    Convert DataFrame to GeoDataFrame

    Arguments:
        df - DataFrame to be converted
    """
    df['p2a'] = pd.to_datetime(df['p2a'])
    df = df.dropna(subset=['d', 'e'])
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df['d'], df['e']),
                                 crs="EPSG:5514")
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """
    Plot graph for each year with location of accident on highway
    or first class road

    Arguments:
        gdf - GeoDataFrame with data
        fig_location - where to store graphs
        show_figure - whether to show plot or not
    """
    gdf = gdf[gdf['region'].isin(['JHM'])].to_crs(epsg=3857)

    y_2018 = get_year(gdf, 2018)
    y_2019 = get_year(gdf, 2019)
    y_2020 = get_year(gdf, 2020)

    fig, ax = plt.subplots(3, 2, figsize=(12, 15), sharex=True, sharey=True)
    fig.suptitle('Nehody v JHM kraji na dálnici a na silnicích 1. třídy v jednotlivých letech', fontsize=20)

    d1 = y_2018[y_2018['p36'] == 0].plot(ax=ax[0][0], markersize=4, label="Dálnice", color='tab:green')
    d1.set_title('JHM: dálnice (2018)')
    s1 = y_2018[y_2018['p36'] == 1].plot(ax=ax[0][1], markersize=4, label="Silnice 1. třídy", color='tab:red')
    s1.set_title('JHM: silnice 1. třídy (2018)')
    d2 = y_2019[y_2019['p36'] == 0].plot(ax=ax[1][0], markersize=4, label="Dálnice", color='tab:green')
    d2.set_title('JHM: dálnice (2019)')
    s2 = y_2019[y_2019['p36'] == 1].plot(ax=ax[1][1], markersize=4, label="Silnice 1. třídy", color='tab:red')
    s2.set_title('JHM: silnice 1. třídy (2019)')
    d3 = y_2020[y_2020['p36'] == 0].plot(ax=ax[2][0], markersize=4, label="Dálnice", color='tab:green')
    d3.set_title('JHM: dálnice (2020)')
    s3 = y_2020[y_2020['p36'] == 1].plot(ax=ax[2][1], markersize=4, label="Silnice 1. třídy", color='tab:red')
    s3.set_title('JHM: silnice 1. třídy (2020)')

    for ax in ax.ravel():
        ctx.add_basemap(ax, crs=gdf.crs.to_string(),
                        source=ctx.providers.Stamen.TonerLite)
        ax.set_axis_off()

    if fig_location:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """
    Plot graph with location of accidents on highway in clusters

    Arguments:
        gdf - GeoDataFrame with data
        fig_location - where to store graphs
        show_figure - whether to show plot or not
    """
    gdf = gdf[gdf['region'].isin(['JHM'])]
    gdf = gdf[gdf['p36'] == 1]

    gdf_c = gdf.copy()
    gdf_c = gdf_c.set_geometry(gdf_c.centroid).to_crs(epsg=3857)
    coords = np.dstack([gdf_c.geometry.x, gdf_c.geometry.y]).reshape(-1, 2)

    db = sklearn.cluster.MiniBatchKMeans(n_clusters=25).fit(coords)
    gdf_plot = gdf_c.copy()
    gdf_plot["cluster"] = db.labels_
    gdf_plot = gdf_plot.dissolve(by="cluster", aggfunc={"p1": "count"}
                                 ).rename(columns=dict(p1="count"))

    plt.figure(figsize=(10, 10))
    plt.suptitle('Nehody v Jihomoravském kraji na silnicích 1. třídy')
    ax = plt.gca()

    gdf_plot.plot(ax=ax, markersize=8, column="count", legend=True, alpha=0.6,
                  legend_kwds={'location': 'bottom',
                               'label': 'Počet nehod v úseku', 'pad': 0.01})
    ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.Stamen.TonerLite)

    ax.set_aspect("auto")
    plt.axis("off")
    plt.tight_layout()

    if fig_location:
        plt.savefig(fig_location, bbox_inches='tight')

    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", False)
    plot_cluster(gdf, "geo2.png", False)
