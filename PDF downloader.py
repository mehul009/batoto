# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:27:55 2024

@author: mehul
"""

import requests
from bs4 import BeautifulSoup
import re
import os
from PIL import Image
from PyPDF2 import PdfMerger
#from fpdf import FPDF
import shutil
from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QFileDialog
import sys

#website extracter
def get_links(url):  
    """
    Extract all links from a webpage
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if link:
            links.append(link.get('href'))
    return links

#folder deleter after converted to pdf
def delete_folder(folder_path):
    # this is to delet all the files at the end
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' and its contents have been deleted.")
    else:
        print(f"Folder '{folder_path}' does not exist.")

#URl asker
def get_user_input(lbl, lbl2="input"):
    app = QApplication(sys.argv)
    
    # Create a QLineEdit for user input
    input_field = QLineEdit()
    
    # Open a dialog box to get user input
    input_text, ok = QInputDialog.getText(None, lbl, lbl2, QLineEdit.EchoMode.Normal, input_field.text())
    
    if ok:
        # Return the user input
        return input_text
    else:
        # If user cancels, return None
        return None

#special character removar for path
def replace_special_chars(input_string):
    special_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for char in special_characters:
        input_string = input_string.replace(char, '-')
    return input_string

#output folder selector
def select_folder():
    app = QApplication(sys.argv)
    folder_path = QFileDialog.getExistingDirectory()
    return folder_path

url = get_user_input("Manga Url","Enter Batoto series link:") #"https://bato.to/series/137919/the-hole-diary"  # series directory

#we will use pyqt box here to get url in future


links = get_links(url) #this will downalod every link from the above url

# to find chapter links
filtered_links = []
for lnk in links:
    if lnk is not None: 
        indices = [i for i, c in enumerate(lnk) if c == "/"]
        if len(indices) == 2:
            substrings = lnk.split("/")
            if substrings[1] == 'chapter':
                filtered_links.append(lnk)
                
filtered_links.sort()  

#now we have all the chapter list

path_list = [] # just storage for all the path

loc = select_folder()


# for all chapter
for url_short in filtered_links:
    url = "https://bato.to"+url_short
    response = requests.get(url)
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
            local_text_sub_value = local_text_sub_match.group(1)
            local_text_epi_value = local_text_epi_match.group(1)
        
            # Remove the surrounding quotes
            series = local_text_sub_value[1:-1]
            chapter = local_text_epi_value[1:-1]
        
    #simple path
    path = loc+ '/' + replace_special_chars(series)+' '+ replace_special_chars(chapter)
    path_list.append(path)
    
    #let's make new folder for each chapter
    os.makedirs(path, exist_ok=True)
    
    pdf_files = [] # PDF holder
    name = 1 # image name holder
    for image_url in img_https_list:
        response = requests.get(image_url)
        # Check if the request was successful
        if response.status_code == 200:
        # Get the image file name from the URL
            image_name = str(name)
            name = name + 1
        
        # Save the image to the current directory
            with open(f"{path}/{image_name}", "wb") as f:
                f.write(response.content)
                
        image = Image.open(f"{path}/{image_name}")
        image.save(f"{path}/{image_name}"+'.pdf','PDF')
        pdf_files.append(f"{path}/{image_name}"+'.pdf')
        image.close()
        
        merger = PdfMerger()
        for file in pdf_files:
            merger.append(file)
            
        with open(loc+ '/' + replace_special_chars(series)+' '+replace_special_chars(chapter)+'.pdf', 'wb') as f:
            merger.write(f)
    
# this require some updates
for path in path_list:
    delete_folder(path)
