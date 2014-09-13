#!/usr/bin/env python

import urllib2
from lxml import etree
import unicodecsv

# This will actually often not work, as many implementing organisations'
# activities will be funded by donor activities that are not tagged with the
# country (e.g. a very large multi-country program).

def check_traceability(directory):
    metadata_f = open(directory+"/metadata.csv", 'r')
    metadata = unicodecsv.DictReader(metadata_f)
    donor_filenames = []
    all_filenames = []
    donor_activities = []
    for row in metadata:
        if (row['official'] == '1'):
            donor_filenames.append(row['filename'])
        all_filenames.append(row['filename'])
    # Build record of iati-identifiers
    for df in donor_filenames:
        doc = etree.parse(directory + "/" + df)
        donor_activities += doc.xpath('//iati-activity/iati-identifier/text()')
    for af in all_filenames:
        doc = etree.parse(directory + "/" + af)
        activities = doc.xpath("//iati-activity")
        for act in activities:
            provideracts = act.xpath('transaction/provider-org/@provider-activity-id')
            for po in provideracts:
                if po.startswith('GB-1'): 
                    print po
                    print act.xpath('reporting-org/text()')

if __name__ == '__main__':
    import sys
    args = sys.argv
    args.pop(0)
    for directory in args:
        check_traceability(directory)
