# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:27:55 2024

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
            
    episode_links = soup.find_all('a', class_='visited chapt')
    episode_list = [] 
    
    for link in episode_links:
        ls = link.get_text()
        ls = ls[1:-1]
        episode_list.append(ls)
    
    episode_list.reverse()
        
    return links, episode_list

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
    special_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
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


ImageFile.LOAD_TRUNCATED_IMAGES = True
url = get_user_input("Manga URL","Enter Batoto series link:")  # series directory


links, chap_name = get_links(url) #this will downalod every link from the above url


# to find chapter links
filtered_links = []
for lnk in links:
    if lnk is not None: 
        indices = [i for i, c in enumerate(lnk) if c == "/"]
        if len(indices) == 2:
            substrings = lnk.split("/")
            if substrings[1] == 'chapter':
                filtered_links.append(lnk)
                
filtered_links.sort()  #now we have all the chapter list


path_list = [] # just storage for all the path

loc = select_folder() # folder selector

# let's ask user for how many chapter they want to downlaod
Result = chapter_selector(chap_name)
all_selected = Result[0]
start_chapter = Result[1]
end_chapter = Result[2]

# for all chapter 
if all_selected == False:
    filtered_links = filtered_links[start_chapter:end_chapter+1]
    
#let's get image for the chapter
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
                img.close()
        else:
            # Image download failed, but a blank image with the URL was created
            with Image.open(f"{path}/{image_name}") as img:
                img.save(f"{path}/{image_name}.pdf", 'PDF')
                img.close()
    
        name += 1
        with Image.open(f"{path}/{image_name}") as image:
            image.save(f"{path}/{image_name}.pdf", 'PDF')
            pdf_files.append(f"{path}/{image_name}.pdf")
            image.close()
        
        merger = PdfMerger()
        for file in pdf_files:
            merger.append(file)
    
        with open(f"{loc}/{chap_no(chapter, chap_name)} {replace_special_chars(series)} {replace_special_chars(chapter)}.pdf", 'wb') as f:
            merger.write(f)
        merger.close()
        f.close()
    
#this require some updates
for path in path_list:
    delete_folder(path)
