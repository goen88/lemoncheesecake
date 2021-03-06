from lemoncheesecake.cli import main
from lemoncheesecake.cli.commands.top import TopSuites, TopTests, TopSteps
from lemoncheesecake.reporting.backends.json_ import save_report_into_file

from helpers.cli import cmdout
from helpers.report import report_in_progress_path
from helpers.testtreemockup import suite_mockup, tst_mockup, step_mockup, make_suite_data_from_mockup, \
    report_mockup, make_report_from_mockup


def test_get_top_suites():
    suite1 = suite_mockup("suite1").add_test(tst_mockup("test", start_time=0.0, end_time=1.0))
    suite2 = suite_mockup("suite2").add_test(tst_mockup("test", start_time=1.0, end_time=4.0))

    top_suites = TopSuites.get_top_suites([make_suite_data_from_mockup(suite) for suite in (suite1, suite2)])
    assert len(top_suites) == 2
    assert top_suites[0][0] == "suite2"
    assert top_suites[0][1] == 1
    assert top_suites[0][2] == "3.000s"
    assert top_suites[0][3] == "75%"
    assert top_suites[1][0] == "suite1"
    assert top_suites[1][1] == 1
    assert top_suites[1][2] == "1.000s"
    assert top_suites[1][3] == "25%"


def test_top_suites_cmd(tmpdir, cmdout):
    suite1 = suite_mockup("suite1").add_test(tst_mockup("test", start_time=0.1, end_time=1.0))
    suite2 = suite_mockup("suite2").add_test(tst_mockup("test", start_time=1.0, end_time=4.0))
    report = report_mockup().add_suite(suite1).add_suite(suite2)

    report_path = tmpdir.join("report.json").strpath
    save_report_into_file(make_report_from_mockup(report), report_path)

    assert main(["top-suites", report_path]) == 0

    lines = cmdout.get_lines()
    assert "suite2" in lines[4]


def test_top_suites_cmd_test_run_in_progress(report_in_progress_path, cmdout):
    assert main(["top-suites", report_in_progress_path]) == 0

    cmdout.dump()
    cmdout.assert_substrs_anywhere(["suite"])


def test_get_top_tests():
    suite1 = suite_mockup("suite1").add_test(tst_mockup("test", start_time=0.0, end_time=1.0))
    suite2 = suite_mockup("suite2").add_test(tst_mockup("test", start_time=1.0, end_time=4.0))

    top_suites = TopTests.get_top_tests([make_suite_data_from_mockup(suite) for suite in (suite1, suite2)])
    assert len(top_suites) == 2
    assert top_suites[0][0] == "suite2.test"
    assert top_suites[0][1] == "3.000s"
    assert top_suites[0][2] == "75%"
    assert top_suites[1][0] == "suite1.test"
    assert top_suites[1][1] == "1.000s"
    assert top_suites[1][2] == "25%"


def test_top_tests_cmd(tmpdir, cmdout):
    suite1 = suite_mockup("suite1").add_test(tst_mockup("test", start_time=0.1, end_time=1.0))
    suite2 = suite_mockup("suite2").add_test(tst_mockup("test", start_time=1.0, end_time=4.0))
    report = report_mockup().add_suite(suite1).add_suite(suite2)

    report_path = tmpdir.join("report.json").strpath
    save_report_into_file(make_report_from_mockup(report), report_path)

    assert main(["top-tests", report_path]) == 0

    lines = cmdout.get_lines()
    assert "suite2.test" in lines[4]


def test_top_tests_cmd_test_run_in_progress(report_in_progress_path, cmdout):
    assert main(["top-tests", report_in_progress_path]) == 0

    cmdout.dump()
    cmdout.assert_substrs_anywhere(["suite.test_2"])


def test_get_top_steps():
    first_step = step_mockup("step1", start_time=0.0, end_time=1.0)
    second_step = step_mockup("step1", start_time=1.0, end_time=3.0)
    third_step = step_mockup("step2", start_time=3.0, end_time=4.0)

    suite1 = suite_mockup("suite1").add_test(tst_mockup().add_step(first_step).add_step(second_step))
    suite2 = suite_mockup("suite2").add_test(tst_mockup().add_step(third_step))

    top_steps = TopSteps.get_top_steps([make_suite_data_from_mockup(suite) for suite in (suite1, suite2)])

    assert len(top_steps) == 2

    assert top_steps[0][0] == "step1"
    assert top_steps[0][1] == "2"
    assert top_steps[0][2] == "1.000s"
    assert top_steps[0][3] == "2.000s"
    assert top_steps[0][4] == "1.500s"
    assert top_steps[0][5] == "3.000s"
    assert top_steps[0][6] == "75%"

    assert top_steps[1][0] == "step2"
    assert top_steps[1][1] == "1"
    assert top_steps[1][2] == "1.000s"
    assert top_steps[1][3] == "1.000s"
    assert top_steps[1][4] == "1.000s"
    assert top_steps[1][5] == "1.000s"
    assert top_steps[1][6] == "25%"


def test_top_steps_cmd(tmpdir, cmdout):
    report = report_mockup().add_suite(
        suite_mockup("suite1").add_test(
            tst_mockup().add_step(
                step_mockup("step1", start_time=0.1, end_time=1.0)
            )
        )
    )

    report_path = tmpdir.join("report.json").strpath
    save_report_into_file(make_report_from_mockup(report), report_path)

    assert main(["top-steps", report_path]) == 0

    lines = cmdout.get_lines()
    assert "step1" in lines[4]


def test_top_steps_cmd_test_run_in_progress(report_in_progress_path, cmdout):
    assert main(["top-steps", report_in_progress_path]) == 0

    cmdout.dump()
    cmdout.assert_substrs_anywhere(["step"])
