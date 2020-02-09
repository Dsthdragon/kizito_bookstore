from flask import jsonify, request, current_app, make_response

from sqlalchemy import or_

from functools import wraps

from app.api import bp

from app.schemas import *

from app import db

import uuid
import random

ALLOWED_EXTENSIONS = ['png', 'jpeg', 'jpg', 'gif']


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        user_id = User.decode_token(request.cookies.get('auth'))
        user = User.query.get(user_id)
        if not user:
            return jsonify(status="failed", message="Login to continue", isAuth=False)
        return f(*args, **kwargs)

    return wrap


# Auth endpoint
@bp.route('/auth')
def user_auth():
    user_id = User.decode_token(request.cookies.get('auth'))
    user = User.query.get(user_id)
    if not user:
        return jsonify(status="failed", message="Invalid token received", isAuth=False)

    client = ClientSchema().dump(user.client)
    is_client = True if user.client else False
    admin = AdminSchema().dump(user.admin)
    is_admin = True if user.admin else False
    return jsonify(status="success", message="User Logged In", isAuth=True, client=client, admin=admin,
                   isClient=is_client, isAdmin=is_admin)


# Roles endpoints
@bp.route("/roles")
def get_roles():
    role_model = Role.query.all()
    role_schema = RoleSchema(many=True).dump(role_model)
    return jsonify(status="success", message="Roles Found", data=role_schema)


@bp.route("/roles", methods=['POST'])
def create_roles():
    data = request.get_json()
    if not data:
        jsonify(status="failed", message="No Data Sent")

    if not data.get('title'):
        jsonify(status="failed", message="Title required!")

    if not data.get('description'):
        jsonify(status="failed", message="Description required!")

    role_model = Role.query.filter_by(title=data['title']).first()

    if role_model:
        return jsonify(status="failed", message="Role already in system!")

    role_model = Role(title=data['title'], description=data['description'])
    db.session.add(role_model)
    db.session.commit()

    return jsonify(status="success", message="Role Created!")


@bp.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(_id):
    role_model = Role.query.get(int(_id))
    if not role_model:
        return jsonify(status="failed", message="Role not found in system")

    db.session.delete(role_model)
    db.session.commit()

    return jsonify(status="success", message="Role Deleted successfully")


@bp.route('/roles/<role_id>')
def get_role(role_id):
    role_model = Role.query.get(int(role_id))
    if not role_model:
        return jsonify(status="failed", message="Role not found in system")
    role_schema = RoleSchema().dump(role_model)
    return jsonify(status="success", message="Role Found", data=role_schema)


# Administrators Endpoints
@bp.route('/administrator')
def get_administrators():
    limited = request.args.get('limited', 1, type=int)
    if limited:
        page = request.args.get("page", 1, type=int)
        admin_model = Admin.query.paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        has_next = admin_model.has_next
        admin_model = admin_model.items
    else:
        admin_model = Admin.query.all()
        has_next = False
    admin_schema = AdminSchema(many=True).dump(admin_model)
    return jsonify(status="success", message="Administrators Found", data=admin_schema, has_next=has_next)


@bp.route('/administrator/<admin_id>')
def get_administrator(admin_id):
    admin_model = Admin.query.get(admin_id)
    if not admin_model:
        return jsonify(status="failed", message="Admin not found in system")

    admin_schema = AdminSchema().dump(admin_model)
    return jsonify(status="success", message="Role Found", data=admin_schema)


# Category endpoint
@bp.route('/category')
def get_categories():
    limited = request.args.get('limited', 1, type=int)
    if limited:
        page = request.args.get("page", 1, type=int)
        category_model = Category.query.order_by(Category.parent_id.asc()).paginate(page, current_app.config[
            'POSTS_PER_PAGE'], False)
        has_next = category_model.has_next
        category_model = category_model.items
    else:
        category_model = Category.query.order_by(Category.parent_id.asc()).all()
        has_next = False
    category_schema = CategorySchema(many=True).dump(category_model)
    return jsonify(status="success", message="Categories Found", data=category_schema, has_next=has_next)


@bp.route('/category/parent/<category_id>')
def get_category_by_parent(category_id):
    parent = category_id if int(category_id) > 0 else None
    category_model = Category.query.filter_by(parent_id=parent).all()

    category_schema = CategorySchema(many=True).dump(category_model)
    return jsonify(status="success", message="Categories Found", data=category_schema)


