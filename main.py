import pywebio
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
from pyecharts.charts import Gauge
from github import Github
from data_extraction import Scope
from dotenv import load_dotenv
import os
from data_processing import *

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
    table.set_global_opts(title_opts=ComponentTitleOpts(title="Repos"))
    put_html(table.render_notebook())


def page2():
    global name
    with use_scope("scope1", clear=True):
        put_markdown("## Repos of " + name)
        task1()
        task2()


def task2():
    info = input_group("repo", [input("enter repo name:", name="name")])
    repo_name = info["name"]
    draw(repo_name)


def draw(repo):
    with use_scope("scope1", clear=True):
        put_button("back", onclick=page2)
        task_typed(repo)
        code_review(repo)
        cycle_time(repo)


def task_typed(repo):
    global usr
    typed_percent = get_typed_percentage(usr, repo)
    c = (
        Gauge()
        .add(
            "Typed Percent",
            [("", typed_percent)],
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color=[(typed_percent / 100, "#77dd77 "), (1, "#ef3038")], width=30
                )
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Percentage of Typed Files in Repo"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    c.width = "100%"
    put_html(c.render_notebook())


def code_review(repo):
    global usr
    x_axis, y_axis = get_code_review_time(usr, repo)
    c = (
        Bar()
        .add_xaxis(x_axis)
        .add_yaxis(repo, y_axis)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(
                title="Code review",
                subtitle="x_axis: Pull request name, y_axis: Closing time in mins",
            ),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="average")
                ]
            ),
        )
    )
    
    c.width = "100%"
    put_html(c.render_notebook())


def cycle_time(repo):
    global usr
    x_axis, y_axis = get_cycle_time(usr, repo)
    c = (
        Bar()
        .add_xaxis(x_axis)
        .add_yaxis(repo, y_axis)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(
                title="Issue cycle time",
                subtitle="x_axis: Issue name, y_axis: Closing time in mins",
            ),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="average")
                ]
            ),
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


pywebio.start_server(main, port=5000, remote_access=True)
