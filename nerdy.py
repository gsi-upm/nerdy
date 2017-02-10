__author__ = 'croman'
# -*- coding: utf-8 -*-
import wrapper
from polyglot.downloader import downloader
from senpy.plugins import SenpyPlugin
from senpy.models import Entry, Results
class nerdyPlugin(SenpyPlugin):
    def activate(self,**params):
        downloader.download("embeddings2.en")
        downloader.download("embeddings2.es")
        downloader.download("ner2.es")
        downloader.download("ner2.en")
    def analyse(self, **params):
        classifier = params.get("classifier", "polyglot-es")
        p = params.get("prefix", None)
        response = Results(prefix=p)
        (entities, types, startIndexes, endIndexes) = wrapper.service(params.get("input"), classifier)
        print (entities, types, startIndexes, endIndexes)
        for x in range(0, len(entities)):
            entry = Entry(id="Entry"+str(x),
                          prefix=p,
                          anchorOf=entities[x],
                          taClassRef="dbo:"+types[x],
                          startIndex=startIndexes[x],
                          endIndex=endIndexes[x])
            response.entries.append(entry)
        return response
