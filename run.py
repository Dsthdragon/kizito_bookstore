from wsgiref.handlers import CGIHandler

from app import create_app

app = create_app()
CGIHandler().run(app)