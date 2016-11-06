'''
Created on Nov 1, 2016

@author: nicolas
'''

import os.path
import tempfile

import pytest

from lemoncheesecake.launcher import importer
from lemoncheesecake.exceptions import *
import lemoncheesecake as lcc
from lemoncheesecake.runtime import get_runtime
from lemoncheesecake.reporting.backends.xml import serialize_report_as_string

from helpers import run_testsuite, run_testsuites, assert_report_from_testsuite, assert_report_from_testsuites, assert_report_stats

def test_simple_test():
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            lcc.check_int_eq("foo", 1, 1)
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1, expected_checks_success=1)
    
    assert report.get_test("sometest").outcome == True

def test_test_with_all_metadata():
    class MySuite(lcc.TestSuite):
        @lcc.link("http://foo.bar", "foobar")
        @lcc.prop("foo", "bar")
        @lcc.tags("foo", "bar")
        @lcc.test("Some test")
        def sometest(self):
            lcc.check_int_eq("foo", 1, 1)
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1, expected_checks_success=1)

    assert report.get_test("sometest").outcome == True

def test_testsuite_with_all_metadata():
    @lcc.link("http://foo.bar", "foobar")
    @lcc.prop("foo", "bar")
    @lcc.tags("foo", "bar")
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            lcc.check_int_eq("foo", 1, 1)
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1, expected_checks_success=1)
    
    assert report.get_test("sometest").outcome == True

def test_multiple_testsuites_and_tests():
    class MySuite1(lcc.TestSuite):
        @lcc.tags("foo")
        @lcc.test("Some test 1")
        def test_1_1(self):
            lcc.check_int_eq("foo", 2, 2)
        
        @lcc.tags("bar")
        @lcc.test("Some test 2")
        def test_1_2(self):
            lcc.check_int_eq("foo", 2, 2)
        
        @lcc.tags("baz")
        @lcc.test("Some test 3")
        def test_1_3(self):
            lcc.check_int_eq("foo", 3, 2)
    
    class MySuite2(lcc.TestSuite):
        @lcc.prop("foo", "bar")
        @lcc.test("Some test 1")
        def test_2_1(self):
            1 / 0
        
        @lcc.prop("foo", "baz")
        @lcc.test("Some test 2")
        def test_2_2(self):
            lcc.check_int_eq("foo", 2, 2)
        
        @lcc.test("Some test 3")
        def test_2_3(self):
            lcc.check_int_eq("foo", 2, 2)
    
        # suite3 is a sub suite of suite3
        class MySuite3(lcc.TestSuite):
            @lcc.prop("foo", "bar")
            @lcc.test("Some test 1")
            def test_3_1(self):
                lcc.check_int_eq("foo", 1, 1)
            
            @lcc.prop("foo", "baz")
            @lcc.test("Some test 2")
            def test_3_2(self):
                raise lcc.AbortTest()
            
            @lcc.test("Some test 3")
            def test_3_3(self):
                lcc.check_int_eq("foo", 1, 1)
    
    run_testsuites([MySuite1, MySuite2])
    
    report = get_runtime().report

    assert_report_from_testsuites(report, [MySuite1, MySuite2])
    assert_report_stats(
        report,
        expected_tests_success=6, expected_tests_failure=3,
        expected_checks_success=6, expected_checks_failure=1, expected_error_logs=2
    )
    
    assert report.get_test("test_1_1").outcome == True
    assert report.get_test("test_1_2").outcome == True
    assert report.get_test("test_1_3").outcome == False

    assert report.get_test("test_2_1").outcome == False
    assert report.get_test("test_2_2").outcome == True
    assert report.get_test("test_2_3").outcome == True

    assert report.get_test("test_3_1").outcome == True
    assert report.get_test("test_3_2").outcome == False
    assert report.get_test("test_3_3").outcome == True

def test_check_success():
    class MySuite(lcc.TestSuite):
        @lcc.test("Test 1")
        def test_1(self):
            lcc.check_eq("somevalue", "foo", "foo")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1, expected_checks_success=1)
    
    test = report.get_test("test_1")
    assert test.outcome == True
    step = test.steps[0]
    assert "somevalue" in step.entries[0].description
    assert "foo" in step.entries[0].description
    assert step.entries[0].outcome == True
    assert step.entries[0].details == None

def test_check_failure():
    class MySuite(lcc.TestSuite):
        @lcc.test("Test 1")
        def test_1(self):
            lcc.check_eq("somevalue", "foo", "bar")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_failure=1, expected_checks_failure=1)
    
    test = report.get_test("test_1")
    assert test.outcome == False
    step = test.steps[0]
    assert "somevalue" in step.entries[0].description
    assert "bar" in step.entries[0].description
    assert step.entries[0].outcome == False
    assert "foo" in step.entries[0].details

