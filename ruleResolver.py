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

from abc import ABCMeta, abstractmethod
import importlib


class RuleResolver(metaclass=ABCMeta):
    """ Used to handle default scraping rules, custom scraping rules, and fake feed rules """

    def __init__(self, rule_file_string):
        self.rule_module = self._import_rules(rule_file_string)
        self.meets_standards = self._check_standards(self.rule_module, rule_file_string)

    def is_usable(self):
        return self.meets_standards

    @staticmethod
    def _import_rules(rule_file):
        try:
            return importlib.import_module(rule_file)
        except ImportError:
            return None

    @staticmethod
    @abstractmethod
    def _check_standards(rule_module, rule_file_string):
        """ Verifies that the rule file matches requirements. Returns True if it does, False if it doesn't. """
        pass

    @abstractmethod
    def select_rule(self, needs_rule_match, job):
        """ Find the matching rule for the given object. """
        pass

    @staticmethod
    @abstractmethod
    def _fallback_rule(needs_rule_match):
        """ Is called when a rule matches, but fails, or when no rule matches. """
        pass




