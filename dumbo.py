# -*- coding: utf-8 -*-

import sys
import random
import json
import yaml
import urllib

from twisted.application import internet, service
from twisted.internet import ssl, reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc

with open('config.yml') as f:
	config = yaml.load(f.read())
HOST, PORT, MODES, NICKNAME, CHANNELS, COMMANDS, OPS, BLOCKED = config['host'], config['port'], config['modes'], config['nickname'], config['channels'], config['commands'], config['ops'], config['blocked']

try:
	urllib.urlretrieve("https://raw.githubusercontent.com/sweepyoface/dumbo-quotes/master/quotes.json", "quotes.json")
except urllib.error.HTTPError:
	log.msg("Unable to retrieve quotes: urllib.error.HTTPError")
	sys.exit(1)


class DumboProtocol(irc.IRCClient):
	nickname = NICKNAME
	realname = NICKNAME

	# @Override
	def signedOn(self):
		for channel in self.factory.channels:
			self.join(channel)
			self.mode(self.nickname, '+', MODES)

	# @Override
	def privmsg(self, user, channel, message):

		nick, _, host = user.partition('!')
		if message.strip().startswith('.'):

			# Quote command
			if message.replace('.', '', 1).strip().lower().split()[0] in COMMANDS['randomquote']:
				if host not in BLOCKED:
					with open('quotes.json') as f:
						quotes = json.load(f.read())
						QUOTES = quotes['quotes']
					# If it's a PM the channel name is their nickname
					if channel == self.nickname:
						self._send_message(random.choice(QUOTES), nick)
					else:
						self._send_message(random.choice(QUOTES).replace("Qball", "Qbal" + u"\u200B" + "l"), channel)  # Zero width space to prevent pinging
						self._log_command(user, channel, message.strip())


			# Sendline command
			elif message.replace('.', '', 1).strip().lower().split()[0] in COMMANDS['sendline']:
				if nick in OPS:
					self.sendLine(message.replace(message.strip().lower().split()[0], '').strip())
					self._log_command(user, channel, message.strip())

			# Tacos command
			if message.replace('.', '', 1).strip().lower().split()[0] in COMMANDS['tacos']:
				if host not in BLOCKED:
					# If it's a PM the channel name is their nickname
					if channel == self.nickname:
						self._send_message(
							u"🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮",
							nick)
					else:
						self._send_message(
							u"🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮🌮",
							channel)
					self._log_command(user, channel, message.strip())

	def _log_command(self, sender, chan, msg):
		log.msg("Command from " + sender + " in " + chan + ": " + msg)

	def _send_message(self, msg, target):
		self.msg(target, msg)

	def _show_error(self, failure):
		return failure.getErrorMessage()


class DumboFactory(protocol.ReconnectingClientFactory):
	protocol = DumboProtocol
	channels = CHANNELS


if __name__ == '__main__':
	reactor.connectSSL(HOST, PORT, DumboFactory(), ssl.ClientContextFactory())
	log.startLogging(sys.stdout)
	reactor.run()

elif __name__ == '__builtin__':
	application = service.Application('Dumbo')
	ircService = internet.TCPClient(HOST, PORT, DumboFactory())
	ircService.setServiceParent(application)
