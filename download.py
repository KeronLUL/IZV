#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import requests
import zipfile
import csv
import os
import re
import io
import gzip
import pickle
from bs4 import BeautifulSoup

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    headers_types = [np.str_, np.int8, np.int8, np.datetime64, np.int8, np.str_, np.int8, np.int8, np.int8, np.int8, 
                    np.int8, np.int8, np.int16, np.int8, np.int8, np.int8, np.int16, np.int8, np.int8, np.int32, 
                    np.int8, np.int8, np.int8, np.int8, np.int8, np.int8, np.int8, np.int8, np.int8, np.int8, 
                    np.int8, np.int8, np.int8, np.int8, np.str_, np.int8, np.int8, np.int8, np.int8, np.int8, 
                    np.int8, np.int16, np.int8, np.int8, np.int8, np.float64, np.float64, np.float64, np.float64, 
                    np.float64, np.float64, np.str_, np.str_, np.str_, np.str_, np.str_, np.int32, np.str_, np.str_, 
                    np.str_, np.int32, np.int32, np.str_, np.int8, np.str_]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    cache = {}

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        if self.folder not in os.listdir():
            os.mkdir(self.folder)

    def download_data(self):
        s = requests.session()
        response = s.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find_all('tr')
        
        links = []
        for entry in data:
            button = entry.find_all(class_='btn btn-sm btn-primary')[-1]
            link = re.split('[(\']*[\')]', button['onclick'])[1]
            links.append(self.url + link)
        
        for link in links:
            filename = link.split('/')[-1]
            if filename not in os.listdir(f"./{self.folder}"):
                with open(f"./{self.folder}/{filename}", 'wb') as fp:
                    with requests.get(link, stream = True) as r:
                        for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                            fp.write(chunk)


    def parse_region_data(self, region):
        self.download_data()
        
        archives = []
        for f in os.listdir(f"./{self.folder}"):
            if re.match(r"^.*\.zip", f) is not None:
                archives.append(f)

        array = np.empty((0, 64))
        for archiv in archives:
            with zipfile.ZipFile(f"./{self.folder}/{archiv}", 'r') as zf:
                for file in zf.namelist():
                    if self.regions[region] == file.split('.csv')[0]:
                        with zf.open(file, 'r') as csvfile:
                            reader = csv.reader(io.TextIOWrapper(csvfile, 'cp1250'), delimiter = ';')
                            foo = np.array(list(reader), dtype = 'U23')
                            
                        array = np.concatenate((array, foo))
        array = np.insert(array, 0, region, axis=1)
        array = np.transpose(array)

        letters = ['A:', 'B:', 'D:', 'E:', 'F:', 'G:', 'H:', 'J:']
        for index, arr in enumerate(array):
            for index_in, elem in enumerate(arr):
                tmp = [ext for ext in letters if ext in elem]
                if tmp != []:
                    for letter in tmp:
                        elem = elem.replace(letter, '')
                if ',' in elem:
                    elem = elem.replace(',', '.')
                if elem == '':
                    elem = -1
                arr[index_in] = elem
        result = {self.headers[x] : array[x + 1] for x, value in enumerate(self.headers)}
        result[region] = array[0]

        
        for index, header in enumerate(self.headers):
            if self.headers_types[index] != np.str_:
                try:
                    result[header] = result[header].astype(self.headers_types[index])
                except ValueError:
                    pass
        

        return result

    def get_dict(self, regions=None):
        if regions is None:
            regions = self.regions.keys()
        for region in regions:
            if region in self.cache.keys():
                stats = self.cache[region]
            elif self.cache_filename.format(region) in os.listdir(f"./{self.folder}"):
                with gzip.open(f'./{self.folder}/{self.cache_filename.format(region)}', 'rb') as cache_file:
                    stats = pickle.load(cache_file)
                self.cache[region] = stats
                
            else:
                stats = self.parse_region_data(region)
                with gzip.open(f'./{self.folder}/{self.cache_filename.format(region)}', 'wb') as cache_file:
                    pickle.dump(stats, cache_file)


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == '__main__':
    regions = DataDownloader().regions
    DataDownloader().get_dict()