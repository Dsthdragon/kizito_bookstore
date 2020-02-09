import os


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL') or 'mysql://root:''@localhost/kizito_bookstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    SECRET_KEY = os.environ.get('SECRET_KEY') or "kizito_secret_key"
    UPLOAD_FOLDER = os.path.abspath(os.path.join("jiClone", "static", "upload", "images", "avatars"))
    PRODUCT_UPLOAD_FOLDER = os.path.abspath(os.path.join("app", "static", "upload", "images", "products"))
    PRODUCT_THUMB_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "products", "thumbs")
    )
    PRODUCT_IMAGE_URL = ("/static", "upload", "images", "products")
    PRODUCT_THUMB_URL = ("/static", "upload", "images", "products", "thumbs")
    IMAGE_SIZE = [500, 500]
    CROP_SIZE = [200, 200]
