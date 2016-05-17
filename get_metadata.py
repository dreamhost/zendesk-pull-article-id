import requests
import sys
import os
import json
from datetime import datetime

def sort_articles(zendesk_domain, email=None, password=None):
    sections = get_sections(zendesk_domain, email, password)
    categories = get_categories(zendesk_domain, email, password)
    categories_dict = {}
    all_articles = []
    articles_by_section = {}
    articles_by_category = {}
    for category in categories['categories']:
        if "Cloud" in category['name']:
            if not category['id'] in articles_by_category.keys():
                articles_by_category[category['id']] = []

            for section in sections['sections']:
                if section['category_id'] == category['id']:
                    articles = get_articles(zendesk_domain, section['id'])
                    if not (str(section['id']) + ' ' + section['name']) in articles_by_section.keys():
                        articles_by_section[str(section['id']) + ' ' + section['name']] = []

                    for article in articles['articles']:
                        all_articles.append(article)
                        articles_by_section[str(section['id']) + ' ' + section['name']].append(article)
                        articles_by_category[category['id']].append(article)

    f = open('metadata', 'w')
    f.write ('All articles = ')
    for article in all_articles:
        f.write(str(article['id']) + '|')

    f.write('\n')
    for section in articles_by_section.keys():
        f.write(section + ' = ')
        for article in articles_by_section[section]:
            f.write(str(article['id']) + '|')

        f.write('\n')

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

sort_articles(zendesk_domain, email, password)
