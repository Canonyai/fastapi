from pywebio.platform.flask import webio_view
from flask import Flask
from pywebio.input import *
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pywebio import config
from pywebio.output import *
from pywebio.pin import *
from pywebio.output import put_html
from pyecharts import options as opts
from pyecharts.charts import Bar
from github import Github
from data_extraction import Scope
from dotenv import load_dotenv
import os
from data_processing import get_repos
from data_processing import get_code_review_time

load_dotenv()
github = Github(os.environ.get("GH_API_TOKEN"))

def task1():
    global usr
    repo_list = get_repos(usr)
    tableSrc = []
    number = 1
    for each in repo_list:
        tableSrc.append([number, each])
        number += 1
    table = Table()
    headers = ["number", "name"]
    rows = tableSrc
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(title="Repos")
    )
    put_html(table.render_notebook())

def page2():
    global name
    with use_scope("scope1", clear=True):
        put_markdown('## Repos of '+name)
        task1()
        task2()


def task2():
    info = input_group("repo", [input('enter repo name:', name='name')])
    repo_name = info['name']
    draw(repo_name)


def draw(repo):
    with use_scope("scope1", clear=True):
        put_button("back", onclick=page2)
        task3(repo)
    

def task3(repo):
    global usr
    x_axis, y_axis = get_code_review_time(usr, repo)
    c = (
        Bar()
        .add_xaxis(
            x_axis
        )
        .add_yaxis(repo, y_axis)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="Code review", subtitle="x_axis: pull request name, y_axis: closing time in mins"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
        )
    
    )
    c.width = "100%"
    put_html(c.render_notebook())
    
    
    

def main():
    global name
    global usr
    name = input("Username")
    usr = Scope(github.get_user(name))
    page2()
        



app = Flask(__name__)

# `task_func` is PyWebIO task function
app.add_url_rule('/tool', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])  # need GET,POST and OPTIONS methods
                 
 # TODO METRIC TEAM:  Add a new URL for YOUR specific metric 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
