# -*- coding: utf-8 -*-
import sys
import tweetstream
import threading
import time
import Queue
import cPickle
import os
from lib.moodClassifierClient import MoodClassifierTCPClient
sys.path.append('dict')
import dictionary
import requests

# sys.path.append('../')

MCC = MoodClassifierTCPClient('127.0.0.1',6666)


class StreamCollector(threading.Thread):
	""" Filter """
	words = ["stock"]
	""" Limit """
	limit = 100
	""" Twitter user/pass"""
	twitterUser = 'toni_gsi'
	twitterPass = 'gsigsi'

	def __init__(self, tweetsQueue):
		threading.Thread.__init__(self)  
		self.queue = tweetsQueue
		self.count = 0


	def run(self):
		with tweetstream.FilterStream(self.twitterUser, self.twitterPass, track=self.words) as stream:
			for tweet in stream:
				if tweet.get('text'):
					if 'rt' in tweet.get('text').lower():
						continue
					#print tweet
					self.queue.put(tweet)
					self.count += 1
					if (self.count >= self.limit):
						break

class StreamWriter(threading.Thread):

	fileNameRaw = os.path.abspath(os.path.join( os.curdir,os.path.normpath('data/output/tweets_raw.dat')))
	fileNameMood = os.path.abspath(os.path.join( os.curdir,os.path.normpath('data/output/tweets_mood.dat')))

	def __init__(self, tweetsQueue):
		threading.Thread.__init__(self)  
		self.queue = tweetsQueue
		self.fileRaw = open(self.fileNameRaw,'w')
		self.fileMood = open(self.fileNameMood,'w')

	def run(self):
		while True:
			tweet = self.queue.get(block=True)
			cPickle.dump(tweet, self.fileRaw,protocol=1)
			text = unicode(tweet.get('text'));
			# borra las search keywords antes de clasificar? puede ser
			# total salen en todos los tweets asi que no aportan informacion...
			textMood = MCC.classify([{'text': text}], "dow jones nasdaq S&P 500 S&P500 stock")
			#print textMood, '\n'

			self.sendFile(tweet, textMood)

			cPickle.dump(tweet, self.fileMood, protocol=1)


	def sendFile(self, tweet, mood):
		params = {'context': 'default'}
		headers = {'Content-Type': 'application/rdf+xml' }
		data = self.createFile(tweet,mood)
		files = {'file':  data}
		r = requests.post("http://shannon.gsi.dit.upm.es/episteme/lmf/import/upload", params=params, data=data, headers=headers)
		print r.headers
		print r.status_code , r.text

	def createFile(self, tweet, mood):
		s = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:dcterms="http://purl.org/dc/terms/"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:sioc="http://rdfs.org/sioc/ns#"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:marl="http://purl.org/marl/">
	<rdf:Description rdf:about="https://api.twitter.com/1/statuses/show/'"""
		s += str(tweet.get('id_str'))
		s += """.json">
		<rdf:type rdf:resource="http://rdfs.org/sioc/types#MicroblogPost"/>
		<dc:title>stock</dc:title>
		<dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">"""
		s += str(tweet.get('created_at'))
		s += """</dcterms:created>
		<sioc:has_creator rdf:resource="https://twitter.com/"""
		s += str(tweet.get('user').get('screen_name')) 
		s += """"/>
		<marl:opinionText>"""
		s += str(tweet.get(u'text'))
		s += """</marl:opinionText>
		<marl:polarityValue>"""
		s += str(mood[0].get('x_mood'))
		s += """</marl:polarityValue>
		<marl:minPolarityValue>-1</marl:minPolarityValue>
		<marl:maxPolarityValue>1</marl:maxPolarityValue>
		<marl:hasPolarity rdf:resource="http://purl.org/marl/ns#"""
		if mood[0].get('x_mood') > 0:
			s += 'Positive"/>'
		elif mood[0].get('x_mood') < 0:
			s += 'Negative"/>'
		else:
			s += 'Neutral"/>'
		s += """
	</rdf:Description>
</rdf:RDF>"""

		# try:
		# 	name = tweet.get("id_str") + '.rdf'
		# 	f = open(name,'wb')
		# 	f.write(s)
		# except IOError:
		# 	print "IOError"
		# 	pass
		# finally:
		# 	f.close()

		return s;
try:
	tweetsQueue = Queue.Queue()
	# collector thread
	c = StreamCollector(tweetsQueue)
	c.daemon = True
	c.start()
	# writer thread
	w = StreamWriter(tweetsQueue)
	w.daemon = True
	w.start()
	while True:
		c.join(500)
		if not c.isAlive():
				break
	print "Finished"

except KeyboardInterrupt:
	print "Ctrl-c pressed ..."
	sys.exit(1)