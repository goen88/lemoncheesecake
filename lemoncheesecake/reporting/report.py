'''
Created on Mar 26, 2016

@author: nicolas
'''

import time
import re
from decimal import Decimal
from functools import reduce

from lemoncheesecake.consts import LOG_LEVEL_ERROR, LOG_LEVEL_WARN
from lemoncheesecake.utils import humanize_duration
from lemoncheesecake.testtree import BaseTest, BaseSuite, flatten_tests, flatten_suites, find_test, find_suite, TreeLocation

__all__ = (
    "LogData", "CheckData", "AttachmentData", "UrlData", "StepData", "TestData",
    "SuiteData", "HookData", "Report"
)

TEST_STATUSES = "passed", "failed", "skipped", "disabled"
DEFAULT_REPORT_TITLE = "Test Report"


# NB: it would be nicer to use:
# datetime.isoformat(sep=' ', timespec='milliseconds')
# unfortunately, the timespec argument is only available since Python 3.6

def format_timestamp(ts, date_time_sep=" ", skip_milliseconds=False):
    ts = round(ts, 3)
    result = time.strftime("%Y-%m-%d{sep}%H:%M:%S".format(sep=date_time_sep), time.localtime(ts))
    if not skip_milliseconds:
        result += ".%03d" % (Decimal(repr(ts)) % 1 * 1000)
    return result


def format_timestamp_as_iso_8601(ts):
    return format_timestamp(ts, date_time_sep="T", skip_milliseconds=True)


def parse_timestamp(s):
    m = re.compile("(.+)\.(\d+)").match(s)
    if not m:
        raise ValueError("s is not valid datetime representation with milliseconds precision")

    dt, milliseconds = m.group(1), int(m.group(2))

    return time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S")) + float(milliseconds) / 1000


def _get_duration(start_time, end_time):
    if start_time is not None and end_time is not None:
        return end_time - start_time
    else:
        return None


class LogData:
    def __init__(self, level, message, ts):
        self.level = level
        self.message = message
        self.time = ts

    def is_successful(self):
        return self.level != LOG_LEVEL_ERROR


class CheckData:
    def __init__(self, description, outcome, details=None):
        self.description = description
        self.outcome = outcome
        self.details = details

    def is_successful(self):
        return self.outcome


class AttachmentData:
    def __init__(self, description, filename):
        self.description = description
        self.filename = filename

    def is_successful(self):
        return True


class UrlData:
    def __init__(self, description, url):
        self.description = description
        self.url = url

    def is_successful(self):
        return True


class StepData:
    def __init__(self, description, detached=False):
        self.description = description
        self._detached = detached  # this attribute is runtime only is not intended to be serialized
        self.entries = []
        self.start_time = None
        self.end_time = None

    def is_successful(self):
        return all(entry.is_successful() for entry in self.entries)

    @property
    def duration(self):
        return _get_duration(self.start_time, self.end_time)


class ResultData(object):
    def __init__(self):
        self.steps = []
        self.start_time = None
        self.end_time = None

    def is_successful(self):
        return all(step.is_successful() for step in self.steps)

    @property
    def duration(self):
        return _get_duration(self.start_time, self.end_time)


class TestData(BaseTest, ResultData):
    def __init__(self, name, description):
        BaseTest.__init__(self, name, description)
        ResultData.__init__(self)
        self.status = None
        self.status_details = None
        # non-serialized attributes (only set in-memory during test execution)
        self.rank = 0


class HookData(ResultData):
    def __init__(self):
        ResultData.__init__(self)
        self.outcome = None

    def is_empty(self):
        return len(self.steps) == 0


class SuiteData(BaseSuite):
    def __init__(self, name, description):
        BaseSuite.__init__(self, name, description)
        self.suite_setup = None
        self.suite_teardown = None
        # non-serialized attributes (only set in-memory during test execution)
        self.rank = 0

    @property
    def start_time(self):
        if self.suite_setup:
            return self.suite_setup.start_time
        elif len(self.get_tests()) > 0:
            return self.get_tests()[0].start_time
        else:
            return None

    @property
    def end_time(self):
        if self.suite_teardown:
            return self.suite_teardown.end_time
        elif len(self.get_tests()) > 0:
            return self.get_tests()[-1].end_time
        else:
            return None

    @property
    def duration(self):
        return reduce(
            lambda x, y: x + y,
            [result.duration for result in flatten_results_from_suites([self])],
            0
        )

    def get_tests(self):
        tests = super(SuiteData, self).get_tests()
        return sorted(tests, key=lambda t: t.rank)

    def get_suites(self, include_empty_suites=False):
        suites = super(SuiteData, self).get_suites(include_empty_suites)
        return sorted(suites, key=lambda s: s.rank)


