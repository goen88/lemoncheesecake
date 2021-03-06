.. _cli:

The ``lcc`` command line tool
=============================

.. _cli_commands:

``lcc`` commands
----------------

In addition to the main command ``run``, the ``lcc`` command provides other commands that work with test project and
reports:

``lcc show``
~~~~~~~~~~~~

Shows the project tests hierarchy.

  .. code-block:: console

      $ lcc show
      * suite_1
          - suite_1.test_1 (slow, priority:low)
          - suite_1.test_2 (priority:low)
          - suite_1.test_3 (priority:medium, #1235)
          - suite_1.test_4 (priority:low)
          - suite_1.test_5 (priority:high)
          - suite_1.test_6 (slow, priority:high)
          - suite_1.test_7 (priority:high)
          - suite_1.test_8 (priority:medium)
          - suite_1.test_9 (priority:medium)
      * suite_2
          - suite_2.test_1 (priority:low)
          - suite_2.test_2 (priority:low)
          - suite_2.test_3 (priority:high)
          - suite_2.test_4 (priority:medium)
          - suite_2.test_5 (priority:low)
          - suite_2.test_6 (priority:low)
          - suite_2.test_7 (priority:medium)
          - suite_2.test_8 (slow, priority:low, #1234)
          - suite_2.test_9 (slow, priority:medium)

``lcc diff``
~~~~~~~~~~~~

Compares two reports.

  .. code-block:: console

      $ lcc diff reports/report-1/ report/
      Added tests (1):
      - suite_3.test_1 (passed)

      Removed tests (1):
      - suite_1.test_9 (failed)

      Status changed (2):
      - suite_2.test_3 (failed => passed)
      - suite_2.test_4 (passed => failed)

``lcc fixtures``
~~~~~~~~~~~~~~~~

Shows available project fixtures.

  .. code-block:: console

      $ lcc fixtures

      Fixture with scope session_prerun:
      +---------+--------------+------------------+---------------+
      | Fixture | Dependencies | Used by fixtures | Used by tests |
      +---------+--------------+------------------+---------------+
      | fixt_1  | -            | 1                | 1             |
      +---------+--------------+------------------+---------------+


      Fixture with scope session:
      +---------+--------------+------------------+---------------+
      | Fixture | Dependencies | Used by fixtures | Used by tests |
      +---------+--------------+------------------+---------------+
      | fixt_2  | fixt_1       | 1                | 2             |
      | fixt_3  | -            | 2                | 1             |
      +---------+--------------+------------------+---------------+


      Fixture with scope suite:
      +---------+--------------+------------------+---------------+
      | Fixture | Dependencies | Used by fixtures | Used by tests |
      +---------+--------------+------------------+---------------+
      | fixt_4  | fixt_3       | 0                | 2             |
      | fixt_6  | fixt_3       | 1                | 1             |
      | fixt_5  | -            | 0                | 0             |
      +---------+--------------+------------------+---------------+


      Fixture with scope test:
      +---------+----------------+------------------+---------------+
      | Fixture | Dependencies   | Used by fixtures | Used by tests |
      +---------+----------------+------------------+---------------+
      | fixt_7  | fixt_6, fixt_2 | 0                | 2             |
      | fixt_8  | -              | 0                | 1             |
      | fixt_9  | -              | 0                | 1             |
      +---------+----------------+------------------+---------------+

``lcc stats``
~~~~~~~~~~~~~

Shows project statistics.

  .. code-block:: console

      $ lcc stats
      Tags:
      +------+-------+------+
      | Tag  | Tests | In % |
      +------+-------+------+
      | slow | 4     | 22%  |
      +------+-------+------+

      Properties:
      +----------+--------+-------+------+
      | Property | Value  | Tests | In % |
      +----------+--------+-------+------+
      | priority | low    | 8     | 44%  |
      | priority | medium | 6     | 33%  |
      | priority | high   | 4     | 22%  |
      +----------+--------+-------+------+

      Links:
      +-------+-------------------------+-------+------+
      | Name  | URL                     | Tests | In % |
      +-------+-------------------------+-------+------+
      | #1234 | http://example.com/1234 | 1     |  5%  |
      | #1235 | http://example.com/1235 | 1     |  5%  |
      +-------+-------------------------+-------+------+

      Total: 18 tests in 2 suites

``lcc report``
~~~~~~~~~~~~~~

Shows a generated report on the console, passing the ``--short`` argument will print it the same way as
``lcc run`` does.

  .. code-block:: console

    Test Organization end-point
    (github.organization)
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    |       | Get lemoncheesecake organization information                                                     |                                                              |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | INFO  | GET https://api.github.com/orgs/lemoncheesecake                                                  |                                                              |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect HTTP code to be equal to 200                                                              | Got 200                                                      |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | INFO  | Response                                                                                         |                                                              |
    |       | {                                                                                                |                                                              |
    |       |     "login": "lemoncheesecake",                                                                  |                                                              |
    |       |     "id": 28742541,                                                                              |                                                              |
    |       |     "node_id": "MDEyOk9yZ2FuaXphdGlvbjI4NzQyNTQx",                                               |                                                              |
    |       |     "url": "https://api.github.com/orgs/lemoncheesecake",                                        |                                                              |
    |       |     "repos_url": "https://api.github.com/orgs/lemoncheesecake/repos",                            |                                                              |
    |       |     "events_url": "https://api.github.com/orgs/lemoncheesecake/events",                          |                                                              |
    |       |     "hooks_url": "https://api.github.com/orgs/lemoncheesecake/hooks",                            |                                                              |
    |       |     "issues_url": "https://api.github.com/orgs/lemoncheesecake/issues",                          |                                                              |
    |       |     "members_url": "https://api.github.com/orgs/lemoncheesecake/members{/member}",               |                                                              |
    |       |     "public_members_url": "https://api.github.com/orgs/lemoncheesecake/public_members{/member}", |                                                              |
    |       |     "avatar_url": "https://avatars3.githubusercontent.com/u/28742541?v=4",                       |                                                              |
    |       |     "description": "Python framework for functional/QA testing",                                 |                                                              |
    |       |     "name": "lemoncheesecake",                                                                   |                                                              |
    |       |     "company": null,                                                                             |                                                              |
    |       |     "blog": "https://github.com/lemoncheesecake/lemoncheesecake",                                |                                                              |
    |       |     "location": null,                                                                            |                                                              |
    |       |     "email": "",                                                                                 |                                                              |
    |       |     "is_verified": false,                                                                        |                                                              |
    |       |     "has_organization_projects": true,                                                           |                                                              |
    |       |     "has_repository_projects": true,                                                             |                                                              |
    |       |     "public_repos": 1,                                                                           |                                                              |
    |       |     "public_gists": 0,                                                                           |                                                              |
    |       |     "followers": 0,                                                                              |                                                              |
    |       |     "following": 0,                                                                              |                                                              |
    |       |     "html_url": "https://github.com/lemoncheesecake",                                            |                                                              |
    |       |     "created_at": "2017-05-16T22:03:10Z",                                                        |                                                              |
    |       |     "updated_at": "2017-05-25T09:58:35Z",                                                        |                                                              |
    |       |     "type": "Organization"                                                                       |                                                              |
    |       | }                                                                                                |                                                              |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    |       | Check API response                                                                               |                                                              |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "type" to be equal to "Organization"                                                      | Got "Organization"                                           |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "id" to be an integer                                                                     | Got 28742541                                                 |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "description" to be not equal to null                                                     | Got "Python framework for functional/QA testing"             |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "login" to be present                                                                     | Got "lemoncheesecake"                                        |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "created_at" to match pattern "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"                    | Got "2017-05-16T22:03:10Z"                                   |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "has_organization_projects" to be a boolean that is equal to true                         | Got true                                                     |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "followers" to be greater than or equal to 0                                              | Got 0                                                        |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "following" to be greater than or equal to 0                                              | Got 0                                                        |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "repos_url" to end with "/repos"                                                          | Got "https://api.github.com/orgs/lemoncheesecake/repos"      |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "issues_url" to end with "/issues"                                                        | Got "https://api.github.com/orgs/lemoncheesecake/issues"     |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "events_url" to end with "/events"                                                        | Got "https://api.github.com/orgs/lemoncheesecake/events"     |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "hooks_url" to end with "/hooks"                                                          | Got "https://api.github.com/orgs/lemoncheesecake/hooks"      |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "members_url" to end with "/members{/member}"                                             | Got "https://api.github.com/orgs/lemoncheesecake/members{/me |
    |       |                                                                                                  | mber}"                                                       |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
    | CHECK | Expect "public_members_url" to end with "/public_members{/member}"                               | Got "https://api.github.com/orgs/lemoncheesecake/public_memb |
    |       |                                                                                                  | ers{/member}"                                                |
    +-------+--------------------------------------------------------------------------------------------------+--------------------------------------------------------------+

``lcc top-suites``
~~~~~~~~~~~~~~~~~~

Show suites ordered by their duration.

  .. code-block:: console

      $ lcc top-suites
      Suites, ordered by duration:
      +---------+----------+------+
      | Suite   | Duration | In % |
      +---------+----------+------+
      | suite_2 | 2.000s   | 66%  |
      | suite_1 | 1.000s   | 33%  |
      +---------+----------+------+

``lcc top-tests``
~~~~~~~~~~~~~~~~~

Shows tests ordered by their duration.

  .. code-block:: console

      $ lcc top-tests
      Tests, ordered by duration:
      +--------------+----------+------+
      | Suite        | Duration | In % |
      +--------------+----------+------+
      | suite_2.test | 2.000s   | 66%  |
      | suite_1.test | 1.000s   | 33%  |
      +--------------+----------+------+

``lcc top-steps``
~~~~~~~~~~~~~~~~~

Shows steps aggregated, ordered by their duration.

  .. code-block:: console

      $ lcc top-steps
      Steps, aggregated and ordered by duration:
      +--------------------+------+--------+--------+--------+--------+------+
      | Step               | Occ. | Min.   | Max    | Avg.   | Total  | In % |
      +--------------------+------+--------+--------+--------+--------+------+
      | Do something       | 2    | 1.000s | 2.000s | 1.500s | 3.000s | 75%  |
      | Do something else  | 1    | 1.000s | 1.000s | 1.000s | 1.000s | 25%  |
      +--------------------+------+--------+--------+--------+--------+------+

Also see the ``--help`` of these sub commands.

.. _cli_filters:

``lcc`` filtering arguments
---------------------------

``lcc`` sub commands ``run``, ``show``, ``stats``, ``report``, ``top-suites``, ``top-tests``, ``top-steps``
and ``diff`` take advantage of a powerful set of filtering arguments. Example for ``lcc run``:

.. code-block:: none

    Filtering:
      path                  Filter on test/suite path (wildcard character '*' can
                            be used)
      --desc DESC [DESC ...]
                            Filter on descriptions
      --tag TAG [TAG ...], -a TAG [TAG ...]
                            Filter on tags
      --property PROPERTY [PROPERTY ...], -m PROPERTY [PROPERTY ...]
                            Filter on properties
      --link LINK [LINK ...], -l LINK [LINK ...]
                            Filter on links (names and URLs)
      --passed              Filter on passed tests (implies/triggers --from-
                            report)
      --failed              Filter on failed tests (implies/triggers --from-
                            report)
      --skipped             Filter on skipped tests (implies/triggers --from-
                            report)
      --non-passed          Alias for --failed --skipped
      --disabled            Filter on disabled tests
      --enabled             Filter on enabled (non-disabled) tests
      --from-report FROM_REPORT
                            When enabled, the filtering is based on the given
                            report


Please note that the available filtering arguments may sightly differ depending on what command is used, please refer
to the corresponding command ``--help``.

The ``--from-report`` argument tells ``lcc`` to use tests from the specified report rather than from the project to build
the actual filter. The ``--passed``, ``--failed``, ``--skipped`` and ``-non-passed`` arguments can only be used in
conjunction with ``--from-report``.  If no ``--from-report`` is specified, then the latest report is used.

A typical application of this functionality is to re-run failed tests from a previous report:

.. code-block:: console

    $ lcc run --failed --from-report reports/report-2

Or simply:

.. code-block:: console

    $ lcc run --failed

if you want to re-run the failed tests from the latest run.
