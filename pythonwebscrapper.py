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
		return (None, None)
	first_time, second_time = -1, -1
	if dash_index == len(sample)-1:
		second_time = 24
		first_time = stringToInt(sample[:dash_index])
	elif dash_index == 0:
		first_time = 0
		second_time = stringToInt(sample[dash_index+1:])
	else:
		second_time = stringToInt(sample[dash_index+1:])
		first_time = stringToInt(sample[:dash_index])
	return (first_time, second_time)

"""
This converts the string from 2pm to 14.
"""
def stringToInt(sample):
	time = int(sample[:-2])
	if sample[-2:] == 'pm' and time != 12:
		time+=12
	if sample == '12am':
		return 0
	return time

for library in library_info:
	URLsoup = library.find('h2', class_ = 'library-name-block')
	URLraw = URLsoup.find(lambda tag: tag.name == 'a' and tag.get('href') and tag.text)
	hourTag = library.find('div', class_ = 'library-hours-block')
	library_names.append(URLparser(URLraw))
	library_hours.append(HoursParser(hourTag))

library_open_times = []
library_closed_times = []

for library in library_hours:
	parsed_hours_string = stringIntaker(library)
	library_open_times.append(parsed_hours_string[0])
	library_closed_times.append(parsed_hours_string[1])
	
library_dataframe = pd.DataFrame({'opening_time' : pd.Series(library_open_times, index = library_names), 'closing_time': pd.Series(library_closed_times, index = library_names)})

df = library_dataframe[library_dataframe.opening_time.notnull() & library_dataframe.closing_time.notnull()]

df.opening_time = df.opening_time.astype('int32')
df.closing_time = df.closing_time.astype('int32')
print(df.head())
