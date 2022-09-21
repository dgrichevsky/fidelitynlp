"""
    This module contains all functions necessary to access and take raw data
    from HTML filings on the SEC website.
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 21:39:39 2018

@author:
"""
import re
import codecs
import urllib3
from bs4 import BeautifulSoup, Tag
import database
import parse
import os, sys

#sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import multiprocessing

Q_CODES = [str(q) + 'Q' + str(y) for q in range(1, 5) for y in range(12, 19)]

QUARTERLY_INDECES = {code: '/input/company_' + code + '.idx' for code in Q_CODES}
REPORT_SECTIONS = ['Risk Factors', 'Quantitative and Qualitative Disclosures about Market Risk',
                   'Management’s Discussion and Analysis of Financial Condition and \
                    Results of Operations']

def get_cik(name):
    """
    get_cik(name) takes the full name of a corporation and returns the
    corresponding CIK identifier.
    INPUT:
        name: The name of a corporation that must match the desired corporation
              in /input/cik-lookup-data.txt.
    OUTPUT:
        The CIK identifier corresponding to the company name (string).
    NOTE:
        This function is deprecated as of the get_CIKs function on the
        interface module. In case that function stops working, this is an ok
        substitute, but is undesirable because of how closely the input string
        must match names in lookup file and because it searches that file
        linearly.
    """

    with codecs.open('./input/cik-lookup-data.txt', 'r', encoding='utf-8', \
                      errors='ignore') as directory:
        for line in directory:
            if name in line:
                company_info = line

    company_info = company_info.split(':')
    cik = company_info[1].lstrip('0')
    return cik

def get_forms(cik, idx='/input/company.idx'):
    """
    get_forms(cik, idx='/input/company.idx') takes the CIK of a company and
    an optional index file path, returning all forms filed by the company in
    the quarter represented by the file.
    INPUT:
        cik: The CIK identifier of a company
        idx: The file path for a local file with all documents filed by all
             SEC registered companies in a given quarter.
    OUTPUT:
        forms: A list of the forms filed by the specified company in the
               quarter represented by the idx file.
    """

    forms = []
    script_dir = os.path.split(os.path.abspath(__file__))[0] + idx

    with open(script_dir, 'r', encoding='utf-8', errors='ignore') as quarterly:
        for line in quarterly:
            if cik in line:
                forms.append(line)
    # print("FORMS: ", forms)
    return forms


def get_10q_url(forms):
    """
    get_10q_url(forms) checks if any of the given filings are a 10-Q or 10-K,
    returning the url to the filing page on the SEC site.
    INPUT:
        forms: A list of filings made by a certain company in a certain quarter,
               represented a a string containing information about that filing.
    OUTPUT:
        The url to the filing page on the SEC website for an element in the
        input that represents a 10-Q or 10-K. If no such filing exists, returns
        an empty string.
    """
    # all_filings = []
    qfiling = None
    for filing in forms:
        # all_filings.append(filing)
        tmp = [a for a in filing.split(' ') if a != '']
        tmp = tmp[:len(tmp) - 1] # chop off new line char
        if tmp[-4] == "10-Q" or tmp[-4] == "10-K":
            # keeps track of which form is the 10-Q
            qfiling = tmp
    return format_url(qfiling) if (qfiling is not None) else ""

def format_url(qfiling):
    """
    format_url(qfiling) converts a string containing information about a filing
    to a url for that filing's page on the SEC website.
    INPUT:
        qfiling: A list of strings that contain information about a certain
                 filing.
    OUTPUT:
        The url for the filing's page on the SEC website.
    """
    # sets filing as the 10-Q
    url_pieces = qfiling[-1].split('/')
    remove_extension = url_pieces[-1].replace('.txt', '') # remove the extension from the file name
    directory_listing = remove_extension.replace('-', '')

    index_page = remove_extension + '-index.html'
    cik_directory = '/'.join(url_pieces[:len(url_pieces) - 1]) # =qfiling[-1]

    # url_save = 'https://www.sec.gov/Archives/' + cik_directory + '/' + directory_listing + '/'
    url = 'https://www.sec.gov/Archives/' + cik_directory + \
           '/' + directory_listing + '/' + index_page
    return url

