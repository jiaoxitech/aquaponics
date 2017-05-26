from flask import Flask, redirect, g, jsonify, request, abort
import sqlite3

DATABASE = 'server.db'

app = Flask(__name__)

def make_dicts(cursor, row):
  return dict((cursor.description[idx][0], value)
    for idx, value in enumerate(row))

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  db.row_factory = make_dicts
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def auth_db(name, password):
    if name == 'admin':
        name = 'admin_password'
    elif name == 'monitor':
        name = 'monitor_password'
    else:
        abort(401)
    if query_db('''SELECT 1 FROM admin WHERE name = ? AND value = ?''', [name, password]):
        return True
    else:
        return False

@app.route("/")
def index():
  return redirect('static/index.html')

@app.route("/auth/<string:password>")
def auth(password):
    if auth_db('admin', password):
        return "OK"
    else:
        abort(401)

@app.route("/admin/password", methods=['POST'])
def updatePassword():
    if auth_db('admin', request.form['passwordOld']):
        type = request.form['type']
        oldPass = request.form['passwordOld']
        newPass = request.form['passwordNew']
        if type == 'admin':
            name = 'admin_password'
        elif type == 'monitor':
            name = 'monitor_password'
        else:
            abort(401)
        query_db('''UPDATE admin SET value = ? WHERE name = ? AND value = ?''', [newPass, name, oldPass])
        query_db('''INSERT INTO admin_log ( entry ) VALUES (?)''', ['''Manually updated {} from: {} to {}'''.format(name, oldPass, newPass)])
        return "OK"
    else:
        abort(401)

@app.route("/admin/relays", methods=['GET', 'POST'])
def relayAdmin():
    if request.method == 'POST':
        #do_the_login()
        abort(401)
    else:
        return jsonify(query_db('''SELECT relay, status, timeOn, timeOff, allDay FROM relays'''))

@app.route("/relay/<int:relay>/<int:status>/<string:password>")
def relayControl(relay, status, password):
    if auth_db('admin', password):
        query_db('''UPDATE relays SET status = ? WHERE relay = ?''', [status, relay])
        return "ok"
    else:
        abort(401)


@app.route("/monitor/submit", methods=['POST'])
def monitorSubmit():
    if auth_db('monitor', request.form['password']):
        print request.form
        return "OK"
    else:
        abort(401)


if __name__ == "__main__":
    app.run()
