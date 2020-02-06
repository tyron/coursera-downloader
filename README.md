# Coursera Video Downloader

This project uses Selenium (framework for automated browser testing) to replay actions needed to download videos from Coursera. Downloading videos from Coursera is an action allowed normally through the UI, so this is just a wrapper to avoid too many clicking.

## Installation

1. Have a macOS :)
1. Have Python3 installed with working pip (suggestion: use pyenv)
    1. If using macOS Mojave 10.14, you might need to install xcode, install the headers and set SDKROOT variable as per https://github.com/pyenv/pyenv/issues/1066#issuecomment-531510186
1. Install Selenium WebDriver for your browser version ([Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads))
1. Clone the repository into your machine with Python 3 installed
1. Create a virtualenv on the directory created: `python -m venv venv`
1. Activate the virtualenv: `source venv/bin/activate`

## Usage


1. Run `pip install -r requirements.txt`
1. Update the variable `course_url` on the main.py file to point to the URL of the course


## To-do

Migrate the `course_url` variable to a parameter passed on the script call
