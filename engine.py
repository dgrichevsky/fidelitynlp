"""
    This module will run NLP analysis on the filings from a set of
    quarters for companies found in input/test_names.txt
"""

from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel as LDA
from gensim.models import LsiModel as LSA
import pyLDAvis.gensim
import fetch
import clean
import database
import interface
import json
import pickle
import pandas as pd
import re

def new_model(data):
    dictFromData = json.loads(data)
    tickers_ciks = interface.convert_tickers(dictFromData['companies'])
    if not tickers_ciks:
        return
    quarters = interface.convert_quarters(dictFromData['quarters'])
    corpus = []
    real_data = []
    real_data, metadata = fetch.fetch_driver(tickers_ciks, quarters, corpus, [])
    if (len(corpus) == 0):
         return("Sorry, we could not create a model for this company and period.")
    else:
        corpus.extend(clean_data(real_data, metadata))
        model = perform_lsa(corpus)
        result = topicShower(model)
        database.push_model(model, dictFromData['model_name'])
        return(result)

def topicShower(lda_model):
    top_words_per_topic = []
    for t in range(lda_model.num_topics):
        top_words_per_topic.extend([(t, ) + x for x in lda_model.show_topic(t)])
    result = []
    for i in top_words_per_topic:
        result.append({"Topic": i[0], "Word": i[1], "Frequency": i[2]})
    return (result)

def edit_model(data):
    dictFromData = json.loads(data)
    model_id = dictFromData['modelToEdit']
    if model_id == "":
        model_id = dictFromData['models'][0]
    tickers_ciks = interface.convert_tickers(dictFromData['companies'])
    if not tickers_ciks:
        return
    quarters = interface.convert_quarters(dictFromData['quarters'])

    model = database.get_model(model_id)
    database.delete_model(model_id)
    corpus = []
    data, metadata = fetch.fetch_driver(tickers_ciks, quarters, corpus, [])
    corpus.extend(clean_data(data, metadata))
    sec_dict = Dictionary(corpus)
    sec_corpus = [sec_dict.doc2bow(text) for text in corpus]

    model.add_documents(sec_corpus)
    database.push_model(model, model_id)
    result = topicShower(model)
    return result

def view_model(data):
    dictFromData = json.loads(data)
    model_id = dictFromData['modelToEdit']
    if model_id == "":
        model_id = dictFromData['models'][0]
    model = database.get_model(model_id)
    result = topicShower(model)
    return result

    
def apply_model(data):

    dictFromData = json.loads(data)
    model_id = dictFromData['modelToEdit']
    if model_id == "":
        model_id = dictFromData['models'][0]
    tickers_ciks = interface.convert_tickers(dictFromData['companies'])
    if not tickers_ciks:
        return
    quarters = interface.convert_quarters(dictFromData['quarters'])

    model = database.get_model(model_id)
    corpus = []
    # data = []
    data, metadata = fetch.fetch_driver(tickers_ciks, quarters, corpus, [])
    corpus.extend(clean_data(data, metadata))

    sec_dict = Dictionary(corpus)
    sec_corpus = [sec_dict.doc2bow(text) for text in corpus]
    vector = model[sec_corpus]
    toReturn = ""

    for topic in vector:
        print(topic)
        for sub_item in topic:
            toReturn += str(sub_item)
            toReturn += " "

    if not toReturn:
        toReturn = "Please apply more documents to the model for accurate results."
    return toReturn

def clean_data(data, metadata):
    """
        Given data and metadata, this function will return an array of
        cleaned text.
    """
    corpus = []
    for text, pair in zip(data, metadata):
        clean_txt = clean.clean(text) #clean module
        if clean_txt:
            database.push_to_db(clean_txt, pair[0], pair[1])
            corpus.append(clean_txt)
    return corpus

def perform_lsa(corpus):

    sec_dict = Dictionary(corpus)
    sec_corpus = [sec_dict.doc2bow(text) for text in corpus]

    lsa = LSA(sec_corpus, id2word=sec_dict)

    return lsa


def perform_lda(corpus):
    """
        Given a corpus, perform LDA analysis and output the results to the console.
    """
    common_dict = Dictionary(corpus)
    common_corpus = [common_dict.doc2bow(text) for text in corpus]
    lda = LDA(common_corpus, num_topics=15, id2word=common_dict)
    print(lda)
    return lda, common_corpus, common_dict

def print_topics(topics):
    """
        Given a list of topics, this function will print out the topics
        in an easily digestible manner.
    """
    for topic_number, words in topics:
        print("\nTOPIC NUMBER " + str(topic_number + 1) + " INCLUDES TERMS SUCH AS:\n")
        for wordfreq in words.split(' + '):
            print(wordfreq)
        print("-"*30)

if __name__ == "__main__":
    print('main')
