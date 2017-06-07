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
        if auth_db('admin', request.form['password']):
            for i in range(1,8):
                query_db('''UPDATE relays SET timeOn = ?, timeOff = ?, allDay = ? WHERE relay = ?''',
                    [request.form['r{}[s]'.format(i)],request.form['r{}[e]'.format(i)],request.form['r{}[a]'.format(i)],i])
                if request.form['r{}[t]'.format(i)] == 2:
                    query_db('''UPDATE relays SET status = 2 WHERE relay = ?''', [i])
            return "OK"
        else:
            abort(401)
    else:
        return jsonify(query_db('''SELECT relay, status, timeOn, timeOff, allDay FROM relays'''))

@app.route("/relay")
def settings():
    query = '''SELECT relay, status, timeOn, timeOff, allDay FROM relays'''
    return jsonify(query_db(query))

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
        for k, v in request.form.iteritems():
            if k != 'password':
             query_db('''INSERT INTO sensor_log (sensor, value) VALUES (?, ?)''', [k, v])
        return "OK"
    else:
        abort(401)


@app.route("/latest")
def latest():
    query = '''SELECT a.sensor, a.timestamp, a.value FROM sensor_log AS a INNER JOIN (SELECT sensor, MAX(timestamp) AS timestamp FROM sensor_log GROUP BY sensor) AS b ON a.sensor     = b.sensor AND a.timestamp = b.timestamp'''
    return jsonify(query_db(query))

@app.route("/charts/airtemp/<int:limits>")
def chartAirTemp(limits):
    query = '''SELECT timestamp, value FROM sensor_log WHERE sensor = 'temp' ORDER BY timestamp DESC LIMIT ?'''
    return jsonify(query_db(query,[limits]))

@app.route("/charts/watertemp/<int:limits>")
def chartWaterTemp(limits):
    query = '''SELECT timestamp, value FROM sensor_log WHERE sensor = 'watertemp' ORDER BY timestamp DESC LIMIT ?'''
    return jsonify(query_db(query,[limits]))

@app.route("/charts/light/<int:limits>")
def chartLight(limits):
    query = '''SELECT timestamp, value FROM sensor_log WHERE sensor = 'light' ORDER BY timestamp DESC LIMIT ?'''
    return jsonify(query_db(query,[limits]))

if __name__ == "__main__":
    app.run()
