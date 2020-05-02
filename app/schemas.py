from app import ma

from app.models import *

from marshmallow import fields


class UserSchema(ma.TableSchema):
    class Meta:
        table = User.__table__


class ClientSchema(ma.TableSchema):
    class Meta:
        table = Client.__table__

    user_id = fields.Int()
    favourites = fields.Nested('ClientFavouriteSchema', many=True)
    views = fields.Nested('ProductViewSchema', many=True)
    avatar_url = fields.String()


class ClientFavouriteSchema(ma.TableSchema):
    class Meta:
        table = ClientFavourite.__table__


class AdminSchema(ma.TableSchema):
    class Meta:
        table = Admin.__table__

    user_id = fields.Int()
    role_id = fields.Int()
    role = fields.Nested('RoleSchema', only=["title", "description"])
    avatar_url = fields.String()


class RoleSchema(ma.TableSchema):
    class Meta:
        table = Role.__table__


class CategorySchema(ma.TableSchema):
    class Meta:
        table = Category.__table__
    children = fields.Nested('CategorySchema', many=True, only=["id", "title", "link",  "products_length"])
    parent = fields.Nested('CategorySchema', only=["id", "title", "link", "products_length"])
    products_length = fields.Integer()


class ProductSchema(ma.TableSchema):
    class Meta:
        table = Product.__table__
    category = fields.Nested('CategorySchema', only=["id", "title", "link", "parent"])
    creator = fields.Nested('CreatorSchema')
    default_image = fields.Nested('ProductImageSchema')
    categories = fields.Nested('CategorySchema', many=True, only=["id", "title", "link"])
    filters = fields.Nested('FilterValueSchema', many=True, only=["id", "value", 'filter'])
    reviews_score = fields.Number()
    reviews_length = fields.Number()
    weighted_score = fields.Number()


class ProductReviewSchema(ma.TableSchema):
    class Meta:
        table = ProductReview.__table__
    client = fields.Nested('ClientSchema', only=["first_name", "last_name"])
    product = fields.Nested('ProductSchema', only=["id", "default_image", "name"])


class ProductViewSchema(ma.TableSchema):
    class Meta:
        table = ProductView.__table__


class CreatorSchema(ma.TableSchema):
    class Meta:
        table = Creator.__table__


class FilterSchema(ma.TableSchema):
    class Meta:
        table = Filter.__table__


class FilterValueSchema(ma.TableSchema):
    class Meta:
        table = FilterValue.__table__
    filter = fields.Nested('FilterSchema', only=["id", "title"])


class ProductImageSchema(ma.TableSchema):
    class Meta:
        table = ProductImage.__table__
    image_url = fields.String()
    thumb_url = fields.String()


class CartSchema(ma.TableSchema):
    class Meta:
        table = Cart.__table__


class CartItemSchema(ma.TableSchema):
    class Meta:
        table = CartItem.__table__
    product = fields.Nested('ProductSchema', only=["id", "default_image", "name", "category"])


class OrderSchema(ma.TableSchema):
    class Meta:
        table = Order.__table__
    payment_type_string = fields.String()
    shipping_string = fields.String()
    status_string = fields.String()

    address = fields.Nested('AddressSchema')
    store_address = fields.Nested('StoreAddressSchema')
    cart = fields.Nested('CartSchema')
    client = fields.Nested('ClientSchema', exclude=['favourites', 'views'])


class AddressSchema(ma.TableSchema):
    class Meta:
        table = Address.__table__
    country = fields.Nested('CountrySchema', only=["id", "name", "short"])


class CountrySchema(ma.TableSchema):
    class Meta:
        table = Country.__table__


class BannerImageSchema(ma.TableSchema):
    class Meta:
        table = BannerImage.__table__
    image_url = fields.String()
    thumb_url = fields.String()


class HomeCarouselSchema(ma.TableSchema):
    class Meta:
        table = HomeCarousel.__table__


class StoreAddressSchema(ma.TableSchema):
    class Meta:
        table = StoreAddress.__table__
