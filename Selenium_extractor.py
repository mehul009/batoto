# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 19:23:36 2024

@author: mehul
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from common_function import sorter


def load_firefox(url):
    # Set the path to the GeckoDriver executable and we will use firefox
    current_path = os.getcwd()
    gecko_driver_path = current_path+'/sub_file/Web_driver/geckodriver.exe'
    firefox_binary_path = current_path+ '/sub_file/FirefoxPortable/App/Firefox64/firefox.exe'
    
    # Create a Firefox WebDriver instance
    options = Options()
    options.add_argument("-headless") # it will hide firefox, so no longer distraction
    options.binary_location = firefox_binary_path
    
    
    # Create a Firefox profile
    profile = FirefoxProfile()
    
    # Path to the add-ons (.xpi files)
    addon_paths = [current_path+ '/sub_file/FirefoxPortable/ublock.xpi'] # let's remove annoying adds from the page
    
    service = Service(executable_path=gecko_driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    driver.get(url)  # Replace with your target URL
    
    # Install each add-on
    for addon_path in addon_paths:  # let's insall ad remove addon
        driver.install_addon(addon_path, temporary=True)
    
    time.sleep(2) # let's wait till it install addons
    driver.refresh() # let's referesh so addon can works
    time.sleep(10) # let's wait till it for basic page loading
    
    return driver
    

def mangafire (url):
    
    driver = load_firefox(url)
    
    
    # Extract the total number of pages
    total_pages_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'html body.read.ctrl-menu-active div.wrapper header div.inner.px-3 div.component div.viewing.mr-3.page-toggler span b.total-page'))
    )
        
    total_pages = int(total_pages_element.text)
    
    #click on the chapter toggler to find the name of chapter
    chap_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div[2]/nav[1]/button[2]')))
    chap_button.click()
    
    chap_name = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'html body.read.ctrl-menu-active div.wrapper main.longstrip div.m-content div#number-panel.sub-panel.scroll-sm.active ul li a.active'))
    )
    

    chapter = chap_name.text # we have chapter name with us

    
    # Click the "Next" button (total_pages - 1) times, it will load all the image on page 
    next_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="page-go-right"]'))
    )
    
    for _ in range(total_pages - 1):
        next_button.click()
        time.sleep(1)  # Wait for the page to load
    
    
    # Wait for the images to be loaded
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.img.loaded img'))
    )
    
    # Locate all image elements
    image_elements = driver.find_elements(By.CSS_SELECTOR, 'div.img.loaded img')
    
    
    img_links = []
    # save links of all image
    for index, image_element in enumerate(image_elements):
        image_url = image_element.get_attribute('src')
        img_links.append(image_url)    
    # Close the browser
    driver.quit()
    
    return img_links, chapter


def mangadex_chap(url):
    
    driver = load_firefox(url) # let's load url in fire fox
    
    chap_name = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'p.mb-1'))
    )
    series = chap_name.text
    
    chap_links = []
    chap_name = []
    
    elements = driver.find_elements(By.CSS_SELECTOR, '.chapter-grid.flex-grow')
    
    for element in elements:
        # Find the <img> tag inside the element
        img_element = element.find_element(By.CSS_SELECTOR, 'img') # finding chapter link
        chapter_name_element = element.find_element(By.CSS_SELECTOR, 'span.line-clamp-1')  # finding chapter name
        chapter_name = chapter_name_element.text

        # Check if the title attribute of the <img> tag is "English"
        if img_element.get_attribute('title') == 'English':
            # Get the 'href' attribute of the parent <a> tag
            href = element.get_attribute('href')
            if 'mangadex' in href:
                chap_name.append(chapter_name)
                chap_links.append(href)
                
    driver.quit()
    
    return chap_links.reverse(), chap_name.reverse(), series
    
