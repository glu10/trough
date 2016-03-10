import unittest
from ruleResolverScraping import *
from unittest.mock import MagicMock
from unittest.mock import patch
from bs4 import BeautifulSoup


class TestScrapingRules(unittest.TestCase):

    def setUp(self):
        self.ridiculous_link = '23k!!!.com!!!5lkj link that should never match'
        self.first_paragraph = 'This is a fake paragraph and has to be long enough to not get filtered.'
        self.second_paragraph = 'This is another fake paragraph and has to be long enough to not get filtered.'
        self.paragraphs = [self.first_paragraph, self.second_paragraph]
        html_paragraphs = '<html><p>' + self.first_paragraph + '</p><p>' + self.second_paragraph + '</p></html>'
        self.soup = BeautifulSoup(html_paragraphs, 'html.parser')

        self.mock_job = MagicMock()
        self.mock_job.get_soup.return_value = self.soup

    def test_example_custom_rules(self):
        resolver = CustomScrapeResolver('custom.examples.custom_scraping_rules')
        self.assertTrue(resolver.is_usable())
        self.assertIsNone(resolver.select_rule(self.ridiculous_link, self.mock_job))  # Unknown links should return None

    def test_default_rules(self):
        resolver = DefaultScrapeResolver('default_scraping_rules')
        self.assertTrue(resolver.is_usable())
        rule_return = resolver.select_rule(self.ridiculous_link, self.mock_job)
        self.assertEquals(rule_return, self.paragraphs)
        self.assertEquals(rule_return, resolver._fallback_rule(self.soup))  # Unknown links use fallback rule

    def test_wrapper(self):
        with patch('builtins.print', MagicMock()):  # Silences the print call about custom rules if they aren't there
            resolver = WrappedScrapeResolver()
            rule_return = resolver.select_rule(self.ridiculous_link, self.mock_job)
        self.assertEquals(self.paragraphs, rule_return)  # Unknown links should use default resolver



