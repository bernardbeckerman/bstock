from flask import Flask,render_template,request,redirect
import requests
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from bokeh.plotting import figure, output_file, save

app = Flask(__name__)

app.vars={}

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('tkrrequest.html')
    else:
        #request was a POST
        app.vars['ticker'] = request.form['ticker']
        return redirect('/main')

@app.route('/main')
def main2():
    return redirect('/next')

@app.route('/next',methods=['GET'])
def next():
    ticker = app.vars['ticker']
    requrl_base = "https://www.quandl.com/api/v3/datasets/WIKI/"
    start_date = (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d')
    end_date   = datetime.datetime.today().strftime('%Y-%m-%d')
    requrl = requrl_base + ticker + '.json?start_date=' + start_date + '&end_date=' + end_date + '&api_key=y_bZCGtW3wX35wfxxNzC'
    r = requests.get(requrl)
    
    # compile json data into dataframe
    qjson      = pd.read_json(r.text)
    if (qjson.keys()[0]=='quandl_error'):
        return render_template('error.html',tkr=ticker)
    data       = qjson['dataset']['data']
    colnames   = qjson['dataset']['column_names']
    df         = pd.DataFrame(data,columns=colnames)
    df['Date'] = pd.to_datetime(df['Date'])

    output_file("templates/monthstock.html")
    p = figure(width=800, height=494, x_axis_type="datetime", title=ticker+" Stock Price")
    p.line(df['Date'], df['Close'], color = 'navy', line_width=2)
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price"
    save(p)
    return render_template('/monthstock.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
