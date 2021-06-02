from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from models import User, BuyOrder, SellOrder, Company, Stock, Cash, get_db
import requests, json

db = get_db()

wallet_bp = Blueprint("wallet",__name__,static_folder="static",template_folder="templates")

@wallet_bp.route('/', methods=["GET", "POST"])
@login_required
def index():
    id = current_user.id #id del usuario actual
    info = User.query.get(id) #usuario actual
    id_sell = None
    id_buy = None

    cash = Cash.query.filter(Cash.user_id == id, Cash.money == 0).one_or_none()
    if not cash: #Si no hay cash lo creamos
        cash = Cash(user_id=id, money=0)
    db.session.add(cash)

    if request.method == "POST": #Si se vende
        sell_amount = request.form.get("amountsell")
        current_price = request.form.get("actionsell").split("-")[3]
        amount = request.form.get("actionsell").split("-")[2]
        id_buy = request.form.get("actionsell").split("-")[1]
        id_company = request.form.get("actionsell").split("-")[0]

        company = Company.query.filter(Company.id == id_company).one_or_none()
        buyOrder = BuyOrder.query.filter(BuyOrder.id == id_buy).one_or_none()
        stock = Stock.query.filter(Stock.company_id == company.id, Stock.user_id == id).one_or_none()
        stock.amount -= int(sell_amount)

        if int(sell_amount) < int(amount):
            db.session.add(BuyOrder(company_id=company.id, user_id=id, created_date=buyOrder.created_date, amount=(int(amount)-int(sell_amount)), price=buyOrder.price)) #Añadimos a la bbdd la orden de compra
            buyOrder.amount = sell_amount

        buyOrder.is_sold = True

        db.session.add(SellOrder(company_id=company.id, user_id=id, buy_id=id_buy, amount=sell_amount, price=current_price)) #Añadimos a la bbdd la orden de venta
        db.session.add(stock)
        id_sell = SellOrder.query.order_by(SellOrder.id.desc()).first().id

    stocks = {}
    getcontext().prec = 15
    sum_money = Decimal(0)

    for stock in info.stocks: #Rellenamos stocks para enviarlo al html
        stocks[stock.company.symbol]= {}
        stocks[stock.company.symbol]['priceClose'] = getClosePrice(stock.company.symbol, stock.company.exchange)
        stocks[stock.company.symbol]['amount'] = stock.amount
        stocks[stock.company.symbol]['symbol'] = stock.company.symbol
        stocks[stock.company.symbol]['exchange'] = stock.company.exchange
        sum_money += Decimal(stock.amount*stocks[stock.company.symbol]['priceClose'])

    last_cash = Cash.query.filter(Cash.user_id == id).order_by(Cash.id.desc()).first()

    sum_money= round(sum_money, 2)

    if last_cash.money != sum_money:
        db.session.add(Cash(user_id=id, money=sum_money))

    if last_cash.date <= datetime.today()-timedelta(1): #Si hay mas de un día de distancia entre la ultima wallet save
        db.session.add(Cash(user_id=id, money=sum_money)) #Añadimos a la bbdd el dinero total actual del usuario

    db.session.commit()
    return render_template("wallet.html",module="wallet", info=info, stocks=stocks, buy_id = request.args.get('buy_id', id_buy), sell_id = id_sell)

def getClosePrice(symbol, exchange):
    params = {
        'access_key' : '3f22c61015f46196c6d24b254a80e4ef'
    }
    #Obtener los ultimos valores de bolsa de la empresa relacionada con el simbolo
    params.setdefault('symbols',symbol)#Añadimos el parametro symbols con el valor symbol a los parámetros que usaremos para hacer esta petición
    params.setdefault('exchange',exchange)#Añadimos el parametro exchange con el valor mic a los parámetros que usaremos para hacer esta petición
    res_value = requests.get("http://api.marketstack.com/v1/eod/latest",params)
    data_value = json.loads(res_value.content)

    return data_value['data'][0]['close']