def test_assert_success():
    class MySuite(lcc.TestSuite):
        @lcc.test("Test 1")
        def test_1(self):
            lcc.assert_eq("somevalue", "foo", "foo")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1, expected_checks_success=1)
    
    test = report.get_test("test_1")
    assert test.outcome == True
    step = test.steps[0]
    assert "somevalue" in step.entries[0].description
    assert "foo" in step.entries[0].description
    assert step.entries[0].outcome == True
    assert step.entries[0].details == None

def test_assert_failure():
    class MySuite(lcc.TestSuite):
        @lcc.test("Test 1")
        def test_1(self):
            lcc.assert_eq("somevalue", "foo", "bar")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_failure=1, expected_checks_failure=1, expected_error_logs=1)
    
    test = report.get_test("test_1")
    assert test.outcome == False
    step = test.steps[0]
    assert "somevalue" in step.entries[0].description
    assert "bar" in step.entries[0].description
    assert step.entries[0].outcome == False
    assert "foo" in step.entries[0].details

def test_all_types_of_logs():
    class MySuite(lcc.TestSuite):
        @lcc.test("Test 1")
        def test_1(self):
            lcc.log_debug("some debug message")
            lcc.log_info("some info message")
            lcc.log_warn("some warning message")
        
        @lcc.test("Test 2")
        def test_2(self):
            lcc.log_error("some error message")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, 
        expected_tests_success=1, expected_tests_failure=1, 
        expected_error_logs=1, expected_warning_logs=1
    )
    
    test = report.get_test("test_1")
    assert test.outcome == True
    step = test.steps[0]
    assert step.entries[0].level == "debug"
    assert step.entries[0].message == "some debug message"
    assert step.entries[1].level == "info"
    assert step.entries[1].message == "some info message"
    assert step.entries[2].level == "warn"
    
    test = report.get_test("test_2")
    assert test.outcome == False
    step = test.steps[0]    
    assert step.entries[0].message == "some error message"
    assert step.entries[0].level == "error"

def test_multiple_steps():
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            lcc.set_step("step 1")
            lcc.log_info("do something")
            lcc.set_step("step 2")
            lcc.log_info("do something else")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1)

    test = report.get_test("sometest")
    assert test.outcome == True
    assert test.steps[0].description == "step 1"
    assert test.steps[0].entries[0].level == "info"
    assert test.steps[0].entries[0].message == "do something"
    assert test.steps[1].description == "step 2"
    assert test.steps[1].entries[0].level == "info"
    assert test.steps[1].entries[0].message == "do something else"

def test_default_step():
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            lcc.log_info("do something")
    
    run_testsuite(MySuite)
    
    report = get_runtime().report

    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1)
    
    test = report.get_test("sometest")
    assert test.outcome == True
    assert test.steps[0].description == "-"
    assert test.steps[0].entries[0].level == "info"
    assert test.steps[0].entries[0].message == "do something"

def test_prepare_attachment(tmpdir):
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            filename = lcc.prepare_attachment("foobar.txt", "some description")
            with open(filename, "w") as fh:
                fh.write("some content")
    
    run_testsuite(MySuite, tmpdir)
    
    report = get_runtime().report
    
    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1)

    test = report.get_test("sometest")
    assert test.steps[0].entries[0].filename.endswith("foobar.txt")
    assert test.steps[0].entries[0].description == "some description"
    assert test.outcome == True
    assert open(os.path.join(get_runtime().report_dir, test.steps[0].entries[0].filename)).read() == "some content"

def test_save_attachment_file(tmpdir):
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            dirname = tempfile.mkdtemp()
            filename = os.path.join(dirname, "somefile.txt")
            with open(filename, "w") as fh:
                fh.write("some other content")
            lcc.save_attachment_file(filename, "some other file")
    
    run_testsuite(MySuite, tmpdir)
    
    report = get_runtime().report
    
    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1)

    test = report.get_test("sometest")
    assert test.steps[0].entries[0].filename.endswith("somefile.txt")
    assert test.steps[0].entries[0].description == "some other file"
    assert test.outcome == True
    assert open(os.path.join(get_runtime().report_dir, test.steps[0].entries[0].filename)).read() == "some other content"

def test_save_attachment_content(tmpdir):
    class MySuite(lcc.TestSuite):
        @lcc.test("Some test")
        def sometest(self):
            lcc.save_attachment_content("foobar", "foobar.txt")
    
    run_testsuite(MySuite, tmpdir)
    
    report = get_runtime().report
    
    assert_report_from_testsuite(report, MySuite)
    assert_report_stats(report, expected_tests_success=1)

    test = report.get_test("sometest")
    assert test.steps[0].entries[0].filename.endswith("foobar.txt")
    assert test.steps[0].entries[0].description == "foobar.txt"
    assert test.outcome == True
    assert open(os.path.join(get_runtime().report_dir, test.steps[0].entries[0].filename)).read() == "foobar"