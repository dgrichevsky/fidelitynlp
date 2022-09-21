"""
    This module allows users to push and retrieve cleaned filings from
    our database
"""

from pymongo import MongoClient
import json
import pickle

CLIENT = MongoClient('mongodb://root:password1@ds113693.mlab.com:13693/nlp_test')
DB = CLIENT['nlp_test']
COLLECTION = DB.test

MODEL_CLIENT = MongoClient('mongodb://root:password1@ds139956.mlab.com:39956/models')
MODEL_DB = MODEL_CLIENT['models']
MODEL_COLLECTION = MODEL_DB.model

def push_to_db(words, cik, date):
    """
        Pushes an array of words, a company name and the quarter of the filing
        to the database
    """
    if words is None:
        return
    data = {
        'cik': cik,
        'quarter': date,
        'words': words
    }
    COLLECTION.insert_one(data)

def get_from_db(cik, date):
    """
        Given a company name and a quarter, this function will retrieve all
        of the corresponding forms in the form of a document.

        Returns an array of documents and a count of documents.
    """
    documents = COLLECTION.find({"cik":cik, "quarter": date})
    count = COLLECTION.count_documents({"cik":cik, "quarter": date})

    return documents, count

def push_model(model, name):
    toPush = pickle.dumps(model)
    MODEL_COLLECTION.insert_one({'model': toPush, 'id':name})

def delete_model(name):
    MODEL_COLLECTION.delete_one({'id': name})
    return name

def get_model(name):
    cursor = MODEL_COLLECTION.find({'id': name})
    for record in cursor:
        return pickle.loads(record['model']);

def get_models():
    cursor = MODEL_COLLECTION.find()
    tempArr = []
    for record in cursor:
        tempArr.append(record['id'])
    return "thisisaseperator".join(tempArr)
     