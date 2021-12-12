#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu
# predstavenou na prednaskach dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat.
Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz
    pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů.
    Měli byste se dostat po 0.5 GB. Neměňte však na kategorický
    typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost
    všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B.
"""
road_types = {
    0: "Žádná z uvedených",
    1: "Dvoupruhová",
    2: "Třípruhová",
    3: "Čtyřpruhová",
    5: "Vícepruhová",
    6: "Rychlostní komunikace"
}

fault = {
    0: "Jiné",
    1: "Řidičem",
    2: "Řidičem",
    3: "Jiné",
    4: "Zvěří",
    5: "Jiné",
    6: "Jiné",
    7: "Jiné",
}

weather = {
    1: "Nestížené",
    2: "Mlha",
    3: "Na počátku deště",
    4: "Déšť",
    5: "Sněžení",
    6: "Náledí",
    7: "Nárazový vítr"
}

regions = ['JHC', 'JHM', 'HKK', 'KVK']


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """
    Get dataframe from file and convert types to category with some exeptions

    Arguments:
        filename - name of file with data
        verbose - print size of data in MB before and after type conversion

    Return:
        Function return converted dataframe
    """
    df = pd.read_pickle(filename)
    if verbose:
        print(f"orig_size={df.memory_usage(deep=True).sum() / 1048576:.1f} MB")

    for column in df:
        if df[column].dtype == 'int64':
            df[column] = pd.to_numeric(df[column], downcast='signed')
        elif df[column].dtype == 'float64':
            df[column] = pd.to_numeric(df[column], downcast='float')
        elif column != 'region' and column != 'p2a':
            df[column] = df[column].astype('category')

    df['p2a'] = pd.to_datetime(df['p2a'])
    df['date'] = df['p2a'].copy()

    if verbose:
        print(f"new_size={df.memory_usage(deep=True).sum() / 1048576:.1f} MB")

    return df


# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic
def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    """
    Plot number of accidents on different road types

    Arguments:
        df - dataframe with data
        fig_location - if specified, store graph in given location
        show_figure - show figure if True
    """
    df_type = df[df['region'].isin(
                regions)][['region', 'p21']]
    df_type['tmp'] = 1
    df_type.loc[df_type['p21'] == 4, 'p21'] = 3
    df_type = df_type.groupby(['region', 'p21']).agg('sum').reset_index()
    df_type = df_type.sort_values(by=['p21'])
    df_type['p21'] = df_type['p21'].map(road_types)

    sns.set_style("darkgrid")
    sns.set_palette("rocket")

    g = sns.catplot(x="region", y="tmp", data=df_type, col="p21", kind="bar",
                    col_wrap=3, height=3.5, aspect=1, ci=None, sharex=False,
                    sharey=False, order=regions)
    (g.set_titles("{col_name}")
        .set_axis_labels("Kraj", "Počet nehod")
        .fig.suptitle('Druh komunikace', weight="bold"))

    for ax in g.axes.ravel():
        for c in ax.containers:
            labels = [f'{v.get_height():.0f}' for v in c]
            ax.bar_label(c, labels=labels, label_type='edge', weight="bold")
        ax.margins(y=0.1)

    g.tight_layout()

    if fig_location:
        plt.savefig(fig_location, bbox_inches='tight')

    if show_figure:
        plt.show()


# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """
    Plot number of accidents including wildlife or domestic animals

    Arguments:
        df - dataframe with data
        fig_location - if specified, store graph in given location
        show_figure - show figure if True
    """
    df_animals = df[df['p58'] == 5]
    df_animals = df_animals[df_animals['region'].isin(
                    regions)][['region', 'p10', 'date']]
    df_animals = df_animals[
                (df_animals['date'] >= pd.to_datetime('2016-1-1'))
                & (df_animals['date'] <= pd.to_datetime('2020-12-31'))]

    df_animals['p10'] = df_animals['p10'].map(fault)
    df_animals['date'] = df_animals['date'].dt.month
    df_animals['tmp'] = 1
    df_animals = df_animals.groupby(
                ['region', 'date', 'p10']).agg('sum').reset_index()

    sns.set_palette(["#52006A", "#FF7600", "#CD113B"])
    g = sns.catplot(x="date", y='tmp', data=df_animals, col="region",
                    kind="bar", col_wrap=2, height=3, aspect=1.5,
                    ci=None, hue="p10", sharex=False, sharey=False)
    (g.set_titles("Kraj: {col_name}")
        .set_axis_labels("Měsíc", "Počet nehod")
        .fig.suptitle('Zavinění nehod', weight="bold"))
    g._legend.set_title("Zavinění")
    g.tight_layout()

    if fig_location:
        plt.savefig(fig_location, bbox_inches='tight')

    if show_figure:
        plt.show()


# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    """
    Plot number of accidents in different weather conditions

    Arguments:
        df - dataframe with data
        fig_location - if specified, store graph in given location
        show_figure - show figure if True
    """
    df_w = df[df['region'].isin(
            regions)][['region', 'p18', 'date']]
    df_w = df_w[
            (df_w['date'] >= pd.to_datetime('2016-1-1'))
            & (df_w['date'] <= pd.to_datetime('2020-12-31'))]

    df_w = df_w[df_w['p18'] != 0]
    df_w['p18'] = df_w['p18'].map(weather)
    df_w['tmp'] = 1
    df_w = df_w.pivot_table(columns='p18', values='tmp', aggfunc='sum',
                            index=['date', 'region']).reset_index()
    df_w = df_w.fillna(0)
    df_w = (df_w.groupby(['region']).resample('M', on='date').sum().
            reset_index())
    df_w = df_w.melt(id_vars=["region", 'date'],
                     var_name="p18", value_name="value")

    sns.set_palette("bright")
    g = sns.relplot(data=df_w, kind="line", x="date", y='value', hue='p18',
                    col='region', col_wrap=2, height=3, aspect=1.5,
                    facet_kws={'sharey': False, 'sharex': False})

    (g.set_titles("Kraj: {col_name}")
        .set_axis_labels("Rok", "Počet nehod")
        .fig.suptitle('Povětrnostní podmínky', weight="bold"))
    g._legend.set_title("Podmínky")

    date_form = DateFormatter("%m/%y")
    for ax in g.axes.flatten():
        ax.xaxis.set_major_formatter(date_form)

    g.tight_layout()
    if fig_location:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=False)
    plot_animals(df, "02_animals.png", False)
    plot_conditions(df, "03_conditions.png", False)
