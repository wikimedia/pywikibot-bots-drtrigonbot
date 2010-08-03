
# http://de.wikipedia.org/wiki/Wikipedia:Letzte_%C3%84nderungen#Letzte_.C3.84nderungen_.C3.BCber_IRC
# (https://bugzilla.wikimedia.org/show_bug.cgi?id=16896)
#
# http://oreilly.com/pub/h/1968
# http://bbs.progenic.com/Topic16046-9-1.aspx


import sys
import socket
import string
import re, threading


HOST		= "browne.wikimedia.org"
PORT		= 6667
NICK		= "DrTrigonBot"
IDENT		= "DrTrigonBot"
REALNAME	= "DrTrigonBot"
CHAN		= "#de.wikipedia"

WIKIMSG		= ':rc!~rc@localhost PRIVMSG #de.wikipedia :'
IRCMSG_SHOW	= False					# suppress IRC messages? or show them?


class Timer(threading.Thread):
	'''
	Timer thread that runs completely stand-alone in sperate thread and continous until 'cancel' is called.
	Variables to use in 'func' have to be stored internally in 'kwargs'.
	'''

	def __init__(self, sec, func, **kwargs):
		threading.Thread.__init__(self)
		self.seconds = sec
		self.function = func
		self.kwargs = kwargs
		self._t = threading.Timer(self.seconds, self._action)
	def _action(self):
		self.function(self)
		del self._t
		self._t = threading.Timer(self.seconds, self._action)
		self._t.start()
	def run(self):
		self._t.start()
	def cancel(self):
		self._t.cancel()

def IRCDaemon(timerobj):
	# new data?
	size = len(timerobj.kwargs['data']) - 1
	if size < 0: return

	# remove older data to process
	readbuffer = timerobj.kwargs['data'][:size]
	timerobj.kwargs['data'] = timerobj.kwargs['data'][size:]

	# process (older) data
	for line in readbuffer:
		line = line.strip()
		if (line == ""): continue

		if (line[:len(WIKIMSG)] == WIKIMSG):
			line = line[len(WIKIMSG):]
			line = re.sub('\x03\d{1,2}', '', line)
			print "WIKIMSG: %s\n" % line
		else:
			if not IRCMSG_SHOW: continue
			print "IRCMSG: %s\n" % line
	return


s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN %s\r\n" % CHAN)	#Join chan

t = Timer(1.0, IRCDaemon, data = [])	# show messages in interval
t.run()

try:					# fetch everything that comes (until Ctrl-C)
	while 1:
		readbuffer = string.join(t.kwargs['data'], "\n")
		t.kwargs['data'] = string.split(readbuffer + s.recv(4096), "\n")
except KeyboardInterrupt:
	pass

print "\nEXITING WIKI IRC CLIENT BOT"

t.cancel()
del t

