#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# by Antoine Mazières (http://mazier.es ; {github|twitter}@mazieres)
# Cortext Lab -- http://www.cortext.net/
#
from sklearn import cluster, decomposition
from sklearn.datasets import load_iris, load_boston
from inspect import getargspec, ismethod
from itertools import chain
import pandas as pd
from random import shuffle
import json

from flask import Flask, request, Response
app = Flask(__name__)

import unittest
import requests

class TestClustever(unittest.TestCase):

    def test_query(self):
        q = {"clustering": {"KMeans": {"n_clusters": 3}}, "dimred": {"PCA": {"n_components": 2}}, "dataset": "iris"}
        r = requests.get('http://{}:{}'.format(addr, port), params={'q': json.dumps(q)})
        tested = r.status_code
        expected = 200
        msg = '\nExpected:\n{}\nGot:\n{}'.format(expected, tested)
        self.assertEqual(expected, tested, msg=msg)

    def test_res(self):
        q = {"clustering": {"KMeans": {"n_clusters": 3}}, "dimred": {"PCA": {"n_components": 2}}, "dataset": "iris"}
        r = requests.get('http://{}:{}'.format(addr, port), params={'q': json.dumps(q)})
        self.assertEqual(3, len(r.json()))
        self.assertEqual(150, sum([len(x['data']) for x in r.json()]))
        self.assertEqual(2, len(r.json()[0]['data'][0]))


# Set to 0.0.0.0 for www (NOT SAFE !)
addr = '127.0.0.1'
port = 5001

# Maps all functions in cluster and decomposition
# to their names.
fns = dict(chain(*[
        {x:f.__dict__[x] for x in f.__all__}.items()
        for f in [cluster, decomposition]
    ]))

# Maps all functions arguments and defaults
# to their function names.
args = {name:dict(zip(args.args[1:], list(args.defaults)))
        for name, args in {k:getargspec(v.__init__)
        for k, v in fns.iteritems()
        if ismethod(v.__init__)
        and getargspec(v.__init__).defaults != None}.iteritems()}

fns = {k:v for k, v in fns.iteritems() if k in args}

# Datasets
dss = {ds.DESCR.split(' ')[0].lower():{
            'title': ds.DESCR.split('\n')[0],
            'df': pd.DataFrame(ds.data, columns=ds.feature_names)}
        for ds in [load_iris(), load_boston()]}

# Colors
colors = [ # http://www.december.com/html/spec/colorrgbadec.html
    'rgba(0, 0, 0, 0.7)', # black
    'rgba(0, 0, 128, 0.7)', # navy
    'rgba(0, 0, 255, 0.7)', # blue
    'rgba(0, 128, 0, 0.7)', # green
    'rgba(0, 128, 128, 0.7)', # teal
    'rgba(0, 255, 0, 0.7)', # lime
    'rgba(0, 255, 255, 0.7)', # aqua
    'rgba(128, 0, 0, 0.7)', # marroon
    'rgba(128, 0, 128, 0.7)', # purple
    'rgba(128, 128, 0, 0.7)', # olive
    'rgba(128, 128, 128, 0.7)', # gray
    'rgba(192, 192, 192, 0.7)', # silver
    'rgba(255, 0, 0, 0.7)', # red
    'rgba(255, 0, 255, 0.7)', # fuchsia
    'rgba(255, 255, 0, 0.7)', # yellow
]
shuffle(colors)


class Clustever(object):
    def __init__(self, q):
        self.q = q
        self.df = dss[self.q['dataset']]['df']
        self.df_norm = self.norm_ds()
        self.clusters = self.clustering()
        self.twod = self.dimred()

    def clustering(self):
        fn_name, fn_args = self.q['clustering'].items()[0]
        fn = fns[fn_name]
        return fn(**fn_args).fit_predict(self.df_norm.values)

    def dimred(self):
        fn_name, fn_args = self.q['dimred'].items()[0]
        fn = fns[fn_name]
        return fn(**fn_args).fit_transform(self.df_norm.values)

    def norm_ds(self):
        return (self.df - self.df.mean()) / self.df.std()

    def series(self):
        self.series = []
        i = 0
        for g in set(self.clusters):
            clust = {
                'name': 'Cluster {}'.format(i),
                'color': colors[i],
                'data': self.twod[self.clusters == g].tolist()
            }
            self.series.append(clust)
            i += 1
        return self.series


@app.route("/")
def hello():
    req = request.args
    print req
    if 'q' in req:
        callback = req['callback']
        q = json.loads(req['q'])
        c = Clustever(q)
        res = c.series()
        return Response("{}({})".format(callback, json.dumps(res)), mimetype='application/javascript')
    else:
        print "toto"
        return "None"

if __name__ == "__main__":
    app.run(host=addr, port=port, debug=True)
