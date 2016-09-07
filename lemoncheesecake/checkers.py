'''
Created on Jan 24, 2016

@author: nicolas
'''

from lemoncheesecake.runtime import get_runtime
from lemoncheesecake.testsuite import AbortTest

import sys
import re

CHECKER_OBJECTS = {}
BASE_CHECKER_NAMES = [ ]

def check(description, outcome, details=None):
    return get_runtime().check(description, outcome, details)

class Check:
    assertion = False
    always_display_details = False
    comparator = None
    description_prefix = "Check that"
    comparator_label = None
    value_type = None
    doc_func_args = "name, actual, expected"
    
    def __init__(self, assertion=False, value_type=None):
        self.assertion = assertion
        self.value_type = value_type
    
    def handle_check_outcome(self, outcome):
        if self.assertion:
            if outcome:
                return
            else:
                raise AbortTest("previous assertion was not fulfilled")
        else:
            return outcome
    
    def __call__(self, name, actual, expected):
        outcome = self.compare(name, actual, expected)
        return self.handle_check_outcome(outcome)
    
    def compare(self, name, actual, expected):
        description = self.format_description(name, expected)
        if self.value_type:
            if type(actual) != self.value_type:
                return check(description, False, self.format_details(actual))
        outcome = self.comparator(actual, expected)
        details = None
        if not outcome or self.always_display_details:
            details = self.format_details(actual)
        return check(description, outcome, details)
    
    def format_actual_value(self, value):
        return "%s" % value
    format_expected_value = format_actual_value
    
    def format_description(self, name, expected):
        description = "{prefix} {name} {comparator} {expected}".format(
            prefix=self.description_prefix, name=name,
            comparator=self.comparator_label, expected=self.format_expected_value(expected)
        )
        if self.value_type:
            description += " (%s)" % self.value_type.__name__
        return description
    
    def format_details(self, actual):
        details = "Got %s" % self.format_actual_value(actual)
        if self.value_type:
            details += " (%s)" % type(actual).__name__
        return details
    
    def build_doc_func_args(self):
        return self.doc_func_args
    
    def build_doc_func_ret(self):
        return self.doc_func_ret
    
    def build_doc_func_description(self):
        return "{prefix} actual {comparator} expected".format(
            prefix=self.description_prefix, comparator=self.comparator_label
        )
    
    def build_doc(self, func_name):
        doc = "%s(%s)" % (func_name, self.build_doc_func_args())
        if not self.assertion:
            doc += " -> bool"
        doc += "\n\n%s" % self.build_doc_func_description()
        if self.value_type:
            doc += " (value's type must be %s)" % self.value_type.__name__
        doc += "\n"
        if self.assertion:
            doc += "Raise AbortTest if the check does not succeed"
        else:
            doc += "Return True if the check succeed, False otherwise"
        return doc

def do_register_checker(name, checker_inst, assertion_inst):
    def make_func(obj, func_name):
        def func(*args, **kwargs):
            return obj(*args, **kwargs)
        func.__doc__ = obj.build_doc(func_name)
        return func
    
    def register_checker_object(name, inst):
        CHECKER_OBJECTS[name] = inst
        setattr(sys.modules[__name__], name, make_func(inst, name))
        
    register_checker_object("check_%s" % name, checker_inst)
    register_checker_object("assert_%s" % name, assertion_inst)

def register_checker(name, checker_class, value_type=None, is_base_checker=True):
    if is_base_checker:
        global BASE_CHECKER_NAMES
        BASE_CHECKER_NAMES.append(name)
    
    checker_class.name = name
    checker_inst = checker_class(value_type=value_type)
    assertion_inst = checker_class(assertion=True, value_type=value_type)
    do_register_checker(name, checker_inst, assertion_inst)

def checker(name, value_type=None, is_base_checker=True):
    def wrapper(klass):
        register_checker(name, klass, value_type, is_base_checker=is_base_checker)
        return klass
    return wrapper

def get_checker_function(name):
    return getattr(sys.modules[__name__], "check_%s" % name)

def get_assertion_function(name):
    return getattr(sys.modules[__name__], "assert_%s" % name)

def get_checker_object(name):
    return CHECKER_OBJECTS["check_%s" % name]

def get_assertion_object(name):
    return CHECKER_OBJECTS["assert_%s" % name]

################################################################################
# Equality / non-equality checkers 
################################################################################

@checker("eq")
class CheckEq(Check):
    comparator_label = "is equal to"
    comparator = staticmethod(lambda a, e: a == e)

@checker("not_eq")
class CheckNotEq(Check):
    comparator_label = "is not equal to"
    comparator = staticmethod(lambda a, e: a != e)
    always_display_details = True

################################################################################
# Greater than and Greater than or equal checkers 
################################################################################

@checker("gt")
class CheckGt(Check):
    comparator_label = "is greater than"
    comparator = staticmethod(lambda a, e: a > e)

@checker("gteq")
class CheckGteq(Check):
    comparator_label = "is greater or equal than"
    comparator = staticmethod(lambda a, e: a >= e)

################################################################################
# Lower than and Lower than or equal checkers 
################################################################################

