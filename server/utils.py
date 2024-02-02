import pickle

import os
import requests, datetime, traceback
import json, re, logging
import phonenumbers

def store_list(r, l):
    data = pickle.dumps(l)
    r.set('temp:list', data)


def load_list(r):
    data = r.get('temp:list')
    if data:
        l = pickle.loads(data)
        return l
    else:
        return []


def load_xy(r):
    xvalues = []
    yvalues = []
    l = load_list(r)
    if l:
        xvalues, yvalues = zip(*l)
    return xvalues, yvalues


