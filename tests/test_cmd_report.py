import os.path as osp

from helpers import run_suite_class, assert_run_output, cmdout

import lemoncheesecake.api as lcc
from lemoncheesecake.cli import main
from lemoncheesecake.reporting.backends.json_ import JsonBackend

@lcc.suite("My suite")
class mysuite:
    @lcc.test("My Test 1")
    def mytest1(self):
        lcc.log_error("failure")

    @lcc.test("My Test 2")
    def mytest2(self):
        pass


def test_report_from_dir(tmpdir, cmdout):
    run_suite_class(mysuite, tmpdir=tmpdir, backends=[JsonBackend()])

    assert main(["report", tmpdir.strpath]) == 0
    assert_run_output(cmdout, "mysuite", successful_tests=["mytest2"], failed_tests=["mytest1"])


def test_report_from_file(tmpdir, cmdout):
    backend = JsonBackend()
    run_suite_class(mysuite, tmpdir=tmpdir, backends=[backend])

    assert main(["report", osp.join(tmpdir.strpath, backend.get_report_filename())]) == 0
    assert_run_output(cmdout, "mysuite", successful_tests=["mytest2"], failed_tests=["mytest1"])


def test_report_with_filter(tmpdir, cmdout):
    run_suite_class(mysuite, tmpdir=tmpdir, backends=[JsonBackend()])

    assert main(["report", tmpdir.strpath, "--passed"]) == 0
    assert_run_output(cmdout, "mysuite", successful_tests=["mytest2"])