# import libraries
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import re

# specify the url
library_page = 'http://www.lib.berkeley.edu/hours'

# query the website and return the html to the variable 'page'
page = urllib.request.urlopen(library_page)

# parse the html using beautiful soup and store in variable 'soup'
soup = BeautifulSoup(page, 'html.parser')

#Initialize library hours, names lists
library_names = []
library_hours = []

library_info = soup.find_all('div', attrs={'class':'library-info-block'})

def URLparser(URLraw):
	URLstring = str(URLraw)
	regex = r"([<]).+?([>])"
	URLstripped = re.sub(regex, '', URLstring)
	list_of_string_remove = ['\n', '&amp']
	for sample in list_of_string_remove:
		URLstripped = URLstripped.replace(sample,'')
	return URLstripped

def HoursParser(hourTag):
	hourString = str(hourTag)
	list_of_string_remove =  ['\n', ' ']
	regex = r"([<]).+?([>])"
	hourString = re.sub(regex, '', hourString)
	for sample in list_of_string_remove:
		hourString = hourString.replace(sample, '')
	if hourString.lower() == 'hoursunavailable':
		return None
	return hourString

for library in library_info:
	URLsoup = library.find('h2', class_ = 'library-name-block')
	URLraw = URLsoup.find(lambda tag: tag.name == 'a' and tag.get('href') and tag.text)
	hourTag = library.find('div', class_ = 'library-hours-block')
	library_names.append(URLparser(URLraw))
	library_hours.append(HoursParser(hourTag))	

print(library_names)
print(library_hours)
