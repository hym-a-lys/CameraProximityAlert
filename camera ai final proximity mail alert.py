import smtplib
import cv2
import time
import datetime

cap = cv2.VideoCapture(0) #setting up camera, the number 0 denotes the camera being used, 
                          #for multiple cameras, change the number as per devices

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") #CascadeClassifier for faces
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml") #CascadeClassifier for bodies 

#parameter setup
detection = False 
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int(cap.get(4))) #framesize
fourcc = cv2.VideoWriter_fourcc(*"mp4v") #videoformat

while True: #condition
    _, frame = cap.read() #camera starts capturing

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #setting the frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5) #KNN Classifier with K = 5 for faces
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5) #KNN Classifier with K = 5 for body

    if len(faces) + len(bodies) > 0: #condition for recording
        if detection:
            timer_started = False
        else:
            detection = True # changing parameter
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") #date and time when recording started
            out = cv2.VideoWriter(
                f"{current_time}.mp4", fourcc, 20, frame_size) #recording name and fps
            print("Started Recording!") #starting recording
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                #changing all parameters to rest
                detection = False 
                timer_started = False
                out.release() #releasing resources
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    for (x, y, width, height) in faces: #condition for proximity
       cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3) #while safe mode, proximity == far
       if (width*height>22333): #setting condition for proximity = close
           cv2.rectangle(frame, (x,y), (x+width,y+height), (0,0,255), 5) #while unsafe mode, proximity == close
           server = smtplib.SMTP_SSL("smtp.gmail.com", 465) #setting up server, for gmail
           server.login("sender's email here","password here") #email details
           server.sendmail("sender's mail","reciever's mail","camera proximity alert") #mail content
           server.quit() #quit server at the end
           #note: to set up the mail, in google settings, need to select the option that enables messages from unreliable sources
           #note: adviced to change the setting only when using the program

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord('q'): #wait key 'q', note: 'q' with capslock ON won't work as it registers 'Q'
        break #breaking from the infinite loop we set up

out.release() #releasing all resources occupied by the program
cap.release() #releasing all resources occupied by cv module
cv2.destroyAllWindows() #destroying all windows, i.e., camera tab, program tab, etc ...

#code by hym-a-lys