"""
    This module will take in uncleaned, raw text and will return text that
    has been cleaned by removing extra whitespace, stopwords, extra numbers
    and puncutation etc.
"""
import re
import unicodedata
import nltk
from nltk.corpus import stopwords
import constants

def clean(text):
    """
        This function will take in uncleaned, raw text and will return text that
        has been cleaned by removing extra whitespace, stopwords, extra numbers
        and puncutation etc.

        Parameters: text (array of words)
        Return: removed_stop (array of words)
    """
    common_words = set(stopwords.words('english'))
    text_token = nltk.word_tokenize(text)
    removed_non_ascii = [unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').\
                         decode('utf-8', 'ignore').lower() for word in text_token]
    removed_stop = []
    num_regex = re.compile('[0-9]+')
    punctuation_regex = re.compile('_+')
    for word in removed_non_ascii:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            if new_word not in common_words and new_word not in constants.MONTHS:
                removed_stop.append(new_word)
    removed_stop = [i for i in removed_stop if not num_regex.search(i)]
    removed_stop = [i for i in removed_stop if not punctuation_regex.search(i)]
    return removed_stop
