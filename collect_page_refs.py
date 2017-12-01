import re
import requests
import pandas as pd
import numpy as np
from time import sleep


def category_page_query(category):
    """
    Params
    ----------
    category : str
        cleaned category text to be used in wiki api call


    Returns
    ----------
    query.json()
        a list of dicts containing information about the page: ns, page id, page title  

    """
    
    query_params = {"action": "query", 
                    "format": "json", 
                    "list": "categorymembers", 
                    "cmtype": "page", 
                    "cmlimit": "max", 
                    "cmtitle": "Category:{}".format(category)}

    query = requests.get('http://en.wikipedia.org/w/api.php', query_params)

    return query.json()

def category_subcat_query(category):
    """
    Params
    ----------
    category : str
        cleaned category text to be used in wiki api call
        
        
    Returns
    ----------
    query.json()
        a list of dicts containing the subcategories withing category  
    """

    query_params = {"action": "query", 
                    "format": "json", 
                    "list": "categorymembers", 
                    "cmtype": "subcat", 
                    "cmlimit": "max", 
                    "cmtitle": "Category:{}".format(category)}

    query = requests.get('http://en.wikipedia.org/w/api.php', query_params)

#     print(query.url)
    return query.json()

def clean_cat_text(category):
    """
    Params
    ----------
    category : str
        uncleaned category text to be used in wiki api call


    Returns
    ----------
    cat_text
        a cleaned category text to be used in wiki api call  

    """

    cat_text = category.replace(' ', '_')
    cat_text = cat_text.replace("Category:", "")
    cat_text = cat_text.lower()
    
    return cat_text

def get_category_pages(category, depth):
    """
    Params
    ----------
    category : str
    category name to be used in wiki api call
    

    Returns
    ----------
    pagelist
        a list of dicts containing all pages associated with the category and any related subcategories, including nested subcategories  

        """
    
#     print("Working on", category)
    pagelist = []
    clean_category = clean_cat_text(category)
    
    #get_subcategories from current category
    subcat_response = category_subcat_query(clean_category)
    
    n_sub = len(subcat_response['query']['categorymembers'])
    sub_df = pd.DataFrame(subcat_response['query']['categorymembers'])
    
    # if there are subcategories, clean the text and recursively call get_category_pages
    if n_sub >= 1:
        depth += 1 

        if depth < 10: 
            for sub in sub_df['title']:
                #sleep(0.1)
                sub_clean = clean_cat_text(sub)
                pagelist.extend(get_category_pages(sub_clean, depth))
    
    #the the pages info from the current category 
    page_response = category_page_query(clean_category)
    
    pagelist.extend(page_response['query']['categorymembers'])
        
        
    return pagelist

#list of categories to traverse
category_list = ['Machine Learning', 'Business Software']
    
pages_df = pd.DataFrame(columns=['ns', 'pageid', 'title'])

for category in category_list:
    depth = 0 # used to control how many subcategory layers are used
    print("Getting pages for the ", category, "category...")
    tmp_list = get_category_pages(category, depth)
    tmp_df = pd.DataFrame(tmp_list)
    pages_df = pages_df.append(tmp_df)
    pages_df = pages_df.drop_duplicates()
    pages_df.to_csv('data/list_of_pages.csv', index=False)
    sleep(2)
    
pages_df = pages_df.drop_duplicates()

pages_df.to_csv('data/list_of_pages.csv', index=False)