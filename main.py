from pywebio.platform.flask import webio_view
from flask import Flask
from pywebio.input import *
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pywebio import config
from pywebio.output import *
from github import Github
from data_extraction import Scope

 # TODO METRIC TEAM:  import your file


def task1(n1, n2):
    github = Github(n2)
    usr1 = Scope(github.get_user(n1))
    set1 = usr1.get_repositories()
    tableSrc = []
    number = 1
    for each in set1:
        tableSrc.append([number, each])
        number += 1
    table = Table()
    headers = ["number", "name"]
    rows = tableSrc
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(title="Table-基本示例", subtitle="我是副标题支持换行哦")
    )
    put_html(table.render_notebook())


@config(theme='dark')
def main():
    info = input_group("login git", [
        input('User name:', name='usr'),
        input('Token:', name='pass')
    ])
    name1 = info['usr']
    name2 = info['pass']

    put_grid([
        [span(put_markdown('## Section A'), col=2)],
        [put_markdown('### Chart 1'), put_markdown('### Chart 2')],
        [put_scope('1-1'), put_scope('1-2')]
    ], cell_widths='60% 60%')
    with use_scope('1-1'):
        task1(name1, name2)



app = Flask(__name__)

# `task_func` is PyWebIO task function
app.add_url_rule('/tool', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])  # need GET,POST and OPTIONS methods
                 
 # TODO METRIC TEAM:  Add a new URL for YOUR specific metric 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
