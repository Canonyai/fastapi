from typing import Dict


class Scope:
    """
    This can be either a user, organisation or team?
    Currently there is no authorisation so only public repos and information are available
    """

    def __init__(self, scope):
        self.scope = scope
        self.repos = []
        self.issues = {}
        self.prs = {}

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
        if repo in self.issues:
            return self.issues[repo]
        else:
            repository = self.scope.get_repo(repo)
            issues = list(repository.get_issues(state="closed"))
            self.issues[repo] = issues

    def get_prs_from_repo(self, repo: str) -> list:
        """
        Returns a list of all closed pull requests from the specified repository.
        """
        if repo in self.prs:
            return self.prs[repo]
        else:
            repository = self.scope.get_repo(repo)
            prs = list(repository.get_pulls(state="closed"))
            self.prs[repo] = prs

    def get_pull_requests(self) -> list:
        """
        Returns a list of all closed pull requests from all repositories in the scope.
        """
        for repo in self.get_repositories():
            if repo.name not in self.prs:
                self.prs[repo.name] = list(repo.get_pulls(state="closed"))

        return self.prs
