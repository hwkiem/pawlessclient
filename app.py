import os
from flask import *
from pdf2image import convert_from_path, convert_from_bytes
# from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

documents = [] # global 2D array, holding docs as lists with pages as array idexes
curDocIdx = 0
curPageIdx = 0


@app.route('/')
def index():
  image = 'james.jpeg'
  return render_template('home.html', img=image)



@app.route('/prepareDocs', methods=['POST', 'GET']) # assume already served documents, held in 'static'; conver to global docs list
def prepareDocs():
  directory = os.fsencode('static')

  for file in os.listdir(directory):
    name, ext = os.path.splitext(file)
    nameStr = name.decode('utf-8')
    extStr = ext.decode('utf-8')
    fileStr = file.decode('utf-8')
    if extStr == '.pdf':
      images = convert_from_path('/Usr/jamesryan/Documents/semester/VisualIstatic/' + fileStr)
      documents.append(images)
    else:
      documents.append(file)
  
  print(documents)
  return redirect(url_for('index'))




@app.route('/another', methods=['POST', 'GET'])
def another():
  return render_template('another.html')




# def build_face_lists():
#     encodings = []
#     names = []

#     directory = os.fsencode('faces')
#     for file in os.listdir(directory):
#         filename = os.fsdecode(file)
#         name = filename.split('.')[0]

#         path = 'faces/' + filename
#         img = face_recognition.load_image_file(path)
#         encoding = face_recognition.face_encodings(img)
#         if len(encoding) < 1:
#             print('No faces found in ' + filename)
#         else:
#             names.append(name)
#             encodings.append(encoding[0])

#     return encodings, names





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