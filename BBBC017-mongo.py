#!/usr/bin/env python

# BBBC017-image.py <metadata.json> <features-mongo.json> <screen-info.json>

import json
import os
from pymongo import MongoClient
import sys

def main(argv=None):
    metadata_file = argv[1]
    metadata = []
    with open(metadata_file) as f:
        for line in f:
            metadata.append(json.loads(line))
            
    feature_file = argv[2]
    feature = []
    with open(feature_file) as f:
        for line in f:
            feature.append(json.loads(line))
            
    info_file = argv[3]
    info = []
    with open(info_file) as f:
            info = eval(f.read())

    for document in metadata:
        col = document['column']
        _id = document['_id']
        document['column'] = "{0:02d}".format(col)
        document['_id'] = 'BBBC017-' + _id
        document['screen'] = 'BBBC017'
        document['control_pos'] = False

    for document in feature:
        _id = document['_id']
        document['_id'] = 'BBBC017-' + _id
        
        if 'neighbours' in document:
            new_array = []
            for item in document['neighbours']:
                new_array.append('BBBC017-' + item)
            document['neighbours'] = new_array

    client = MongoClient('localhost', 27017)
    db_micro = client['microscopium']
    micro_images = db_micro['samples']
    micro_screens = db_micro['screens']

    foo = micro_images.insert(metadata)

    for document in feature:
        current_id = document['_id']
        micro_images.update({'_id': current_id}, {"$set": document})

    micro_screens.insert(info)

if __name__ == '__main__':
    main(sys.argv)