@bp.route('/category', methods=['POST'])
def create_category():
    data = request.get_json()

    if not data:
        return jsonify(status='failed', message='No data sent!')

    if not data.get('title'):
        return jsonify(status='failed', message='Title required!')

    title = str(data.get('title'))
    category_model = Category.query.filter_by(title=title).first()

    if category_model:
        return jsonify(status='failed', message='Category already in system!')

    category_model = Category()
    category_model.title = title
    category_model.link = (title.replace(' ', '_') + "_" + str(random.randint(100, 100000))).lower()
    if data.get('parent'):
        category_model.parent_id = data.get('parent')

    db.session.add(category_model)
    db.session.commit()

    return jsonify(status='success', message='Category Created!')


@bp.route('/category/<string:link>')
def get_category_by_link(link):
    category_model = Category.query.filter_by(link=link).first()

    if not category_model:
        return jsonify(status='failed', message="Category Not Found")

    category_schema = CategorySchema().dump(category_model)
    return jsonify(status='success', message='Category Found', data=category_schema)


@bp.route('/category/<int:category_id>')
def get_category_by_id(category_id):
    category_model = Category.query.get(category_id)

    if not category_model:
        return jsonify(status='failed', message="Category Not Found")

    category_schema = CategorySchema().dump(category_model)
    return jsonify(status='success', message='Category Found', data=category_schema)


@bp.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    category_model = Category.query.get(category_id)
    if not category_model:
        return jsonify(status='failed', message="Category Not Found")

    db.session.delete(category_model)
    db.session.commit()
    return jsonify(status='success', message='Category Deleted')


@bp.route('/category/product/<int:product_id>')
def get_unassociated_product_categories(product_id):
    category_model = Category.query.filter(~Category.products.any(Product.id == product_id))
    category_schema = CategorySchema(many=True).dump(category_model)
    return jsonify(status='success', message='Category Found', data=category_schema)


# Product Endpoint
@bp.route('/product')
def get_products():
    order_by = request.args.get("order_by", "created", type=str)
    order = request.args.get("order", 'desc', type=str)
    limited = request.args.get('limited', 1, type=int)
    product_model = Product.query
    if order == 'desc':
        product_model = product_model.order_by(getattr(Product, order_by).desc())
    else:
        product_model = product_model.order_by(getattr(Product, order_by).asc())
    if limited:
        page = request.args.get("page", 1, type=int)
        product_model = product_model.paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        has_next = product_model.has_next
        product_model = product_model.items
    else:
        product_model = product_model.all()
        has_next = False
    product_schema = ProductSchema(many=True).dump(product_model)
    return jsonify(status="success", message="Products Found", data=product_schema, has_next=has_next)


@bp.route('/product/filter/<int:product_id>', methods=['POST'])
def add_filter_product(product_id):
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No data sent')

    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message='Product not Found')

    for filter_data in data:
        filter_value_model = FilterValue.query.filter_by(
            filter_id=filter_data['id'], value=filter_data['value']
        ).first()

        if not filter_value_model:
            filter_value_model = FilterValue(filter_id=filter_data['id'], value=filter_data['value'])
            db.session.add(filter_value_model)
        product_model.filters.append(filter_value_model)

    db.session.commit()

    return jsonify(status='success', message='Filter Added To Product')


@bp.route('/product/filter/<int:product_id>/<int:filter_id>', methods=['DELETE'])
def delete_filter_product(product_id, filter_id):
    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message='Product not Found!')

    filter_value_model = FilterValue.query.get(filter_id)
    if not product_model:
        return jsonify(status='failed', message='Filter not Found!')

    product_model.filters.remove(filter_value_model)
    db.session.commit()

    return jsonify(status='success', message='Filter Removed From Product')


@bp.route('/product/category/<int:product_id>', methods=['POST'])
def add_category_product(product_id):
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No data sent')

    if not data.get('category'):
        return jsonify(status='failed', message='Category Required')

    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message='Product not Found')
    for x in data.get('category'):
        category_model = Category.query.get(x)
        while category_model:
            if category_model:
                product_model.categories.append(category_model)
            if category_model.parent_id:
                category_model = Category.query.category_model(category_model.parent_id)
            else:
                category_model = None

    db.session.commit()
    return jsonify(status='success', message='Category Added')


