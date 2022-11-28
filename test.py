from __future__ import annotations
from data_extraction import Scope
from github import Github
import pytest
from utils import Content, Language
import os
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta

########## SETUP ##########
load_dotenv()


@pytest.fixture
def github() -> Github:
    return Github(os.environ.get("GH_API_TOKEN"))


@pytest.fixture
def organization(github) -> Scope:
    return Scope(github.get_organization("SwengProject3Team9"))


@pytest.fixture
def user1(github) -> Scope:
    return Scope(github.get_user("algo-1"))


@pytest.fixture
def user2(github) -> Scope:
    return Scope(github.get_user("charliermarsh"))


@pytest.fixture
def nov_16_2022() -> datetime:
    return datetime(year=2022, month=11, day=16)


@pytest.fixture
def two_months_to_nov_16_2022(nov_16_2022) -> datetime:
    return nov_16_2022 - relativedelta(months=2)


########## TESTS ##########
def test_repos(organization: Scope, user1: Scope):
    assert compare_list_to_set(
        organization.get_repositories(),
        {"sweng-metrics-front-end", "fastapi"},
        flag=Content.REPO,
    )
    assert compare_list_to_set(
        user1.get_repositories(),
        {
            "AdventOfCode2020",
            "aqua-challenge",
            "drumwebsite",
            "google-hashcode",
            "ciphers",
            "seasonalbot",
            "simple-git",
            "learn-rust",
            "VancouverBusManagementSystem",
            "todolist",
            "tictactoe",
            "textgenerator",
        },
        flag=Content.REPO,
    )


def test_issues(
    organization: Scope,
    user2: Scope,
    nov_16_2022: datetime,
    two_months_to_nov_16_2022: datetime,
):
    assert partial_compare(
        organization.get_issues(),
        {"fastapi": ["Add test file and data extraction ", "Add .gitignore"]},
        Content.ISSUE,
    )
    assert partial_compare(
        user2.get_issues(),
        {
            "vscode-ruff": [
                "Upgrade to ruff 0.0.116",
                "Attempt to debug missing native binaries",
            ]
        },
        Content.ISSUE,
    )
    assert compare_list_to_set(
        user2.get_issues_from_repo("ocaml-futures"), {"Fix copy"}, flag=Content.ISSUE
    )
    assert compare_list_to_set(
        user2.get_issues_by_time(
            repo="vscode-ruff", before=two_months_to_nov_16_2022, after=nov_16_2022
        ),
        {"Error when trying to use ruff from selected virtual environment"},
        flag=Content.ISSUE,
    )


def test_prs(
    organization: Scope,
    user2: Scope,
    nov_16_2022: datetime,
    two_months_to_nov_16_2022: datetime,
):
    assert partial_compare(
        organization.get_pull_requests(),
        {"fastapi": ["Add test file and data extraction ", "Add .gitignore"]},
        Content.PR,
    )
    assert partial_compare(
        user2.get_pull_requests(),
        {
            "vscode-ruff": [
                "Attempt to debug missing native binaries",
                "Add .idea and .ruff_cache to .vscodeignore",
            ]
        },
        Content.PR,
    )
    assert compare_list_to_set(
        user2.get_prs_from_repo("ocaml-futures"), {"Fix copy"}, flag=Content.PR
    )
    assert compare_list_to_set(
        user2.get_prs_by_time(
            repo="vscode-ruff", before=two_months_to_nov_16_2022, after=nov_16_2022
        ),
        {"Fix incorrect repository URL"},
        flag=Content.PR,
    )


def test_file_contents(organization: Scope, user1: Scope):
    assert compare_list_to_set(
        organization.get_files_by_language("fastapi", Language.PY),
        {"data_extraction.py", "test.py"},
        flag=Content.FILE,
    )
    assert compare_list_to_set(
        organization.get_files_by_language("sweng-metrics-front-end", Language.JS),
        {"src/containers/Topbar/InsideHeader/index.js", "config-overrides.js"},
        flag=Content.FILE,
    )

    assert compare_list_to_set(
        user1.get_files_by_language("simple-git", Language.PY),
        {"tests/test_ezgit.py"},
        flag=Content.FILE,
    )
    assert compare_list_to_set(
        user1.get_files_by_language("drumwebsite", Language.JS),
        {"index.js"},
        flag=Content.FILE,
    )


def test_commits(
    organization: Scope,
    user1: Scope,
    user2: Scope,
    nov_16_2022: datetime,
    two_months_to_nov_16_2022: datetime,
):
    assert compare_list_to_set(
        organization.get_all_commits_in_repo("fastapi"),
        {
            "4f3f0360539b63cd9146a4b1baa8699e61068566",
            "623013fe7dd7b1387633dbf708e3f5f5228f5054",
        },
        Content.COMMIT,
    )
    assert compare_list_to_set(
        user1.get_all_commits_in_repo("learn-rust"),
        {
            "c0d81df78bbfed46ebd8f762587d03492c7f3978",
            "a7046cb82b1b4d9bb1d656786dbe5b2ef238fcbf",
        },
        Content.COMMIT,
    )

    commits = organization.get_commits_by_time(
        "fastapi", two_months_to_nov_16_2022, nov_16_2022
    )
    assert len(commits) == 25
    assert compare_list_to_set(
        commits,
        {
            "4f3f0360539b63cd9146a4b1baa8699e61068566",
            "623013fe7dd7b1387633dbf708e3f5f5228f5054",
        },
        Content.COMMIT,
    )

    commits = user2.get_commits_by_time(
        "vscode-ruff", two_months_to_nov_16_2022, nov_16_2022
    )
    assert len(commits) == 29
    assert compare_list_to_set(
        commits,
        {
            "82134820d794e1f87d818fa5dc75fb9d41ad5436",
            "25a1684cc60d193ffbaeb7e88d3b2d63f939fa91",
        },
        Content.COMMIT,
    )


########## HELPER FUNCTIONS ##########
def compare_list_to_set(api_result, expected_values, flag) -> bool:
    assert isinstance(flag, Content), TypeError("flag expects a Content Enum.")
    a_values = {
        val
        for val in map(
            lambda x: x.name
            if flag == Content.REPO
            else (
                x.path
                if flag == Content.FILE
                else (x.sha if flag == Content.COMMIT else x.title)
            ),
            api_result,
        )
    }
    lesser, greater = minmax(a_values, expected_values)
    for v in lesser:
        if v not in greater:
            return False
    return True


def partial_compare(api_result, expected, flag) -> bool:
    """
    The repos with issues usually have a lot of repos, issues and prs, so for testing we just check a subset of issues in a subset of repos
    Alternatively, we could create a mock github account that is concise enough for testing the functions exactly.
    """
    lesser, greater = minmax(api_result, expected)
    assert len(lesser) > 0  # We are not testing anything if lesser is empty
    for key in lesser:
        if key not in greater:
            return False
        if expected == lesser:
            if not compare_list_to_set(greater[key], set(lesser[key]), flag):
                return False
        else:
            if not compare_list_to_set(lesser[key], set(greater[key]), flag):
                return False
    return True


def minmax(a, b):
    if len(a) <= len(b):
        return a, b
    return b, a
