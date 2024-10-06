# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 15:54:30 2024

@author: mehul
"""

import requests
from bs4 import BeautifulSoup
import re
import os
from PIL import Image, ImageDraw, ImageFont, ImageFile
from PyPDF2 import PdfMerger
import shutil
from PyQt5.QtWidgets import QApplication, QInputDialog, QFileDialog, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QCheckBox, QListWidget, QComboBox
import sys
import time
import urllib.request
import wget
import pycurl

from Selenium_extractor import mangafire
from common_function import manga_web


#Html extractor
def html_extract(soup, main, class_name = None):
    if class_name is None:
        return soup.find_all(main)
    else:
        return soup.find_all(main, class_=class_name)

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
        filtered_links.sort()
        
        episode_links = html_extract(soup, 'a', 'visited_chapt') 
        for link in episode_links:
            ls = link.get_text()  # let's get text
            ls = ls[1:-1]
            episode_list.append(ls)
        
        episode_list.reverse()
        name = html_extract(soup,'h3','item-title')
        name_fun = name[0].get_text()
        
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
    

    return filtered_links, episode_list, cap_low(replace_special_chars(name_fun), ' ', False, True) #last variable is series name

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

#URL asker
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

#special character remover for path
def replace_special_chars(input_string):
    special_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", ","]
    for char in special_characters:
        input_string = input_string.replace(char, '-')
    return input_string

#output folder selector
def select_folder():
    app = QApplication(sys.argv)
    folder_path = QFileDialog.getExistingDirectory()
    return folder_path

#Chapter selector window start
class ChapterSelectorWindow(QWidget):
    def __init__(self, chapters):
        super().__init__()
        self.chapters = chapters
        self.initUI()
        self.result = None
    def initUI(self):
        self.setWindowTitle('Chapter Selector')
        layout = QVBoxLayout()
        self.all_checkbox = QCheckBox('Include all chapters')
        layout.addWidget(self.all_checkbox)
        self.start_label = QLabel('Start chapter:')
        layout.addWidget(self.start_label)
        self.start_combo = QComboBox()
        self.start_combo.addItems([str(i) for i in self.chapters])
        layout.addWidget(self.start_combo)
        self.end_label = QLabel('End chapter:')
        layout.addWidget(self.end_label)
        self.end_combo = QComboBox()
        self.end_combo.addItems([str(i) for i in self.chapters])
        layout.addWidget(self.end_combo)
        self.selected_chapters_label = QLabel('Selected Chapters:')
        layout.addWidget(self.selected_chapters_label)
        self.selected_chapters_list = QListWidget()
        layout.addWidget(self.selected_chapters_list)
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
    def submit(self):
        all_chapters = self.all_checkbox.isChecked()
        start_chapter = self.start_combo.currentText()
        end_chapter = self.end_combo.currentText()
        self.result = [all_chapters, start_chapter, end_chapter]
        self.close()
def chapter_selector(chapters):
    app = QApplication(sys.argv)
    window = ChapterSelectorWindow(chapters)
    window.show()
    app.exec()        
    return [window.result[0], chapters.index(window.result[1]), chapters.index(window.result[2])]
#Chapter selector window end

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
