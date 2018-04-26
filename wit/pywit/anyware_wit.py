# CS499, Spring 2018
# AnyWare Chat Bot (based on wit.ai)
# Authors: Aaron Mueller, Jacob Pawlak, Isaac Cook, Jordan Samuels

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from wit import Wit
import xlrd
import datetime

# Database will not be hardcoded in final version; will be command-line arg
# run by website automatically upon user login
database = "../../data/sample_database.xlsx"
data = xlrd.open_workbook(database)
sheet = data.sheet_by_name(data.sheet_names()[0])

# Ensure that program is being run correctly;
# Token should be provided in shell script
if len(sys.argv) < 2:
    print('usage: python ' + sys.argv[0] + ' <wit-token>')
    exit(1)
access_token = sys.argv[1]

### INTENT HANDLING ###
# Specify how the bot should handle each intent.
# What should it grab from the database? How should it search?

# Given an SKU number, return the location(s) of the item matching the number.
# Return format: tuple w/ sku number and array of locations
def WhereIsSKU(entities):
    if 'number' in entities:
        sku = entities['number'][0]['value']
    else:
        return (None, None)
    locations = []
    for rowno in range(1, sheet.nrows):
        if int(sheet.row(rowno)[4].value) == int(sku):
            locations.append(sheet.row(rowno)[0].value)

    return (sku, locations)

# Returns the edit distance between two strings
# source: https://stackoverflow.com/posts/32558749/revisions
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(str(s1))+1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1+1], distances_[-1])))
        distances = distances_
    return distances[-1]

# Given an item description, return the location(s) of the item matching the description.
# Return format: tuple w/ item description and array of locations
def WhereIsDesc(entities):
    if 'search_query' in entities:
        item = entities['search_query'][0]['value'] # item description from utterance
    else:
        return (None, None)
    distancelist = []
    locations = []
    # get edit distances from `item` to every item description in spreadsheet
    for rowno in range(1, sheet.nrows):
        distancelist.append(levenshteinDistance(sheet.row(rowno)[5].value.lower(), item.lower()))
    
    # go with item(s) with minimum edit distance from user's query
    min_distance = min(distancelist)
    for index, value in enumerate(distancelist):
        if value == min_distance:
            # if this item description's edit distance = minimum edit distance in distancelist,
            # add this item's location to our final location list
            locations.append(sheet.row(index+1)[0].value)

    return (item, locations)

# Find all items in spreadsheet whose expiration date is behind today's date.
# Return format: array of expired items; each element is a tuple w/ location
# and item description.
def AllExpiredItems():
    expireditems = []

    for rowno in range(1, sheet.nrows):
        expdate = sheet.row(rowno)[11].value
        if expdate == '':
            continue

        # expdate[0] = month; expdate[1] = day; expdate[2] = year
        expdate = expdate.split(' ')[0].split('/')
        now = datetime.datetime.now()
        now = [now.month, now.day, now.year]

        if int(expdate[2]) > now[2]:        # if expiration year > current year
            continue
        elif int(expdate[2]) == now[2]:     # if expiration year == current year
            if int(expdate[0]) > now[0]:    # if expiration month > current month
                continue
            elif int(expdate[0]) == now[0]: # if expiration month == current month
                if int(expdate[1]) > now[1]:# if expiration day > current day
                    continue
                else: # int(expdate[1]) <= now[1]
                    expireditems.append((sheet.row(rowno)[0].value, sheet.row(rowno)[5].value))
            else: # int(expdate[0]) < now[0]
                expireditems.append((sheet.row(rowno)[0].value, sheet.row(rowno)[5].value))
        else: # int(expdate[2]) < now[2]
            expireditems.append((sheet.row(rowno)[0].value, sheet.row(rowno)[5].value))

    return expireditems

# Find all items that are missing in the warehouse.
# Return format: array of missing items; every element is a tuple w/
# last known location and item description.
def AllMissingItems():
    missingitems = []
    for rowno in range(1, sheet.nrows):
        if sheet.row(rowno)[3].value == 'Missing':
            missingitems.append((sheet.row(rowno)[0].value, sheet.row(rowno)[5].value))

    return missingitems

# Find all items that are misplaced in the warehouse.
# Return format: array of misplaced items; every element is a tuple w/
# item's current location and item description.
def AllMisplacedItems():
    misplaceditems = []
    for rowno in range(1, sheet.nrows):
        if sheet.row(rowno)[3].value == 'Misplaced':
            misplaceditems.append((sheet.row(rowno)[0].value, sheet.row(rowno)[5].value))

    return misplaceditems

### MESSAGE HANDLING ###
# Extracts the intent from the JSON returned by
# the wit.ai API; handles it according to intent.
def handle_message(response):
    entities = response['entities']
    if 'intent' in entities:
        intent = entities['intent'][0]['value']
    else:
        intent = ''
    
    if intent == 'WhereIsSKU':
        return WhereIsSKU(entities)
    elif intent == 'WhereIsDesc':
        return WhereIsDesc(entities)
    elif intent == 'AllExpiredItems':
        return AllExpiredItems()
    elif intent == 'AllMissingItems':
        return AllMissingItems()
    elif intent == 'AllMisplacedItems':
        return AllMisplacedItems()
    else:
        return response

### MAIN ###
client = Wit(access_token=access_token)
if len(sys.argv) == 3:
    client.message(sys.argv[2], handle_message=handle_message)
else:
    print(len(sys.argv))
    client.interactive(handle_message=handle_message)
