import unicodedata

from werkzeug.utils import redirect

from data import db_session
from flask import Flask, render_template
from forms.search import SearchForm
from forms.login import LoginForm, RegisterForm
from forms.amount import Amount
from data.users import User
from data.items import Item
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import json
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'onlineshop_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/', methods=['GET', 'POST'])
def main_page():
    form = SearchForm()
    if form.validate_on_submit():
        res = form.search.data
        return redirect('/search/{}/1'.format(res))
    return render_template("index.html", title="Главная", form=form)


@app.route('/search/<title>/<page_number>', methods=['GET', 'POST'])
def search(title, page_number):
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.title.like('%{}%'.format(title))).all()
    limit = math.ceil(len(items) / 12)
    items_len = len(items)
    return render_template("items.html", items=items, title=title, category='Найдено по запросу: ' + title,
                           number=int(page_number),
                           length=items_len, limit=limit, link='search/' + title)


@app.route('/gadget', methods=['GET', 'POST'])
def gadgets():
    with open("categories.json", "rt", encoding="utf8") as f:
        cat_list = json.loads(f.read())
    return render_template("categories_page.html", title="Гаджеты", category="Гаджеты", cat=cat_list['gadgets'])


@app.route('/computers', methods=['GET', 'POST'])
def computers():
    with open("categories.json", "rt", encoding="utf8") as f:
        cat_list = json.loads(f.read())
    return render_template("categories_page.html", title="Компьютеры", category="Компьютеры", cat=cat_list['computers'])


@app.route('/<category>')
def redirect_to_items(category):
    return redirect('/{}/1'.format(category))


@app.route('/<category>/0')
def redirect_to_items2(category):
    return redirect('/{}/1'.format(category))


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_page(item_id):
    form = Amount()
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == int(item_id)).first()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            amount = form.amount.data
            id = current_user.get_id()
            user = db_sess.query(User).filter(User.id == id).first()
            cart = user.cart
            if cart is not None:
                cart = cart.split(', ')
                cart.append(str(item_id) + ': ' + str(amount))
                user.cart = ', '.join(cart)
                db_sess.commit()
            else:
                cart = [str(item_id) + ': ' + str(amount)]
                user.cart = ', '.join(cart)
                db_sess.commit()
            return render_template("item_page.html", item=item, form=form,
                                   message='Добавлено в корзину', title=item.title)
        else:
            return render_template("item_page.html", item=item, form=form,
                                   message='Авторизируйтесь для продолжения', title=item.title)
    return render_template("item_page.html", item=item, form=form, title=item.title)


@app.route('/cart', methods=['GET', 'POST'])
def buy_page():
    id = current_user.get_id()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    cart = user.cart
    cart_dict = {}
    cart = cart.split(', ')
    for el in cart:
        el = el.split(': ')
        item = db_sess.query(Item).filter(Item.id == int(el[0])).first()
        price = item.price
        price = price[2:]
        price = unicodedata.normalize("NFKD", price)
        price = price.strip()
        if item.title in cart_dict.keys():
            it = {
                'price': int(''.join(price.split())),
                'amount': int(el[1]) + int(cart_dict[item.title]['amount']),
                'image': item.image,
                'link': '/item/{}'.format(el[0]),
                'id': el[0]
            }
        else:
            it = {
                'price': int(''.join(price.split())),
                'amount': int(el[1]),
                'image': item.image,
                'link': '/item/{}'.format(el[0]),
                'id': el[0]
            }
        cart_dict[item.title] = it
    total = 0
    for key, value in cart_dict.items():
        total += value['price']
    return render_template('buying_page.html', cart=cart_dict, title='Корзина', total=total)


@app.route('/<category>/<page_number>')
def category_page(category, page_number):
    with open("categories.json", "rt", encoding="utf8") as f:
        c_list = json.loads(f.read())
    cat = 'Категория'
    for el in c_list:
        for c in c_list[el]:
            if c['category'][1:] == category:
                cat = c['name']
                break
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.category == category).all()
    limit = math.ceil(len(items) / 12)
    items_len = len(items)
    return render_template("items.html", items=items, title=cat, category=cat, number=int(page_number),
                           length=items_len, limit=limit, link=items[0].category)


@app.route('/item_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    user_id = current_user.get_id()
    user = db_sess.query(User).filter(User.id == user_id).first()
    cart = user.cart
    cart = cart.split(', ')
    for el in cart:
        if str(id) in el:
            cart.remove(el)
    user.cart = ', '.join(cart)
    db_sess.commit()
    return redirect('/cart')


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
