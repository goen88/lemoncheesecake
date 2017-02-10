'''
Created on Sep 8, 2016

@author: nicolas
'''

import fnmatch

FILTER_SUITE_MATCH_PATH = 0x01
FILTER_SUITE_MATCH_TEST_DESCRIPTION = 0x02
FILTER_SUITE_MATCH_SUITE_DESCRIPTION = 0x04
FILTER_SUITE_MATCH_TAG = 0x08
FILTER_SUITE_MATCH_LINK_NAME = 0x10
FILTER_SUITE_MATCH_PROPERTY = 0x20

__all__ = ("Filter", "add_filter_args_to_cli_parser", "get_filter_from_cli_args")

def _get_path(suite, test=None):
    return ".".join([s.name for s in suite.get_path()] + ([test.name] if test else []))

def value_match_patterns(value, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(value, pattern):
            return 1
    return 0

def values_match_patterns(values, patterns):
    for pattern in patterns:
        if fnmatch.filter(values, pattern):
            return 1
    return 0

def keyvalues_match_keyvalues(keyvalues, patterns):
    for key, value in patterns.items():
        if key in keyvalues and keyvalues[key] == value:
            return 1
    return 0

def listelem_match_patterns(lsts, idx, patterns):
    for pattern in patterns:
        if pattern in map(lambda l: l[idx], lsts):
            return 1
    return 0

class Filter:
    def __init__(self):
        self.path = []
        self.test_description = []
        self.testsuite_description = []
        self.tags = [ ]
        self.properties = {}
        self.link_names = [ ]
    
    def is_empty(self):
        count = 0
        for value in self.path, self.test_description, \
            self.testsuite_description, self.tags, self.properties, self.link_names:
            count += len(value)
        return count == 0
    
    def get_testsuite_only_criteria_as_flags(self):
        flags = 0
        if self.testsuite_description:
            flags |= FILTER_SUITE_MATCH_SUITE_DESCRIPTION
        return flags
    
    def get_test_criteria_as_flags(self):
        flags = 0
        if self.path:
            flags |= FILTER_SUITE_MATCH_PATH
        if self.test_description:
            flags |= FILTER_SUITE_MATCH_TEST_DESCRIPTION
        if self.tags:
            flags |= FILTER_SUITE_MATCH_TAG
        if self.link_names:
            flags |= FILTER_SUITE_MATCH_LINK_NAME
        if self.properties:
            flags |= FILTER_SUITE_MATCH_PROPERTY
        return flags
    
    def match_test(self, test, suite, parent_suite_match=0):
        # retrieve all the criteria that must be matched individually
        # so that the test match
        flags = self.get_test_criteria_as_flags() ^ parent_suite_match

        funcs = []
        if flags & FILTER_SUITE_MATCH_PATH:
            funcs.append(lambda: value_match_patterns(_get_path(suite, test), self.path))
        if flags & FILTER_SUITE_MATCH_TEST_DESCRIPTION:
            funcs.append(lambda: value_match_patterns(test.description, self.test_description))
        if flags & FILTER_SUITE_MATCH_TAG:
            funcs.append(lambda: values_match_patterns(test.tags, self.tags))
        if flags & FILTER_SUITE_MATCH_PROPERTY:
            funcs.append(lambda: keyvalues_match_keyvalues(test.properties, self.properties))
        if flags & FILTER_SUITE_MATCH_LINK_NAME:
            funcs.append(lambda: listelem_match_patterns(test.links, 1, self.link_names))
        
        for func in funcs:
            if func() <= 0:
                return False
                
        return True
    
    def match_testsuite(self, suite, parent_suite_match=0):
        match = 0

        if self.path and not parent_suite_match & FILTER_SUITE_MATCH_PATH:
            for path in self.path:
                if fnmatch.fnmatch(_get_path(suite), path):
                    match |= FILTER_SUITE_MATCH_PATH
                    break
                
        if self.testsuite_description and not parent_suite_match & FILTER_SUITE_MATCH_SUITE_DESCRIPTION:
            for desc in self.testsuite_description:
                if fnmatch.fnmatch(suite.description, desc):
                    match |= FILTER_SUITE_MATCH_SUITE_DESCRIPTION
                    break

        if self.tags and not parent_suite_match & FILTER_SUITE_MATCH_TAG:
            for tag in self.tags:
                if fnmatch.filter(suite.tags, tag):
                    match |= FILTER_SUITE_MATCH_TAG
                    break

        if self.properties and not parent_suite_match & FILTER_SUITE_MATCH_PROPERTY:
            for key, value in self.properties.items():
                if key in suite.properties and suite.properties[key] == value:
                    match |= FILTER_SUITE_MATCH_PROPERTY
                    break

        if self.link_names and not parent_suite_match & FILTER_SUITE_MATCH_LINK_NAME:
            for link in self.link_names:
                if link in [name for url, name in suite.links]:
                    match |= FILTER_SUITE_MATCH_LINK_NAME
                    break

        return match

def add_filter_args_to_cli_parser(cli_parser):
    def property_value(value):
        splitted = value.split(":")
        if len(splitted) != 2:
            raise ValueError()
        return splitted

    cli_parser.add_argument("path", nargs="*", default=[], help="Filters on test/testsuite path (wildcard character '*' can be used)")
    cli_parser.add_argument("--test-desc", nargs="+", default=[], help="Filters on test descriptions")
    cli_parser.add_argument("--suite-desc", nargs="+", default=[], help="Filters on test suite descriptions")
    cli_parser.add_argument("--tag", "-a", nargs="+", default=[], help="Filters on test & test suite tags")
    cli_parser.add_argument("--property", "-m", nargs="+", type=property_value, default=[], help="Filters on test & test suite property")
    cli_parser.add_argument("--link", "-l", nargs="+", default=[], help="Filters on test & test suite link names")

def get_filter_from_cli_args(cli_args):
    filter = Filter()
    filter.path = cli_args.path
    filter.test_description = cli_args.test_desc
    filter.testsuite_description = cli_args.suite_desc
    filter.tags = cli_args.tag
    filter.properties = dict(cli_args.property)
    filter.link_names = cli_args.link
    return filter