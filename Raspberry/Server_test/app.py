from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
# import MySQLdb
import sqlite3
import math
import time
import configparser as ConfigParser
import random
import serial.tools.list_ports

async_mode = None
# async_mode = 'threading'

app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
filename = config.get('files', 'filename')
db_path = config.get('sqlite3DB', 'path')

# db = sqlite3.connect(db_path)
# cur = db.cursor()
# cur.execute('''CREATE TABLE prva (popis TEXT);''')
# cur.execute('''INSERT INTO prva (popis) VALUES ("Ahoj svet!");''')
# db.commit()



print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread1(args):
    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    portList = []

    for onePort in ports:
        portList.append(str(onePort))
        #print(str(onePort))

    #val = input("select port: ")
    val = "/dev/ttyUSB0"

    for x in range(0, len(portList)):
        if portList[x].startswith(str(val)):
            portVar = str(val)
            print(portList[x])

    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()

    dataList = []
    while True:
        if args:
          A = dict(args).get('A')
          dbV = dict(args).get('db_value')
        elif serialInst.in_waiting:
            packet = serialInst.readline()
            print('this is packet.decode: ' + packet.decode('utf'))
            print('this is args: ' + args)
            socketio.sleep(2)
            count = packet.decode('utf')
            print('this is count: ' + count)
            premS = math.sin(int(count))
            premC = 3 * math.cos(int(count))
            dataDict = {
                "t": time.time(),
                "x": count,
                "y": premS,
                "z": premC}
            dataList.append(dataDict)
            socketio.emit('my_response',
                      {'data': float(A) * float(prem), 'count': count},
                      namespace='/test')


def background_thread(args):
    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    portList = []

    for onePort in ports:
        portList.append(str(onePort))
        #print(str(onePort))

    #val = input("select port: ")
    val = "/dev/ttyUSB0"

    for x in range(0, len(portList)):
        if portList[x].startswith(str(val)):
            portVar = str(val)
            print(portList[x])

    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()

    dataList = []
    count = 0
    dataCounter = 0
    dataList = []
    # db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    # db = sqlite3.connect(db_path)

    while True:
        if serialInst.in_waiting:
            if args:
              A = dict(args).get('A')
              dbV = dict(args).get('db_value')
            else:
              A = 1
              dbV = 'nieco'
            packet = serialInst.readline()
            print(dbV)
            print(args)
            socketio.sleep(2)
            count += 1
            dataCounter +=1
            prem = packet.decode('utf')
            if dbV == 'start':
              dataDict = {
                "t": time.time(),
                "x": dataCounter,
                "ys": A*math.sin(dataCounter),
                "yc": A*math.cos(dataCounter)
              }
              dataList.append(dataDict)
            else:
              if len(dataList)>0:
                fuj = str(dataList).replace("'", "\"")
                print(fuj)
                print("*****************************")
                write2file(fuj)

              dataList = []
              dataCounter = 0
            # socketio.emit('my_response',
            #               {'data': float(A)*prem, 'sinus': A*math.sin(dataCounter), 'cosinus': A*math.cos(dataCounter), 'count': count},
            #               namespace='/test')
            socketio.emit('my_response',
                          {'data': float(A) * float(prem), 'count': count},
                          namespace='/test')
        # db.close()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

#  "a" - Append - will append to the end of the file
#  "w" - Write - will overwrite any existing content
#  "r" - Read - will read the content of the file
# pri zapise do suboru musia byt na nadradenom adresari nastavene prava na zapis do adresaru

@app.route('/write')
def write2file(val):
    print(val)
    fo = open("static/files/test.txt","a+")
    # val = '[{"y": 0.6551787400492523, "x": 1, "t": 1522016547.531831}, {"y": 0.47491473008127605, "x": 2, "t": 1522016549.534749}, {"y": 0.7495528524284468, "x": 3, "t": 1522016551.537547}, {"y": 0.19625207463282368, "x": 4, "t": 1522016553.540447}, {"y": 0.3741884249440639, "x": 5, "t": 1522016555.543216}, {"y": 0.06684808042190538, "x": 6, "t": 1522016557.546104}, {"y": 0.17399442194131343, "x": 7, "t": 1522016559.54899}, {"y": 0.025055174467733865, "x": 8, "t": 1522016561.551384}]'
    fo.write("%s\r\n" %val)
    return "done"

@app.route('/read/<string:num>')
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('graph.html', async_mode=socketio.async_mode)

@socketio.on('db_event', namespace='/test')
def db_message(message):
    session['db_value'] = message['value']

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['A'] = message['value']
    # emit('my_response',
    #      {'data': message['value'], 'count': session['receive_count']})

@socketio.on('load_from_file', namespace='/test')
def load_from_file(message):
    lines = []
    with open(filename, 'r') as f:
        lines = f.read()

    emit('load_from_file_response',
         {'data': lines})


@socketio.on('write_to_file', namespace='/test')
def write_to_file(message):
    with open(filename, 'w') as f:
        f.write(message['value'])


@socketio.on('load_from_db', namespace='/test')
def load_from_db(message):
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute("SELECT * FROM prva WHERE rowid = 1")
    lines = cur.fetchall()
    print(lines)

    emit('load_from_db_response',
         {'data': lines[0]})

    db.close()

@socketio.on('write_to_db', namespace='/test')
def write_to_db(message):
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute("UPDATE prva SET popis = ? WHERE rowid = ?", (message['value'], 1) );
    db.commit()

    db.close()

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
