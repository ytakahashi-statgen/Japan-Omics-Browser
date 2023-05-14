from google.cloud import storage
from flask import Flask, render_template, request, redirect
from flask import url_for
from flask_bootstrap import Bootstrap
import pandas as pd
from flask_paginate import Pagination, get_page_parameter
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool,)
from bokeh.embed import file_html
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.resources import CDN
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import RangeTool
from bokeh.models import RangeSlider
from io import BytesIO
import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, text

#初期設定
app = Flask(__name__)
bootstrap=Bootstrap(app)

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """ Initializes a Unix socket connection pool for a Cloud SQL instance of MySQL. """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_socket": unix_socket_path},
        ),
        # ...
    )
    return pool

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        # フォームの入力値を取得
        input_value = request.form['input_value']  #index.htmlのform(name="input_value")から値を取ってくる。
        # chrが含まれる場合はvariant.htmlを表示
        # input_value.count(":") == 3 or input_value.count("_") == 3 or input_value.startswith('rs'):
        if input_value.startswith('chr') or input_value.startswith('rs'):
            return redirect(url_for('variant',input_value=input_value))
        # それ以外はindex.htmlを表示
        else:
            return redirect(url_for('gene',input_value=input_value))
    # GETの場合は index.html を表示する
    return render_template("index.html")

# @app.route('/overview')
# def overview_page():
#     #現在のページ番号を取得
#     page = request.args.get(get_page_parameter(), type=int, default=1)

#     # ページに表示する項目をスライス
#     per_page = 10 #1ページに表示する行数
#     start = (page - 1) * per_page
#     end = start + per_page
#     items = df_tf[start:end]
#     total = len(df_tf)  # 総行数
#     pagination = Pagination(page=page, total=total, per_page=per_page)

#     return render_template('overview.html',data=items,pagination=pagination)
    
@app.route('/variant')
def variant():
    input_value = request.args.get('input_value') # URLから'input_value'の引数を取得する

    # SQLクエリを選択
    if input_value.startswith('chr'):
        query = "SELECT * FROM mytable WHERE variant_id_hg38 = :input_value"
    elif input_value.startswith('rs'):
        query = "SELECT * FROM mytable WHERE rsid = :input_value"
    else:
        return 'Invalid input value.'

    # Execute a SQL query using the engine
    engine = connect_unix_socket()
    with engine.connect() as conn:
        params = {'input_value': input_value}
        df = pd.read_sql(text(query), conn, params=params)
        df.sort_values('tss_distance', inplace=True,ascending=True,key=abs)

    if len(df) == 0:
        error_message = f"No data found for input value: {input_value}"
        return render_template('index.html', error_message=error_message)
    else:
        table_data = df.head(10)
        return render_template('variant.html', table_data=table_data,title_name=input_value)   


@app.route('/gene', methods=['GET'])
def gene():
    input_value = request.args.get('input_value') # URLから'input_value'の引数を取得する

    # SQLクエリを選択
    if input_value.startswith('ENSG'):
        input_value = input_value.split('.')[0]  # ドットより前の文字列を抽出
        query = "SELECT * FROM mytable WHERE gene_id = :input_value"
    else:
        query = "SELECT * FROM mytable WHERE gene_name = :input_value"

    # Execute a SQL query using the engine
    engine = connect_unix_socket()
    with engine.connect() as conn:
        params = {'input_value': input_value}
        df = pd.read_sql(text(query), conn, params=params)

    if len(df) == 0:
        error_message = f"No data found for input value: {input_value}"
        return render_template('index.html', error_message=error_message)
    
    else:
        # create data source
        source = ColumnDataSource(df)
        # HoverToolの設定
        hover = HoverTool(tooltips=[("hg38", "@variant_id_hg38"),("pQTL PIP", "@pQTL_pip_fm"),("eQTL PIP", "@eQTL_pip_fm"),("EMS", "@EMSv2_Whole_Blood")])

        # create two plots
        plot1 = figure(width=1080, height=250, title="pQTL PIP",x_axis_label=f'Distance to TSS of {input_value}', y_axis_label='pQTL PIP',tools=[hover,BoxZoomTool(), ResetTool()],x_range=([-1e6, 1e6]),y_range = [0, 1])
        plot1.circle('tss_distance', 'pQTL_pip_fm',color='orange', size=14, source=source)
        plot1.yaxis.axis_label_text_font_size = "18pt"
        plot1.title.text_font_size = "14pt"

        plot2 = figure(width=1080, height=250, title="eQTL PIP",x_axis_label=f'Distance to TSS of {input_value}', y_axis_label='eQTL PIP',tools=[hover,BoxZoomTool(), ResetTool()], x_range=plot1.x_range,y_range = [0, 1])
        plot2.circle('tss_distance', 'eQTL_pip_fm',color='royalblue', size=14, source=source)
        plot2.yaxis.axis_label_text_font_size = "18pt"
        plot2.title.text_font_size = "14pt"

        plot3 = figure(width=1080, height=250, title="EMS",x_axis_label=f'Distance to TSS of {input_value}', y_axis_label='EMS',tools=[hover,BoxZoomTool(), ResetTool()], x_range=plot1.x_range)
        plot3.circle('tss_distance', 'EMSv2_Whole_Blood',color='green', size=14, source=source)
        plot3.yaxis.axis_label_text_font_size = "18pt"
        plot3.title.text_font_size = "14pt"

        # RangeToolのfigure
        plot4 = figure(width=1080, height=150, title="EMS",x_axis_label=f'Distance to TSS of {input_value}', y_axis_label='EMS',x_range=plot1.x_range, toolbar_location=None)
        plot4.circle('tss_distance', 'EMSv2_Whole_Blood',color='green', size=14, source=source)
        range_tool = RangeTool(x_range=plot1.x_range)  # (1) で作成されたRange1dオブジェクト
        plot4.add_tools(range_tool)
        
        # RangeSliderの作成
        slider = RangeSlider(start=-1e6, end=1e6, value=(-1e6, 1e6), step=1, title="X Range")

        # Box selection
        box = BoxAnnotation(fill_alpha=0.5, line_alpha=0.5, level='underlay', left=-1e6, right=1e6)
        # コールバックの作成
        def callback(attr, old, new):
            box.left = new[0]
            box.right = new[1]
            plot1.x_range.start = new[0]
            plot1.x_range.end = new[1]

        # RangeSliderにコールバックを追加
        slider.on_change('value', callback)

        # create layout and add plots
        layout = column(plot1, plot2,plot3,plot4,slider, sizing_mode='stretch_width')
        html = file_html(layout, CDN, "my plot")  
        df.sort_values('EMSv2_Whole_Blood', inplace=True,ascending=False)
        df.reset_index(inplace=True, drop=True)
        table_data = df.head(10) #Table表示として、とりあえずTop10 EMS

        return render_template('gene.html', html=html,table_data=table_data,title_name=input_value)

# @app.route('/download')
# def download_page():
#     df = df_tf[df_tf["ensg_id"]=="ENSG00000198879"]
#     # create data source
#     source = ColumnDataSource(df)
#     tc = [TableColumn(field = c,title=c) for c in df.columns]
#     data_table = DataTable(source = source, columns = tc,width=800, height=500, fit_columns=True, sizing_mode='stretch_width')
#     html = file_html(data_table, CDN, "my plot")  

#     return render_template('download.html',html=html)

@app.route('/about')
def about_page():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)

