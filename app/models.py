from datetime import datetime

from PIL import Image
from io import BytesIO

import base64
import os

import jwt

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from app import db

from config import Config

import enum

product_filters = db.Table('product_filters',
                           db.Column('value_id', db.Integer, db.ForeignKey('filter_value.id'), primary_key=True),
                           db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
                           )

category_filters = db.Table('category_filters',
                            db.Column('filter_id', db.Integer, db.ForeignKey('filter.id'), primary_key=True),
                            db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
                            )

product_categories = db.Table('product_categories',
                              db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
                              db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                              )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    client = db.relationship("Client", backref=db.backref("user", lazy=True), uselist=False)
    admin = db.relationship("Admin", backref=db.backref("user", lazy=True), uselist=False)

    def generate_token(self):
        return jwt.encode(
            {
                'id': self.id
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        ).decode()

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY)
            return payload['id']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    phone = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=True)
    first_name = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    last_name = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'))
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def avatar_url(self):
        return "/static/upload/images/avatars/client/" + str(self.avatar)

    @staticmethod
    def crop_image(img, path):
        crop_height, crop_width = Config.AVATAR_CROP_SIZE
        width, height = img.size

        height_ratio = height / crop_height
        width_ratio = width / crop_width

        optimal_ratio = width_ratio
        if height_ratio < width_ratio:
            optimal_ratio = height_ratio

        optimal_size = (int(width / optimal_ratio), int(height / optimal_ratio))
        img = img.resize(optimal_size)

        width, height = img.size

        left = (width - crop_width) / 2
        top = (height - crop_height) / 2
        right = (width + crop_width) / 2
        bottom = (height + crop_height) / 2

        img = img.crop((left, top, right, bottom))
        img.save(path)

    def save_image(self, filename, image64):
        crop_path = os.path.join(Config.AVATAR_CLIENT_UPLOAD_FOLDER, filename)
        img = Image.open(BytesIO(base64.b64decode(image64)))

        self.crop_image(img, crop_path)
        if self.avatar:
            old = os.path.join(Config.AVATAR_CLIENT_UPLOAD_FOLDER, self.avatar)
            if os.path.exists(old):
                os.remove(old)
        self.avatar = filename


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    fullname = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    email = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    password_hash = db.Column(db.String(400), nullable=False)
    avatar = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def avatar_url(self):
        return "/static/upload/images/avatars/admin/" + str(self.avatar)

    @staticmethod
    def crop_image(img, path):
        crop_height, crop_width = Config.AVATAR_CROP_SIZE
        width, height = img.size

        height_ratio = height / crop_height
        width_ratio = width / crop_width

        optimal_ratio = width_ratio
        if height_ratio < width_ratio:
            optimal_ratio = height_ratio

        optimal_size = (int(width / optimal_ratio), int(height / optimal_ratio))
        img = img.resize(optimal_size)

        width, height = img.size

        left = (width - crop_width) / 2
        top = (height - crop_height) / 2
        right = (width + crop_width) / 2
        bottom = (height + crop_height) / 2

        img = img.crop((left, top, right, bottom))
        img.save(path)

    def save_image(self, filename, image64):
        crop_path = os.path.join(Config.AVATAR_ADMIN_UPLOAD_FOLDER, filename)
        img = Image.open(BytesIO(base64.b64decode(image64)))

        self.crop_image(img, crop_path)
        if self.avatar:
            old = os.path.join(Config.AVATAR_ADMIN_UPLOAD_FOLDER, self.avatar)
            if os.path.exists(old):
                os.remove(old)
        self.avatar = filename


class ClientFavourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("favourites", lazy=True, cascade="all,delete"))
    product = db.relationship("Product", backref=db.backref("favourites", lazy=True, cascade="all,delete"))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    administrators = db.relationship(
        "Admin", cascade="all,delete", backref=db.backref("role", lazy=True), lazy=True
    )


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete='CASCADE'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship(
        "Category", cascade="all,delete", backref=db.backref("children"), remote_side=id
    )

    filters = db.relationship(
        'Filter', secondary=category_filters, lazy='subquery',
        backref=db.backref('categories', lazy=True)
    )

    @hybrid_property
    def products_length(self):
        return len(self.products)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id", ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete='CASCADE'), nullable=False)
    default_image_id = db.Column(db.Integer, db.ForeignKey('product_image.id', ondelete='SET NULL'), nullable=True)
    summary = db.Column(db.String(1000))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    on_sale_price = db.Column(db.Float, nullable=True)
    condition = db.Column(db.String(100), nullable=False, default='new')
    stock = db.Column(db.Integer, default=0)
    on_sale = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('Creator', backref=db.backref("products"))
    category = db.relationship('Category', backref=db.backref("direct_products"))
    default_image = db.relationship('ProductImage', foreign_keys=default_image_id, post_update=True)

    categories = db.relationship(
        'Category', secondary=product_categories, lazy='subquery',
        backref=db.backref('products', lazy=True)
    )

    filters = db.relationship(
        'FilterValue', secondary=product_filters, lazy='subquery',
        backref=db.backref('products', lazy=True)
    )

    @hybrid_property
    def reviews_length(self):
        return len(self.reviews)

    @hybrid_property
    def reviews_score(self):
        return (
            sum(
                review.score
                for review in self.reviews
            ) / len(self.reviews)
            if self.reviews
            else 0
        )

    @hybrid_property
    def weighted_score(self):
        total_reviews = ProductReview.query.all()
        v = self.reviews_length
        r = self.reviews_score
        m = len(total_reviews) / Config.PERCENTAGE_OF_TOTAL_REVIEWS
        c = (
            sum(
                review.score
                for review in total_reviews
            ) / len(total_reviews)
            if total_reviews
            else 0
        )
        return (r * v + c * m) / (v + m)


class Creator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())


class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())


class FilterValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filter_id = db.Column(db.Integer, db.ForeignKey('filter.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    filter = db.relationship(
        "Filter", cascade="all,delete", backref=db.backref("values")
    )


class ProductView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=True)
    client_ip = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("views", lazy=True, cascade="all,delete"))
    client = db.relationship("Client", backref=db.backref("views", lazy=True, cascade="all,delete"))


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    @hybrid_property
    def image_url(self):
        return "/static/upload/images/products/" + self.image

    @hybrid_property
    def thumb_url(self):
        return "/static/upload/images/products/thumbs/" + self.image

    @staticmethod
    def crop_image(img, path):
        crop_height, crop_width = Config.CROP_SIZE
        width, height = img.size

        height_ratio = height / crop_height
        width_ratio = width / crop_width

        optimal_ratio = width_ratio
        if height_ratio < width_ratio:
            optimal_ratio = height_ratio

        optimal_size = (int(width / optimal_ratio), int(height / optimal_ratio))
        img = img.resize(optimal_size)

        width, height = img.size

        left = (width - crop_width) / 2
        top = (height - crop_height) / 2
        right = (width + crop_width) / 2
        bottom = (height + crop_height) / 2

        img = img.crop((left, top, right, bottom))
        img.save(path)

    @staticmethod
    def resize_image(img, path, size):
        new_height, new_width = size
        width, height = img.size

        height_ratio = height / new_height
        width_ratio = width / new_width

        optimal_ratio = width_ratio
        if height_ratio < width_ratio:
            optimal_ratio = height_ratio

        optimal_size = (int(width / optimal_ratio), int(height / optimal_ratio))
        img = img.resize(optimal_size)
        img.save(path)

    def save_image(self, filename, image64):
        path = os.path.join(Config.PRODUCT_UPLOAD_FOLDER, filename)
        crop_path = os.path.join(Config.PRODUCT_THUMB_UPLOAD_FOLDER, filename)
        img = Image.open(BytesIO(base64.b64decode(image64)))

        self.resize_image(img, path, Config.IMAGE_SIZE)
        self.resize_image(img, crop_path, Config.CROP_SIZE)

        self.image = filename


class ProductReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("reviews", lazy=True, cascade="all,delete"))
    client = db.relationship("Client", backref=db.backref("reviews", lazy=True, cascade="all,delete"))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("carts", lazy=True))

    def cart_total(self):
        return (
            sum(
                cart_item.price
                for cart_item in self.cart_items
            )
            if self.cart_items
            else 0
        )


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("cart_items", lazy=True, cascade="all,delete"))
    cart = db.relationship("Cart", backref=db.backref("cart_items", lazy=True, cascade="all,delete"))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id', ondelete='CASCADE'))
    store_address_id = db.Column(db.Integer, db.ForeignKey('store_address.id', ondelete='CASCADE'))
    price = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(1000))
    payment_type = db.Column(db.String(30))
    paid = db.Column(db.Boolean, default=False)
    shipping = db.Column(db.Boolean, default=True)
    status = db.Column(db.Integer,  default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    address = db.relationship("Address", backref=db.backref("orders", lazy=True))
    store_address = db.relationship("StoreAddress", backref=db.backref("orders", lazy=True))
    client = db.relationship("Client", backref=db.backref("orders", lazy=True, cascade="all,delete"))
    cart = db.relationship("Cart", backref=db.backref("orders", lazy=True))

    @hybrid_property
    def payment_type_string(self):
        return 'Online by card' if self.payment_type == 'online' else 'Payment upon receipt'

    @hybrid_property
    def shipping_string(self):
        return 'Delivery ' if self.shipping else 'Pick up from Store'

    @hybrid_property
    def status_string(self):
        statuses = ['PROCESSING', 'READY', 'COMPLETED', 'CANCELLED']
        return statuses[self.status]


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id', ondelete='CASCADE'), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    postal_code = db.Column(db.String(10))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("addresses", lazy=True, cascade="all,delete"))
    country = db.relationship("Country", backref=db.backref("addresses", lazy=True, cascade="all,delete"))


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    short = db.Column(db.String(10))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StoreAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    iframe = db.Column(db.Text, nullable=False)
    opened = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HomeCarousel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())


class BannerImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300), nullable=False)
    caption = db.Column(db.String(300))
    active = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @hybrid_property
    def image_url(self):
        return "/static/upload/images/banners/" + self.image

    @hybrid_property
    def thumb_url(self):
        return "/static/upload/images/banners/thumbs/" + self.image

    @staticmethod
    def resize_image(img, path, size):
        new_height, new_width = size
        width, height = img.size

        height_ratio = height / new_height
        width_ratio = width / new_width

        optimal_ratio = width_ratio
        if height_ratio < width_ratio:
            optimal_ratio = height_ratio

        optimal_size = (int(width / optimal_ratio), int(height / optimal_ratio))
        img = img.resize(optimal_size)
        img.save(path)

    def save_image(self, filename, image64):
        path = os.path.join(Config.BANNER_UPLOAD_FOLDER, filename)
        crop_path = os.path.join(Config.BANNER_THUMB_UPLOAD_FOLDER, filename)
        img = Image.open(BytesIO(base64.b64decode(image64)))

        self.resize_image(img, path, Config.BANNER_SIZE)
        self.resize_image(img, crop_path, Config.CROP_SIZE)

        self.image = filename


@event.listens_for(ProductImage, 'after_delete')
def delete_image(mapper, connection, target):
    old = os.path.join(Config.PRODUCT_UPLOAD_FOLDER, target.image)
    if os.path.exists(old):
        os.remove(old)
    old = os.path.join(Config.PRODUCT_THUMB_UPLOAD_FOLDER, target.image)
    if os.path.exists(old):
        os.remove(old)


@event.listens_for(BannerImage, 'after_delete')
def delete_banner_image(mapper, connection, target):
    old = os.path.join(Config.BANNER_UPLOAD_FOLDER, target.image)
    if os.path.exists(old):
        os.remove(old)
    old = os.path.join(Config.BANNER_THUMB_UPLOAD_FOLDER, target.image)
    if os.path.exists(old):
        os.remove(old)
