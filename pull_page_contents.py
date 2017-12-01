"""
The purpose of this file is to pull the conents of the named wikipedia pages and place them into a mongoDB
"""

import pip

def install(package):
    pip.main(['install', package])

# Example
if __name__ == '__main__':
    install('pymongo')
    install('bs4')


import requests
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bs4 import BeautifulSoup
from time import sleep


def get_page_contents(pageid):
    """
    Params
    ---------
    pageid
        the unique identifier for pages in wikipedia


    Returms
    ---------
    query.json()
        a dictionary contain both the text of the wikipedia page as well as a list of the related categories
    """

    query_params = {
        "action": "parse",
        "format": "json",
        "pageid": int(pageid),
        "prop": "text|categories"

    }

    query = requests.get('http://en.wikipedia.org/w/api.php', query_params)

    return query.json()

df = pd.read_csv('data/list_of_pages.csv')

pagelist = df['pageid']


# connect to mongodb
client = MongoClient('ec2-54-69-203-249.us-west-2.compute.amazonaws.com', 27016)
wiki_db = client.wiki #create a db
page_ref = wiki_db.wiki_pages #create a collection


for pageid in pagelist:


    try:
        content = get_page_contents(pageid) #retrieve page contents
        soup = BeautifulSoup(content['parse']['text']['*'], "html5lib")
        content['parse']['text'] = soup.text
        
        page_ref.insert_one(content['parse']) #getting the contents of 'parse' will allow us to query mongo on pageid later
    except:
        pass
    
    sleep(0.2)

client.close()