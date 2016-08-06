"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see {http://www.gnu.org/licenses/}.

    Trough homepage: https://github.com/glu10/trough
"""

from inspect import signature

from ruleResolver import RuleResolver


class FakeFeedResolver(RuleResolver):

    @staticmethod
    def _check_standards(rule_module, rule_file_string):
        if not rule_module:
            print('NOTICE:', rule_file_string, 'was unable to be imported, so it will not be used.',
                  'This is normal if the file is not present.')
            return False
        try:
            assert type(rule_module.rules) == dict
            assert len(rule_module.rules) > 0
            for name, func in rule_module.rules.items():
                assert type(name) == str
                assert hasattr(func, '__call__')
                assert len(signature(func).parameters) == 2  # Makes sure each rule func accepts exactly 1 argument.
            return True
        except (AssertionError, AttributeError) as e:
            print('Scraping rule file', rule_file_string, 'will not be used due to the following error:', e)
            return False

    def select_rule(self, feed_name, job):
        if not self.is_usable():
            return self._fallback_rule(feed_name)

        result = None
        if feed_name in self.rule_module.rules:
            result = self.rule_module.rules[feed_name](feed_name, job)
        if not result:
            result = self._fallback_rule(feed_name)
        return result

    @staticmethod
    def _fallback_rule(feed_name):
        return list()