@bp.route('/product/category/<int:product_id>/<int:category_id>', methods=['DELETE'])
def delete_category_product(product_id, category_id):
    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message='Product not Found!')

    category_model = Category.query.get(category_id)
    if not category_model:
        return jsonify(status='failed', message='Category not Found!')

    product_model.categories.remove(category_model)
    db.session.commit()

    return jsonify(status='success', message='Category Removed Deleted')


@bp.route('/product/category/<int:category_id>')
def get_products_by_category(category_id):
    limited = request.args.get('limited', 1, type=int)
    if limited:
        page = request.args.get("page", 1, type=int)

        product_model = Product.query.filter(Product.categories.any(Category.id == category_id))

        product_model = product_model.paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        has_next = product_model.has_next
        product_model = product_model.items
    else:
        product_model = Product.query.all()
        has_next = False
    product_schema = ProductSchema(many=True).dump(product_model)
    return jsonify(status="success", message="Products Found", data=product_schema, has_next=has_next)


@bp.route('/find_products')
def find_products():
    title = request.args.get("title", "", type=str)
    category = request.args.get("category", None, type=int)
    order_by = request.args.get("order_by", "created", type=str)
    order = request.args.get("order", 'desc', type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 0, type=int)
    per_page = per_page if per_page != 0 else current_app.config['POSTS_PER_PAGE']

    product_model = Product.query
    if title:
        print(title)
        product_model = product_model.filter(
            or_(
                Product.name.ilike(f"%{title}%"),
                Product.description.ilike(f"{title}%"),
                Product.summary.ilike(f"%{title}%"),
                Product.creator.has(Creator.title.ilike(f"%{title}%"))
            )
        )

    if category:
        product_model = product_model.filter(Product.categories.any(Category.id == category))

    if order == 'desc':
        product_model = product_model.order_by(getattr(Product, order_by).desc())
    else:
        product_model = product_model.order_by(getattr(Product, order_by).asc())

    product_model = product_model.paginate(page, per_page, False)
    has_next = product_model.has_next
    total = product_model.total
    product_model = product_model.items

    product_schema = ProductSchema(many=True).dump(product_model)
    return jsonify(status="success", message="product_model Found", data=product_schema, has_next=has_next, total=total)


@bp.route('/product/<product_id>')
def get_product(product_id):
    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message="Product Not Found")

    product_schema = ProductSchema().dump(product_model)

    return jsonify(status='success', message="Product Found", data=product_schema)


@bp.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No data sent')

    if not data.get('creator'):
        return jsonify(status='failed', message='Creator Required')

    creator_model = Creator.query.filter_by(title=str(data.get('creator')).lower()).first()
    if not creator_model:
        creator_model = Creator(title=str(data.get('creator')).lower())
        db.session.add(creator_model)
        db.session.commit()

    if not data.get('name'):
        return jsonify(status='failed', message='Name Required!')

    if not data.get('category'):
        return jsonify(status='failed', message='Category Required!')

    if not data.get('price'):
        return jsonify(status='failed', message='Price Required!')

    if not data.get('summary'):
        return jsonify(status='failed', message='Summary Required!')

    if not data.get('description'):
        return jsonify(status='failed', message='description Required!')

    product_model = Product()
    product_model.category_id = data.get('category')
    product_model.price = data.get('price')
    product_model.name = data.get('name')
    product_model.creator = creator_model
    product_model.description = data.get('description')
    product_model.summary = data.get('summary')

    category_model = Category.query.get(data.get('category'))
    while category_model:
        if category_model:
            product_model.categories.append(category_model)
        if category_model.parent_id:
            category_model = Category.query.get(category_model.parent_id)
        else:
            category_model = None

    db.session.add(product_model)
    db.session.commit()

    product_schema = ProductSchema().dump(product_model)

    return jsonify(status='success', message='Product Created', data=product_schema)


@bp.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message="Product Not Found")

    db.session.delete(product_model)
    db.session.commit()

    return jsonify(status='success', message="Product Deleted")


