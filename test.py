from data_extraction import Scope
from github import Github
import pytest
from typing import Type
from utils import Content
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
        organization.get_issues(), {"sweng-metrics-front-end": [], "fastapi": []}
    )
    assert partial_compare(
        user2.get_issues(),
        {
            "vscode-ruff": [
                "Upgrade to ruff 0.0.116",
                "Attempt to debug missing native binaries",
            ]
        },
    )
    assert compare_list_to_set(
        user2.get_issues_from_repo("ocaml-futures"), {"Fix copy"}, flag=Content.ISSUE
    )


def test_prs(organization: Type[Scope], user2: Type[Scope]):
    assert partial_compare(
        organization.get_pull_requests(), {"sweng-metrics-front-end": [], "fastapi": []}
    )
    assert partial_compare(
        user2.get_pull_requests(),
        {
            "vscode-ruff": [
                "Attempt to debug missing native binaries",
                "Add .idea and .ruff_cache to .vscodeignore",
            ]
        },
    )
    assert compare_list_to_set(
        user2.get_prs_from_repo("ocaml-futures"), {"Fix copy"}, flag=Content.PR
    )


########## HELPER FUNCTIONS ##########
def compare_list_to_set(a, b, flag) -> bool:
    assert isinstance(flag, Content), TypeError("flag expects a Content Enum.")
    a_values = {
        val for val in map(lambda x: x.name if flag == Content.REPO else x.title, a)
    }
    return a_values == b


def compare_list_to_set_issues(api_result, expected_values, flag) -> bool:
    assert isinstance(flag, Content), TypeError("flag expects a Content Enum.")
    assert flag == Content.ISSUE, ValueError("flag should be the Content.ISSUE Enum.")
    a_values = {
        val
        for val in map(
            lambda x: x.name if flag == Content.REPO else x.title, api_result
        )
    }
    lesser, greater = minmax(a_values, expected_values)
    for v in lesser:
        if v not in greater:
            return False
    return True


def partial_compare(api_result, expected) -> bool:
    """
    The repos with issues usually have a lot of repos and issues so for testing we just check a subset of issues in a subset of repos
    Alternatively, we could create a mock github account that is concise enough for testing the functions exactly.
    """
    lesser, greater = minmax(api_result, expected)
    assert len(lesser) > 0  # We are not testing anything if lesser is empty
    for key in lesser:
        if key not in greater:
            return False
        if expected == lesser:
            if not compare_list_to_set_issues(
                greater[key], set(lesser[key]), flag=Content.ISSUE
            ):
                return False
        else:
            if not compare_list_to_set_issues(
                lesser[key], set(greater[key]), flag=Content.ISSUE
            ):
                return False
    return True


def minmax(a, b):
    if len(a) <= len(b):
        return a, b
    return b, a
