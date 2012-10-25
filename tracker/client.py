# -*- coding: utf-8 -*-
import sys
import tweetstream
import threading
import time
import Queue
import cPickle
import os
sys.path.append('../')
from tracker.lib.moodClassifierClient import MoodClassifierTCPClient

MCC = MoodClassifierTCPClient('127.0.0.1',6666)


class StreamCollector(threading.Thread):
	""" Filter """
	words = ["españa"]
	""" Limit """
	limit = 10
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
				self.queue.put(tweet)
				self.count += 1
				if (self.count >= self.limit):
					break

class StreamWriter(threading.Thread):

	fileNameRaw = os.path.abspath(os.path.join( os.curdir,os.path.normpath('data/tweets_raw.dat')))
	fileNameMood = os.path.abspath(os.path.join( os.curdir,os.path.normpath('data/tweets_mood.dat')))

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
			textMood = MCC.classify([{'text': text }], 'search')
			print textMood, '\n'
			cPickle.dump(tweet, self.fileMood,protocol=1)

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