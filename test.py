#!/usr/bin/env python

import unicodecsv
from lxml import etree
from foxpath import test as ftest
from lib import ctests
current_test = "activity-date[@type='end-planned']/@iso-date or activity-date[@type='end-planned']/text() or activity-date[@type='end-actual']/@iso-date or activity-date[@type='end-actual']/text() or transaction-date/@iso-date (for any transaction[transaction-type/@code='D']|transaction[transaction-type/@code='E']) is less than 13 months ago?"
from lib import codelists

def run_file_test(filename, test, test_name, exclude_hierarchies):
    x = ftest.test_doc_json_out(filename, 
                                test, 
                                current_test, 
                                lists=codelists.CODELISTS,
                                test_name=test_name,
                                exclude_hierarchies=exclude_hierarchies)
    return x['summary']

def get_avg_project_size(f, projectsize_csv):
    doc = etree.parse(f)
    activities = doc.xpath('//iati-activity')
    num_activities = len(activities)
    budgets = float(0)
    commitments = float(0)
    disbursements = float(0)
    h1 = len(doc.xpath('//iati-activity[@hierarchy="1"]')) if doc.xpath('//iati-activity/@hierarchy="1"') else 0
    h2 = len(doc.xpath('//iati-activity[@hierarchy="2"]')) if doc.xpath('//iati-activity/@hierarchy="2"') else 0
    h3 = len(doc.xpath('//iati-activity[@hierarchy="3"]')) if doc.xpath('//iati-activity/@hierarchy="3"') else 0
    h4 = len(doc.xpath('//iati-activity[@hierarchy="4"]')) if doc.xpath('//iati-activity/@hierarchy="4"') else 0
    
    for act in activities:
        currency=(doc.xpath('//iati-activities/@default-currency') or 
                  act.xpath('@default-currency'))
        currency = currency[0] if currency else ""
        if act.xpath('budget'):
            for b in act.xpath('budget'):
                budgets += float(b.xpath('value/text()')[0])
        if act.xpath('transaction/transaction-type/@code'):
            for c in act.xpath('transaction[transaction-type/@code="C"]'):
                commitments += float(c.xpath('value/text()')[0])
            for d in act.xpath('transaction[transaction-type/@code="D"]|transaction[transaction-type/@code="E"]'):
                disbursements += float(d.xpath('value/text()')[0])

    print budgets, commitments, disbursements, num_activities
    conversion = ctests.currency_usd[currency]
    budgets_avg = (budgets/num_activities)
    commitments_avg = (commitments/num_activities)
    disbursements_avg = (disbursements/num_activities)
    if h1 >0: 
        budgets_avg_h1 = (budgets/h1)
        commitments_avg_h1 = (commitments/h1)
        disbursements_avg_h1 = (disbursements/h1) 
    else: 
        budgets_avg_h1 = (budgets/num_activities)
        commitments_avg_h1 = (commitments/num_activities)
        disbursements_avg_h1 = (disbursements/num_activities)

    projectsize_csv.writerow({
        'filename':f, 
        'num': num_activities,
        'budgets': budgets,
        'commitments': commitments,
        'disbursements': disbursements,
        'currency': currency,
        'h1': h1,
        'h2': h2,
        'h3': h3,
        'h4': h4,
        'budgets_avg': budgets_avg,
        'commitments_avg': commitments_avg,
        'disbursements_avg': disbursements_avg,
        'budgets_avg_h1': budgets_avg_h1,
        'commitments_avg_h1': commitments_avg_h1,
        'disbursements_avg_h1': disbursements_avg_h1,
        'conversion': conversion
        })

def run(filenames, tests, current_test, exclude_hierarchies):
    fieldnames = ['filename', 'test', 'success', 'fail', 'percentage']
    csv_f = open('results.csv', 'w')
    csv = unicodecsv.DictWriter(csv_f, fieldnames)
    csv.writeheader()

    projectsize_csv_f = open('projectsize.csv', 'w')
    projectsize_fieldnames = ['filename', 
                              'num', 
                              'budgets', 
                              'commitments', 
                              'disbursements', 
                              'currency', 
                              'h1', 
                              'h2', 
                              'h3', 
                              'h4',
                              'budgets_avg',
                              'commitments_avg',
                              'disbursements_avg',
                              'budgets_avg_h1',
                              'commitments_avg_h1',
                              'disbursements_avg_h1',
                              'conversion',
                              ]
    projectsize_csv = unicodecsv.DictWriter(projectsize_csv_f, projectsize_fieldnames)
    projectsize_csv.writeheader()

    for f in filenames:

        for t in tests:
            data = run_file_test(f, 
                                 t['expression'],
                                 t['name'], 
                                 exclude_hierarchies)
            csv.writerow({
                'filename':f, 
                'test':t['name'], 
                'success':data['success'], 
                'fail':data['fail'],
                'percentage': data['percentage'],
                })
        
        get_avg_project_size(f, projectsize_csv)        

    projectsize_csv_f.close()
    csv_f.close()

def get_filenames():
    csv_f = open('data/metadata.csv')
    csv = unicodecsv.DictReader(csv_f)
    files_to_test = []
    for row in csv:
        print row
        if row['official'] == '1':
            files_to_test.append("data/"+row['filename'])
    return files_to_test

if __name__ == '__main__':
    filenames=get_filenames()
    tests = ctests.country_tests
    exclude_hierarchies = ctests.exclude_hierarchies
    print tests
    run(filenames, tests, current_test, exclude_hierarchies)
