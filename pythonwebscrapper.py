# import libraries
import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import re

# specify the url
library_page = 'http://www.lib.berkeley.edu/hours'

# query the website and return the html to the variable 'page'
page = urllib2.urlopen(library_page)

# parse the html using beautiful soup and store in variable 'soup'
soup = BeautifulSoup(page, 'html.parser')
