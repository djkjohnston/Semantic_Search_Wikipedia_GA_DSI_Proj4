from sklearn.externals import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import sys
import spacy
import re

nlp = spacy.load('en')


def cleaner(text):
    mapping = [('&#39;', ''), 
               ('<br />', ''), 
               ('<.*>.*</.*>', ''), 
               ('\\ufeff', ''), 
               ('[\d]', ''),  
               ('\[.*\]', ''),  
               ('[^a-z ]', '')]
    for k, v in mapping:
        text = re.sub(k, v, text)
        
    text = ' '.join(i.lemma_ for i in nlp(text))
    text = ' '.join(text.split())
    
    return text


tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl') 
SVD = joblib.load('SVD.pkl') 
svd_matrix_df = pd.read_pickle('svd_matrix_df.pkl')

def search_for_pages(search_term):
    tmp_svd_df = svd_matrix_df.copy()
    
    clean_search = search_term.lower().replace("\n", " ") # converts to lowercase and drops any \n
    clean_search = cleaner(clean_search) #cleans other special characters, whitespace, numbers, etc.
    clean_search = [clean_search]
    
    tfdif_search = tfidf_vectorizer.transform(clean_search)
    svd_search = SVD.transform(tfdif_search)
    
    cosine = cosine_similarity(tmp_svd_df, svd_search)
    # pearson = tmp_svd_df.apply(lambda x: np.corrcoef(x, svd_search)[0][1], axis = 1)
    
    tmp_svd_df['cosine_similarity'] = cosine
    # tmp_svd_df['pearson_similarity'] = pearson
#     print(tmp_svd_df.shape)
#     print(svd_search[0])

    return tmp_svd_df[['cosine_similarity']]

search_term = ' '.join(sys.argv[1:])
print(type(search_term))
print("Searching wiki articles for: {}".format(search_term))

search_df = search_for_pages(search_term)

print("Top pages based on cosine cosine similarity")
print(search_df.sort_values('cosine_similarity', ascending=False).head())
# print("")
# print("Top pages based on cosine Pearson similarity")
# df[['pearson_similarity']].sort_values('cosine_similarity', ascending=False).head()