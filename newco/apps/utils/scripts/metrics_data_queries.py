#! /usr/bin/env python

import sys
import csv
import pprint

from django.conf import settings
settings.LANGUAGE_CODE = 'en-us'

from items.models import Question, Answer, Item
from profiles.models import Profile

def pub_date(x):
    return [x.pub_date]


def author(x):
    return [x.author.get_profile()]


def items(x):
    return [item for item in x.items.all()]


def tags(x):
    return [tag for tag in x.tags.all()]


def date_joined(x):
    return [x.user.date_joined]

# list models to export
# for each model you define functions to add data to each row
models = {
    Question: (pub_date, author, items, tags),
    Answer: (pub_date, author, items, tags),
    Item: (pub_date, tags),
    Profile: (date_joined,)
}
file_suffix = 'file.2012'

for model in models:
    prefix = model._meta.verbose_name_plural.title().lower()
    print prefix
    with open('{0}.{1}.csv'.format(prefix, file_suffix), 'wb') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        data = model.objects.all()
        filters = models[model]
        for x in data:
            row = [x]
            for f in filters:
                row += f(x)
            wr.writerow(row)

sys.exit()
