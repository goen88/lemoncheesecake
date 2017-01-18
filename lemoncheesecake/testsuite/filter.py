'''
Created on Sep 8, 2016

@author: nicolas
'''

import fnmatch

FILTER_SUITE_MATCH_ID = 0x01
FILTER_SUITE_MATCH_DESCRIPTION = 0x02
FILTER_SUITE_MATCH_TAG = 0x04
FILTER_SUITE_MATCH_LINK_NAME = 0x08
FILTER_SUITE_MATCH_PROPERTY = 0x10

__all__ = ("Filter", "add_filter_args_to_cli_parser", "get_filter_from_cli_args")

class Filter:
    def __init__(self):
        self.test_id = []
        self.test_description = []
        self.testsuite_id = []
        self.testsuite_description = []
        self.tags = [ ]
        self.properties = {}
        self.link_names = [ ]
    
    def is_empty(self):
        count = 0
        for value in self.test_id, self.testsuite_id, self.test_description, \
            self.testsuite_description, self.tags, self.properties, self.link_names:
            count += len(value)
        return count == 0
    
    def get_flags_to_match_testsuite(self):
        flags = 0
        if self.testsuite_id:
            flags |= FILTER_SUITE_MATCH_ID
        if self.testsuite_description:
            flags |= FILTER_SUITE_MATCH_DESCRIPTION
        return flags
    
    def match_test(self, test, parent_suite_match=0):
        match = False
        
        if self.test_id:
            for id in self.test_id:
                if fnmatch.fnmatch(test.id, id):
                    match = True
                    break
            if not match:
                return False
        
        if self.test_description:
            for desc in self.test_description:
                if fnmatch.fnmatch(test.description, desc):
                    match = True
                    break
            if not match:
                return False
        
        if self.tags and not parent_suite_match & FILTER_SUITE_MATCH_TAG:
            for tag in self.tags:
                if fnmatch.filter(test.tags, tag):
                    match = True
                    break
            if not match:
                return False
                
        if self.properties and not parent_suite_match & FILTER_SUITE_MATCH_PROPERTY:
            for key, value in self.properties.items():
                if key in test.properties and test.properties[key] == value:
                    match = True
                    break
            if not match:
                return False
                
        if self.link_names and not parent_suite_match & FILTER_SUITE_MATCH_LINK_NAME:
            for link in self.link_names:
                if link in [ l[1] for l in test.links if l[1] ]:
                    match = True
                    break
            if not match:
                return False
        
        return True
    
    def match_testsuite(self, suite, parent_suite_match=0):
        match = 0
        
        if self.testsuite_id and not parent_suite_match & FILTER_SUITE_MATCH_ID:
            for id in self.testsuite_id:
                if fnmatch.fnmatch(suite.id, id):
                    match |= FILTER_SUITE_MATCH_ID
                    break
                
        if self.testsuite_description and not parent_suite_match & FILTER_SUITE_MATCH_DESCRIPTION:
            for desc in self.testsuite_description:
                if fnmatch.fnmatch(suite.description, desc):
                    match |= FILTER_SUITE_MATCH_DESCRIPTION
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
                if link in [ l[0] for l in suite.links ]:
                    match |= FILTER_SUITE_MATCH_LINK_NAME
                    break

        return match

def add_filter_args_to_cli_parser(cli_parser):
    def property_value(value):
        splitted = value.split(":")
        if len(splitted) != 2:
            raise ValueError()
        return splitted

    cli_parser.add_argument("--test-id", "-t", nargs="+", default=[], help="Filters on test IDs")
    cli_parser.add_argument("--test-desc", nargs="+", default=[], help="Filters on test descriptions")
    cli_parser.add_argument("--suite-id", "-s", nargs="+", default=[], help="Filters on test suite IDs")
    cli_parser.add_argument("--suite-desc", nargs="+", default=[], help="Filters on test suite descriptions")
    cli_parser.add_argument("--tag", "-a", nargs="+", default=[], help="Filters on test & test suite tags")
    cli_parser.add_argument("--property", "-m", nargs="+", type=property_value, default=[], help="Filters on test & test suite property")
    cli_parser.add_argument("--link", "-l", nargs="+", default=[], help="Filters on test & test suite link names")

def get_filter_from_cli_args(cli_args):
    filter = Filter()
    filter.test_id = cli_args.test_id
    filter.test_description = cli_args.test_desc
    filter.testsuite_id = cli_args.suite_id
    filter.testsuite_description = cli_args.suite_desc
    filter.tags = cli_args.tag
    filter.properties = dict(cli_args.property)
    filter.link_names = cli_args.link
    return filter