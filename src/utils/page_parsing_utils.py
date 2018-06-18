# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import logging
import pymorphy2
import requests

logger = logging.getLogger(__name__)


def get_keywords(url):
    try:
        data = requests.get(url, verify=True).text
        soup = BeautifulSoup(data, "html.parser")
        keywords = soup.find("meta",  attrs={'name': 'Keywords'})
        return normalize_keywords(keywords["content"].split(u',')) if keywords else []        
    except Exception as e:
        logger.error(str(e))
        return []


def get_title(url):
    try:
        data = requests.get(url, verify=True).text
        soup = BeautifulSoup(data, "html.parser")
        return soup.title.string
    except Exception as e:
        logger.error(str(e))
        return ""


def normalize_keywords(args):
    normalized_keywords = []
    morph = pymorphy2.MorphAnalyzer()
    for x in args:
        p = morph.parse(x)[0]
        if p.tag.POS == 'NOUN':
            normalized_keywords.append(p.normal_form)
    return normalized_keywords