@bp.route('/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    product_model = Product.query.get(product_id)
    if not product_model:
        return jsonify(status='failed', message="Product not Found")

    data = request.get_json()

    if not data:
        return jsonify(status='failed', message="No Data sent")

    for d in data:
        setattr(product_model, d, data[d])

    db.session.commit()

    return jsonify(status='success', message="Update Successful")


# Product Images Endpoint
@bp.route('/image', methods=['POST'])
def upload_image():
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No Data Sent!")
    product_model = Product.query.get(data.get('id'))
    if not product_model:
        return jsonify(status="failed", message="Product Not Found")

    if not data.get('type'):
        return jsonify(status="failed", message="Image type required!")

    if not data.get('img'):
        return jsonify(status="failed", message="Image data not sent!")

    if data.get('type').lower() not in ALLOWED_EXTENSIONS:
        return jsonify(status="failed", message="Extension not supported!")

    unique_filename = str(uuid.uuid4()) + '.' + data['type'].lower()
    product_image_model = ProductImage()
    product_image_model.save_image(unique_filename, data['img'])
    product_image_model.product_id = product_model.id
    if not product_model.default_image_id:
        product_model.default_image = product_image_model

    db.session.add(product_image_model)
    db.session.commit()

    return jsonify(status='success', message='Image uploaded')


@bp.route('/image/<product_id>')
def get_product_images(product_id):
    product_image_model = ProductImage.query.filter_by(product_id=product_id).all()
    product_image_schema = ProductImageSchema(many=True).dump(product_image_model)

    return jsonify(status="success", message="Product Images Found", data=product_image_schema)


@bp.route('/image/<product_image_id>', methods=['DELETE'])
def delete_image(product_image_id):
    product_image_model = ProductImage.query.get(product_image_id)
    if not product_image_model:
        return jsonify(status='failed', message='Product Image not found')

    db.session.delete(product_image_model)
    db.session.commit()
    return jsonify(status='failed', message='Product Image Deleted')


@bp.route('/image/<product_image_id>', methods=['PUT'])
def change_main(product_image_id):
    product_image_model = ProductImage.query.get(product_image_id)
    if not product_image_model:
        return jsonify(status='success', message='Product Image not found!')

    product_model = Product.query.get(product_image_model.product_id)

    if not product_model:
        return jsonify(status='success', message='Product Image found!')

    product_model.default_image = product_image_model

    db.session.commit()

    return jsonify(status='success', message='Product Made Main')


# Filters Endpoint
@bp.route('/filter')
def get_filters():
    limited = request.args.get('limited', 1, type=int)
    if limited:
        page = request.args.get("page", 1, type=int)
        filter_model = Filter.query.paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        has_next = filter_model.has_next
        filter_model = filter_model.items
    else:
        filter_model = Filter.query.all()
        has_next = False
    filter_schema = FilterSchema(many=True).dump(filter_model)
    return jsonify(status="success", message="Filters Found", data=filter_schema, has_next=has_next)


@bp.route('/filter', methods=['POST'])
def create_filter():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='Data Required!')

    if not data.get('title'):
        return jsonify(status='failed', message='Filter Title Required!')

    title = data.get('title')
    filter_model = Filter.query.filter_by(title=title).first()

    if filter_model:
        return jsonify(status='failed', message='Filter Already in System!')

    filter_model = Filter(title=title)
    db.session.add(filter_model)
    db.session.commit()

    return jsonify(status='success', message='Filter Added To System')


@bp.route('/filter/<int:filter_id>')
def get_filter(filter_id):
    filter_model = Filter.query.get(filter_id)
    if not filter_model:
        return jsonify(status='failed', message='Filter Not Found')

    filter_schema = FilterSchema().dump(filter_model)

    return jsonify(status='success', message='Filter Found', data=filter_schema)


@bp.route('/filter/<int:filter_id>', methods=['DELETE'])
def delete_filter(filter_id):
    filter_model = Filter.query.get(filter_id)
    if not filter_model:
        return jsonify(status='failed', message='Filter Not Found')

    db.session.delete(filter_model)
    db.session.commit()

    return jsonify(status='success', message='Filter Deleted')


@bp.route('/filter/product/<int:product_id>')
def get_unassociated_product_filter(product_id):
    filter_model = Filter.query.filter(~Filter.values.any(FilterValue.products.any(Product.id == product_id)))
    filter_schema = FilterSchema(many=True).dump(filter_model)
    return jsonify(status='success', message='Filters Found Found', data=filter_schema)


