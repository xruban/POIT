from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import math
import serial.tools.list_ports

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

def background_thread(args):
    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    portList = []

    for onePort in ports:
        portList.append(str(onePort))

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
        if serialInst.in_waiting:
            packet = serialInst.readline()
            print(packet.decode('utf'))
            print(args)
            socketio.sleep(2)
            count = packet.decode('utf')
            premS = float(count)
            premC = 4
            dataDict = {
                "t": time.time(),
                "x": count,
                "y": premS,
                "z": premC}
            dataList.append(dataDict)
            socketio.emit('my_response',
                          {'dataSin': premS, 'dataCos': premC, 'count': count},
                          namespace='/test')


def background_thread_cv8(args):
    count = 0    
    dataList = []          
    while True:
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
          sliderV = dict(args).get('slider_value')
        else:
          A = 1
          btnV = 'null' 
          sliderV = 0 
        print(args)  
        socketio.sleep(2)
        count += 1
        premS = math.sin(count)
        premC = math.cos(count)
        dataDict = {
          "t": time.time(),
          "x": count,
          "y": float(A)*premS,
          "z": float(A)*premC}
        dataList.append(dataDict)
        socketio.emit('my_response',
                      {'dataSin': float(A)*premS, 'dataCos': float(A)*premC, 'count': count},
                      namespace='/test')  

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
       
@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)
      
@socketio.on('my_event', namespace='/test')
def test_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})
 
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

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('slider_event', namespace='/test')
def slider_message(message):  
    #print(message['value'])   
    session['slider_value'] = message['value']  

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
