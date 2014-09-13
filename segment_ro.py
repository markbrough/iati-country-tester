#!/usr/bin/env python

# Takes apart large IATI XML files and outputs one file per reporting org.

# Copyright 2013 Mark Brough.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License v3.0 as 
# published by the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

from lxml import etree
import unicodecsv
import sys
import os

# FIXME: if there are multiple countries/countries+regions, then don't
# output to the same file.
def segment_file(prefix, filename, output_directory):
    print "Segmenting file", filename
    doc=etree.parse(os.path.join(filename))
    extorgs = set(doc.xpath("//iati-activity/reporting-org/@ref"))
    print "Found orgs", list(extorgs)
    
    out = {}

    iatiactivities = doc.xpath('//iati-activities')[0]

    for org in extorgs:
        out[org] = {
            'title': prefix.upper() + " Activity file " + org,
            'data': etree.Element('iati-activities')
        }
        for attribute, attribute_value in iatiactivities.items():
            out[org]['data'].set(attribute, attribute_value)

    activities = doc.xpath('//iati-activity')

    for activity in activities:
        if (activity.xpath("reporting-org/@ref")) and (activity.xpath("reporting-org/@ref")[0] != ""):
            org = activity.xpath("reporting-org/@ref")[0]
            out[org]['orgname'] = activity.xpath("reporting-org/text()")[0] if activity.xpath("reporting-org/text()") else ""
            out[org]['orgtype'] = activity.xpath("reporting-org/@type")[0] if activity.xpath("reporting-org/@type") else ""
            out[org]['data'].append(activity)

    # Create metadata file...
    fieldnames = ['org', 'orgname', 'orgtype', 'official', 'filename', 'url', 
                  'package_name',  'package_title']
    metadata_file = open(output_directory + 'metadata.csv', 'w')
    metadata = unicodecsv.DictWriter(metadata_file, fieldnames)
    metadata.writeheader()

    for org, data in out.items():
        print "Writing data for", org
        # Check not empty
        if data['data'].xpath('//iati-activity'):
            d = etree.ElementTree(data['data'])
            d.write(output_directory+prefix+"-"+org+".xml", 
                    pretty_print=True, 
                    xml_declaration=True,
                    encoding="UTF-8")
            metadata.writerow({
                'org':org, 
                'orgname':data['orgname'], 
                'orgtype':data['orgtype'], 
                'filename':prefix+"-"+org+'.xml',
                'package_name': prefix+"-"+org,
                'package_title': data['title']})
    print "Finished writing data, find the files in", output_directory

    metadata_file.close()

if __name__ == '__main__':
    arguments = sys.argv
    arguments.pop(0)
    prefix = arguments[0]
    arguments.pop(0)
    filenames = arguments
    output_directory = 'data/'

    if not filenames:
        print "No filenames"
    else:
        for filename in filenames:
            segment_file(prefix, filename, output_directory)
