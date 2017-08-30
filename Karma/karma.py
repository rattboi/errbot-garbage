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

    def promote_karma(self, what):
        return self._update_karma(what, 1)

    def demote_karma(self, what):
        return self._update_karma(what, -1)

    def strip_at(self, element):
        return element.lstrip('@')

    def strip_parens(self, element):
        if element.startswith('(') and element.endswith(')'):
            return element[1:-1]
        return element

    def strip_operator(self, element):
        if element.endswith('++'):
            return element.rstrip('+')
        elif element.endswith('--'):
            return element.rstrip('-')
        return element

    def strip(self, element):
        l = element.lower()
        o = self.strip_operator(l)
        p = self.strip_parens(o)
        a = self.strip_at(p)
        return a

    def increment_all(self, msg):
        for element in re.findall(r"\([^)]+\)\+\+|\S+\+\+", msg.body):
            self.promote_karma(self.strip(element))

    def decrement_all(self, msg):
        for element in re.findall(r"\([^)]+\)\-\-|\S+\-\-", msg.body):
            self.demote_karma(self.strip(element))

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
            value = self.get_karma(self.strip_at(what.lower()))
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
