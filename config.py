import os


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:''@localhost/kizito_bookstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY') or 'sk_test_ea5f84af6fdf29d466ca49c8920216ad9567d9e1';
    POSTS_PER_PAGE = 10
    SECRET_KEY = os.environ.get('SECRET_KEY') or "kizito_secret_key"
    AVATAR_ADMIN_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "avatars", "admin")
    )
    AVATAR_CLIENT_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "avatars", "client")
    )
    PRODUCT_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "products")
    )
    PRODUCT_THUMB_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "products", "thumbs")
    )
    BANNER_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "banners")
    )
    BANNER_THUMB_UPLOAD_FOLDER = os.path.abspath(
        os.path.join("app", "static", "upload", "images", "banners", "thumbs")
    )
    PRODUCT_IMAGE_URL = ("/static", "upload", "images", "products")
    PRODUCT_THUMB_URL = ("/static", "upload", "images", "products", "thumbs")
    BANNER_IMAGE_URL = ("/static", "upload", "images", "banners")
    BANNER_THUMB_URL = ("/static", "upload", "images", "banners", "thumbs")
    IMAGE_SIZE = [500, 500]
    CROP_SIZE = [200, 200]
    AVATAR_CROP_SIZE = [100, 100]
    BANNER_SIZE = [1280, 400]
    PERCENTAGE_OF_TOTAL_REVIEWS = 10
