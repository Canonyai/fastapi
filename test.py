from data_extraction import Scope
from github import Github
import pytest
from typing import Type
from utils import Content, Language
import os

########## SETUP ##########
@pytest.fixture
def github() -> Type[Github]:
    return Github(os.environ.get("GH_API_TOKEN"))


@pytest.fixture
def organization(github) -> Type[Scope]:
    return Scope(github.get_organization("SwengProject3Team9"))


@pytest.fixture
def user1(github) -> Type[Scope]:
    return Scope(github.get_user("algo-1"))


@pytest.fixture
def user2(github) -> Type[Scope]:
    return Scope(github.get_user("charliermarsh"))


########## TESTS ##########
def test_repos(organization: Type[Scope], user1: Type[Scope]):
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


def test_issues(organization: Type[Scope], user2: Type[Scope]):
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


def test_prs(organization: Type[Scope], user2: Type[Scope]):
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


def test_file_contents(organization: Type[Scope], user1: Type[Scope]):
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


########## HELPER FUNCTIONS ##########
def compare_list_to_set(api_result, expected_values, flag) -> bool:
    assert isinstance(flag, Content), TypeError("flag expects a Content Enum.")
    a_values = {
        val
        for val in map(
            lambda x: x.name
            if flag == Content.REPO
            else (x.path if flag == Content.FILE else x.title),
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
