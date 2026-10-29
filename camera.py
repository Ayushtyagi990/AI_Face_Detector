"""
===========================================
RAJI BABA AI SECURITY CAMERA PRO

Camera Module
===========================================
"""


import cv2
import time
import os
from datetime import datetime
from settings import Settings
from database import create_database,save_person
import numpy as np
import threading
create_database()
class Camera:


    def __init__(self):

        self.camera = None

        self.running = False

        self.frame = None

        self.fps = 0

        self.previous_time = time.time()


        # Create evidence folder

        os.makedirs(
            "evidence",
            exist_ok=True
        )


        # Face detector

        self.face_detector = cv2.CascadeClassifier(

            cv2.data.haarcascades
            +
            "haarcascade_frontalface_default.xml"

        )



    # =====================================
    # START CAMERA
    # =====================================


    def start(self):


        

        settings = Settings()

        camera_id = settings.get("camera_id")

        self.camera=cv2.VideoCapture(camera_id)


        # HD Camera

        self.camera.set(

            cv2.CAP_PROP_FRAME_WIDTH,

            1280

        )


        self.camera.set(

            cv2.CAP_PROP_FRAME_HEIGHT,

            720

        )



        if not self.camera.isOpened():

            print(
                "Camera not available"
            )

            return False



        self.running=True


        return True




    # =====================================
    # GET FRAME
    # =====================================


    def get_frame(self):


        if self.running:


            success, frame = self.camera.read()



            if success:


                self.frame = frame



                self.calculate_fps()



                return frame



        return None





    # =====================================
    # FPS
    # =====================================


    def calculate_fps(self):


        current=time.time()


        difference=current-self.previous_time


        if difference>0:

            self.fps=int(
                1/difference
            )


        self.previous_time=current





    # =====================================
    # FACE DETECTION
    # =====================================


    def detect_faces(self,frame):


        gray=cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2GRAY

        )


        faces=self.face_detector.detectMultiScale(

            gray,

            scaleFactor=1.2,

            minNeighbors=5

        )


        return faces




    # =====================================
    # DRAW FACE BOX
    # =====================================


    def draw_faces(self,frame):


        faces=self.detect_faces(
            frame
        )


        for x,y,w,h in faces:


            cv2.rectangle(

                frame,

                (x,y),

                (x+w,y+h),

                (0,255,0),

                2

            )



            cv2.putText(

                frame,

                "FACE DETECTED",

                (x,y-10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0,255,0),

                2

            )



        return frame, len(faces)





    # =====================================
    # SAVE EVIDENCE
    # =====================================


    def save_evidence(self):


        if self.frame is not None:



            filename=(

                "evidence/"

                +

                datetime.now()
                .strftime(
                "%Y%m%d_%H%M%S"
                )

                +

                ".jpg"

            )



            cv2.imwrite(

                filename,

                self.frame

            )


            return filename



        return None





    # =====================================
    # CAMERA INFO
    # =====================================


    def get_status(self):


        return {


            "camera":

            "ONLINE"
            if self.running
            else
            "OFFLINE",



            "fps":

            self.fps



        }




    # =====================================
    # STOP CAMERA
    # =====================================


    def stop(self):


        self.running=False



        if self.camera:


            self.camera.release()


            self.camera=None