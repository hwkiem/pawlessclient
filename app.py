import os
from flask import *
from flask import Flask, render_template
from flask import send_file, current_app as app
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import json

import cups

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = 'dOntgUesstHispLease'


class User(UserMixin):
    def __init__(self, id, files=[], curDocIdx=0, curPageIdx=0):
        self.id = id
        self.files = files
        self.curDocIdx = curDocIdx


@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/getdoc')
def getdoc():
    print(len(current_user.files))
    print(current_user.curDocIdx)
    # here we will figure out which pdf we actually want to display
    f = current_user.files[current_user.curDocIdx]
    f = 'pls.pdf'
    print(f)
    # return render_template('doc.html', doc_id=f)
    #ext = os.path.splitext(f)[1].decode('utf-8')
    ext = f.split('.')[-1]
    if ext == 'pdf':
        id = current_user.files[current_user.curDocIdx]
        id = 'pls.pdf'
        path = 'static/' + id
        return send_file(path, attachment_filename=id)
        #return send_file(path, attachment_filename=id)
        return show_static_pdf(f)
    print("here")
    
    return render_template('imageFile.html', img=f)


def show_static_pdf(id):
    path = 'static/' + id
    return send_file(path, attachment_filename=id)


@app.route('/fileList', methods=['POST', 'GET'])
def fileList():
    if len(current_user.files) == 0:
        directory = os.fsencode('static')
        for file in os.listdir(directory):
            current_user.files.append(os.fsdecode(file))

    return redirect(url_for('getdoc'))
    return render_template('fileList.html', files=current_user.files, curDocIdx=current_user.curDocIdx)


@app.route('/login/<uni>', methods=['POST', 'GET'])
def login(uni):
    if uni != 'Unknown':
        user = User(uni, [], 0, 0)
        login_user(user)
        return redirect(url_for('fileList'))
    return redirect(url_for('index'))



@app.route('/nextDoc', methods=['POST', 'GET'])  # update page and then route back to /getDoc
def goRight():
    if current_user.curDocIdx < len(current_user.files) - 1:
        current_user.curDocIdx += 1
    #return render_template('fileList.html', files=current_user.files, curDocIdx=current_user.curDocIdx)
    return redirect(url_for('getdoc'))


@app.route('/prevDoc', methods=['POST', 'GET'])
def goLeft():
    if current_user.curDocIdx < len(current_user.files) - 1:
        current_user.curDocIdx -= 1
    #return render_template('fileList.html', files=current_user.files, curDocIdx=current_user.curDocIdx)
    return redirect(url_for('getdoc'))

@app.route('/print', methods=['POST', 'GET'])
def print_out():
  # print out pdf
  path = 'static/' + current_user.files[current_user.curDocIdx]
  conn = cups.Connection()
  printers = conn.getPrinters()
  printer_name = printers.keys()[0]
  conn.printFile(printer_name, path, "", {})

  # delete file

  if len(current_user.files) - 1 > current_user.curDocIdx:
    current_user.curDocIdx -= 1
  elif current_user.curDocIdx < len(current_user.files) - 1:
    current_user.curDocIdx += 1
  else:
    return render_template('home.html', loggedin = True)

  #return render_template('fileList.html', files=current_user.files, curDocIdx=current_user.curDocIdx)
  return redirect(url_for('getdoc'))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
  logout_user()
  return(redirect(url_for('index')))


# @app.before_request
# def before_request(): # on the event of a new connection
#   """
#   This function is run at the beginning of every web request
#   (every time you enter an address in the web browser).
#   We use it to setup a database connection that can be used throughout the request.

#   The variable g is globally accessible.
#   """
#   try:
#     g.conn = engine.connect()
#   except:
#     print("uh oh, problem connecting to database")
#     import traceback; traceback.print_exc()
#     g.conn = None

# @app.teardown_request
# def teardown_request(exception): # on the event of a connection terminating
#   """
#   At the end of the web request, this makes sure to close the database connection.
#   If you don't, the database could run out of memory!
#   """
#   try:
#     g.conn.close()
#   except Exception as e:
#     pass

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
