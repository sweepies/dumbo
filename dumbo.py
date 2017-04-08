import sys, yaml
import random
import twisted
from twisted.internet import ssl, reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.application import internet, service

with open('config.yml') as f:
    config = yaml.load(f.read())
HOST, PORT, MODES = config['host'], config['port'], config['modes']

class DumboProtocol(irc.IRCClient):
    nickname = 'Dumbo'
    realname = 'Dumbo'

    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
            self.mode(self.nickname, '+', MODES)

    def privmsg(self, user, channel, message):
        nick, _, host = user.partition('!')
        if message.strip().startswith('.'):
            if message.strip() == '.dumball':
                with open('quotes.yml') as f:
                    quotes = yaml.load(f.read())
                    QUOTES = quotes['quotes']
                if channel == self.nickname:
                    self._send_message(random.choice(QUOTES), nick)
                else:
                    self._send_message(random.choice(QUOTES), channel)
                print("Command from " + nick + ": " + message.strip())
            elif message.startswith('.sendline'):
                if nick == "Sweepyoface":
                    self.sendLine(message.replace('.sendline', '').strip())
                print("Command from " + nick + ": " + message.strip())

    def _send_message(self, msg, target):
        self.msg(target, msg)

    def _show_error(self, failure):
        return failure.getErrorMessage()

class DumboFactory(protocol.ReconnectingClientFactory):
    protocol = DumboProtocol
    #channels = ['#paper']
    channels = ['#hell']

if __name__ == '__main__':
    reactor.connectSSL(HOST, PORT, DumboFactory(), ssl.ClientContextFactory())
    log.startLogging(sys.stdout)
    reactor.run()

elif __name__ == '__builtin__':
    application = service.Application('Dumbo')
    ircService = internet.TCPClient(HOST, PORT, DumboFactory())
    ircService.setServiceParent(application)