def mangadex_img(url):    #require different method to download images as they are java script infused
    driver = load_firefox(url) # let's load url in fire fox
    
    img_list = []
    
    #total_page_element = driver.find_elements(By.CSS_SELECTOR, '.reader--meta.page')
    #total_page = int(total_page_element[0].text.split('/')[-1])
    
    
    
    
    return img_list, driver
    

def mangasub_chap(url):
    
    driver = load_firefox(url) # let's load url in fire fox
    
    chap_name = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.post-title'))
    )
    series = chap_name.text
    
    chap_links = []
    chap_name = []
    
    elements = driver.find_elements(By.CSS_SELECTOR, 'li.wp-manga-chapter')
    
    for element in elements:
        img_element = element.find_element(By.CSS_SELECTOR, 'a')
        chap_links.append(img_element.get_attribute('href'))
        chap_name.append(img_element.text)
    
    #chap_name, chap_links = sorter(chap_name,chap_links)
    
    driver.quit()
    return chap_links, chap_name, series
    
def mangasub_img(url):
    img_list = []
    
    driver = load_firefox(url) # let's load url in fire fox
    
    page_element = driver.find_elements(By.CSS_SELECTOR, 'div.c-selectpicker.selectpicker_page')
    
    total_page = len(page_element[1].text.split('\n'))
    
    img_element = driver.find_elements(By.CSS_SELECTOR,'img')
    
    for img in img_element:
        lnk = img.get_attribute('src')
        if '/WP-manga/data' in lnk:
            img_list.append(lnk)
            
    next_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div/div[3]/div[2]/div[2]'))
    )
    for _ in range(total_page - 1):
        next_button.click()
        time.sleep(1)  # Wait for the page to load
        
        img_element = driver.find_elements(By.CSS_SELECTOR,'img')
        
        for img in img_element:
            lnk = img.get_attribute('src')
            if '/WP-manga/data' in lnk:
                img_list.append(lnk)
    
    driver.quit()            
    return img_list


def platinumscan_chap(url):
    driver = load_firefox(url)
    chap_name = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.post-title'))
    )
    series = chap_name.text
    
    chap_links = []
    chap_name = []
    
    show_more_button = (By.CSS_SELECTOR, 'span.btn.btn-link.chapter-readmore.less-chap') # let's find show more button
    
    try:  # let's click on show more button till everything is loaded
        while True: 
            # Wait for the 'Show more' button to be clickable
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable(show_more_button))

            # Click the 'Show more' button
            driver.find_element(*show_more_button).click()

            # You can add a delay here if needed
            time.sleep(2)
    except Exception as e:
        print("All chapter loaded.")
    
    elements = driver.find_elements(By.CSS_SELECTOR, 'li.wp-manga-chapter')
    
    for element in elements:
        img_element = element.find_element(By.CSS_SELECTOR, 'a')
        chap_links.append(img_element.get_attribute('href'))
        chap_name.append(img_element.text)
    
    #chap_name, chap_links = sorter(chap_name,chap_links)
    
    driver.quit()
    chap_name.reverse()
    chap_links.reverse()
    
    return chap_links, chap_name, series

def platinumscan_img(url):
    img_list = []
    
    driver = load_firefox(url+'?style=paged') # let's load url in fire fox
    
    page_element = driver.find_elements(By.CSS_SELECTOR, 'div.c-selectpicker.selectpicker_page')
    
    total_page = len(page_element[1].text.split('\n'))
    
    img_element = driver.find_elements(By.CSS_SELECTOR,'img')
    
    for img in img_element:
        lnk = img.get_attribute('src')
        if '/WP-manga/data' in lnk:
            img_list.append(lnk)
            
    next_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div/div[3]/div[2]/div[2]/a'))
    )
    for _ in range(total_page - 1):
        next_button.click()
        time.sleep(1)  # Wait for the page to load
        
        img_element = driver.find_elements(By.CSS_SELECTOR,'img')
        
        for img in img_element:
            lnk = img.get_attribute('src')
            if '/WP-manga/data' in lnk:
                img_list.append(lnk)
    
    driver.quit()            
    return img_list




    