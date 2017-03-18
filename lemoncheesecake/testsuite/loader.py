'''
Created on Feb 5, 2017

@author: nicolas
'''

import os.path as osp
import inspect

from lemoncheesecake.importer import get_matching_files, get_py_files_from_dir, strip_py_ext, import_module
from lemoncheesecake.exceptions import ProgrammingError, ImportTestSuiteError, serialize_current_exception
from lemoncheesecake.testsuite.core import Test, TestSuite, TESTSUITE_HOOKS

__all__ = "import_testsuite_from_file", "import_testsuites_from_files", "import_testsuites_from_directory", \
    "load_testsuite_from_class", "load_testsuites"

def is_testsuite(obj):
    return inspect.isclass(obj) and \
        hasattr(obj, "_lccmetadata") and \
        obj._lccmetadata.is_testsuite

def is_test(obj):
    return inspect.ismethod(obj) and \
        hasattr(obj, "_lccmetadata") and \
        obj._lccmetadata.is_test

def load_test_from_method(method):
    md = method._lccmetadata
    test = Test(md.name, md.description, method)
    test.tags.extend(md.tags)
    test.properties.update(md.properties)
    test.links.extend(md.links)
    return test

def _list_object_attributes(obj):
    return [getattr(obj, n) for n in dir(obj) if not n.startswith("__")]

def get_test_methods_from_class(obj):
    return sorted(filter(is_test, _list_object_attributes(obj)), key=lambda m: m._lccmetadata.rank)

def get_sub_suites_from_class(obj):
    sub_suites = obj.sub_suites[:] if hasattr(obj, "sub_suites") else []
    return sorted(filter(is_testsuite, _list_object_attributes(obj) + sub_suites), key=lambda c: c._lccmetadata.rank)

def load_testsuite_from_class(klass, parent_suite=None):
    md = klass._lccmetadata
    try:
        inst = klass()
    except Exception:
        raise ProgrammingError("Got an unexpected error while instanciating testsuite class '%s':%s" % (
            klass.__name__, serialize_current_exception()
        ))
    suite = TestSuite(inst, md.name, md.description, parent_suite)
    suite.tags.extend(md.tags)
    suite.properties.update(md.properties)
    suite.links.extend(md.links)
    
    for hook_name in TESTSUITE_HOOKS:
        if hasattr(inst, hook_name):
            suite.add_hook(hook_name, getattr(inst, hook_name))

    for test_method in get_test_methods_from_class(inst):
        suite.add_test(load_test_from_method(test_method))
    
    for sub_suite_klass in get_sub_suites_from_class(inst):
        suite.add_sub_testsuite(load_testsuite_from_class(sub_suite_klass, parent_suite=suite))

    return suite

def import_testsuite_from_file(filename):
    """Get testsuite class from Python module.
    
    The testsuite class must have the same name as the containing Python module.
    
    Raise a ImportTestSuiteError if the testsuite class cannot be imported.
    """
    mod = import_module(filename)
    mod_name = strip_py_ext(osp.basename(filename))
    try:
        klass = getattr(mod, mod_name)
    except AttributeError:
        raise ImportTestSuiteError("Cannot find class '%s' in '%s'" % (mod_name, mod.__file__))
    return klass

def import_testsuites_from_files(patterns, excluding=[]):
    """
    Import testsuites from a list of files:
    - patterns: a mandatory list (a simple string can also be used instead of a single element list)
      of files to import; the wildcard '*' character can be used
    - exclude: an optional list (a simple string can also be used instead of a single element list)
      of elements to exclude from the expanded list of files to import
    Example: import_testsuites_from_files("test_*.py")
    """
    return [import_testsuite_from_file(f) for f in get_matching_files(patterns, excluding)]

def import_testsuites_from_directory(dir, recursive=True):
    """Find testsuite classes in modules found in dir.
    
    The function expect that:
    - each module (.py file) contains a class that inherits TestSuite
    - the class name must have the same name as the module name (if the module is foo.py 
      the class must be named foo)
    If the recursive argument is set to True, sub testsuites will be searched in a directory named
    from the suite module: if the suite module is "foo.py" then the sub suites directory must be "foo".
    
    Raise ImportTestSuiteError if one or more testsuite cannot be imported.
    """
    if not osp.exists(dir):
        raise ImportTestSuiteError("Directory '%s' does not exist" % dir)
    suites = [ ]
    for filename in get_py_files_from_dir(dir):
        suite = import_testsuite_from_file(filename)
        if recursive:
            subsuites_dir = strip_py_ext(filename)
            if osp.isdir(subsuites_dir):
                suite.sub_suites = import_testsuites_from_directory(subsuites_dir, recursive=True)
        suites.append(suite)
    if len(list(filter(lambda s: hasattr(s, "_rank"), suites))) == len(suites):
        suites.sort(key=lambda s: s._rank)
    return suites

def _load_testsuite(suite, loaded_tests, loaded_suites, metadata_policy):
        # process suite
        if metadata_policy:
            metadata_policy.check_suite_compliance(suite)
        loaded_suites[suite.name] = suite

        # process tests
        for test in suite.get_tests():
            if metadata_policy:
                metadata_policy.check_test_compliance(test)
            loaded_tests[test.name] = test
        
        # process sub suites
        for sub_suite in suite.get_sub_testsuites():
            _load_testsuite(sub_suite, loaded_tests, loaded_suites, metadata_policy)

def load_testsuites(suite_classes, metadata_policy=None):
    """Load testsuites classes.
    
    - testsuite classes get instantiated into objects
    - sanity checks are performed (among which unicity constraints)
    - test and testsuites are checked using metadata_policy
    """
    loaded_tests = {}
    loaded_suites = {}
    suites = []
    suites_ranks = {}
    for suite_class in suite_classes:
        suite = load_testsuite_from_class(suite_class)
        suites.append(suite)
        suites_ranks[suite] = suite_class._lccmetadata.rank
        _load_testsuite(suite, loaded_tests, loaded_suites, metadata_policy)
    return sorted(suites, key=lambda suite: suites_ranks[suite])
