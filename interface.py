"""
    This module serves as the interface for the engine that allows users
    to enter quarters and tickers. The module will then return the matching
    CIKs for every stock ticker and quarter.
"""

import re
import requests
import os

# This function borrowed from https://gist.github.com/ddd1600/3934032
def get_CIKs(tickers):
    """
    get_CIKs(tickers) returns the corresponding CIK Identifier for each ticker
    in a list of tickers.
    INPUT:
        tickers: A list of tickers (strings)
    OUTPUT:
        A dictionary with tickers as keys and CIK identifiers as values;
        types of both keys and values are strings.
    """

    url = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    cik_re = re.compile(r'.*CIK=(\d{10}).*')
    cik_dict = {}
    for ticker in tickers:
        f = requests.get(url.format(ticker), stream=True)
        results = cik_re.findall(f.text)
        if results:
            results[0] = int(re.sub('\.[0]*', '.', results[0]))
            cik_dict[str(ticker).upper()] = str(results[0])
    return cik_dict

def convert_tickers(result):
    cik_dict = {}
    for tkr in result.split(' '):
        result_pair = get_CIKs([tkr])
        if result_pair:
            if not cik_dict.get(list(result_pair.values())[0]):
                cik_dict.update(result_pair)
        else:
            print('Sorry, we could not find ' + tkr + '.')
    return cik_dict

def convert_quarters(result):
    regex = re.compile('[1-4]Q[1-9][0-9]')
    qlist = []
    if '->' in result:
        range = result.split('->')
        rangeresult = handle_range(range)
        if rangeresult:
            qlist = add_valid_qcodes(rangeresult, qlist)
    else:
        qlist = add_valid_qcodes(result.split(' '), qlist)
    if not qlist:
        return ['1Q18']
    return qlist

def ask_tickers():
    """
    ask_tickers() prompts the user for a string of tickers, returning a
    dictionary of those tickers and their corresponding CIKS. The user may
    choose to enter the tickers via the command line or upload a text file with
    one ticker per line.
    INPUT:
        None
    OUTPUT:
        A dictionary with tickers as keys and CIK identifiers as values;
        types of both keys and values are strings.
    """

    result = ''
    cik_dict = {}
    while result != '-':
        result = input('Please enter a ticker, type UPLOAD to import a file of ticker names, or type "-" to run: ')
        if result != '-' and result != 'UPLOAD':
            for tkr in result.split(' '):
                result_pair = get_CIKs([tkr])
                if result_pair:
                    if not cik_dict.get(list(result_pair.values())[0]):
                        cik_dict.update(result_pair)
                else:
                    print('Sorry, we could not find ' + tkr + '.')
        elif result == 'UPLOAD':
            fpath = input('Please provide a file path: ')
            for ticker in import_tickers(fpath):
                result_pair = get_CIKs([ticker])
                if result_pair:
                    cik_dict.update(result_pair)
                else:
                    print('Sorry, we could not find ' + ticker + '.')
    return cik_dict

def ask_quarters():
    """
    ask_quarters() returns a list of quarters parsed from user commandline
    input; the accepted format is [QUARTER NUMBER]Q[YEAR (YY)]. Default on no
    input is 1Q18.
    INPUT:
        None
    OUTPUT:
        A list of quarter codes (strings).
    """

    regex = re.compile('[1-4]Q[1-9][0-9]')
    result = ''
    qlist = []
    while result != '-':
        result = input('Please enter fiscal quarters in the form [QUARTER NUMBER]Q[YEAR] \n' +
                       '(for example, 3Q17 for third quarter 2017). The default is 1Q18 if no \n' +
                       'quarters are given. To specify a range, seperate two quarters by "->" ' +
                       '(for example, 2Q17->3Q18). Enter - to run. ')
        if result != '-':
            if '->' in result:
                range = result.split('->')
                rangeresult = handle_range(range)
                if rangeresult:
                    qlist = add_valid_qcodes(rangeresult, qlist)
            else:
                qlist = add_valid_qcodes(result.split(' '), qlist)

    if not qlist:
        return ['1Q18']
    return qlist

