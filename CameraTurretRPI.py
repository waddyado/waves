import cv2, imutils, socket
import numpy as np
import time
import base64
import threading
#import RPi.GPIO as GPIO

def recieve_commands():
        '''
        GPIO.setwarnings(False)
        GPIO.setup(18,GPIO.OUT)
        x = GPIO.PWM(27, 50)
        y = GPIO.PWM(22, 50)
        '''
        connected = True
        ADDR = ('192.168.2.72',5000)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f'[INFO] Listening on {ADDR[0]}:{ADDR[1]}\n')
        print(f'[WAITING] Waiting for connections...\n')
        conn, addr = server.accept()
        
        with conn:
                print(f'Connected to {addr[0]}')
                while True:
                        msg = conn.recv(1024).decode('utf-8')
                        if msg == 'Up':
                                print('Up')
                                
                        elif msg == 'Down':
                                print('Down')
                                
                        elif msg == 'Right':
                                print('Right')
                                
                        elif msg == 'Left':
                                print('Left')
                                
                        elif msg == 'Enter':
                                print('Enter')
                        
                        
def video_stream():


        visual = False
        BUFF_SIZE = 65536
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        host_name = socket.gethostname()
        hostip = '192.168.2.72'   #socket.gethostbyname(host_name)
        port = 5001
        host_addr = (hostip, port)
        


        vid = cv2.VideoCapture(0)
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
