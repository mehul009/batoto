# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 11:45:13 2024

@author: mehul
"""

def sorter (Series1, Series2):
    # Zip Series1 and Series2 to create pairs
    pairs = list(zip(Series1, Series2))

    # Sort the pairs based on the values in Series1
    sorted_pairs = sorted(pairs, key=lambda x: x[0])

    # Unzip the sorted pairs back into two separate lists
    sorted_Series1, sorted_Series2 = zip(*sorted_pairs)

    series1 = list(sorted_Series1)
    series2 = list(sorted_Series2)
    
    return series1, series2

# to find which website is used
def manga_web(url):
    web = 0 # 1 = batoto; 2 = kissmanga; 3 = Manga fire; 4 = mangadex; 5 = mangasub; 99 = not supported
    if "bato" in url:
        web = 1 
    elif "kissmanga" in url:
        web = 2
    elif "mangafire" in url:
        web = 3
    elif "mangadex" in url:
        web = 4
    elif "mangasub" in url:
        web = 5
    else:
        web = 99
    
    return web