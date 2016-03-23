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

import re
from ruleResolver import RuleResolver
from inspect import signature


class WrappedScrapeResolver(RuleResolver):
    """ Hides the differences between default and custom rule behavior """

    def __init__(self):
        # Note: intentionally skipping super() init call
        self.default_resolver = DefaultScrapeResolver('default_scraping_rules')
        assert self.default_resolver.is_usable()  # There's no excuse for the default rules to be invalid

        self.custom_resolver = CustomScrapeResolver('custom.custom_scraping_rules')

    @staticmethod
    def _check_standards(rule_module, rule_file_string):
        pass  # Should not be called because it doesn't make sense for a wrapper.

    def select_rule(self, link, job):
        soup = job.get_soup(link)

        result = None
        if self.custom_resolver.is_usable():
            result = self.custom_resolver.select_rule(link, job, soup)
        if not result:
            result = self.default_resolver.select_rule(link, job, soup)
        assert type(result) == list
        return result

    @staticmethod
    def _fallback_rule(link):
        pass  # Not needed, default rules will use a heuristic if nothing matches in its rule list.


class DefaultScrapeResolver(RuleResolver):

    @staticmethod
    def _check_standards(rule_module, rule_file_string):
        if not rule_module:  # Common missing file case, so it deserves a less scary print statement
            print('NOTICE:', rule_file_string, 'was unable to be imported, so it will not be used.',
                  'This is normal if the file is not present.')
            return False
        try:
            assert type(rule_module.ordered_rules == list)
            assert len(rule_module.ordered_rules) > 0
            for rule in rule_module.ordered_rules:
                assert type(rule[0]) == str
                re.compile(rule[0])  # will raise re.error if the regular expression doesn't compile
                assert hasattr(rule[1], '__call__')
                assert len(signature(rule[1]).parameters) == 2  # Makes sure each rule func accepts exactly 2 arguments.
            return True
        except (AttributeError, AssertionError, IndexError, re.error) as e:
            print('Scraping rule file', rule_file_string, 'will not be used due to the following error:', e)
            return False

    def select_rule(self, link, job, soup=None):
        if not soup:
            soup = job.get_soup(link)

        if not self.is_usable():
            return self._fallback_rule(soup)

        for rule in self.rule_module.ordered_rules:
            identifier = rule[0]
            scrape_rule = rule[1]

            if re.search(identifier, link):
                try:
                    return self._cleanup(scrape_rule(soup, job))
                except AttributeError:  # A rule couldn't find what it assumed would be there
                    print('NOTICE: The link', link, 'matched with ' + identifier +
                          ', but the scraping rule returned None. Using the default scraping rule as a fallback.')
                    return self._fallback_rule(soup)

        return self._fallback_rule(soup)

    @staticmethod
    def _fallback_rule(soup):
        """ Making a best guess as to where the article is contained """
        paragraphs = DefaultScrapeResolver._cleanup(soup.find_all('p'))

        # Only keeps paragraphs past a certain threshold length
        filtered_paragraphs = [p for p in paragraphs if len(p) >= 20]  # TODO: Configuration for this threshold

        if filtered_paragraphs:
            return filtered_paragraphs
        elif paragraphs:
            return paragraphs
        else:
            return ['No paragraphs could be found.']

    @staticmethod
    def _cleanup(paragraphs):
        cleaned = list()
        for p in paragraphs:

            if type(p) != str:
                p = p.getText()

            # Remove extraneous whitespace
            p = re.sub(r'\s+', ' ', p)
            p = re.sub(r'\n\n(\n+)', '\n\n', p)

            p = re.sub(r'<.*?>', '', p)  # Remove any leftovers from HTML

            # Remove small annoyances
            temp = p.lower()
            if temp.find('hide caption') != -1 or temp == 'advertisement' or temp.startswith('see more'):
                continue
            else:
                cleaned.append(p)
        return cleaned


class CustomScrapeResolver(DefaultScrapeResolver):
    """ Behaves like the default rule resolver, except it just gives up when no match occurs. """

    @staticmethod
    def _fallback_rule(soup):
        return None
