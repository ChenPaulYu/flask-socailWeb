from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Required
# from parsefb.parsefanpage import parsefb
import random
import os 
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app) 


@app.route('/', methods=['GET', 'POST'])
def index():
    state = None
    form = NameForm()
    if form.validate_on_submit():
        account = form.account.data
        code = form.code.data
        want = form.want.data
        order = form.order.data
        daylength = form.daylength.data

        form.account.data = ''
        form.code.data = ''
        form.want.data = ''
        form.order.data = ''
        form.daylength.data = ''
        
        # search(account, code, want, order, daylength)

        # try:
        # crawlfb(name, url, day)
        state = '成功新增'
        # except:
        #     state = '新增失敗'

    return render_template('index.html', form=form,state=state)


@app.route("/chart")
def chart():
    bars_count = 60
    data = {"days": [], "bugs": [], "costs": []}
    for i in range(1, bars_count + 1):
        data['days'].append(i)
        data['bugs'].append(random.randint(1, 100))
        data['costs'].append(random.uniform(1.00, 1000.00))
    hover = create_hover_tool()
    plot = create_bar_chart(data, "Emotion ", "days","bugs", hover)
    script, div = components(plot)
    return render_template("chart.html", bars_count=bars_count,the_div=div, the_script=script)



class NameForm(Form):
    account = StringField('帳戶', validators=[Required()])
    code = StringField('密碼', validators=[Required()])
    want = StringField('關鍵字', validators=[Required()])
    order = StringField('想取幾名', validators=[Required()])
    daylength = StringField('天數', validators=[Required()])
    submit = SubmitField('確認')


def create_hover_tool():
    # we'll code this function in a moment
    return None


def create_bar_chart(data, title, x_name, y_name, hover_tool=None,width=1200, height=300):
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=data[x_name])
    ydr = Range1d(start=0, end=max(data[y_name]) * 1.2)

    tools = []
    if hover_tool:
        tools = [hover_tool, ]

    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                  plot_height=height, h_symmetry=False, v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools,
                  responsive=True, outline_line_color="#666666")

    glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8,
                 fill_color="#e12127")
    plot.add_glyph(source, glyph)

    xaxis = LinearAxis()
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = "情緒指數"
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = "距離現在天數"
    plot.xaxis.major_label_orientation = 1
    return plot

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
