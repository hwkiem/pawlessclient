import os
from flask import *
# from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


login_manager = LoginManager()
login_manager.init_app(app)

# app.secret_key = 'dOntgUesstHispLease'

# class User(UserMixin):
#   def __init__(self, id):
#     self.id = id


# @login_manager.user_loader
# def load_user(userid):
#   return User(userid)


@app.route('/') # force to login first
def index():
  if current_user.is_authenticated:
    return redirect(url_for('homePage'))
  return redirect(url_for('login'))
















@app.before_request
def before_request(): # on the event of a new connection
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception): # on the event of a connection terminating
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()