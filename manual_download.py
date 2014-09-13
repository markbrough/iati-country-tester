#!/usr/bin/env python

import os
import unicodecsv
import urllib

def download_and_replace(filename, url):
    print "Requesting", url
    print "Writing to", filename
    urllib.urlretrieve(url, 'data/'+filename)

if __name__ == '__main__':
    csv_f = open('data/metadata.csv')
    csv = unicodecsv.DictReader(csv_f)
    for row in csv:
        if row['url'] != "":
            print row['url']
            download_and_replace(row['filename'], row['url'])
