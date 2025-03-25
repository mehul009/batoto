# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 15:54:30 2024

@author: mehul
"""

import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
import time
import urllib.request
import wget
import pycurl

from common_function import manga_web, cap_low, replace_special_chars, chap_no, filterd_link


#Html extractor
def html_extract(soup, main, class_name = None):
    if class_name is None:
        return soup.find_all(main)
    else:
        return soup.find_all(main, class_=class_name)
   
#website extracter
def get_links(url):  
    """
    Extract all links from a webpage
    """
    #decide which manga uploader has been used
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a'): # find all the links
        href = link.get('href')
        if link:
            links.append(link.get('href'))
            
    episode_list = [] 
    
    if manga_web(url) == 1: #if it is batoto
        filtered_links = filterd_link(links, '/chapter/')
        
        episode_links = html_extract(soup, 'a', 'visited chapt') 
        for link in episode_links:
            ls = link.get_text()  # let's get text
            ls = ls[1:-1]
            episode_list.append(ls)
        
        
        name = html_extract(soup,'h3','item-title')
        name_fun = name[0].get_text()
        
        chap_name_final = cap_low(html_extract(soup,'h3')[0].text,sym=' ', lwr=False, spc_rmv=False)
        
        episode_list.reverse()
        filtered_links.reverse()
        
        
    elif manga_web(url) == 2: #if it is kiss manga
        name = html_extract(soup, 'div', 'post-title') # this is series name for kiss manga
        name = name[0].find('h1')
        name_fun = name.text # let's get series name
        name_text = cap_low(name_fun)
        filtered_links = filterd_link(links, name_text+'/'+'chapter-')
        filtered_links.sort()
        
        episode_links = html_extract(soup, 'li', 'wp-manga-chapter')
        for link in episode_links:
            ls_html = html_extract(link, 'a')
            ls = cap_low(ls_html[0].get_text(), ' ', False)  # let's get text
            episode_list.append(ls)
        
        episode_list.reverse()
        
    elif manga_web(url) == 3: #if it is manga fire
        links = []
        name_fun = html_extract(soup,'h1')[0].text  # chapter name
        links_2 = html_extract(soup, 'li', 'item') #it will find only important links
        links_2.reverse()
        for lnk in links_2:
            links.append('https://mangafire.to'+str(lnk.find_all('a')[0].get('href')))
            episode_list.append(lnk.find_all('span')[0].text)
        
        filtered_links = links
        
        chap_name_final = html_extract(soup, 'title')[0].text
        
    elif manga_web(url)==7: #if it is mangaberry
        links = []
        episode_list = []
        filtered_links = []
        series = html_extract(soup,'h1')[0].text
        series = cap_low(series)
        
        chap_links = html_extract(soup, 'a', 'link no-decoration')
        
        for lnk in chap_links:
            if series+'/' in lnk.get('href'):
                filtered_links.append(lnk.get('href'))
                episode_list.append(cap_low(lnk.text))
        
        filtered_links.reverse()
        episode_list.reverse()
        
    
        
    return filtered_links, episode_list, chap_name_final #last variable is series name

#image downloader
def download_image(url, path, image_name):
    # Try downloading with requests
    for attempt in range(3):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            with open(f"{path}/{image_name}", 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # Verify the image integrity
            try:
                img = Image.open(f"{path}/{image_name}")
                img.verify()  # Raises an exception if the image is corrupted
                return True
            except IOError as e:
                print(f"Error verifying image: {e}")
                time.sleep(60)  # Wait for 1 minute before retrying
        except requests.RequestException as e:
            print(f"Error downloading image with requests: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying

    # Try downloading with urllib
    try:
        urllib.request.urlretrieve(url, f"{path}/{image_name}")
        img = Image.open(f"{path}/{image_name}")
        img.verify()  # Raises an exception if the image is corrupted
        return True
    except Exception as e:
        print(f"Error downloading image with urllib: {e}")

    # Try downloading with wget
    try:
        wget.download(url, f"{path}/{image_name}")
        img = Image.open(f"{path}/{image_name}")
        img.verify()  # Raises an exception if the image is corrupted
        return True
    except Exception as e:
        print(f"Error downloading image with wget: {e}")

    # Try downloading with pycurl
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        with open(f"{path}/{image_name}", 'wb') as f:
            c.setopt(pycurl.WRITEFUNCTION, f.write)
            c.perform()
        c.close()
        img = Image.open(f"{path}/{image_name}")
        img.verify()  # Raises an exception if the image is corrupted
        return True
    except Exception as e:
        print(f"Error downloading image with pycurl: {e}")

    # If all else fails, create a blank image with the URL written on it
    img = Image.new('RGB', (400, 200), color = (73, 109, 137))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((10,10), url, font=font)
    img.save(f"{path}/{image_name}")

    return False
  
def PDF_maker(loc, series, chapter, path_list, img_https_list, chap_name): # let's make pdf from images
    path = loc+ '/' + replace_special_chars(series)+' '+ replace_special_chars(chapter)
    path_list.append(path)
    
    #let's make new folder for each chapter
    os.makedirs(path, exist_ok=True)
    
    pdf_files = [] # PDF holder
    name = 1 # image name holder
    
    for image_url in img_https_list:
        image_name = str(name)
        if download_image(image_url, path, image_name):
            # Image downloaded successfully
            with Image.open(f"{path}/{image_name}") as img:
                img.save(f"{path}/{image_name}.pdf", 'PDF')
                #img.close()
        else:
            # Image download failed, but a blank image with the URL was created
            with Image.open(f"{path}/{image_name}") as img:
                img.save(f"{path}/{image_name}.pdf", 'PDF')
                #img.close()
    
        name += 1
        with Image.open(f"{path}/{image_name}") as image:
            image.save(f"{path}/{image_name}.pdf", 'PDF')
            pdf_files.append(f"{path}/{image_name}.pdf")
            #image.close()
        
        merger = PdfMerger()
        for file in pdf_files:
            merger.append(file)
    
        with open(f"{loc}/{chap_no(chapter, chap_name)} {replace_special_chars(series)} {replace_special_chars(chapter)}.pdf", 'wb') as f:
            merger.write(f)
        merger.close()
        f.close()
    return path_list