class _Stats:
    def __init__(self):
        self.tests = 0
        self.enabled_tests = 0
        self.test_statuses = {s: 0 for s in TEST_STATUSES}
        self.successful_tests_percentage = 0
        self.errors = 0
        self.checks = 0
        self.check_successes = 0
        self.check_failures = 0
        self.error_logs = 0
        self.warning_logs = 0
        self.duration = None
        self.duration_cumulative = 0


def _update_stats_from_results(stats, results):
    for result in results:
        if result.duration is not None:
            stats.duration_cumulative += result.duration
        for step in result.steps:
            for entry in step.entries:
                if isinstance(entry, CheckData):
                    stats.checks += 1
                    if entry.outcome == True:
                        stats.check_successes += 1
                    elif entry.outcome == False:
                        stats.check_failures += 1
                if isinstance(entry, LogData):
                    if entry.level == LOG_LEVEL_WARN:
                        stats.warning_logs += 1
                    elif entry.level == LOG_LEVEL_ERROR:
                        stats.error_logs += 1


def _update_stats_from_tests(stats, tests):
    stats.tests = len(tests)

    for test in tests:
        if test.status:
            stats.test_statuses[test.status] += 1

    stats.enabled_tests = len(tests) - stats.test_statuses["disabled"]

    stats.successful_tests_percentage = \
        (float(stats.test_statuses["passed"]) / stats.enabled_tests * 100) if stats.enabled_tests else 0


def get_stats_from_report(report):
    stats = _Stats()

    if report.end_time is not None:
        stats.duration = (report.end_time - report.start_time)
    _update_stats_from_results(stats, flatten_results_from_report(report))
    _update_stats_from_tests(stats, list(flatten_tests(report.suites)))

    return stats


def get_stats_from_suites(suites):
    stats = _Stats()

    _update_stats_from_results(stats, flatten_results_from_suites(suites))
    _update_stats_from_tests(stats, list(flatten_tests(suites)))

    return stats


class Report:
    def __init__(self):
        self.info = []
        self.test_session_setup = None
        self.test_session_teardown = None
        self.suites = []
        self.start_time = None
        self.end_time = None
        self.report_generation_time = None
        self.title = DEFAULT_REPORT_TITLE
        self.nb_threads = 1

    @property
    def duration(self):
        return _get_duration(self.start_time, self.end_time)

    def add_info(self, name, value):
        self.info.append([name, value])
    
    def add_suite(self, suite):
        self.suites.append(suite)
    
    def get_suites(self):
        return sorted(self.suites, key=lambda s: s.rank)

    def get_suite(self, hierarchy):
        return find_suite(self.suites, hierarchy)

    def get_test(self, hierarchy):
        return find_test(self.suites, hierarchy)

    def get_stats(self):
        return get_stats_from_report(self)

    def get(self, location):
        if location.node_type == TreeLocation.TEST_SESSION_SETUP:
            return self.test_session_setup
        elif location.node_type == TreeLocation.TEST_SESSION_TEARDOWN:
            return self.test_session_teardown
        elif location.node_type == TreeLocation.SUITE_SETUP:
            suite = self.get_suite(location.node_hierarchy)
            return suite.suite_setup
        elif location.node_type == TreeLocation.SUITE_TEARDOWN:
            suite = self.get_suite(location.node_hierarchy)
            return suite.suite_teardown
        elif location.node_type == TreeLocation.TEST:
            return self.get_test(location.node_hierarchy)
        else:
            raise Exception("Unknown location type %s" % location.node_type)

    def is_successful(self):
        return all(test.status in ("passed", "disabled") for test in flatten_tests(self.suites))

    def serialize_stats(self):
        stats = self.get_stats()

        return (
            ("Start time", time.asctime(time.localtime(self.start_time))),
            ("End time", time.asctime(time.localtime(self.end_time)) if self.end_time else "n/a"),
            ("Duration", humanize_duration(self.end_time - self.start_time) if self.end_time else "n/a"),
            ("Tests", str(stats.tests)),
            ("Successful tests", str(stats.test_statuses["passed"])),
            ("Successful tests in %", "%d%%" % stats.successful_tests_percentage),
            ("Failed tests", str(stats.test_statuses["failed"])),
            ("Skipped tests", str(stats.test_statuses["skipped"])),
            ("Disabled tests", str(stats.test_statuses["disabled"]))
        )


def flatten_steps(suites):
    for test in flatten_tests(suites):
        for step in test.steps:
            yield step


def flatten_results_from_suites(suites):
    for suite in flatten_suites(suites):
        if suite.suite_setup:
            yield suite.suite_setup
        for test in suite.get_tests():
            yield test
        if suite.suite_teardown:
            yield suite.suite_teardown


def flatten_results_from_report(report):
    if report.test_session_setup:
        yield report.test_session_setup
    for result in flatten_results_from_suites(report.get_suites()):
        yield result
    if report.test_session_teardown:
        yield report.test_session_teardown
