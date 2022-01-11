#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import math

road_types = {
    0: "Žádná z uvedených",
    1: "Dvoupruhová",
    2: "Třípruhová",
    3: "Čtyřpruhová",
    5: "Vícepruhová",
    6: "Rychlostní komunikace"
}


def get_df():
    """
    Read data
    """
    df = pd.read_pickle("accidents.pkl.gz")
    return df


def get_police_df(df: pd.DataFrame, columns: list):
    """
    Get police data

    Arguments:
        df - dataframe with data
        columns - wanted columns
    """
    df[df['p48a'] == 13] == 12
    df = df[df['p48a'] == 12]
    df = df[columns]
    return df


def print_police_stats(df: pd.DataFrame):
    """
    Print police statistics

    Arguments:
        df - dataframe with data
    """
    df = get_police_df(df, ['region'])
    print(f"Total number of police accidents: {df.shape[0]}")

    df['tmp'] = 1
    df = df.groupby(['region']).agg('sum').reset_index()
    df = df.sort_values(by='tmp').reset_index()
    print(f"Lowest number of accidents involving police: {df.iloc[0]['tmp']} in region {df.iloc[0]['region']}")
    print(f"Highest number of accidents involving police: {df.iloc[-1]['tmp']} in region {df.iloc[-1]['region']}")
    print(f"Mean: {math.ceil(df['tmp'].mean())}")


def print_table(df: pd.DataFrame):
    """
    Print LaTeX table with police data

    Arguments:
        df - dataframe with data
    """
    df = get_police_df(df, ['p2a', 'p21'])
    df['p2a'] = pd.to_datetime(df['p2a'])
    df.loc[df['p21'] == 4, 'p21'] = 3
    df['p21'] = df['p21'].map(road_types)
    df['tmp'] = 1

    df.rename(columns={'p2a': 'Rok', 'p21': 'Druh komunikace'}, inplace=True)

    df = df.pivot_table(columns='Druh komunikace', values='tmp', aggfunc='sum',
                        index=['Rok']).reset_index()
    df = df.fillna(0)
    df = df.resample('Y', on='Rok').sum().reset_index()
    df['Rok'] = df['Rok'].dt.year
    df = df.set_index('Rok')
    print(f"\nLatex table:\n{df.to_latex()}")


def police_plot(df: pd.DataFrame, fig_location: str = None):
    """
    Plot number of accidents involving the police

    Arguments:
        df - dataframe with data
        fig_location - plot location
    """
    df = get_police_df(df, ['region'])
    df['tmp'] = 1
    df = df.groupby(['region']).agg('sum').reset_index()

    sns.set_style('darkgrid')

    ax = sns.barplot(x='region', y='tmp', data=df, palette='rocket')
    ax.set_title('Počet nehod, kterých byla součástí policie v jednotlivých krajích', weight='bold')
    ax.set(xlabel='Kraj', ylabel='Počet nehod')
    for c in ax.containers:
        labels = [f'{v.get_height():.0f}' for v in c]
        ax.bar_label(c, labels=labels, label_type='edge', weight='bold')

    if fig_location:
        plt.savefig(fig_location)


if __name__ == "__main__":
    df = get_df()
    print_police_stats(df)
    print_table(df)
    police_plot(df, 'fig.png')
