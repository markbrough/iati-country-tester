#!/usr/bin/env python

import unicodecsv
# read metadata file => get each country
# read results file => get
#   - simple avg
#   - weighted avg by % in country

metadata_f = open('data/metadata.csv')
metadata_csv = unicodecsv.DictReader(metadata_f)
results_f = open('results.csv')
results_csv = unicodecsv.DictReader(results_f)

files_weights = {}

for row in metadata_csv:
    if row['official'] == '1':
        files_weights['data/'+row['filename']] = row['pct']

results = {}

for row in results_csv:
    if row['test'] not in results:
        results[row['test']] = {
            'test': row['test'],
            'success': 0.0,
            'fail': 0.0,
            'percentage_avg': 0.0,
            'percentage_weighted_avg': 0.0
            }
    rt = results.get(row['test'])

    if (row['test'] == "1 - Pipeline/identification projects" and float(row['percentage']) > 0):
        row['percentage'] = 100.00

    rt['success'] += float(row['success'])
    rt['fail'] += float(row['fail'])
    rt['percentage_avg'] += float(row['percentage']) / float(len(files_weights))
    weight = files_weights.get(row['filename'])
    print row['filename']
    print weight
    rt['percentage_weighted_avg'] += float(row['percentage'])*float(weight)

    results[row['test']] = rt

consolidated_results_f = open('consolidated_results.csv', 'w')
fieldnames = ['test', 'success', 'fail', 'percentage_avg', 'percentage_weighted_avg']
consolidated_results_csv = unicodecsv.DictWriter(consolidated_results_f, fieldnames)
consolidated_results_csv.writeheader()
for r in results.values():
    print r
    consolidated_results_csv.writerow(r)
print results
