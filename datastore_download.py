#!/usr/bin/env python

from lxml import etree
import urllib2
import os

URL = "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?recipient-country=%s&stream=True"

def download_data(country):
    def write_data(doc):
        path = os.path.join("iati_data_" + country + '.xml')
        iati_activities = etree.tostring(doc.find("iati-activities"))
        with file(path, 'w') as localFile:
            localFile.write(iati_activities)

    the_url = URL % (country)
    print the_url

    xml_data = urllib2.urlopen(the_url, timeout=60).read()
    doc = etree.fromstring(xml_data)
    write_data(doc)

if __name__ == '__main__':
    import sys
    import os
    args = sys.argv
    args.pop(0)

    for arg in args:
        download_data(arg)
