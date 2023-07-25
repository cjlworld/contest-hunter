import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

config = {
    'SQLALCHEMY_DATABASE_URI' : 'sqlite:///' + os.path.join(BASE_DIR, 'data.sqlite'),
}