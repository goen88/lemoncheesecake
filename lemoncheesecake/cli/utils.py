'''
Created on Mar 12, 2017

@author: nicolas
'''

from lemoncheesecake.filter import get_filter_from_cli_args, filter_suites
from lemoncheesecake.exceptions import UserError


def filter_suites_from_cli_args(suites, cli_args):
    filtr = get_filter_from_cli_args(cli_args)
    if filtr.is_empty():
        return suites

    suites = filter_suites(suites, filtr)
    if len(suites) == 0:
        raise UserError("The filter does not match any test")

    return suites


def get_suites_from_project(project, cli_args):
    suites = project.get_suites()
    if not any(suite.has_selected_tests() for suite in suites):
        raise UserError("No test is defined in your lemoncheesecake project.")

    return filter_suites_from_cli_args(suites, cli_args)
