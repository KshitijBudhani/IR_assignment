'''
    Author: Kshitij Budhani
    Course: Information Retrieval
    Contact: f2013083@pilani.bits-pilani.ac.in
'''

''' Kshitij is avoiding using Nltk as much as possible for now as the searches will be very slow otherwise '''

import sys
import re
import gc
from porterStemmer import PorterStemmer
from collections import defaultdict
from array import array


index_porter = PorterStemmer()

class Index:
    def __init__(self):
        self.index = defaultdict(list)

    def remove_stop_words(self):
        file = open(self.stopwordsFile, 'rw')
        stop_words = [line.rstrip() for line in file]
        '''rstrip removes whitespace characters(by default)'''
        self.stop_words_dict = dict.fromkeys(stop_words)
        file.close()

    def process_text(self, line):
        line = line.lower()
        line=re.sub(r'[^a-z0-9 ]',' ',line)
        '''need to revisit this as Kshitij is not including any other character other than alphanumerics'''
        line = line.split()
        '''desi tokenizer(no NLTK) :P'''
        line = [word for word in line if word not in self.stop_words_dict]
        line = [index_porter.stem(word , 0 , len(word) - 1) for word in line]
        return line

    def parse_wiki(self):
        doc = []
        for line in self.collFile:
            if line == '</page>\n':
                break
            doc.append(line)

        Page = ''.join(doc)
        pageid=re.search('<id>(.*?)</id>', Page, re.DOTALL)
        pagetitle=re.search('<title>(.*?)</title>', Page, re.DOTALL)
        pagetext=re.search('<text>(.*?)</text>', Page, re.DOTALL)

        if pageid==None or pagetitle==None or pagetext==None:
            return {}

        d={}
        d['id']=pageid.group(1)
        d['title']=pagetitle.group(1)
        d['text']=pagetext.group(1)

        return d
    def index_to_file(self):
        f = open(self.indexFile, 'w')
        for term in self.index.iterkeys():
            postinglist=[]
            for p in self.index[term]:
                docID=p[0]
                positions=p[1]
                postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            print >> f, ''.join((term,'|',';'.join(postinglist)))

        f.close()

    def get_param(self):
        param = sys.argv
        self.stopwordsFile = param[1]
        self.collectionFile = param[2]
        self.indexFile = param[3]

    def create_index(self):
        self.get_param()
        self.collFile = open(self.collectionFile,'r')
        self.remove_stop_words()

        gc.disable()

        pagedict = {}
        pagedict=self.parse_wiki()


        while pagedict!={}:
            lines = '\n'.join((pagedict['title'],pagedict['text']))
            pageid = int(pagedict['id'])
            terms = self.process_text(lines)

            termdictpage = {}
            for position,term in enumerate(terms):
                try:
                    termdictpage[term][1].append(position)
                except:
                    termdictpage[term]=[pageid,array('I',[position])]

            for termpage,postingpage in termdictpage.iteritems():
                self.index[termpage].append(postingpage)

            pagedict = self.parse_wiki()

        gc.enable()

        self.index_to_file()

if __name__=="__main__":
    i=Index()
    i.create_index()
