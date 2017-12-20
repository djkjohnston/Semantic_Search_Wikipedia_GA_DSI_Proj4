# Dan Johnston - Semantic Search

## The Task
The objective of this assignment is to engineer a novel wikipedia search engine using what you've learned about data collection, infrastructure, and natural language processing.

The task has two **required sections:**
- Data collection - Complete
- Search algorithm development - Complete

And one **optional section:** 
  - Predictive modeling - Not implemented

### Part 1 -- Collection 

I separated this into two stages:

	1. Collect page names/ids from designated categories (including sub categories, up to 10 layers deep.)
	2. Collect page content

1. This was executed with the `collect_page_refs.py` script. I ran this script on an AWS instance using `tmux` to allow me to disconnect from the session. The list of categories was hard coded into the script, rather than pulling from the shell command; I did this largely to avoid spelling errors. The resulting list of pages was deduplicated and then saved to `data/list_of_pages.csv`
1. The collection of actual page contents was executed with the `pull_page_contents.py` script, which was also run from the command line. This script was also run using `tmux` on an AWS instance. For each entry in the full list of pages previously identified, the script did the following:
	* Queried Wikipedia's API for page contents (in `HTML`) along with the associated categories
	* Used BeautifulSoup to extract the plain text from the `HTML` object
	* Store the plain text and categories in a `mongoDB` server running on a separate AWS instance. 
	
Some pages existed without holding any page contents which caused some errors when trying to parse the plain text. My script uses the `try`/`except` functionality to skip any queries that threw an error. The result was 46010 separate Wikipedia pages in my `mongoDB`
	

### Part 2 -- Search

#### 2.1 Cleaning and Data Prep

Before starting to set up the search functionality, I performed some cleaning and feature engineering on my collected data. 

* There were two kinds of duplicated entries. Both were removed 
	* "This article may not meet wikipedia general..."
	* "This article has multiple issues..."
* Mentions of '[Edit]' were removed as they related to Wikipedia's format, not the actual page contents
* Special characters, symbols, and digits were removed
* All characters were converted to lowercase
* All words were lemmatized using the `spacy` library

#### 2.2 Model Pipeline

In order to implement the search functionality, I needed to transform the page contents into a format that was more accessible at scale, rather than doing a simple `str.contains()` call. My final model pipeline is as follows:

* TF-IDF
	* Removing English Stop Words
	* Accepting grams and bigrams
	* Minimum Document Frequency of 25. 
	* Resulting Document Term Martix had 42839 rows and 59284 columns
		* These parameters were partially chosen in order to keep the size of the .pkl fil managable

The ~60k columns resulting from TF-IDF were too many to quickly compare similarity, so I needed to reduce the number of features:

* Truncated SVD 
	*	100 components
	
This resulted in a matrix with 42839 rows and 100 columns. This matrix formed the basis of comparison for the search implementation.

	
#### The Search

The Search implementation was relatively simple:

1. Take in a search term
1. Transform the search term using the fitted model pipeline created in step 2.2
1. Calculate cosine similarity between the search term and all wiki pages
	* I also implimented Pearson similarity, but the results were analagous to the cosine scores.
1. Return the page names with the highest (i.e. strongest) similarity scores

The Search can be executed in one of two ways:
1. Using the `Final Search implimentation.ipynb` notebook
2. From the command line using following command: 
```
$ docker run --rm -v $(pwd):/home/jovyan dj/scipy-notebook-extended python wiki_search_results.py "SEARCH TERM"
```

Please note that the docker image used as a template must include the `spacey` library. A screenshot has been provided below as an illustration of the functionality.

<img src='https://git.generalassemb.ly/raw/dannyboyjohnston/semantic_search/master/assets/semantic_search_command_line_example.png'>