# Clients routes

@bp.route('/client/login', methods=['POST'])
def login_client():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message="No data sent!")

    client_model = Client.query.filter_by(email=data.get('email')).first()
    if client_model and client_model.check_password(data.get('password')):
        resp = make_response(jsonify(status="success", message="Login Successful!"))
        resp.set_cookie('auth', client_model.user.generate_token())
        return resp

    return jsonify(status='failed', message='Invalid email/password')


@bp.route('/client', methods=['POST'])
def register_client():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No Data sent!')

    if not data.get('first_name'):
        return jsonify(status='failed', message="First Name required!")

    if not data.get('email'):
        return jsonify(status='failed', message="Email address required!")

    if not data.get('password'):
        return jsonify(status='failed', message="Password required!")

    client_model = Client.query.filter_by(email=data.get('email')).first()
    if client_model:
        return jsonify(status='failed', message='Email Already in system')

    user_model = User()

    client_model = Client()
    client_model.user = user_model
    client_model.email = data.get('email')
    client_model.phone = data.get('phone')
    client_model.first_name = data.get('first_name')
    client_model.last_name = data.get('last_name')
    client_model.set_password(data.get('password'))

    db.session.add_all([user_model, client_model])
    db.session.commit()

    resp = make_response(jsonify(status="success", message="Client Created!"))
    resp.set_cookie('auth', client_model.user.generate_token())
    return resp


@bp.route('/client/<int:client_id>', methods=['PUT'])
@login_required
def update_client(client_id):
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No Data sent!')

    if not data.get('first_name'):
        return jsonify(status='failed', message="First Name required!")

    client_model = Client.query.get(client_id)
    if not client_model:
        return jsonify(status='failed', message='Client Not Found')

    client_model.first_name = data.get('first_name')
    client_model.last_name = data.get('last_name')
    client_model.phone = data.get('phone')

    db.session.commit()
    client_schema = ClientSchema().dump(client_model)
    return jsonify(status='success', message='Client Update', data=client_schema)


@bp.route('/client/change_password/<int:client_id>', methods=['PUT'])
@login_required
def change_password(client_id):
    data = request.get_json()

    if not data:
        return jsonify(status='failed', message='No Data sent!')

    if not data.get('password'):
        return jsonify(status='failed', message="Password is required!")

    if not data.get('new_password'):
        return jsonify(status='failed', message="New Password is required!")

    client_model = Client.query.get(client_id)
    if not client_model:
        return jsonify(status='failed', message='Client Not Found')

    if not client_model.check_password(data.get('password')):
        return jsonify(status='failed', message='Invalid Password')

    client_model.set_password(data.get('new_password'))

    db.session.commit()
    client_schema = ClientSchema().dump(client_model)
    return jsonify(status='success', message='Client Password Update', data=client_schema)


@bp.route('/client/<int:client_id>')
def get_client(client_id):
    client_model = Client.query.get(client_id)
    if not client_model:
        return jsonify(status='failed', message='Client Not Found')

    client_schema = ClientSchema().dump(client_model)

    return jsonify(status='success', message='Client Found', data=client_schema)


@bp.route('/logout')
def logout_user():
    resp = make_response(jsonify(status="success", message="Logout Successful!"))
    resp.set_cookie('auth', '')
    return resp


@bp.route('/product/favourite', methods=['POST'])
@login_required
def add_favourite():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message='No Data sent!')
    client_model = Client.query.get(data.get('client'))
    if not client_model:
        return jsonify(status='failed', message='Client not found!')
    product_model = Product.query.get(data.get('product'))
    if not product_model:
        return jsonify(status='failed', message='product not found!')

    client_favourite = ClientFavourite.query.filter_by(
        client_id=client_model.id,
        product_id=product_model.id
    ).first()

    if client_favourite:
        return jsonify(status='failed', message='Product already favourite!')

    client_favourite = ClientFavourite()
    client_favourite.client_id = client_model.id
    client_favourite.product_id = product_model.id

    db.session.add(client_favourite)
    db.session.commit()

    return jsonify(status='success', message='Product added to favourite!')


