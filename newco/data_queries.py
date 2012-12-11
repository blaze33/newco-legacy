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

question_data=Question.objects.all()
filename = 'questions.%s.%06d.csv' %("file",2012)
csv_file = open(filename, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

for i in range(len(question_data)):
    list=[]
    q=question_data[i]
    pprint.pprint(q)
    list.append(q);
    list.append(q.pub_date)
    list.append(q.author.get_profile())
    pprint.pprint(q.author.get_profile())
    if q.items.all:
        for item in q.items.all():
            list.append(item);
    if q.tags.all:
        for tag in q.tags.all():
            list.append(tag)
    wr.writerow(list)
    
answer_data=Answer.objects.all()
filename = 'answers.%s.%06d.csv' %("file",2012)
csv_file = open(filename, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
#wr.writerow(data)

for i in range(len(answer_data)):
    list=[]
    answer=answer_data[i]
    pprint.pprint(answer)
    list.append(answer);
    list.append(answer.pub_date)
    list.append(answer.author.get_profile())
    q_answer=answer.question
    if q_answer.items.all:
        for item in q_answer.items.all():
            list.append(item);
    if q_answer.tags.all:
        for tag in q_answer.tags.all():
            list.append(tag)
    wr.writerow(list)

item_data=Item.objects.all()
filename = 'items.%s.%06d.csv' %("file",2012)
csv_file = open(filename, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

for i in range(len(item_data)):
    list=[]
    item=item_data[i]
    pprint.pprint(item)
    list.append(item);
    list.append(item.pub_date)
    for tag in item.tags.all():
        list.append(tag)
    wr.writerow(list)

profile_data=Profile.objects.all()
filename = 'profiles.%s.%06d.csv' %("file",2012)
csv_file = open(filename, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

for i in range(len(profile_data)):
    list=[]
    profile=profile_data[i]
    pprint.pprint(profile)
    list.append(profile);
    list.append(profile.user.date_joined)
    wr.writerow(list)
