# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
from tracker.lib.moodClassifierClient import MoodClassifierTCPClient
import cPickle
import os


dataDir = "/home/toni/git/financial-twitter-sentiment-analyzer/tracker/data"


MCC = MoodClassifierTCPClient('127.0.0.1',6666)

tweetsFile = open(os.path.join(dataDir,'tweets_positive_raw.dat'),'rb')
while True:
	tweet = None
	try:
		tweet = cPickle.load(tweetsFile)
		print 'loaded'
	except EOFError:
		print "done for %s" % mood
		break
	except:
		print "error"
		pass    

	if tweet:
		print 'tweet'
		text = unicode(tweet.get('text'))
		test_data  = [
			{'text': text }
		]
		print MCC.classify(test_data, 'search')





#test_data  = [
#{'text':u'this is a test text 1'},
#{'text':u'this is a test text 2'},
#{'text':u'Prueba de idioma tiene que poner es en el tag y esto tiene que dar bueno asi que digo que es muy bonito'},
#{'text':u'Otra prueba, el producto es muy malo'},
#{'text':u'So nasty'},
#
#]

#print MCC.classify(test_data, 'search')
