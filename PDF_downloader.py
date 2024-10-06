# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:27:55 2024

@author: mehul
"""

import requests
from bs4 import BeautifulSoup
import re
from PIL import ImageFile

from Selenium_extractor import mangafire, mangadex_chap, mangasub_chap, mangasub_img, platinumscan_chap, platinumscan_img

from beautifulsoup_extracter import html_extract, cap_low, get_links, delete_folder, get_user_input, select_folder, chapter_selector, filterd_link, PDF_maker

from common_function import manga_web

ImageFile.LOAD_TRUNCATED_IMAGES = True #if image are not proper it will just help to carry on

url = get_user_input("Manga URL","Enter link:")  # series directory
    
img_https_list = [] # just storing for img https_list
path_list = []  #just for storing paths

if manga_web(url) == 1: #if it is batoto

    filtered_links, chap_name, series = get_links(url) #this will downalod every link from the above url

    loc = select_folder() # folder selector

    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]

    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]
        
        
    for url_short in filtered_links:
        url_bt = "https://bato.to"+url_short
        response = requests.get(url_bt)
        page_content = response.content
        soup = BeautifulSoup(page_content, "html.parser") #let's make a soup of html page
        script_tags = soup.find_all('script')
        
        # let's find url for img and series and chapter name
        for scrpt in script_tags:
            img_https_match = re.search(r'imgHttps\s*=\s*(\[[^\]]+\])', scrpt.text)
            if img_https_match:
                img_https_value = img_https_match.group(1)
                img_https_list = eval(img_https_value)  # Convert string to list
                
            local_text_sub_match = re.search(r'local_text_sub\s*=\s*(\'[^\']+\')', scrpt.text)
            local_text_epi_match = re.search(r'local_text_epi\s*=\s*(\'[^\']+\')', scrpt.text)
        
            if local_text_sub_match and local_text_epi_match:
                local_text_epi_value = local_text_epi_match.group(1)
                # Remove the surrounding quotes
                chapter = local_text_epi_value[1:-1]
                
        path_list = PDF_maker(loc, series, chapter, path_list, img_https_list, chap_name) #download image and also store path
                
elif manga_web(url) == 2: #if it is kissmanga
    filtered_links, chap_name, series = get_links(url) #this will downalod every link from the above url

    loc = select_folder() # folder selector

    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]

    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]
        
        
    for url_short in filtered_links:
        url_bt = url_short
        response = requests.get(url_bt)
        page_content = response.content
        soup = BeautifulSoup(page_content, "html.parser")
        links = []
        for link in soup.find_all('img','wp-manga-chapter-img'): # find all the links
            src = link.get('src')
            if link:
                links.append(link.get('src'))
        links = filterd_link(links, 'WP-manga/data')
        for lnk in links:
            img_https_list.append(cap_low(lnk,' ', False, False))
            
        chap = html_extract(soup,'li','active')
        chapter = cap_low(chap[0].get_text(), ' ', False, True)
        
        path_list = PDF_maker(loc, series, chapter, path_list, img_https_list, chap_name) #download image and also store path

elif manga_web(url) == 3: #if it is manga fire
    filtered_links, chap_name, series = get_links(url) #this will downalod every link from the above url

    loc = select_folder() # folder selector

    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]

    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]
        
    for url_short in filtered_links:
        img_https_list, chapter = mangafire(url_short)        
        path_list = PDF_maker(loc, series, chapter, path_list, img_https_list, chap_name)

elif manga_web(url) == 4:  #if it is manga dex
    filtered_links, chap_name, series = mangadex_chap(url)   
     # just storage for all the path

    loc = select_folder() # folder selector
    
    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]

    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]

    for lnk in filtered_links:
        img_https_list = []

elif manga_web(url) == 5:  #if it is mangasub
    filtered_links, chap_name, series = mangasub_chap(url)
    
    loc = select_folder() # folder selector
    
    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]
    
    chapter_name = chap_name
    
    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]
        chapter_name = chapter_name[start_chapter:end_chapter+1]
    
    i = 0
    for lnk in filtered_links:
        img_https_list = mangasub_img(lnk)
        path_list = PDF_maker(loc, series, chapter_name[i], path_list, img_https_list, chap_name)
        i = i + 1

elif manga_web(url) == 6: # if if is platinumscans
    filtered_links, chap_name, series = platinumscan_chap(url)
    
    loc = select_folder() # folder selector
    
    # let's ask user for how many chapter they want to downlaod
    Result = chapter_selector(chap_name)
    all_selected = Result[0]
    start_chapter = Result[1]
    end_chapter = Result[2]
    
    chapter_name = chap_name
    
    # for all chapter 
    if all_selected == False:
        filtered_links = filtered_links[start_chapter:end_chapter+1]
        chapter_name = chapter_name[start_chapter:end_chapter+1]
    
    i = 0
    for lnk in filtered_links:
        img_https_list = platinumscan_img(lnk)
        path_list = PDF_maker(loc, series, chapter_name[i], path_list, img_https_list, chap_name)
        i = i + 1


#let's delet trash
for path in path_list:
    delete_folder(path)
