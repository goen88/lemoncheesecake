#!/usr/bin/python

import sys
sys.path.append("..")

from lemoncheesecake.launcher import Launcher, import_testsuites_from_directory, PropertyValidator
from lemoncheesecake.worker import Worker
from lemoncheesecake.reporting import get_backend, enable_backend

class MyWorker(Worker):
    pass

enable_backend("xml")
get_backend("json").pretty_formatting = True
get_backend("xml").indent_level = 4

property_validator = PropertyValidator()
property_validator.set_test_property_accepted_values("priority", ("low", "medium", "high"))
property_validator.make_suite_property_mandatory("type")

launcher = Launcher()
launcher.set_worker(MyWorker())
launcher.load_testsuites(import_testsuites_from_directory("suites"))
launcher.handle_cli()