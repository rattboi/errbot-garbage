from errbot import BotPlugin, botcmd, re_botcmd
from itertools import chain

CONFIG_TEMPLATE = {'byself': False, 'feedback': False}


class Karma(BotPlugin):
    """Karma plugin for Errbot"""

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(),
                          configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(Karma, self).configure(config)

    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def _update_karma(self, what, amount, method='+'):
        value = int(self.get_karma(what))
        try:
            if method == '+':
                self['karma'][what] = value + amount
            else:
                self['karma'][what] = value - amount
        except Exception as e:
            self.log.debug("update %s fail, e: %s" % ('karma', e))

    def promote_karma(self, what, amount):
        return self._update_karma(what, amount, '+')

    def demote_karma(self, what, amount):
        return self._update_karma(what, amount, '-')

    def _parse_msg(self, msg, amount, method='+'):
        try:
            what = msg.body.split(method)[0].strip().split().pop()
        except Exception as e:
            self.log.debug("parse message fail - %s." % (e))
            return None
        return what, method, amount

    def parse_promote(self, msg):
        return self._parse_msg(msg, 1, method='+')

    def parse_demote(self, msg):
        return self._parse_msg(msg, 1, method='-')

    def get_karma(self, what):
        value = str(0)
        if 'karma' in self:
            if what in self['karma']:
                value = self['karma'][what]
            else:
                self['karma'][what] = value
        else:
            self['karma'] = {what: value}
        return value

    def get_karma_value(self, msg, args):
        result = ""
        if len(args) == 1:
            if len(args[0]) == 0:
                what = msg.frm.nick
            else:
                what = args[0]
            value = self.get_karma(what)
            if value == "0" or value is None:
                result = "%s has no karma." % what
            else:
                result = "%s's karma points are : %s" % (what, value)
        else:
            result = "!karma <thing> - Reports karma status for <thing>."
        return result

    def update_karma_value(self, msg, parse_fun, update_fun):
        """Update karma status for specific user"""
        what, method, amount = parse_fun(msg)
        if what:
            # not allow self (pro|de)mote
            if not self.config['byself']:
                if what == msg.frm.nick:
                    return
            # update karma
            update_fun(what, amount)

    @re_botcmd(pattern=r'^[[\w][\S]+[\+]{2}', prefixed=False)
    def promote_karma_cmd(self, msg, args):
        """Update karma status for thing if get '++' message."""
        return self.update_karma_value(msg, self.parse_promote, self.promote_karma)

    @re_botcmd(pattern=r'^[[\w][\S]+[\-]{2}', prefixed=False)
    def demote_karma_cmd(self, msg, args):
        """Update karma status for specific user if get '--' message."""
        return self.update_karma_value(msg, self.parse_demote, self.demote_karma)

    @botcmd(split_args_with=' ')
    def karma(self, msg, args):
        """Command to show the karma status for specific user"""
        result = self.get_karma_value(msg, args)
        return result
