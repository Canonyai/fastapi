# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc


from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from github import Github
import os
from data_extraction import Scope
from datetime import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()
app = FastAPI()
github = Github(os.environ.get("GH_API_TOKEN"))
org = Scope(github.get_organization("SwengProject3Team9"))
user1 = Scope(github.get_user("charliermarsh"))


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.get("/repos")
def repos(token: str):
    repos = get_repos(token)
    return repos

@app.get("/linesofcode")
def lines_of_code(token: str, start_date: str, end_date: str):
    return {"lines": 100}


@app.get("/codereview")
def code_review_time(token: str, start_date: str, end_date: str):
    return {"tmp": 0}


@app.get("/codereview/{repo}")
def code_review_time_for_repo(repo: str, token: str, start_date: str, end_date: str):
    args = [""] * 3 + [repo]
    times = get_pr_turnaround_time(*args)
    result = []
    for title, secs in times:
        result.append({"title": title, "time_in_seconds": secs})

    return result

@app.get("/typedstats/{repo}")
def typed_stats(repo: str, token: str):
    py, js = get_typed_stats(token, repo)
    result = {
        "python" : {
            "typed": py[0],
            "untyped": py[1]
        }, 
        "javascript" :  {
            "typed": js[0],
            "untyped": js[1]
        }
    }
    return result

def get_pr_turnaround_time(token: str, start_date: str, end_date: str, repo: str):
    user = user1
    after = datetime.today()  # parse_date(start_date)
    before = after - relativedelta(months=2)  # parse_date(end_date)
    prs = user.get_prs_by_time(repo, before, after)
    time_taken = [(pr.title, user.get_time_taken(pr).seconds) for pr in prs]
    print(*time_taken, sep="\n")
    return time_taken

def get_typed_stats(token, repo):
    user = org
    python_files = user.get_python_files(repo)
    javascript_files = user.get_javascript_files(repo)
    py = [(file.name, file.decoded_content) for file in python_files]
    js = [(file.name, file.decoded_content) for file in javascript_files]
    print("PYTHON")
    print(*py[:2], sep="\n")
    print("JS")
    print(*js[:2], sep="\n")
    return calculate_percent_typed_py(py), calculate_percent_typed_js(js)
    
def parse_date():
    pass

def calculate_percent_typed_py(files):
    count = 0
    for (filename, content) in files:
        lines = set([x.strip() for x in content.decode().split("\n")])
        if "import pydantic" in lines:
            count += 1
    return count,  len(files) - count

def calculate_percent_typed_js(files):
    count = 0
    for (filename, content) in files:
        if filename.endswith((".ts", ".tsx")):
            count += 1
    return count, len(files) - count

def get_repos(token: str):
    user = user1
    repos = user.get_repositories()
    repositories = [repo.name for repo in repos]
    return repositories
