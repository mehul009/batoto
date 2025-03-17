# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 11:45:13 2024

@author: mehul
"""
import os
import shutil
import time
import re

def sorter (Series1, Series2):
    # Zip Series1 and Series2 to create pairs
    pairs = list(zip(Series1, Series2))

    # Sort the pairs based on the values in Series1
    sorted_pairs = sorted(pairs, key=lambda x: (len(str(x[0])), x[0]))

    # Unzip the sorted pairs back into two separate lists
    sorted_Series1, sorted_Series2 = zip(*sorted_pairs)

    series1 = list(sorted_Series1)
    series2 = list(sorted_Series2)
    
    return series1, series2

# to find which website is used
def manga_web(url):
    web = 0 # 1 = batoto; 2 = kissmanga; 3 = Manga fire; 4 = mangadex; 5 = mangasub; 6= platinum scan, 99 = not supported
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
    elif "platinumscans" in url:
        web = 6
    elif "mangaberri" in url:
        web = 7
    else:
        web = 99
    
    return web

def cap_low(name_text, sym='-', lwr = True, spc_rmv = True):  # this is used to replace space with sym, and lower case of required, it will also remove space from frist and last
    if lwr == True:
        name_text = name_text.lower() # let's make it lower
    else:
        name_text = name_text
    name_text = name_text.replace("\n", '') # let's remove \n
    name_text = name_text.replace("\t", '') # let's remove \t
    name_new = name_text
    
    if spc_rmv == True:
        for i in name_text:  #this for loop will remove all initial and end space if any
            if name_new[0]==' ':
                name_new = name_new[1:len(name_new)]
            elif name_new[len(name_new)-1:len(name_new)] == ' ':
                name_new = name_new[:len(name_new)-1]
            else:
                name_new = name_new
    
    name_new = name_new.replace(" ", sym) # let's repalce spalce with sym
    return name_new

#folder deleter after converted to pdf
def delete_folder(folder_path, retries=3, delay=1):
    # This is to delete all the files at the end
    if os.path.exists(folder_path):
        for attempt in range(retries):
            try:
                shutil.rmtree(folder_path)
                print(f"Folder '{folder_path}' and its contents have been deleted.")
                break
            except PermissionError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
        else:
            print(f"Failed to delete folder '{folder_path}' after {retries} attempts.")
    else:
        print(f"Folder '{folder_path}' does not exist.")
        
#special character remover for path
def replace_special_chars(input_string):
    special_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", ","]
    for char in special_characters:
        input_string = input_string.replace(char, '-')
    return input_string

#function for number adding for easy sorting
def chap_no(chap, name):
    ch_no = re.findall(r'\d+', chap)
    if len(ch_no) != 0:
        if len(ch_no[0])==1:
            return "0" + str(ch_no[0])
        else:
            return str(ch_no[0])
    else:
        ind = name.index(chap)
        cntr = 1 
        if ind==0:
            return "00"
        else:
            while len(re.findall(r'\d+', name[ind-cntr])) > 0:
                cntr = cntr+1 
                if ind-cntr == 0:
                    break
            return str(ind-cntr) + "_" + str(cntr)
        
#link filtering
def filterd_link(links, argument):
    filterd_lnk = []
    #links = list(set(links))  #it removes all duplicates from the list
    for lnk in links:
        if lnk is not None:
            if argument in lnk:
                filterd_lnk.append(lnk)
    
    return filterd_lnk

        