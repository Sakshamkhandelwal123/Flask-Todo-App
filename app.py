import os

from . import create_app

app = create_app(os.getenv("CONFIG_MODE"))

@app.route('/')
def hello():
  return 'Todo App!'

from .users import controllers
from .todos import controllers

if __name__ == '__main__':
  app.run(host="0.0.0.0")