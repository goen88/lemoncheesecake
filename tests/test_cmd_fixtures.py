import os
import pytest

from helpers import generate_project, cmdout

from lemoncheesecake.cli import main

FIXTURES_MODULE = """import lemoncheesecake as lcc

@lcc.fixture(scope="session")
def foo():
    pass

@lcc.fixture(scope="testsuite")
def bar(foo):
    pass


@lcc.fixture(scope="test")
def baz(bar):
    pass
"""

TEST_MODULE = """import lemoncheesecake as lcc

@lcc.testsuite("My Suite")
class mysuite:
    @lcc.test("My Test 1")
    def mytest1(self, foo, bar, baz):
        pass
    
    @lcc.test("My Test 2")
    def mytest2(self, foo, baz):
        pass
    
"""

EMPTY_TEST_MODULE = """import lemoncheesecake as lcc

@lcc.testsuite("My Suite")
class mysuite:
    pass
"""

@pytest.fixture()
def project(tmpdir):
    generate_project(tmpdir.strpath, "mysuite", TEST_MODULE, FIXTURES_MODULE    )
    old_cwd = os.getcwd()
    os.chdir(tmpdir.strpath)
    yield
    os.chdir(old_cwd)

@pytest.fixture()
def notest_project(tmpdir):
    generate_project(tmpdir.strpath, "mysuite", EMPTY_TEST_MODULE)
    old_cwd = os.getcwd()
    os.chdir(tmpdir.strpath)
    yield
    os.chdir(old_cwd)

def test_fixtures(project, cmdout):
    assert main(["fixtures"]) == 0
    
    cmdout.assert_lines_match(".+foo.+ 1 .+ 2 .+")
    cmdout.assert_lines_match(".+bar.+foo.+ 1 .+ 1 .+")
    cmdout.assert_lines_match(".+baz.+bar.+ 0 .+ 2 .+")

def test_fixtures_empty_project(notest_project, cmdout):
    assert main(["fixtures"]) == 0
    
    cmdout.assert_lines_match(".*session.*:.*none.*")
    cmdout.assert_lines_match(".*testsuite.*:.*none.*")
    cmdout.assert_lines_match(".*test.*:.*none.*")