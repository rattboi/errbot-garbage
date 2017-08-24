from errbot import BotPlugin, botcmd, re_botcmd
from itertools import chain
import re

CONFIG_TEMPLATE = {'byself': False}


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

    def _update_karma(self, what, amount):
        value = int(self.get_karma(what))
        try:
            new_value = value + amount
            d = self['karma']
            d[what] = new_value
            self['karma'] = d
        except Exception as e:
            self.log.debug("update %s fail, e: %s" % ('karma', e))

    def promote_karma(self, what, amount):
        return self._update_karma(what, amount)

    def demote_karma(self, what, amount):
        return self._update_karma(what, amount)

    def strip_parens(self, element):
        if element.startswith('(') and element.endswith(')'):
            return element[1:-1]
        return element

    def strip_operator(self, element):
        if element.endswith('++'):
            return element.replace('++', '')
        elif element.endswith('--'):
            return element.replace('--', '')
        return element

    def increment_all(self, msg):
        for m in re.findall(r"\([^)]+\)\+\+|\S+\+\+", msg.body):
            l = m.lower()
            o = self.strip_operator(l)
            p = self.strip_parens(o)
            self.log.debug("increment: %s %s %s" % (l, o, p))
            self.promote_karma(p, 1)

    def decrement_all(self, msg):
        for m in re.findall(r"\([^)]+\)\-\-|\S+\-\-", msg.body):
            self.demote_karma(
                    self.strip_parens(self.strip_operator(m.lower())),
                    -1)

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
        if len(args) > 0:
            what = ' '.join(args)
            self.log.debug("what: %s" % what)
            value = self.get_karma(what)
            if value == "0" or value is None:
                result = "'%s' has no karma." % what
            else:
                result = "'%s' has %s karma points" % (what, value)
        else:
            result = "!karma <thing> - Reports karma status for <thing>."
        return result

    @re_botcmd(pattern=r'\S+\+\+', prefixed=False)
    def promote_karma_cmd(self, msg, args):
        """Update karma status for thing if get '++' message."""
        return self.increment_all(msg)

    @re_botcmd(pattern=r'\S+--', prefixed=False)
    def demote_karma_cmd(self, msg, args):
        """Update karma status for specific user if get '--' message."""
        return self.decrement_all(msg)

    @botcmd(split_args_with=' ')
    def karma(self, msg, args):
        """Command to show the karma status for specific user"""
        return self.get_karma_value(msg, args)
