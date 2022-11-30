from datetime import datetime
from dateutil.relativedelta import relativedelta
from data_extraction import Scope
from github import Github
from dotenv import load_dotenv
import os


# time taken for code review time metric
# example of what is required is provided
def get_code_review_time(user: Scope, repo: str):
    x_axis = []
    y_axis = []
    after = datetime.today()  # parse_date(start_date)
    before = after - relativedelta(months=2)  # parse_date(end_date)
    prs = user.get_prs_by_time(repo, before, after)
    # time_taken = [(pr.title, user.get_time_taken(pr).minutes) for pr in prs]

    for pr in prs:
        x_axis.append(pr.title)
        y_axis.append(round(user.get_time_taken(pr).seconds / 60, 3))

    # print(*time_taken, sep="\n")
    return x_axis, y_axis
    
    
# time taken for cycle time (issues start to completion) metric    
def get_cycle_time(user: Scope, repo: str):
    x_axis = []
    y_axis = []
    after = datetime.today()  # parse_date(start_date)
    before = after - relativedelta(months=2)  # parse_date(end_date)
    prs = user.get_issues_by_time(repo, before, after)
    # time_taken = [(issue.title, user.get_time_taken(issue).minutes) for issue in issues]

    for issue in issue:
        x_axis.append(issue.title)
        y_axis.append(round(user.get_time_taken(issue).seconds / 60, 3))

    # print(*time_taken, sep="\n")
    return x_axis, y_axis


# get repositories
def get_repos(user: Scope):
    repos = user.get_repositories()
    repositories = [repo.name for repo in repos]
    return repositories


# get percentage of typed files in repo
def get_typed_percentage(user: Scope, repo: str):
    # get all typed and untyped files in repo
    files_typed = user.get_typed_files(repo)
    files_untyped = user.get_untyped_files(repo)
    # calculate percentage
    percentage = (len(files_typed) / (len(files_typed) + len(files_untyped))) * 100
    return round(percentage, 2)


# get pull request turnaround time
def get_pr_turnaround_time(user: Scope, start_date: str, end_date: str, repo: str):
    pass


# get percentage of python in files
# N/B could be implemented to aid func in line 21 (your choice)
def calculate_percent_typed_py(files: str):
    pass


# get percentage of js in files
# #N/B could be implemented to aid func in line 21 (your choice)
def calculate_percent_typed_js(files: str):
    pass


# get number of lines of code in repo
def get_lines_count(user: Scope, repo: str):
    pass


# get number of commits to project
def get_commits(user: Scope, repo: str):
    pass


# get code coverage stats from test files
def get_code_coverage(user: Scope, repo: str, file: str):
    pass


if __name__ == "__main__":
    load_dotenv()
    github = Github(os.environ.get("GH_API_TOKEN"))
    usr = Scope(github.get_user("charliermarsh"))
    print(get_code_review_time(usr, "ruff"))