@bp.route('/product/favourite/<int:product_id>/<int:client_id>', methods=['DELETE'])
@login_required
def remove_favourite(product_id, client_id):
    client_favourite = ClientFavourite.query.filter_by(
        client_id=client_id,
        product_id=product_id
    ).first()
    if client_favourite:
        db.session.delete(client_favourite)
        db.session.commit()

    return jsonify(status='success', message='Product remove from favourite!')


@bp.route('/client/favourite/<int:client_id>')
def get_user_favourite(client_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 0, type=int)
    per_page = per_page if per_page != 0 else current_app.config['POSTS_PER_PAGE']

    product_model = Product.query.filter(
        Product.favourites.any(ClientFavourite.client_id == client_id)
    )

    product_model = product_model.paginate(page, per_page, False)
    has_next = product_model.has_next
    total = product_model.total
    product_model = product_model.items
    product_schema = ProductSchema(many=True).dump(product_model)

    return jsonify(status="success", message="Products Found!", data=product_schema, has_next=has_next, total=total)


@bp.route('/product/review', methods=['POST'])
@login_required
def product_review():
    data = request.get_json()

    if not data:
        return jsonify(status='failed', message='No Data sent!')

    client_model = Client.query.get(data.get('client'))
    if not client_model:
        return jsonify(status='failed', message='Client not found!')

    product_model = Product.query.get(data.get('product'))
    if not product_model:
        return jsonify(status='failed', message='Product not found!')

    if not data.get('review'):
        return jsonify(status='failed', message='Review Required!')

    if not data.get('score'):
        return jsonify(status='failed', message='Score Required!')

    product_review_model = ProductReview.query.filter_by(product_id=product_model.id, client_id=client_model.id).first()
    if product_review_model:
        return jsonify(status='failed', message='Client Already Reviewed product!')

    product_review_model = ProductReview()
    product_review_model.client = client_model
    product_review_model.product = product_model
    product_review_model.score = data.get('score')
    product_review_model.review = data.get('review')

    db.session.add(product_review_model)
    db.session.commit()

    return jsonify(status='success', message='Product reviewed!')


@bp.route('/product/review/<int:product_id>')
def product_reviews(product_id):
    product_review_model = ProductReview.query.filter_by(product_id=product_id).all()
    product_review_schema = ProductReviewSchema(many=True).dump(product_review_model)

    return jsonify(status="success", message="Products Reviews Found!", data=product_review_schema)


# Cart routes
@bp.route('/cart/add', methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No data sent")
    product_model = Product.query.get(data.get('product'))

    if not product_model:
        return jsonify(status="failed", message="Product not found")

    cart_model = Cart.query.get(data.get('cart'))
    if not cart_model:
        client_model = Client.query.get(data.get('client'))
        if not client_model:
            return jsonify(status="failed", message="Client not found")
        cart_model = Cart.query.filter_by(client_id=client_model.id,complete=False).first()
        if not cart_model:
            cart_model = Cart()
            cart_model.client = client_model
            db.session.add(cart_model)
            db.session.commit()

    cart_item_model = CartItem.query.filter_by(cart_id=cart_model.id, product_id=product_model.id).first()
    if cart_item_model:
        cart_item_model.quantity += data.get('quantity')
        cart_item_model.price = cart_item_model.unit_price * cart_item_model.quantity
    else:
        cart_item_model = CartItem()
        cart_item_model.product = product_model
        cart_item_model.cart = cart_model
        cart_item_model.unit_price = product_model.on_sale_price if product_model.on_sale else product_model.price
        cart_item_model.quantity = data.get('quantity')
        cart_item_model.price = cart_item_model.unit_price * cart_item_model.quantity

        db.session.add(cart_item_model)

    db.session.commit()

    cart_schema = CartSchema().dump(cart_model)

    return jsonify(status="success", message="Product added to cart", data=cart_schema)


@bp.route('/cart/products/<int:cart_id>')
def cart_products(cart_id):
    cart_item_model = CartItem.query.filter_by(cart_id=cart_id).all()
    cart_item_schema = CartItemSchema(many=True).dump(cart_item_model)

    return jsonify(status="success", message="Cart Items Found!", data=cart_item_schema)


@bp.route('/cart/remove/<int:cart_item_id>')
@login_required
def cart_remove_item(cart_item_id):
    cart_item_model = CartItem.query.get(cart_item_id)
    db.session.delete(cart_item_model)
    db.session.commit()

    return jsonify(status="success", message="Cart Items Removed!")
