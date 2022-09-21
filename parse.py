"""
    This module writes data to new files
"""

import codecs

# only prints out 1 quarter because each one gets written over

def parse(cik, raw):
    """
        Given a company name and a set of words, this function will
        open or create a file and write the words to said file.
    """
    file_10qparsed = codecs.open("./companytext/" + cik + "10qparsed.txt", "w+", encoding='utf-8')
    file_10qparsed.write(raw)
    file_10qparsed.close()
    return raw






