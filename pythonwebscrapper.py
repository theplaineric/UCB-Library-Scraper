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
	list_of_string_remove =  ['By appointment only','\n', ' ']
	regex = r"([<]).+?([>])"
	hourString = re.sub(regex, '', hourString)
	for sample in list_of_string_remove:
		hourString = hourString.replace(sample, '')
	if hourString.lower() == 'hoursunavailable':
		return None
	return hourString

"""
This divides up the hours string into two different strings to be converted into times
"""
def stringIntaker(sample):
	dash_index = sample.find('-')
	if dash_index == -1:
		return None
	first_time = stringToInt(sample[:dash_index])
	second_time = -1
	if dash_index == len(sample)-1:
		second_time = 24
	else:
		second_time = stringToInt(sample[dash_index+1:])
	
"""
This converts the string from 2pm to 14.
"""
def stringToInt(sample):
	time = int(sample[:-2])
	if sample[-2:] == 'pm':
		time+=12
	return time
	

for library in library_info:
	URLsoup = library.find('h2', class_ = 'library-name-block')
	URLraw = URLsoup.find(lambda tag: tag.name == 'a' and tag.get('href') and tag.text)
	hourTag = library.find('div', class_ = 'library-hours-block')
	library_names.append(URLparser(URLraw))
	library_hours.append(HoursParser(hourTag))	

library_INFO = pd.DataFrame(