def add_valid_qcodes(qcodes, qlist):
    """
    add_valid_qcodes(qcodes, qlist) inserts the quarter codes in qcodes into
    qlist provided they are formatted correctly and are not already in qlist.
    INPUT:
        qcodes: A list of quarter codes to insert.
        qlist: A list of quarter codes to add to.
    OUTPUT:
        qlist: An updated list including all quarter codes in qcodes that were
        formatted correctly and not already in qlist.
    """

    regex = re.compile('[1-4]Q[1-9][0-9]')
    for qc in qcodes:
        if regex.match(qc):
            if qc not in qlist:
                qlist.append(qc)
        else:
            print('Sorry, the format of "' + qc + '" is not correct.')
    return qlist

def handle_range(range):
    """
    handle_range(range) returns a list of quarters specified by a range.
    INPUT:
        range: A list containing two elements, the first of which is the start
        of the range, the latter of which is the end of the range.
    OUTPUT:
        A list representing all quarters inbetween the specified quarters,
        inclusive.
    """

    priorqs = range[0].split(' ')
    latterqs = range[-1].split(' ')
    rangestart = priorqs[-1]
    rangeend = latterqs[0]

    if len(add_valid_qcodes([rangestart, rangeend], [])) < 2:
        print('Format of quarter codes in specified range was not valid. Please try again.\n')
        return []

    if (int(rangestart[2:]) > int(rangeend[2:])) or ((int(rangestart[2:]) == int(rangeend[2:])) and (int(rangestart[0]) > int(rangeend[0]))):
        print('Please make sure the beginning of your range is before the end of your range.\nNone of the quarters in that input were added.')
        return []

    rangeqs = []
    rangeqs.append(rangestart)
    currq = priorqs[-1]
    while currq != rangeend:
        if (currq[0] == '4'):
            currq = '1Q' + str(int(currq[2:]) + 1)
        else:
            currq = str(int(currq[0]) + 1) + currq[1:]
        rangeqs.append(currq)
    rangeqs = list(set(priorqs) | set(rangeqs))
    rangeqs = list(set(latterqs) | set(rangeqs))
    return rangeqs

def import_tickers(filename):
    """
    import_tickers(filename) reads in a file of tickers and returns the
    specified tickers in a list.
    INPUT:
        filename: The path name for a text file that contains one ticker per line.
    OUTPUT:
        A list of tickers (strings).
    """

    tickers = []
    if os.path.exists(filename):
        fp = open(filename, 'r')
        for name in fp:
            tickers.append(name[:-1])
        fp.close()
    else:
        print('Sorry, we could not find that file.')
    return tickers

def ask_use():
    """
    ask_use() prompts the user to choose which functionality to execute.
    INPUT:
        None
    OUTPUT:
        The user's chosen functionality (A: Build a new model
                                         B: Edit an existing model
                                         C: Apply to an existing model)
    """

    answer = ''
    while answer not in ['A', 'B', 'C']:
        answer = input('Would you like to:\nA) Build a new model\nB) Edit an old model\nC) Apply a new corpus to an old model\nPlease enter the letter corresponding to your task: ')
        if answer not in ['A', 'B', 'C']:
            print('Sorry, that was not one of the choices. Please enter A, B, or C.')
    return answer

def ask_model():
    """
    ask_model() prompts the user to search for an existing model to edit or
    apply a corpus to.
    INPUT:
        None
    OUTPUT:
        The name of a model the user wants to use.
    """

    model_name = input('Please give the name of the saved model you wish to load.\nOr, if you wish to browse saved models, enter "BROWSE": ')
    if model_name == 'BROWSE':
        savedmodels = [mname for mname in os.listdir('models/') if '.projection' not in mname and mname != 'README.md']
        savedmodels.sort()
        print('The following models are currently saved:\n')
        for model in savedmodels:
            print(model)
        model_name = input('\nWhich model would you like to load? ')
    return model_name

def ask_save_name():
    """
    ask_save_name() is a wrapper for input that prompts the user to provide a
    name under which the program will save a model.
    INPUT:
        None
    OUTPUT:
        The name of the model to be saved (string).
    """

    return input('Please enter the name you want to give this model: ')