@checker("lt")
class CheckLt(Check):
    comparator_label = "is lower than"
    comparator = staticmethod(lambda a, e: a < e)
    always_display_details = True

@checker("lteq")
class CheckLteq(Check):
    comparator_label = "is lower or equal than"
    comparator = staticmethod(lambda a, e: a <= e)
    always_display_details = True

################################################################################
# str checkers 
################################################################################

@checker("str_eq")
class CheckStrEq(CheckEq):
    format_expected_value = format_actual_value = staticmethod(lambda s: "'%s'" % s)

@checker("str_not_eq")
class CheckStrNotEq(CheckStrEq, CheckNotEq):
    always_display_details = True

@checker("str_match")
class CheckStrMatchPattern(CheckStrEq):
    comparator_label = "match pattern"
    format_expected_value = staticmethod(lambda p: "'%s'" % p.pattern)
    comparator = staticmethod(lambda a, e: bool(e.match(a)))
    always_display_details = True

@checker("str_does_not_match")
class CheckStrDoesNotMatchPattern(CheckStrMatchPattern):
    comparator_label = "does not match pattern"
    comparator = staticmethod(lambda a, e: not bool(e.match(a)))

@checker("str_contains")
class CheckStrContains(CheckStrEq):
    comparator_label = "contains"
    comparator = staticmethod(lambda a, e: e in a)

@checker("str_does_not_contain")
class CheckStrDoesNotContain(CheckStrEq):
    comparator_label = "does not contain"
    comparator = staticmethod(lambda a, e: e not in a)

################################################################################
# Numeric checkers
################################################################################

def generate_comparator_checkers_for_type(type_):
    checker_classes = CheckEq, CheckNotEq, CheckGt, CheckGteq, CheckLt, CheckLteq
    for klass in checker_classes:
        do_register_checker("%s_%s" % (type_.__name__, klass.name), 
                    klass(value_type=type_), klass(value_type=type_, assertion=True))

generate_comparator_checkers_for_type(int)
generate_comparator_checkers_for_type(float)

################################################################################
# list checkers 
################################################################################

@checker("list_eq")
class CheckListEq(CheckEq):
    pass

@checker("list_len")
class CheckListLen(Check):
    comparator = staticmethod(lambda a, e: len(a) == e)
    def format_description(self, name, expected):
        return "{prefix} {name} contains {expected} elements".format(
            prefix=self.description_prefix, name=name, expected=expected
        )
    def format_details(self, actual):
        return "Got %d elements: %s" % (len(actual), actual)

@checker("list_contains")
class CheckListContains(Check):
    comparator_label = "contains elements"
    always_display_details = True
    
    def compare(self, name, actual, expected):
        description = self.format_description(name, expected)
        
        missing = expected[:]
        for elem in missing:
            if elem in actual:
                missing.remove(elem)
        if missing:
            details = "Missing elements %s in list %s" % (missing, actual)
            return check(description, False, details)
        else:
            return check(description, True, None)

################################################################################
# dict checkers 
################################################################################

def register_dict_checkers(dict_checker_name_fmt, dict_checker):
    def wrapper(value_checker):
        class dict_value_checker(dict_checker):
            def build_doc_func_description(self):
                return "{prefix} key[d] {comparator} expected".format(
                    prefix=self.description_prefix, comparator=value_checker.comparator_label
                )
            
            def __call__(self, *args, **kwargs):
                kwargs["value_checker"] = value_checker
                return dict_checker.__call__(self, *args, **kwargs)
        return dict_value_checker
    global BASE_CHECKER_NAMES
    for name in BASE_CHECKER_NAMES:
        klass = wrapper(get_checker_object(name))
        do_register_checker(dict_checker_name_fmt % name, klass(), klass(assertion=True))

@checker("dict_has_key", is_base_checker=False)
class CheckDictHasKey(Check):
    doc_func_args = "key, d"
    
    def build_doc_func_description(self):
        return "{prefix} d has entry key".format(
            prefix=self.description_prefix
        )
    
    def __call__(self, expected_key, actual):
        description = "{prefix} entry '{key}' is present".format(prefix=self.description_prefix, key=expected_key)
        outcome = check(description, expected_key in actual)
        self.handle_check_outcome(outcome)
        return outcome

@checker("dict_value", is_base_checker=False)
class CheckDictValue(Check):
    doc_func_args = "key, d, expected, value_checker"
    
    def build_doc_func_description(self):
        return "Check key[d] against expected using value_checker"
    
    def __call__(self, expected_key, actual, expected_value, value_checker):
        if actual.has_key(expected_key):
            ret = value_checker("'%s'" % expected_key, actual[expected_key], expected_value)
        else:
            check(value_checker.format_description(expected_key, expected_value), False,
                  "There is no key '%s'" % expected_key)
            ret = False
        return self.handle_check_outcome(ret)

register_dict_checkers("dictval_%s", CheckDictValue)

###
# Build symbol list for wild import
###

__all__ = ()
for symbol in dir():
    if symbol.startswith("check_") or symbol.startswith("assert_"):
        __all__ = __all__ + (symbol,)