#%%
from bs4 import BeautifulSoup
import os, re
import pandas as pd
import calendar

#%%
html = BeautifulSoup(open('2019 in the United States - Wikipedia.html'), 'html.parser')

#%%
## Starting with January
monthNum = 1
month = calendar.month_name[monthNum]
events = []

## Every month has a header
headers = html.find_all('h3')
for header in headers:
    if header.span.text == month:
        eventList = header.findNextSibling('ul')
        days = eventList.find_all('li', recursive=False)

        for day in days:
            ## Example of formats: 
            ## January 1 
            ## January 1–2
            ## See if there are multiple dates first
            date = re.search(f'{month} \d+–\d+', day.text)

            if date != None:
                start, end = date.span()
                start += len(month) + 1
                ## Just go with first
                dayNum, _ = day.text[start:end].split('–')
                dayNum = int(dayNum)
            else:
                date = re.search(f'{month} \d+', day.text)
                if date == None:
                    continue
                start, end = date.span()
                start += len(month) + 1
                dayNum = int(day.text[start:end])
                
            subEvents = day.find('ul')
            if subEvents != None:
                for event in subEvents.find_all('li'):
                    events.append({
                        'month' : monthNum,
                        'day' : dayNum,
                        'event' : event.text.strip()
                        })
            else:
                ## should have an em (maybe en) dash
                text = day.text[end:]
                eventText = text.split('–', 1)
                ## if not, it's just a hyphen
                if len(eventText) != 2:
                    ## Trim off date first
                    eventText = text.split('-', 1)

                events.append({
                        'month' : monthNum,
                        'day' : dayNum,
                        'event' : eventText[1].strip()
                        })

        monthNum += 1
        if monthNum > 12:
            break
        month = calendar.month_name[monthNum]

## Make into dataframe
events = pd.DataFrame(events, columns=['month', 'day', 'event'])

## Remove citations
events['event'] = events['event'].str.replace('\[\d+\]', '')

#%%
events.to_csv('2019_events.csv', index=False)
