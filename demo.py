import cv2
from deepface import DeepFace
from datetime import datetime
import pyttsx3
import time
import os
import json
import numpy as np
import winsound
import threading
from winotify import Notification

# =========================
# VOICE AI
# =========================

engine = pyttsx3.init()
engine.setProperty("rate",160)

last_voice = 0



def speak(text):

    global last_voice

    if time.time()-last_voice > 8:

        print("AI:",text)

        engine.say(text)

        engine.runAndWait()

        last_voice=time.time()


def show_notification():
    
    toast = Notification(

        app_id="RAJI BABA AI SECURITY",

        title="Face Detected",

        msg="AI Camera detected a person"

    )

    toast.show()
# =========================
# EVIDENCE STORAGE
# =========================

os.makedirs(
    "evidence",
    exist_ok=True
)


LOG_FILE="security_log.json"


if not os.path.exists(LOG_FILE):

    with open(LOG_FILE,"w") as f:
        json.dump([],f)



def save_log(data):

    try:

        with open(LOG_FILE,"r") as f:
            logs=json.load(f)


        logs.append(data)


        with open(LOG_FILE,"w") as f:
            json.dump(
                logs,
                f,
                indent=4
            )

    except Exception as e:

        print("LOG ERROR:",e)


# =========================
# LAPTOP VIBRATION ALERT
# =========================

last_vibration = 0


def vibrate_laptop():

    global last_vibration


    # prevent continuous vibration

    if time.time()-last_vibration < 10:

        return



    def alert():


        for i in range(5):

            # frequency, duration

            winsound.Beep(
                1800,
                300
            )


            time.sleep(0.2)



    threading.Thread(
        target=alert,
        daemon=True
    ).start()



    last_vibration=time.time()

# =========================
# FACE DETECTOR
# =========================


face_detector=cv2.CascadeClassifier(

    cv2.data.haarcascades+
    "haarcascade_frontalface_default.xml"

)


eye_detector=cv2.CascadeClassifier(

    cv2.data.haarcascades+
    "haarcascade_eye.xml"

)



# =========================
# CAMERA
# =========================


camera=cv2.VideoCapture(0)


camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)


camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)



if not camera.isOpened():

    print("Camera not found")
    exit()



speak(
    "Raji Baba AI security camera online"
)



# =========================
# MEMORY
# =========================


age_histories={}


previous_time=time.time()

capture_time=0



# =========================
# MAIN LOOP
# =========================


while True:


    ret,frame=camera.read()


    if not ret:
        break



    current=time.time()


    fps=int(
        1/(current-previous_time)
    )

    previous_time=current



    gray=cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )



    faces=face_detector.detectMultiScale(

        gray,

        scaleFactor=1.2,

        minNeighbors=5

    )



    security_status="SAFE"



    for index,(x,y,w,h) in enumerate(faces):


        if index not in age_histories:

            age_histories[index]=[]



        # add padding around face
        pad = 40

        x1=max(0,x-pad)
        y1=max(0,y-pad)
        x2=min(frame.shape[1],x+w+pad)
        y2=min(frame.shape[0],y+h+pad)


        face_img=frame[y1:y2,x1:x2]



        age=0
        gender="Unknown"
        emotion="Unknown"
        category="Unknown"



        # =====================
        # FACE QUALITY
        # =====================


        brightness=np.mean(face_img)


        if brightness<50:

            quality="Poor"

        elif brightness<120:

            quality="Medium"

        else:

            quality="Good"



        # =====================
        # EYE STATUS
        # =====================


        eyes=eye_detector.detectMultiScale(

            gray[y:y+h,x:x+w]

        )


        if len(eyes)>0:

            eye_status="Open"

        else:

            eye_status="Closed"



        # =====================
        # DEEPFACE AI
        # =====================


        try:


            result=DeepFace.analyze(

                face_img,

                actions=[

                    "age",

                    "gender",

                    "emotion"

                ],

                detector_backend="retinaface",

                enforce_detection=False

            )



            if isinstance(result,list):

                result=result[0]



            current_age=int(
                result["age"]
            )



            age_histories[index].append(
                current_age
            )



            if len(age_histories[index])>30:
                age_histories[index].pop(0)



            age=int(

                sum(age_histories[index])

                /

                len(age_histories[index])

            )



            gender=result[
                "dominant_gender"
            ]



            emotion=result[
                "dominant_emotion"
            ]



            # =====================
            # PERSON CATEGORY
            # =====================


            if age < 13:

                category="Child"


            elif age < 18:

                category="Teen"


            elif gender.lower()=="man":

                category="Man"


            else:

                category="Woman"



            speak(
                f"{category} detected"
            )



        except Exception as e:

            print(
                "DeepFace Error:",
                e
            )



        # =====================
        # DRAW FACE BOX
        # =====================


        cv2.rectangle(

            frame,

            (x,y),

            (x+w,y+h),

            (0,255,0),

            2

        )



        info=[

            f"FACE ID : {index+1}",

            f"TYPE : {category}",

            f"AGE : {age}",

            f"GENDER : {gender}",

            f"MOOD : {emotion}",

            f"EYE : {eye_status}",

            f"QUALITY : {quality}"

        ]



        yy=y-10



        for text in info:


            cv2.putText(

                frame,

                text,

                (x,yy),

                cv2.FONT_HERSHEY_SIMPLEX,

                .55,

                (0,255,0),

                2

            )


            yy-=22



        # =====================
        # SAVE LOG
        # =====================


        save_log({

            "time":
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

            "face_id":
            index+1,

            "age":
            age,

            "gender":
            gender,

            "emotion":
            emotion,

            "category":
            category,

            "quality":
            quality

        })




    # =========================
    # DASHBOARD
    # =========================


    cv2.rectangle(

        frame,

        (0,0),

        (390,170),

        (30,30,30),

        -1

    )



    dashboard=[

        "RAJI BABA AI SECURITY",

        "CAMERA : ONLINE",

        f"FACES : {len(faces)}",

        f"FPS : {fps}",

        f"STATUS : {security_status}",

        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    ]



    y=30


    for d in dashboard:


        cv2.putText(

            frame,

            d,

            (10,y),

            cv2.FONT_HERSHEY_SIMPLEX,

            .65,

            (255,255,255),

            2

        )

        y+=25




    # =========================
    # EVIDENCE IMAGE
    # =========================


    if len(faces)>0:


        if time.time()-capture_time>10:


            filename="evidence/"+datetime.now().strftime(

                "%Y%m%d_%H%M%S.jpg"

            )


            cv2.imwrite(

                filename,

                frame

            )


            capture_time=time.time()




    cv2.imshow(

        "RAJI BABA AI SURVEILLANCE PRO",

        frame

    )



    if cv2.waitKey(1)&0xff==ord("q"):

        break




camera.release()

cv2.destroyAllWindows()
