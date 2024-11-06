from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import os
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    shoppingcart = db.relationship("ShoppingCart", backref="user")
    wishlist = db.relationship("Wishlist", backref="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email!r}>'


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cateid = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(120), unique=True)
    price = db.Column(db.Float)
    img = db.Column(db.String(200), unique=True)
    shoppingcart = db.relationship("ShoppingCart", backref="goods")
    wishlist = db.relationship("Wishlist", backref="goods")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    goods = db.relationship("Goods", backref="category")


class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    goodsid = db.Column(db.Integer, db.ForeignKey('goods.id'))


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    goodsid = db.Column(db.Integer, db.ForeignKey('goods.id'))


with app.app_context():
    db.drop_all()
    db.create_all()

    user = User(email="admin@admin.com", password_hash=generate_password_hash("root"))
    db.session.add(user)

    user = User(email="111@111.com", password_hash=generate_password_hash("111"))
    db.session.add(user)

    cart1 = ShoppingCart(userid="2", goodsid="1")
    cart2 = ShoppingCart(userid="2", goodsid="2")
    db.session.add(cart1)
    db.session.add(cart2)

    cate1 = Category(name="Men")
    cate2 = Category(name="Women")
    db.session.add(cate1)
    db.session.add(cate2)

    goods1 = Goods(cateid="1", name="1", price="1", img="img/men_1.jpeg")
    goods2 = Goods(cateid="1", name="2", price="1", img="img/men_2.jpeg")
    goods3 = Goods(cateid="2", name="3", price="1", img="img/women_1.jpeg")
    goods4 = Goods(cateid="2", name="4", price="1", img="img/women_2.jpeg")
    goods5 = Goods(cateid="2", name="5", price="1", img="img/women_3.jpeg")
    goods6 = Goods(cateid="2", name="6", price="1", img="img/women_4.jpeg")
    goods7 = Goods(cateid="2", name="7", price="1", img="img/women_5.jpeg")
    goods8 = Goods(cateid="2", name="8", price="1", img="img/women_6.jpeg")
    goods9 = Goods(cateid="2", name="9", price="1", img="img/women_7.jpeg")

    db.session.add(goods1)
    db.session.add(goods2)
    db.session.add(goods3)
    db.session.add(goods4)
    db.session.add(goods5)
    db.session.add(goods6)
    db.session.add(goods7)
    db.session.add(goods8)
    db.session.add(goods9)

    cart = ShoppingCart(userid=1, goodsid=1)
    db.session.add(cart)

    wish = Wishlist(userid=1, goodsid=1)
    db.session.add(wish)

    db.session.commit()


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Invalid input.')
            return redirect(url_for('signin'))

        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.validate_password(password):
                login_user(user)
                flash('Login success.')
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('signin'))
    return render_template("signin.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        repeatpassword = request.form['repeatpassword']

        if not email or not password or not repeatpassword or password != repeatpassword:
            flash('Invalid input.')
            return redirect(url_for('signup'))

        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('User already exist.')
            return redirect(url_for('signup'))
        else:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)

            db.session.commit()
            flash('User created.')
            return redirect(url_for("signin"))

    return render_template("signup.html")


@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/men')
def men():
    return render_template("men.html", goods=Goods.query.filter_by(cateid="1").all())


@app.route('/women')
def women():
    return render_template("women.html", goods=Goods.query.filter_by(cateid="2").all())


@app.route('/addcart//<goodsid>', methods=['GET'])
@login_required
def addcart_not_signin():
    return redirect(url_for("signin"))


@app.route('/addcart/<useremail>/<goodsid>', methods=['GET'])
@login_required
def addcart(useremail, goodsid):
    user = User.query.filter_by(email=useremail).first()
    cart = ShoppingCart.query.filter(and_(ShoppingCart.userid == user.id, ShoppingCart.goodsid == goodsid))
    if cart.first() is not None:
        flash("Good already added.")
        wish = Wishlist.query.filter(and_(Wishlist.userid == user.id, Wishlist.goodsid == goodsid)).first()
        if wish is not None:
            db.session.delete(wish)
            db.session.commit()
    else:
        cart = ShoppingCart(userid=user.id, goodsid=goodsid)
        db.session.add(cart)
        wish = Wishlist.query.filter(and_(Wishlist.userid == user.id, Wishlist.goodsid == goodsid)).first()
        if wish is not None:
            db.session.delete(wish)
        db.session.commit()
        flash('Add to cart successfully.')
    return redirect(url_for("shoppingcart"))


@app.route('/removecart/<useremail>/<goodsid>', methods=['GET'])
@login_required
def removecart(useremail, goodsid):
    user = User.query.filter_by(email=useremail).first()
    cart = ShoppingCart.query.filter(and_(ShoppingCart.userid == user.id, ShoppingCart.goodsid == goodsid)).first()
    db.session.delete(cart)
    db.session.commit()
    flash('Removed.')
    return redirect(url_for("shoppingcart"))


@app.route('/addwish//<goodsid>', methods=['GET'])
@login_required
def addwish_not_signin():
    return redirect(url_for("signin"))


@app.route('/addwish/<useremail>/<goodsid>', methods=['GET'])
@login_required
def addwish(useremail, goodsid):
    user = User.query.filter_by(email=useremail).first()
    wish = Wishlist.query.filter(and_(Wishlist.userid == user.id, Wishlist.goodsid == goodsid))
    if wish.first() is not None:
        flash("Good already added.")
        cart = ShoppingCart.query.filter(and_(ShoppingCart.userid == user.id, ShoppingCart.goodsid == goodsid)).first()
        if cart is not None:
            db.session.delete(cart)
            db.session.commit()
    else:
        wish = Wishlist(userid=user.id, goodsid=goodsid)
        db.session.add(wish)
        cart = ShoppingCart.query.filter(and_(ShoppingCart.userid == user.id, ShoppingCart.goodsid == goodsid)).first()
        if cart is not None:
            db.session.delete(cart)
        db.session.commit()
        flash('Add to wishlist successfully.')
    return redirect(url_for("wishlist"))


@app.route('/removewish/<useremail>/<goodsid>', methods=['GET'])
@login_required
def removewish(useremail, goodsid):
    user = User.query.filter_by(email=useremail).first()
    wish = Wishlist.query.filter(and_(Wishlist.userid == user.id, Wishlist.goodsid == goodsid)).first()
    db.session.delete(wish)
    db.session.commit()
    flash('Removed.')
    return redirect(url_for("wishlist"))


@app.route('/shoppingcart')
@login_required
def shoppingcart():
    goods = Goods.query.join(ShoppingCart, ShoppingCart.goodsid == Goods.id).filter(
        ShoppingCart.userid == current_user.get_id())
    goods_len = Goods.query.join(ShoppingCart, ShoppingCart.goodsid == Goods.id).filter(
        ShoppingCart.userid == current_user.get_id()).count()
    sum_price = 0
    for good in goods:
        sum_price += good.price
    return render_template("shoppingcart.html", goods=goods, goods_first=goods.first(), goods_len=goods_len, sum_price=sum_price+5)


@app.route('/wishlist')
@login_required
def wishlist():
    goods = Goods.query.join(Wishlist, Wishlist.goodsid == Goods.id).filter(
        Wishlist.userid == current_user.get_id())
    return render_template("wishlist.html", goods=goods)


if __name__ == '__main__':
    app.run()
