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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time

def mangafire (url):
    # Set the path to the GeckoDriver executable
    current_path = os.getcwd()
    gecko_driver_path = current_path+'/sub_file/Web_driver/geckodriver.exe'
    firefox_binary_path = current_path+ '/sub_file/FirefoxPortable/App/Firefox64/firefox.exe'
    
    # Create a Firefox WebDriver instance
    options = Options()
    options.binary_location = firefox_binary_path
    options.headless = True  # Set to False to see the scrolling
    
    
    # Create a Firefox profile
    profile = FirefoxProfile()
    
    # Path to the add-ons (.xpi files)
    addon_paths = [current_path+ '/sub_file/FirefoxPortable/ublock.xpi']
    
    service = Service(executable_path=gecko_driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    driver.get(url)  # Replace with your target URL
    
    # Install each add-on
    for addon_path in addon_paths:
        driver.install_addon(addon_path, temporary=True)
    
    time.sleep(2) # let's wait till it install addons
    driver.refresh() # let's referesh so addon can works
    time.sleep(10) # let's wait till it for basic loading
    # Extract the total number of pages
    total_pages_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'html body.read.ctrl-menu-active div.wrapper header div.inner.px-3 div.component div.viewing.mr-3.page-toggler span b.total-page'))
    )
        
    total_pages = int(total_pages_element.text)
    
    chap_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div[2]/nav[1]/button[2]')))
    chap_button.click()
    
    chap_name = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'html body.read.ctrl-menu-active div.wrapper main.longstrip div.m-content div#number-panel.sub-panel.scroll-sm.active ul li a.active'))
    )
    

    chapter = chap_name.text

    
    # Click the "Next" button (total_pages - 1) times
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
    # Download each image
    for index, image_element in enumerate(image_elements):
        image_url = image_element.get_attribute('src')
        img_links.append(image_url)    
    # Close the browser
    driver.quit()
    
    return img_links, chapter