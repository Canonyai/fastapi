from typing import Dict, Type
from collections import deque
from datetime import datetime

from utils import Language


class Scope:
    """
    This can be either a user, organisation or team?
    Currently there is no authorisation so only public repos and information are available
    All prs and issues returned are closed as we don't care about open prs for our metrics.
    """

    JS_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")
    PY_EXTENSIONS = (".py",)
    TYPED_EXTENSIONS = (
        ".java",
        ".ts",
        ".tsx",
        ".c",
        ".cs",
        ".cpp",
        ".c++",
        ".cc",
        ".cp",
        ".cxx",
        ".h",
        ".h++",
        ".hh",
        ".hpp",
        ".hxx",
        ".inc",
        ".inl",
        ".ipp",
        ".tcc",
        ".tpp",
    )
    UNTYPED_EXTENSIONS = (".js", ".jsx", ".py", ".rb", ".ruby", ".perl")

    def __init__(self, scope):
        self.scope = scope
        self.repos = []
        self.issues = {}
        self.prs = {}
        self.python_files = {}
        self.javascript_files = {}
        self.typed_files = {}
        self.untyped_files = {}

    def get_repositories(self) -> list:
        """
        returns a list of all public repositories including forked repos
        """
        if not self.repos:
            self.repos = list(self.scope.get_repos())
        return self.repos

    def get_issues(self) -> Dict[str, list]:
        """
        Returns a list of all the closed issues from all the repositories in the scope
        """
        for repo in self.get_repositories():
            if repo.name not in self.issues:
                self.issues[repo.name] = list(repo.get_issues(state="closed"))

        return self.issues

    def get_issues_from_repo(self, repo: str) -> list:
        """
        Returns a list of all the closed issues from the specified repository.
        """
        if repo not in self.issues:
            repository = self.scope.get_repo(repo)
            issues = list(repository.get_issues(state="closed"))
            self.issues[repo] = issues

        return self.issues[repo]

    def get_prs_from_repo(self, repo: str) -> list:
        """
        Returns a list of all closed pull requests from the specified repository.
        """
        if repo not in self.prs:
            repository = self.scope.get_repo(repo)
            prs = list(repository.get_pulls(state="closed"))
            self.prs[repo] = prs

        return self.prs[repo]

    def get_pull_requests(self) -> list:
        """
        Returns a list of all closed pull requests from all repositories in the scope.
        """
        for repo in self.get_repositories():
            if repo.name not in self.prs:
                self.prs[repo.name] = list(repo.get_pulls(state="closed"))

        return self.prs

    def get_issues_by_time(
        self, repo: str, before: Type[datetime], after: Type[datetime]
    ) -> list:
        """
        Returns a list of issues in the specified timeframe
        """
        issues = self.get_issues_from_repo(repo)
        return [val for val in issues if self.get_values_in_range(val, before, after)]

    def get_prs_by_time(
        self, repo: str, before: Type[datetime], after: Type[datetime]
    ) -> list:
        """
        Returns a list of prs in the specified timeframe
        """
        prs = self.get_prs_from_repo(repo)
        return [val for val in prs if self.get_values_in_range(val, before, after)]

    def get_files_by_language(self, repo: str, language) -> list:
        """
        Returns a list of files in a repo that match the specified language
        """
        if language == Language.PY:
            if repo in self.python_files:
                return self.python_files[repo]
            else:
                self.python_files = self.populate_cache_with_file_content(
                    repo, self.PY_EXTENSIONS, self.python_files
                )
                return self.python_files[repo]
        elif language == Language.JS:
            if repo in self.javascript_files:
                return self.javascript_files[repo]
            else:
                self.javascript_files = self.populate_cache_with_file_content(
                    repo, self.JS_EXTENSIONS, self.javascript_files
                )
                return self.javascript_files[repo]
        elif language == Language.TYPED:
            if repo in self.typed_files:
                return self.typed_files[repo]
            else:
                self.typed_files = self.populate_cache_with_file_content(
                    repo, self.TYPED_EXTENSIONS, self.typed_files
                )
                return self.typed_files[repo]
        elif language == Language.UNTYPED:
            if repo in self.untyped_files:
                return self.untyped_files[repo]
            else:
                self.untyped_files = self.populate_cache_with_file_content(
                    repo, self.UNTYPED_EXTENSIONS, self.untyped_files
                )
                return self.untyped_files[repo]
        else:
            raise TypeError(
                "A Language Enum should be passed in for the language parameter."
            )

    def get_python_files(self, repo) -> list:
        """
        Returns a list of python files in the repo
        """
        return self.get_files_by_language(repo, Language.PY)

    def get_javascript_files(self, repo) -> list:
        """
        Reeturns a list of javascript files in the repo
        """
        return self.get_files_by_language(repo, Language.JS)

    def get_typed_files(self, repo) -> list:
        """
        Reeturns a list of typed files in the repo
        """
        return self.get_files_by_language(repo, Language.TYPED)

    def get_untyped_files(self, repo) -> list:
        """
        Reeturns a list of untyped files in the repo
        """
        return self.get_files_by_language(repo, Language.UNTYPED)

    def get_commits(self, repo):
        pass

    def populate_cache_with_file_content(self, repo, file_extensions, cache):
        cache[repo] = []
        repository = self.scope.get_repo(repo)
        contents = deque(repository.get_contents(""))
        while contents:
            file_content = contents.popleft()
            if file_content.type == "dir":
                contents.extend(repository.get_contents(file_content.path))
            else:
                if file_content.path.endswith(file_extensions):
                    cache[repo].append(file_content)
        return cache

    def get_values_in_range(self, object, before, after):
        return object.created_at >= before and object.closed_at <= after

    def get_time_taken(self, object) -> datetime:
        """
        Takes in a closed issue or pr and returns how long it takes to close the repo
        """
        return object.closed_at - object.created_at
