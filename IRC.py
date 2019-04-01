import socket as soc
import random
import sys, select
import re, requests
import shutil
from bs4 import BeautifulSoup as bf
IP = ('10.0.2.15', 6667)
"""
height = shutil.get_terminal_size().lines-1
sys_write = sys.stdout.buffer.write
CSI = b'\x1b['
CURSOR_UP = CSI + b'1A'
CLEAR = CSI + b'2J'
CLEAR_LINE = CSI + b'2K'
SAVE_CURSOR = CSI + b's'
UNSAVE_CURSOR = CSI + b'u'
GOTO =CSI + b'%d;0H' % (height + 1)
"""
def set_scroll(n):
	return CSI + b'0;%dr' % n
def buff(*arg):
	sys_write(b''.join(arg))
#buff(CLEAR, set_scroll(height))
class IRC():
	def __init__(self, IP):
		#init connection
		self.irc = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
		print(soc.gethostname())
		self.irc.connect(IP)
		msg = 'NICK bot_b05902046\r\nUSER Bon\r\nJOIN #CN_DEMO\r\n'
		self.irc.send(bytes(msg, encoding = 'utf-8'))
		self.privmsg('#CN_DEMO', "I'm b05902046")
		#variables for the irc
		self.table = {}#[name, cond]
		self.chatting = False
		self.guessing = False
		self.constel = {'Capricorn': '表面上很灑脫，其實，在很多時候，卻是放不下的', 'Aquarius': '樂觀、內心超級柔軟、講義氣', 'Pisces':'偏執、悲觀、輕微強迫症，白天理性，夜晚感性，白天堅強，夜晚脆弱', 'Aries': '對朋友很珍惜，真心對待', 'Taurus':'從不哭，從不認輸，從不屈服', 'Gemini':'喜歡在傷心的時候聽傷心的歌，喜歡在開心的時候和在乎的人分享',
		'Cancer':'很不容易發脾氣，再低三落四的事，他也能硬著頭皮過', 'Leo':'討厭虛偽，討厭謊言，討厭欺騙', 'Virgo':'不喜歡自負的人，不自私，有主見的人是她們的最愛', 'Libra':'外表冷，內心其實很熱，很溫暖', 'Scorpio':'喜歡淡淡的生活，靜悄悄地走過每一天', 'Sagittarius':'可以幽默，可以冷漠，可以柔弱，可以堅強'}
		self.chatwith = None
		self.rand = 0
		self.guess_table = []

	#def pong(self, msg):
	#	self.irc.send(bytes('PONG ' + msg.split()[1] + '\n', encoding = 'utf-8'))
	def privmsg(self, who ,msg):
		self.irc.send(bytes('PRIVMSG ' + who + ' :' + msg + '\n', encoding = 'utf-8'))
	def mode_handle(self, user, rmsg):
		num = self.table[user]
		if num == 1:
			rmsg = rmsg.split()
			if len(rmsg) > 1 or not rmsg[0].isdigit():
				return
				#self.privmsg(user, 'Please enter ONE integer')
			else:
				val = int(rmsg[0])
				if val < 1 or val > 10:
					return
					#self.privmsg(user, 'Please enter a integer that is within the bound ==')
				else:
					if val in self.guess_table:
						self.privmsg(user, 'You have guessed number %d before, enter another integer' % val)
					elif val > self.rand:
						self.privmsg(user, 'Lower!')
						self.guess_table.append(val)
					elif val < self.rand:
						self.privmsg(user, 'Higher!')
						self.guess_table.append(val)
					else:
						self.privmsg(user, 'Congrats, GGWP')
						del self.table[user]
						self.guess_table = []
						self.guessing = False
		elif num == 2:
			msg = rmsg
			rmsg = rmsg.split()
			#buff(SAVE_CURSOR)
			if len(rmsg) == 1 and rmsg[0] == '!bye':
				
				print('%s: !bye' % user)
				print('==========%s has left==========' % user)
				self.chatting = False  
				del self.table[user]
				
			else:
				
				print('\r%s:' % user, msg)
			#buff(UNSAVE_CURSOR)
	def song(self, song):
		url = 'https://www.youtube.com/results?search_query='
		res = requests.get(url + song)
		soup = bf
		soup = bf(res.text, 'html.parser')

		for entry in soup.select('a'):
			m = re.search("v=(.*)", entry['href'])
			if m:
				return 'https://www.youtube.com/watch?v='+m.group(1)
		return 'NONE'
	def unpack(self, ircmsg):
		regex = re.compile(r':(.*?)!')
		match = re.search(regex, ircmsg)
		user = match.group(1)
		regex = re.compile(r'bot_b05902046 :(.*)')
		match = re.search(regex, ircmsg)
		return user, match.group(1)

bot = IRC(IP)
inputs = [bot.irc, sys.stdin]

while True:
	#buff(GOTO)
	r, w, e = select.select(inputs, [], [])
	for end in r:
		if end == sys.stdin:
			if bot.chatting:
				msg = input()
				
				bot.privmsg(bot.chatwith, msg)
			else:
				junk = input()
				if junk == "exit":
					bot.irc.close()
					#buff(set_scroll(height + 1), GOTO, CLEAR_LINE)
					exit()
				bot.privmsg("#CN_DEMO", junk)
				#buff(GOTO, CLEAR_LINE)
		elif end == bot.irc:
			ircmsg = bot.irc.recv(2048).decode()
			if ircmsg.find('PRIVMSG') != -1:
				user, rmsg = bot.unpack(ircmsg)
				if user in bot.table:
					bot.mode_handle(user, rmsg)
				else:
					rmsg = rmsg.split()
					if len(rmsg) == 1:
						if rmsg[0] in bot.constel:
							bot.privmsg(user, bot.constel[rmsg[0]])
						elif rmsg[0] == '!guess'and not bot.guessing:
							bot.cond = 1
							bot.privmsg(user, 'Choose a number between 1 ~ 10')
							bot.guessing = True
							bot.rand = random.randrange(1, 11)
							bot.table[user] = 1
						elif rmsg[0] == '!chat' and not bot.chatting:
							print('==========%s is contacting you==========' % user)
							bot.chatwith = user
							bot.chatting = True
							bot.table[user] = 2
					
						
					else:
						if rmsg[0] == '!song':
							bot.privmsg(user, bot.song(' '.join(rmsg)))
			if not bot.chatting:	
				print (ircmsg)
