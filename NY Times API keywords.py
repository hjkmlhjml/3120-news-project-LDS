import requests as r
import pandas as pd
from io import StringIO
import seaborn as sns
import matplotlib.pyplot as plt
#import spacy
import numpy as np
from collections import Counter
from collections import OrderedDict
from datetime import datetime
import operator
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import config

# NY Times API keyword tracking project by Luca Shapiro


API_KEY = config.api_key
search_begin_date=("20240101")
search_end_date=("20240405")
news_desk=("Politics")
format_string = "%Y-%m-%d"

print ("starting now \n")

# all_info is the main data structure to hold all the information we want from the API call
# it will a two dim list, for each row (article) it will have the pub date, a string for the title, and a list of keywords (strings)
# once I finish pulling all the data, it will cycle through the list and make a dictionary of keywords 
# to determine the top 10 for the whole date range
all_info = []
page = 0

main_title = []
main_keywords = []
articles_per_day = {} 
# query is limited to a 1000 results per NY Times API documentation, a page is 10 results so at most there can be 100 pages
# with 10 articles per page
# also I added a try except break to catch if the query returns a fault when there are no more articles which will cause a KeyError when assigning the response
while page <100:
    search_results = r.get(f"https://api.nytimes.com/svc/search/v2/articlesearch.json?page={page}&sort=newest&fq=news_desk:({news_desk})&begin_date={search_begin_date}&end_date={search_end_date}&api-key={API_KEY}").content.decode()
   
    nyt_home = pd.read_json(StringIO(search_results))
    
    try:
        query_response = nyt_home['response']
    except KeyError:
        break
    docs = query_response['docs']
    #print ("len of docs = ", len(docs), "\n")
    
    for i in range(len(docs)):
        a = docs[i]
        title = a['headline']
        keywords = a['keywords']
        main_title.append(title['main'])
        main_keywords = []
        #keywords is a list of dictionaries for each article so it needs to cycle through the list
        for y in range(len(keywords)):
            main_keywords.append(keywords[y]['value'])
        all_info.append([a['pub_date'], title['main'], main_keywords])
        #count the number of articles on each date for the line graph
        current_article_date = a['pub_date'][:10]
        if current_article_date in articles_per_day:
            articles_per_day[current_article_date] += 1
        else:
            articles_per_day[current_article_date]= 1
    page += 1
    
    
#now that all_info is full, it needs to create the keyword_top10 dictionary so it can count the keywords
keyword_top10 = {}
for x in range(len(all_info)):
    for y in range(len(all_info[x][2])):
        keyword = all_info[x][2][y]
        #print("adding ", keyword, " to top 10 or inc it \n")
        if keyword in keyword_top10:
            keyword_top10[keyword] += 1
        else:
            keyword_top10[keyword] = 1

    
#print ("sorting the list\n")

sorted_top10 = sorted(keyword_top10.items(), key = operator.itemgetter(1), reverse=True)
#print("printing sorted list of keywords: \n")
#print(sorted_top10)

# Select the top 10 keywords
top10={}
for x in range(10):
    print("x = ", x, " sorted_top10 entry = ", sorted_top10[x])
    top10[sorted_top10[x][0]] = sorted_top10[x][1]

#print ("top 10 = ", top10, "\n")

# Plotting the bar chart
plt.figure(figsize=(20, 6))
plt.bar(top10.keys(), top10.values())
plt.title('Top 10 Most Frequently Used Keywords for the ' + news_desk + ' Newsdesk for dates ' + search_begin_date + ' to ' + search_end_date)
plt.xlabel('Keywords')
plt.ylabel('Frequency')
plt.xticks(rotation=45)
plt.show()


# Plotting the line graph for articles per day
plt.figure(figsize=(20, 6))
articles_per_day_plt = sorted(articles_per_day.items())
x, y = zip(*articles_per_day_plt)
plt.plot(x, y)

#articles_per_day_plt.plot(kind='line', marker='o', linestyle='-')
plt.title('Number of Articles Published per Day for the ' + news_desk + ' Newsdesk for dates ' + search_begin_date + ' to ' + search_end_date)
plt.xlabel('Date')
plt.ylabel('Number of Articles')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

#plot a wordcloud showing the most used keywords larger in size
unique_string = ""
for row in range(len(sorted_top10)):
    for num_word in range(sorted_top10[row][1]):
        unique_string+= sorted_top10[row][0] + " "
wordcloud=WordCloud(width=1600, height=700).generate(unique_string)
plt.figure(figsize=(20,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
plt.close()

print("starting the plots for keywords by date\n")

#plot graphs for each of the top 3 keywords to show progression of use over time
for x in range(3):
    # need to traverse all_info to match top 3 keywords, and for each match copy the date into a new dictionary to plot by date
    keyword_date_dictionary = {}
    for row in range(len(all_info)):
        for y in range(len(all_info[row][2])):
            if all_info[row][2][y] == sorted_top10[x][0]:
                #print ("Adding or incrementing for keyword for row = ", row, " y = ", y, " date = ", all_info[row][0], "\n")
                temp_date = all_info[row][0][:10]
                if temp_date in keyword_date_dictionary:
                    keyword_date_dictionary[temp_date] += 1
                else:
                    keyword_date_dictionary[temp_date] = 1
    keyword_date_plt = sorted(keyword_date_dictionary.items())
    x_axis, y = zip(*keyword_date_plt)
    plt.figure(figsize=(20, 6))
    plt.title('Number of articles that mention keyword ' + sorted_top10[x][0])
    plt.xlabel('Date')
    plt.ylabel('Number of Articles')
    plt.plot(x_axis, y)
    plt.show()
    plt.close()
