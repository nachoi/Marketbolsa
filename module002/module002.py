from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
import requests
import json

module002 = Blueprint("module002",__name__,static_folder="static",template_folder="templates")

@module002.route('/', methods=["GET", "POST"])
def module002_index():
    legends = [request.form.get("company"),request.form.get("vs")]
    labels = [(datetime.today()-timedelta(7)).strftime("%y/%m/%d"),(datetime.today()-timedelta(6)).strftime("%y/%m/%d"),(datetime.today()-timedelta(5)).strftime("%y/%m/%d"),(datetime.today()-timedelta(4)).strftime("%y/%m/%d"),(datetime.today()-timedelta(3)).strftime("%y/%m/%d"),(datetime.today()-timedelta(2)).strftime("%y/%m/%d"),(datetime.today()-timedelta(1)).strftime("%y/%m/%d")]
    params = {
      'access_key' : '8d7275eb2c1718096946265b1b7c15e3'
    }
    values = [0, 0, 0, 0, 0, 0, 0]
    if request.method == "GET":
        return render_template("module002_index.html",module="module002",values=values,labels=labels,legends=legends)

    #Valores primera empresa
    symbol = legends[0].split(" ",1)[0]
    params.setdefault('symbols',symbol)#Añadimos el parametro symbols con el valor symbol a los parámetros que usaremos para hacer esta petición
    params.setdefault('date_from',(datetime.today()-timedelta(20)).strftime("%Y-%m-%d"))#Añadimos el parametro date_from con el valor de la primera fecha a los parámetros que usaremos para hacer esta petición
    params.setdefault('date_to',(datetime.today()-timedelta(1)).strftime("%Y-%m-%d"))#Añadimos el parametro date_to con el valor de la ultima fecha a los parámetros que usaremos para hacer esta petición
    res = requests.get("http://api.marketstack.com/v1/eod",params)
    data1 = json.loads(res.content)
    #Valores segunda empresa
    symbol = legends[1].split(" ",1)[0]
    params.pop('symbols')#Eliminamos el parámetro symbols
    params.setdefault('symbols',symbol)#Añadimos el parametro symbols con el valor symbol a los parámetros que usaremos para hacer esta petición
    ress = requests.get("http://api.marketstack.com/v1/eod",params)
    data2 = json.loads(ress.content)
    return render_template("module002_index.html",module="module002",values=values,labels=labels,legends=legends,data1=data1,data2=data2)

@module002.route('/test')
def module002_text():
    return 'OK'