def grab_form(url, cik):
    """
    grab_form(url, cik) takes a url to a filing's page on the SEC website and
    the CIK of the company that filed it, returning the text in the desired
    sections of that report.
    INPUT:
        url: The url to a certain filing's page on the SEC website.
        cik: The cik of the company that filed the report specified by url.
    OUTPUT:
        A string representing all the text in the desired sections of the
        filing. If the HTML filing itself cannot be found, returns an empty
        string.
    """
    # Get the HTML content of the url page and convert it to a bs object
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager()
    html = http.request('GET', url)
    soup = BeautifulSoup(html.data, features='html.parser')

    # Find the link to the HTML filing itself from the filing page
    tables = soup.findChildren('table')
    rows = tables[0].findChildren(['td'])
    ending = ""
    for row_num, row in enumerate(rows):
        # If the row element has 10-Q or 10-K in it and the element is not a description
        if row.string in ['10-Q', '10-K'] and (rows[row_num - 1].contents[0].name == 'a'):
            ending = rows[row_num - 1].contents[0]["href"]
            the_type = row.string
            break
    if ending == "":
        return ""
    url10q = 'https://www.sec.gov/' + ending
    html = http.request('GET', url10q)
    soup = BeautifulSoup(html.data, features='html.parser')
    isolated_sections_text = isolate_section_reports(soup, REPORT_SECTIONS)

    return isolated_sections_text

def find_stop_href(result):
    """
    find_stop_href(result) finds the tag that represents the section in the
    filing that immediately follows the desired section.
    INPUT:
        result: A BeautifulSoup object that represents the entry in the
                filing's table of contents for the desired section.
    OUTPUT:
        The anchor for the section of the filing immediately following the
        desired section.
    """
    element = result.next_element
    to_return = []
    seen_tr = False
    while element.next_element:
        if isinstance(element, Tag):
            if element.name == "tr":
                seen_tr = True
            if element.get("href") and seen_tr:
                to_return.append(element.get("href")[1:])
                break
        element = element.next_element
    return to_return

def isolate_section_reports(report, sections):
    """
    isolate_section_reports(report, sections) takes a BeautifulSoup object of
    a 10-Q or 10-K filing and a list of sections for which text will be pulled.
    INPUT:
        report: A BeautifulSoup object for the HTML version of a 10-Q or 10-K
        sections: A list of section names to pull text from
    OUTPUT:
        A string representing the text of all specified sections in the report.
    """

    href_start_list = []
    href_stop_list = []
    for section in sections:
        regex_match = ("[a-zA-Z0-9]*" + section + "[a-zA-Z0-9]*")
        for result in report.find_all('a', href=True, text=re.compile(regex_match, re.IGNORECASE)):
            href_start_list.append(str(result["href"])[1:])
            href_stop_list.extend(find_stop_href(result))

    section = []
    for index, value in enumerate(href_start_list):
        start = value
        stop = href_stop_list[index]
        temp = stop
        yes = report.find(attrs={'name': start})
        if yes is not None:
            temp = yes["name"]
        while temp != stop:
            if yes is None:
                break
            if isinstance(yes, Tag):
                if yes.get("name"):
                    temp = yes["name"]
                section.append(yes.get_text(' ', strip=True))
            yes = yes.next_element
    return(" ").join(section)

##########################################################
#                       Drivers
##########################################################

def fetch(name):
    """
    fetch(name) is the most basic driver, pulling down
    the filing for a specified company for the default quarter.
    INPUT:
        name: The name of a company.
    OUTPUT:
        The text in the desired sections of the report.
    NOTE: This is not currently in use but is useful to
    understand how the different parts of this module fit together.
    """

    cik = get_cik(name)
    forms = get_forms(cik)
    url = get_10q_url(forms)
    text = grab_form(url, name)
    return text

