import cv2, imutils, socket
import numpy as np
import time
import base64
import threading
import RPi.GPIO as GPIO

def recieve_commands():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(22,GPIO.OUT)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        trigger = True
        connected = True
        ADDR = ('192.168.2.161',5000)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f'[INFO] Listening on {ADDR[0]}:{ADDR[1]}\n')
        print(f'[WAITING] Waiting for connections...\n')
        conn, addr = server.accept()
        duty_cyclex = 5
        duty_cycley = 5
        p = GPIO.PWM(17, 50) # GPIO 17 for PWM with 50Hz
        p.start(2.5) # Initialization
        p2 = GPIO.PWM(27, 50)
        p2.start(2.5)
        p2.ChangeDutyCycle(duty_cycley)
        p.ChangeDutyCycle(duty_cyclex)
        with conn:
                print(f'Connected to {addr[0]}')
                while True:
                        p2.ChangeDutyCycle(duty_cycley)
                        p.ChangeDutyCycle(duty_cyclex)
                        msg = conn.recv(1024).decode('utf-8')
                        if msg == 'Up':
                                print('Up')
                                duty_cycley -= 0.75
                                if duty_cycley < 1:
                                        duty_cycley = 1
                                p2.ChangeDutyCycle(duty_cycley)
                        elif msg == 'Down':
                                print('Down')
                                duty_cycley += 0.75
                                if duty_cycley > 10:
                                   duty_cycley = 10
                                p2.ChangeDutyCycle(duty_cycley)
                        elif msg == 'Right':
                                print('Right')
                                duty_cyclex -= 0.75
                                if duty_cyclex < 1:
                                   duty_cyclex = 1
                                p.ChangeDutyCycle(duty_cyclex)
                        elif msg == 'Left':
                                print('Left')
                                duty_cyclex += 0.75
                                if duty_cyclex > 10:
                                   duty_cyclex = 10
                                p.ChangeDutyCycle(duty_cyclex)
                        elif msg == 'Enter':
                                print('Enter')
                                if trigger == True:
                                   GPIO.output(22,GPIO.LOW)
                                   trigger = False
                                elif trigger == False:
                                   GPIO.output(22,GPIO.HIGH)
                                   trigger = True
def video_stream():


        visual = False
        BUFF_SIZE = 65536
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        host_name = socket.gethostname()
        hostip = '192.168.2.72'   #socket.gethostbyname(host_name)
        port = 5001
        host_addr = (hostip, port)



        vid = cv2.VideoCapture(-1)
        fps,st,frames_to_count,cnt = (0,0,20,0)
        print(f'[STARTED] Transmitting Video to {hostip}...')


        while True:
                    WIDTH=400
                    while(vid.isOpened()):
                        _,frame = vid.read()
                        frame = imutils.resize(frame,width=WIDTH)
                        encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                        message = base64.b64encode(buffer)
                        client_socket.sendto(message,host_addr)
                        frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                        if visual == True:
                                cv2.imshow('Video Stream',frame)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                                client_socket.close()
                                break
                        if cnt == frames_to_count:
                                try:
                                        fps = round(frames_to_count/(time.time()-st))
                                        st=time.time()
                                        cnt=0
                                except:
                                        pass
                        cnt+=1


t1 = threading.Thread(target=video_stream)
t1.start()

t2 = threading.Thread(target=recieve_commands)
t2.start()

