"""
A testsuite module can safely import this module using a wild import. The content
of the following modules will be directly accessible:
- lemoncheesecake.testsuite
- lemoncheesecake.runtime
- lemoncheesecake.checkers
"""

from lemoncheesecake.testsuite import *
from lemoncheesecake.runtime import *
from lemoncheesecake.checkers import *
from lemoncheesecake.exceptions import AbortTest, AbortTestSuite, AbortAllTests

worker = None
def set_worker(wrk):
    global worker
    worker = wrk