def fetch_multiple_qs(name, q_codes):
    """
    fetch_multiple_qs(name, q_codes) pulls down text from multiple
    quarters for a given company.
    INPUT:
        name: The name of a company.
        q_codes: A list of quarter codes to pull text from (e.g. 3Q17).
    OUTPUT:
        text: A list of strings, each representing the text from all desired
              sections of a report.
        metadata: A list of tuples, each with the name of the company and a
                  quarter code. The text at the same list index in the text
                  return variable is the text from the file for the company and
                  quarter described in metadata.
    NOTE: This is not currently in use but demonstrates how to find and return
    data from multiple filings.
    """

    text = []
    metadata = []
    cik = get_cik(name)
    for code in q_codes:
        forms = get_forms(cik, idx=QUARTERLY_INDECES[code])
        url = get_10q_url(forms)
        if url != "":
            text.append(grab_form(url, name))
            metadata.append((name, code))
    return text, metadata

def fetch_multiple_qs_with_CIK(cik, q_codes, count, total_docs, ticker):
    text = []
    metadata = []
    for code in q_codes:
        forms = get_forms(cik, idx=QUARTERLY_INDECES[code])
        url = get_10q_url(forms)
        print("URLS: ", url)
        if url != "":
            text.append(grab_form(url, cik))
            metadata.append((cik, code))
        count += 1
        # printProgressBar(count, total_docs, 'Fetching Docs:', 'Currently Fetching for ' + ticker, length=30)
    return text, metadata, count

def fetch_driver(companies_dict, quarters, corpus, data):
    total_docs = len(companies_dict) * len(quarters)
    doc_count = 0
    metadata = []
    # printProgressBar(doc_count, total_docs, 'Fetching Docs:', length = 30)
    for ticker, cik in companies_dict.items():
        quarters_to_fetch = []
        for quarter in quarters:
            cursor, count = database.get_from_db(cik, quarter)
            if count == 0:
                quarters_to_fetch.append(quarter)
            else:
                corpus.append(cursor[0]['words'])
                doc_count += 1
                # printProgressBar(doc_count, total_docs, 'Fetching Docs:', 'Currently Fetching for ' + ticker, length = 30)
        raw, linkeddata, doc_count = fetch_multiple_qs_with_CIK(cik, quarters_to_fetch, doc_count, total_docs, ticker) #fetch module
        for raw_out, formdata in zip(raw, linkeddata):
            data.append(raw_out) #parse module
            metadata.append(formdata)
    return data, metadata

def simple_fetch(cik_q_code_tuple):
    """
    simple_fetch(cik_q_code_tuple) is a simple fetch function that returns
    text and metadata for a filing specified by a CIK and quarter code.
    INPUT:
        cik_q_code_tuple: A tuple containing the CIK of a company and a
                          quarter code.
    OUTPUT:
        A tuple containing the text from the desired filing and the input tuple.
    """

    cik = cik_q_code_tuple[0]
    code = cik_q_code_tuple[1]
    forms = get_forms(cik, idx=QUARTERLY_INDECES[code])
    url = get_10q_url(forms)
    text = grab_form(url, cik)
    # return input in a tuple in case processes finish
    # out of order
    return (text, cik_q_code_tuple)

def fetch_multiprocessing(tickers_ciks, quarters, corpus):
    """
    fetch_multiprocessing(tickers_ciks, quarters, corpus) is a comprehensive
    fetching function for multiple filings that uses multiprocessing.
    INPUT:
        tickers_ciks: A dictionary with keys as tickers and values as
                      corresponding CIKs.
        quarters: A list of quarter codes to pull data from for each company.
        corpus: The existing corpus (likely empty)
    OUTPUT:
        data: A list of strings, each containing the text of the desired
              sections of a specific filing.
        metadata: A list of corresponding information for each element in
                  data; a tuple containing the cik and quarter code for that
                  filing.
    """
    data = []
    metadata = []
    tasks = []

    for cik in tickers_ciks.values():
        for quarter in quarters:
            cursor, count = database.get_from_db(cik, quarter)
            if count == 0:
                tasks.append((cik, quarter))
            else:
                corpus.append(cursor[0]['words'])

    pool = multiprocessing.Pool()
    tuple_list = pool.map(simple_fetch, tasks)

    for text, linkeddata in tuple_list:
        data.append(text)
        metadata.append(linkeddata)

    return data, metadata
