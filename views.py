from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from application import get_app
from models import User, Comment, Company, get_db, Stock, BuyOrder

import requests
import json

app = get_app()
db = get_db()

from forms import RegisterForm, LoginForm, ProfileForm, SearchForm

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    form = ProfileForm(email=current_user.email,
                       username=current_user.username,
                       profile=current_user.profile)
    return render_template("profile.html",module="profile", form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(or_(User.email==form.emailORusername.data,
                                         User.username==form.emailORusername.data)).first()
            if not user or not check_password_hash(user.password, form.password.data):
                flash("Wrong user or Password!")
            else:
                login_user(user)
                flash("Welcome back {}".format(current_user.username))
                return redirect(url_for('index'))
    return render_template('login.html',module="login", form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Ejercicio - juntar la dos partes!!! Coger del formulario y meter en base de datos!
            try:
                password_hashed=generate_password_hash(form.password.data,method="sha256")
                newuser = User(email=form.email.data,
                               username=form.username.data,
                               password=password_hashed)
                db.session.add(newuser)
                db.session.commit()
                flash("User created successfully!")
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash("Error creating user!")
    return render_template('signup.html',module="signup", form=form)

@app.route('/logout')
@login_required
def logout():
    flash("See you soon {}".format(current_user.username))
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=["GET", "POST"])
def index():
    #Obtener news
    res = requests.get("https://eodhistoricaldata.com/api/news?api_token=OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX&s=AAPL.US&offset=0&limit=5")
    data = json.loads(res.content)
    if request.method == "POST":
        if not current_user.is_authenticated:#Si el usuario no está autenticado y quiere comentar se redigirá a la pagina principal
            return redirect(url_for('index'))
        comment = Comment(content=request.form["contents"], commenter=current_user)
        db.session.add(comment)
        db.session.commit()
        last_comment = db.session.query(Comment).order_by(Comment.id.desc()).first()
        return render_template('index.html',module="home",comments=Comment.query.all(),data=data,id=last_comment.id)
    return render_template('index.html',module="home",comments=Comment.query.all(),data=data)

#Ruta market
@app.route('/market/', methods=["GET", "POST"])
def market():
    form = SearchForm(request.form)
    if request.method == "GET":
        #Obtener datos de las empresas
        search_limit = 7; #Máximo 50 para poder sacar sus valores
        params = {
          'access_key' : '329a00fb1ff242e35b6701acd1c98e20'
        }
        params.setdefault('limit',search_limit)
        res = requests.get("http://api.marketstack.com/v1/tickers",params)
        data = json.loads(res.content)
        #Obtener los valores de bolsa de las empresas obtenidas anteriormente
        array_symbols = [data['data'][i].get("symbol") for i in range(search_limit)] #Pasamos los simbolos de las empresas que tiene el diccionario a un array
        all_symbols = ",".join(array_symbols)#Pasamos el array a un string
        params.pop('limit')#Eliminamos el parámetro limit
        params.setdefault('symbols',all_symbols)#Añadimos el parametro symbols con el valor all_symbols a los parámetros que usaremos para hacer esta petición
        res_value = requests.get("http://api.marketstack.com/v1/eod/latest",params)
        data_value = json.loads(res_value.content)
        return render_template("market.html",module="market",data=data,data_value=data_value,form=form)
    return redirect(url_for('show_companies',symbol=request.form["company"]))

#Ruta companies database
@app.route('/companies/')
def countrydic():
    res = Company.query.all()
    list_companies = [r.as_dict() for r in res]
    return jsonify(list_companies)

#Ruta process search bar
@app.route('/process', methods=['POST'])
def process():
    company = request.form['company']
    if company:
        return jsonify({'company':company})
    return jsonify({'error': 'missing data..'})

    if __name__ == '__main__':
        app.run(debug=True)

#Ruta compañias por simbolo
@app.route('/companies/<symbol>')
def show_companies(symbol):
    #Obtener datos de las empresas
    params = {
      'access_key' : '6f62d772885243d6d10213665419268e'
    }
    params.setdefault('search',symbol)
    res = requests.get("http://api.marketstack.com/v1/tickers",params)
    data = json.loads(res.content)
    #Obtener los valores de bolsa de las empresas obtenidas anteriormente
    num_companies = data['pagination'].get("total")
    array_symbols = [data['data'][i].get("symbol") for i in range(num_companies)] #Pasamos los simbolos de las empresas que tiene el diccionario a un array
    all_symbols = ",".join(array_symbols)#Pasamos el array a un string
    params.pop('search')#Eliminamos el parámetro search
    params.setdefault('symbols',all_symbols)#Añadimos el parametro symbols con el valor all_symbols a los parámetros que usaremos para hacer esta petición
    res_value = requests.get("http://api.marketstack.com/v1/eod/latest",params)
    data_value = json.loads(res_value.content)
    return render_template("companies.html",module="market",data=data,data_value=data_value)

#Ruta compañia por simbolo
@app.route('/company/<mic>/<symbol>', methods=['GET','POST'])
def show_company(mic,symbol):
    params = {
        'access_key' : '6f62d772885243d6d10213665419268e'
        }
    if request.method=='GET':
        #Obtener datos de las empresas
        params.setdefault('limit',1)
        params.setdefault('search',symbol)
        res = requests.get("http://api.marketstack.com/v1/tickers",params)
        data = json.loads(res.content)
        #Obtener los ultimos valores de bolsa de la empresa relacionada con el simbolo
        params.pop('limit')#Eliminamos el parámetro limit
        params.pop('search')#Eliminamos el parámetro search
        params.setdefault('symbols',symbol)#Añadimos el parametro symbols con el valor symbol a los parámetros que usaremos para hacer esta petición
        params.setdefault('exchange',mic)#Añadimos el parametro exchange con el valor mic a los parámetros que usaremos para hacer esta petición
        res_value = requests.get("http://api.marketstack.com/v1/eod/latest",params)
        data_value = json.loads(res_value.content)
        if "error" in data_value:
            return render_template("404.html")
        #Obtener los valores (fecha) de bolsa de la empresa relacionada con el simbolo
        params.setdefault('date_from',(datetime.today()-timedelta(30)).strftime("%Y-%m-%d"))#Añadimos el parametro date_from con el valor de la primera fecha a los parámetros que usaremos para hacer esta petición
        params.setdefault('date_to',(datetime.today()-timedelta(1)).strftime("%Y-%m-%d"))#Añadimos el parametro date_to con el valor de la ultima fecha a los parámetros que usaremos para hacer esta petición
        res_values = requests.get("http://api.marketstack.com/v1/eod",params)
        data_value2 = json.loads(res_values.content)
        #Comprobar si existe en la bbdd y si no guardarlo
        company = Company.query.filter(Company.symbol == symbol, Company.exchange == mic).one_or_none()
        if not company:
            newcompany = Company(symbol=symbol,name=data['data'][0]['name'],exchange=mic)
            db.session.add(newcompany)
            db.session.commit()
        return render_template("company.html",module="market",data=data,data_value=data_value,data_value2=data_value2,symbol=symbol)
    else:
        #Obtener los ultimos valores de bolsa de la empresa relacionada con el simbolo
        params.setdefault('symbols',symbol)#Añadimos el parametro symbols con el valor symbol a los parámetros que usaremos para hacer esta petición
        params.setdefault('exchange',mic)#Añadimos el parametro exchange con el valor mic a los parámetros que usaremos para hacer esta petición
        res_value = requests.get("http://api.marketstack.com/v1/eod/latest",params)
        data_value = json.loads(res_value.content)
        data = request.form
        id = current_user.id
        company = Company.query.filter(Company.symbol == symbol, Company.exchange == mic).one()
        stock = Stock.query.filter(Stock.company_id == company.id, Stock.user_id == id).one_or_none()
        if not stock: #Si no hay stock lo creamos
            stock = Stock(company_id=company.id, user_id=id, amount=0)

        stock.amount += int(data.get('num'))

        db.session.add(BuyOrder(company_id=company.id, user_id=id, amount=data.get('num'), price=data_value['data'][0]['close'])) #Añadimos a la bbdd la orden de compra
        db.session.add(stock)
        db.session.commit()
        return redirect(url_for('wallet.index',buy_id=BuyOrder.query.order_by(BuyOrder.id.desc()).first().id))


@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template("500.html"), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def access_denied(e):
    return render_template("403.html"), 403
