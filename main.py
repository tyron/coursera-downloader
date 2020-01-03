from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import pickle
import urllib.request
import time
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urlparse
import os
import pathlib
import re
import collections, functools, operator 

course_url = "https://www.coursera.org/learn/leveraging-unstructured-data-dataproc-gcp/home/welcome"

# pass the url of a week's, returns all links that start with Video:
def get_all_videos_subpage(driver, page_url) -> List[str]:
    driver.get(page_url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rc-LessonCollectionBody")))

    sublinksElems : List[WebElement] = driver.find_elements_by_class_name("rc-WeekItemName")
    pages_with_videos=[]

    for sublink_elem in sublinksElems:
        try:
            t:WebElement = sublink_elem.find_element_by_tag_name("strong")
            if t.text.startswith("Video"):
                link = driver.execute_script("return arguments[0].parentNode.parentNode.parentNode.parentNode", sublink_elem).get_property('href')
                pages_with_videos.append(link)
        except:
            pass

    return pages_with_videos

def download_videos_from_links(driver, all_links, folder="."):
    # each entry represents a new week
    for entry in all_links:
        index=1

        # each entry is a link for a video within that week
        for link in entry["subpages"]:
            driver.get(link)
            
            wait = WebDriverWait(driver, 30)
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".item-page-content")))

            v_url : str
            v_title : str
            try:
                # video=driver.find_element_by_tag_name("video")

                # v_url = video.get_property('src')
                v_url = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video"))).get_property('src')
                v_title = wait.until(EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, ".video-name"))).text
            except:
                # if there's no video, continue to next iteration
                continue

            try:
                parse = urlparse(v_url)
                path = parse.path
                ext = os.path.splitext(path)[1]

                filename = 'W%s-V%s %s%s' % (entry["page"]["week"], index, v_title, ext)

                if not os.path.isfile(filename): # only downloads if doesnt exists
                    urllib.request.urlretrieve(v_url, "{0}/{1}".format(folder, filename))

            except Exception as e:
                # failed to save the video, maybe try manually
                print(e)
                pass

            finally:
                index += 1

driver : webdriver
try:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(options=chrome_options)
except:
    exit()

driver.get(course_url)
try:
    driver.find_element_by_link_text("Log In")
    already_logged = False
except:
    already_logged = True
    pass

if not already_logged:
    try:
        WebDriverWait(driver, 300).until(EC.invisibility_of_element(driver.find_element_by_link_text("Log In")))
        # only gets here if I logged, otherwise it goes to except
        already_logged = True
    except:
        driver.quit()
        exit(1)

time.sleep(10)

course_title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "course-name"))).text

if not os.path.isdir(course_title):
    os.mkdir(course_title)

# WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "rc-NavigationDrawerLink")))
elems=driver.find_elements_by_class_name("rc-NavigationDrawerLink")

weeks=[]
for item in elems:
    weeks.append({ "title": item.text, "week": int(re.search("(\d*)$", item.text).group(1)), "url": item.get_property('href') })

all_links = []
try:
    for page_url in weeks:
        #if not page_url["week"] == 1:
        subpages_url = get_all_videos_subpage(driver, page_url["url"])
        entry = { "page": page_url, "subpages": subpages_url }
        all_links.append(entry)
except:
    driver.quit()



download_videos_from_links(driver, all_links, folder=course_title)
