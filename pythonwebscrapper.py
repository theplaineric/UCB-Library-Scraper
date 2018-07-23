# import libraries
import urllib
from datetime import datetime, time, timedelta
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
	time = datetime.strptime('12:00am', '%I:%M%p').time()
	dash_index = sample.find('-')
	if dash_index == -1:
		return (None, None)
	first_time, second_time = -1, -1
	if dash_index == len(sample)-1:
		second_time = time
		first_time = stringToTime(sample[:dash_index])
	elif dash_index == 0:
		first_time = time
		second_time = stringToTime(sample[dash_index+1:])
	else:
		second_time = stringToTime(sample[dash_index+1:])
		first_time = stringToTime(sample[:dash_index])
	return (first_time, second_time)

"""
Checks if a string is an integer
"""
def represent_Int(i):
	try:
		int(i)
		return True
	except ValueError:
		return False

"""
This converts the string from 2pm to 14.
"""
def stringToTime(sample):
	if sample == '12noon':
		sample = '12:00pm'
	colon_index = sample.find(':')
	#checks if second character is a string, then zero-pads
	if not represent_Int(sample[1]):
		sample = '0'+sample
	if colon_index == -1:
		sample = sample[:2]+':00'+sample[-2:]
	time = datetime.strptime(sample,'%I:%M%p').time()
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

def open_or_close(time, now_time, opening = True):
	if opening:
		if now_time>time:
			return True
	else:
		if now_time<time:
			return True
	return False

def time_distance_calculator(time_A, time_B):
	#time_A should be current time
	time_delta_A = timedelta(hours = time_A.hour(), minutes = time_A.minute())
	time_delta_B = timedelta(hours = time_B.hour(), minutes = time_B.minute())
	#calculate time until closing_time
	difference = time_delta_B - time_delta_A
	if abs(difference) != difference:
		return None
	return difference


#grab current system time
now_time = datetime.now().time()
opened = df.opening_time.map(lambda time: open_or_close(time, now_time))
before_closed = df.closing_time.map(lambda time: open_or_close(time, now_time, False))
is_library_open = opened & before_closed
df['still_open'] = is_library_open
df['time_til_open'] = df.opening_time.map(lambda time: time_distance_calculator(now_time, time))
df['time_til_close'] = df.closing_time.map(lambda time: time_distance_calculator(now_time, time))

print(df.loc[df['time_til_close'] != None])
print(df.loc[df['time_til_open'] != None])
#We want:
#If open, how long until it closes; if closed, how long until open
