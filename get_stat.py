#!/usr/bin/env python3
"""
IZV project part 1
Author: Karel Norek, xnorek01
"""
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import argparse
import os
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader


def plot_stat(data_source, fig_location=None, show_figure=False):
    """
    Generate figures form given data set

    Arguments:
        data_source     Data source
        fig_location    If set save figure in that location
        show_figure     If set, show figure
    """
    regions = data_source['region']
    reg_dict = {}
    for region in set(regions):
        indx = np.where(data_source['region'] == region)
        none = np.sum(data_source['p24'][indx] == 0)
        yellow = np.sum(data_source['p24'][indx] == 1)
        out_order = np.sum(data_source['p24'][indx] == 2)
        sign = np.sum(data_source['p24'][indx] == 3)
        sign_transport = np.sum(data_source['p24'][indx] == 4)
        rules = np.sum(data_source['p24'][indx] == 5)

        reg_dict[region] = np.array([yellow, out_order, sign, sign_transport, rules, none])

    plot_regions = list(DataDownloader().regions.keys())
    plot_regions.sort()
    plot_yaxis = ['Preřušovana žluta', 'Semafor mimo provoz', 'Dopravními značky', 'Přenosné dopravní značky', 'Nevyznačena', 'Žádná úprava']

    array = np.zeros((14, 6))
    for indx, region in enumerate(plot_regions):
        array[indx] = reg_dict[region]

    relative = 100 * (array / np.sum(array, axis=0))
    relative = np.transpose(relative)
    r_max = relative.max()
    r_min = relative.min()
    relative[relative == 0.0] = np.nan

    array = np.transpose(array)
    array[array == 0] = np.nan

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    im1 = ax1.imshow(array, norm=LogNorm())
    im2 = ax2.imshow(relative, norm=Normalize(r_min, r_max), cmap='plasma')

    cbar1 = fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('Počet nehod')
    ax1.set_xticks(np.arange(len(plot_regions)))
    ax1.set_yticks(np.arange(len(plot_yaxis)))
    ax1.set_xticklabels(plot_regions)
    ax1.set_yticklabels(plot_yaxis)
    ax1.set_title('Absolutně')

    cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label('Podíl nehod pro danou příčinu [%]')
    ax2.set_xticks(np.arange(len(plot_regions)))
    ax2.set_yticks(np.arange(len(plot_yaxis)))
    ax2.set_xticklabels(plot_regions)
    ax2.set_yticklabels(plot_yaxis)
    ax2.set_title('Relativně vůči příčine')

    fig.tight_layout()

    if fig_location:
        path = fig_location.rsplit('/', 1)[0: -1]
        if path != []:
            path = path[0]
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except PermissionError:
                    print('Permission denied while trying to create directories')
        plt.savefig(fig_location)
    if show_figure:
        plt.show()

    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--show_figure', default=False, action='store_true')
    parser.add_argument('--fig_location', type=str)
    args = parser.parse_args()
    data = DataDownloader().get_dict()
    plot_stat(data, args.fig_location, args.show_figure)
