import sqlite3
from datetime import datetime
from database import create_database,save_person

DB_NAME="security_camera.db"



def create_database():

    conn=sqlite3.connect(DB_NAME)

    cursor=conn.cursor()


    cursor.execute("""

    CREATE TABLE IF NOT EXISTS detected_persons(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        detect_time TEXT,

        face_id INTEGER,

        age INTEGER,

        gender TEXT,

        emotion TEXT,

        category TEXT,

        quality TEXT,

        image_path TEXT,

        camera_name TEXT

    )

    """)


    conn.commit()

    conn.close()



def save_person(
        face_id,
        age,
        gender,
        emotion,
        category,
        quality,
        image_path
):


    conn=sqlite3.connect(DB_NAME)

    cursor=conn.cursor()



    cursor.execute("""

    INSERT INTO detected_persons(

        detect_time,
        face_id,
        age,
        gender,
        emotion,
        category,
        quality,
        image_path,
        camera_name

    )

    VALUES(?,?,?,?,?,?,?,?,?)

    """,

    (

    datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    ),

    face_id,

    age,

    gender,

    emotion,

    category,

    quality,

    image_path,

    "RAJI BABA AI CAMERA"

    ))



    conn.commit()

    conn.close()