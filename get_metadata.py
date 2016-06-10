import requests
import sys
import os
import json
from datetime import datetime

def sort_articles(zendesk_domain, file_name, email=None, password=None):
    sections = get_sections(zendesk_domain, email, password)
    categories = get_categories(zendesk_domain, email, password)
    categories_dict = {}
    all_articles = {}
    for category in categories['categories']:
        if "Cloud" in category['name']:
            category_name = str(category['id']) + ' ' + category['name']
            if not category_name in all_articles.keys():
                all_articles[category_name] = {}

            for section in sections['sections']:
                if section['category_id'] == category['id']:
                    section_name = str(section['id']) + ' ' + section['name']
                    articles = get_articles(zendesk_domain, section['id'])
                    if not section_name in all_articles[category_name].keys():
                        all_articles[category_name][section_name] = []

                    for article in articles['articles']:
                        all_articles[category_name][section_name].append(article)

    f = open(file_name, 'w')
    f.write ('All articles = ')
    for category in all_articles.keys():
        for section in all_articles[category].keys():
            for article in all_articles[category][section]:
                f.write(str(article['id']) + '|')

    f.write('\n')

    for category in all_articles.keys():
        for section in all_articles[category].keys():
            f.write(category + ', ' + section + ' = ')
            for article in all_articles[category][section]:
                f.write(str(article['id']) + '|')

            f.write('\n')

    f.close

def get_articles(zendesk_domain, section_id, email=None, password=None):
    session = requests.Session()
    if email and password:
        session.auth = (email, password)

    url = zendesk_domain + "/api/v2/help_center/sections/" + str(section_id) + "/" + "articles.json?per_page=100"
    response_raw = session.get(url)
    articles = json.loads(response_raw.content)
    next_page = articles['next_page']
    while next_page is not None:
        page_raw = session.get(next_page)
        page = json.loads(page_raw.content)
        articles['articles'] = articles['articles'] + page['articles']
        next_page = page['next_page']

    return articles

def get_sections(zendesk_domain, email=None, password=None):
    session = requests.Session()
    if email and password:
        session.auth = (email, password)

    response_raw = session.get(zendesk_domain + "/api/v2/help_center/sections.json?per_page=100")
    sections = json.loads(response_raw.content)
    next_page = sections['next_page']
    while next_page is not None:
        page_raw = session.get(next_page)
        page = json.loads(page_raw.content)
        sections['sections'] = sections['sections'] + page['sections']
        next_page = page['next_page']

    return sections

def get_categories(zendesk_domain, email=None, password=None):
    session = requests.Session()
    if email and password:
        session.auth = (email, password)

    response = session.get(zendesk_domain + "/api/v2/help_center/categories.json?per_page=1000")
    categories = json.loads(response.content)
    return categories

# Grab variables for authentication and the url from the environment
env = os.environ

try:
    email = env['EMAIL']
except:
    email = None

try:
    password = env['ZENDESK_PASS']
except:
    password = None

try:
    zendesk_domain = env['ZENDESK_URL']
except:
    zendesk_domain = input("Enter the zendesk url: ")
file_name = 'metadata.txt'
sort_articles(zendesk_domain, file_name, email, password)
