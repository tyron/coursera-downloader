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
import string
import sys, getopt

def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.
 
Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.
 
"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    # filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename

# pass the url of a week's, returns all links that start with Video:
def get_all_videos_subpage(driver, page_url) -> List[dict]:
    driver.get(page_url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rc-LessonCollectionBody")))

    sublinksElems : List[WebElement] = driver.find_elements_by_class_name("rc-WeekItemName")
    pages_with_videos : List[dict] = []
    
    for sublink_elem in sublinksElems:
        try:
            t:WebElement = sublink_elem.find_element_by_tag_name("strong")
            if t.text.startswith("Video"):
                link = driver.execute_script("return arguments[0].parentNode.parentNode.parentNode.parentNode", sublink_elem).get_property('href')
                title = re.search("(?s:.*)\n(.*)", sublink_elem.text).group(1)
                pages_with_videos.append({ "title": title, "link": link })
        except:
            pass

    return pages_with_videos

def download_videos_from_links(drivexxr, all_links, folder="."):
    # each entry represents a new week
    for entry in all_links:
        index=1
        week_num = entry["page"]["week"]

        # each entry is a link for a video within that week
        for subpage in entry["subpages"]:
            v_title : str = subpage["title"]
            link = subpage["link"]

            if os.path.isfile("{0}/{1}".format(folder, format_filename("W{0}-V{1} {2}{3}".format(week_num, index, v_title, ".mp4")))) or \
               os.path.isfile("{0}/{1}".format(folder, format_filename("W{0}-V{1} {2}{3}".format(week_num, index, v_title, ".webm")))):
               index += 1
               continue

            driver.get(link)
            
            wait = WebDriverWait(driver, 30)
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".item-page-content")))

            v_url : str
            try:
                # v_title = wait.until(EC.presence_of_element_located(
                #                    (By.CSS_SELECTOR, ".video-name"))).text
                v_url = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video"))).get_property('src')
                
                vid_sources = driver.find_elements_by_tag_name("source")
                for source in vid_sources:
                    if source.get_property("type") == "video/mp4":
                        v_url = source.get_property("src")

                print("Downloading video '{0}' from {1}".format(v_title, v_url))
            except:
                # if there's no video, continue to next iteration
                continue

            try:
                parse = urlparse(v_url)
                path = parse.path
                ext = os.path.splitext(path)[1]

                filename = format_filename("W{0}-V{1} {2}{3}".format(week_num, index, v_title, ext))

                if not os.path.isfile(filename): # only downloads if doesnt exists
                    urllib.request.urlretrieve(v_url, "{0}/{1}".format(folder, filename))

            except Exception as e:
                # failed to save the video, maybe try manually
                print(e)
                pass

            finally:
                index += 1

def main(argv):

    course_url : str = "" 

    try:
        opts, args = getopt.getopt(argv,"hu:",["url="])
    except getopt.GetoptError:
        print('main.py -u <inputUrl>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -u <inputUrl>')
            sys.exit()
        elif opt in ("-u", "--url"):
            course_url = arg

    # course_url = "https://www.coursera.org/learn/hybrid-cloud-infrastructure-foundations-anthos/home/welcome"
    if not course_url:
        print('URL not provided')
        sys.exit()

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

    time.sleep(3)

    course_title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "course-name"))).text

    if not os.path.isdir(course_title):
        os.mkdir(course_title)

    # WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "rc-NavigationDrawerLink")))
    elems=driver.find_elements_by_class_name("rc-NavigationDrawerLink")

    weeks=[]
    for item in elems:
        print('Got week: {0}'.format(item.text))
        weeks.append({ "title": item.text, "week": int(re.search("(\d*)$", item.text).group(1)), "url": item.get_property('href') })

    all_links = []
    try:
        for page_url in weeks:
            #if not page_url["week"] == 1:
            subpages = get_all_videos_subpage(driver, page_url["url"])
            entry = { "page": page_url, "subpages": subpages }
            all_links.append(entry)
            print('Identified {0} videos on {1}'.format(len(subpages), page_url["title"]))
    except:
        driver.quit()

    download_videos_from_links(driver, all_links, folder=course_title)

    print("Completed!")


if __name__ == "__main__":
    main(sys.argv[1:])