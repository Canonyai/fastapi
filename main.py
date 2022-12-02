import pywebio
from pywebio.input import *
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pywebio.output import *
from pywebio.pin import *
from pywebio.output import put_html
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Liquid
from pyecharts.charts import PictorialBar
from pyecharts.globals import SymbolType
from github import Github
from data_extraction import Scope
from dotenv import load_dotenv
import os
from data_processing import *

load_dotenv()
github = Github(os.environ.get("GH_API_TOKEN"))


def repo_list():
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
        repo_list()
        info = input_group("repo", [input("enter repo name:", name="name")])
        repo_name = info["name"]
        draw(repo_name)


def draw(repo):
    with use_scope("scope1", clear=True):
        put_button("back", onclick=page2)
        put_row([put_scope("c1"), None, put_scope("c2")], size='40% 10px 100%')
        commit_count(repo)
        code_review(repo)
        cycle_time(repo)
        with use_scope("c1"):
            task_typed(repo)
        with use_scope("c2"):
            file_type(repo)


def task_typed(repo):
    global usr
    typed_percent = get_typed_percentage(usr, repo)
    c = (
        Liquid()
        .add(
            "Typed files percentage",
            [typed_percent/100],
            label_opts=opts.LabelOpts(
                font_size=50,
                position="inside",
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="Typed files percentage"))
    
    )

    c.width = "100%"
    put_html(c.render_notebook())


def file_type(repo):
    global usr
    python_num = get_py_num(usr, repo)
    java_num = get_java_num(usr, repo)
    js_num = get_js_num(usr, repo)
    c_num = get_C_num(usr, repo)
    cpp_num = get_CPP_num(usr, repo)
    location = ["C++", "C", "JS", "Java", "Python"]
    values = [cpp_num, c_num, js_num, java_num, python_num]

    c = (
        PictorialBar()
        .add_xaxis(location)
        .add_yaxis(
            "",
            values,
            label_opts=opts.LabelOpts(is_show=False),
            symbol_size=18,
            symbol_repeat="fixed",
            symbol_offset=[0, 0],
            is_symbol_clip=True,
            symbol=SymbolType.ROUND_RECT,
        )
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Language detail"),
            xaxis_opts=opts.AxisOpts(is_show=False),
            yaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(opacity=0)
                ),
            ),
        )

    )

    c.width = "100%"
    put_html(c.render_notebook())


def commit_count(repo):
    global usr
    x_axis, y_axis = get_commits(usr, repo)
    c = (
        Bar()
        .add_xaxis(x_axis)
        .add_yaxis(repo, y_axis)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(
                title="commit count",
                subtitle="x_axis: time range in month, y_axis: Commits",
            )
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
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
