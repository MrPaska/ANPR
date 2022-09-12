import tkinter as tk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
from tkinter import PhotoImage
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import datetime
import re
import back_end as bck
import mysql.connector as mariadb
import sys


try:
    conn = mariadb.connect(
            user="root",
            password="",
            host="localhost",
            port=3306,
            database = "number_plate_recognition") # db connectionas
    print("Database connection successful...")
except mariadb.Error as e:
    print("Error connecting to MariaDB Platform: {e}")
    sys.exit(1) # isejimas is programos su erroru

cur = conn.cursor()

root = Tk() # sukuriamas root(pagrindinis) langas
root.geometry('900x700') # lango dydis
root.title('Number Plate Recognition System') # lango pavadinimas
root.configure(background='#29313A') # root bacground spalva
text = Label(root, text="NUMBER PLATE RECOGNITION SYSTEM", foreground='white', background='#29313A', font=('verdana',22,'bold')) # etike ir jos spalvos, sriftas
text.place(x=145,y=50) # etiketes vieta
number_plate = Label(root, background='#29313A', font=('verdana',15,'bold'))
info = Label(root, background='#29313A', font=('verdana',11,'bold'))
sign_image = Label(root, bd=10) # etike img vietai

def classify(file_path):

    img = cv2.imread(file_path) # Nuskaito is pasirinkto failo img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Spalvos keitimas spalvos kodas: cv2.COLOR_BGR2GRAY
    plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)) # Kovertuojamas per koda cv2.COLOR_BGR2RGB i RGB, nes matplotlib reikia RGB
    plt.show() # img rodimas naudojant matplotlib


    bfiler = cv2.bilateralFilter(gray, 11, 17, 17) # Triuksmo mazinimas padaro img svaresne, dailesne; islyginimo parametrai: 11, 17, 17
    edged = cv2.Canny(bfiler, 30, 200) # Krastu aptikimas(is img krastu istraukimas)
    plt.imshow(cv2.cvtColor(edged, cv2.COLOR_BGR2RGB))
    plt.show()

    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Suranda konturus(figura); TREE grazina ivairaus lygio konturus; CHAIN sudeda taskus tik ant figuros kampu(galu)
    contours = imutils.grab_contours(keypoints) # Paima konturus
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10] # Surusiuoja konturus pagal konturo plota(key=cv2.contourArea), mazejanciai(revesre=True), grazina 10 didziausiu konturu

    location = None
    try:
     for contour in contours: # Is konturu saraso "contours"
        approx = cv2.approxPolyDP(contour, 5, True) # Sudaro apytikslio daugiakampio koordinates(pasiima konturu sarasa; is kiek tasku gali but sudarytas(max))
        if len(approx) == 4: # jei taskai 4 tai greiciausiai numeriu remelis
            location = approx
            break # loop end
    except:
       print("KLAIDA! Numeris nerastas...")
       sys.exit(1)

    print(location)

    mask = np.zeros(gray.shape, np.uint8) # Sukuriama matrica su 0 reiksmem(np.uint8) same formos kaip gray img(gray.shape)
    new_image = cv2.drawContours(mask, [location], 0, 255, -1) # Piesiami konturai pagal numeriu remelius; mask(blank img);[location](numeriu remeliu kampu koordinates); Parametrai draw
    new_image = cv2.bitwise_and(img, img, mask=mask) # Ant org img uzdedamas mask
    plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
    plt.show()

    (x, y) = np.where(mask == 255) # Kintamieji remeliu pozicijai
    (x1, y1) = (np.min(x), np.min(y)) # min x, y
    (x2, y2) = (np.max(x), np.max(y)) # max x, y
    cropped_image = gray[x1:x2 + 1, y1:y2 + 1] # Sucropinama is gray img; +1 kad susvelninti pacius remus
    plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    plt.show()

    reader = easyocr.Reader(['en']) # aprasomas readeris ir jo readinimo kalba
    result = reader.readtext(cropped_image) # skaitomas tekstas is croppped_image
    print(result)

    if len(result[0][-2]) == 3:

        text = result[0][-2] + result[1][-2]

    else:
        text = result[0][-2]

    pattern = re.compile('\W') # \W(Atitinka bet kurį simbolį, kuris nėra žodžio simbolis(,./\;:))
    text = re.sub(pattern, '', text) # Panaikina rasta - (\W) is "text"

    if len(text) != 0:
        print("****************************")
        print("VALSTYBINIS NUMERIS: " + text)
        print("****************************")
        number_plate.configure(foreground='white', text= "VALSTYBINIS NUMERIS: " + text)

    else:
        print(">>>NUMERIS NERASTAS<<<")
        info.configure(foreground='white', text="NUMERIS NERASTAS\n")
    raides = "".join(re.split("[^a-zA-Z]*", text)) # Splitina i raides nuo a-z ir A-Z
    skaiciai = "".join(re.split("[^0-9]*", text)) # Splitina i skaicius nuo 0-9
    print("# Raidės:", str(raides))
    print("# Skaičiai:", str(skaiciai))
    print("****************************")

    if len(raides) == 3 and len(skaiciai) == 3:

        print("--LIETUVOS RESPUBLIKA--")
        print(">>>NUMERIS TINKA<<<")
        print("****************************")
        info.configure(foreground='white', text="--LIETUVOS RESPUBLIKA--\n\n>>>NUMERIS TINKA<<<")
        try:
          date = datetime.datetime.now() # Data laikas now
          my_sql = 'INSERT INTO lt_numeriai (Numeris, Data_Laikas) VALUES (%s, %s)'; # Duomenu iterpimo sakinys i lentele; %s(rodo, jog bus iterpiamas parametras)
          insert = (text, date) # Kintamieji kuriuos norime iterpti
          cur.execute(my_sql, insert) # Vykdo iterpima
          conn.commit(); # Issaugo irasa
          print("Duomenis įrašyti sėkmingai..")
        except:
           print("Nepavyko įrašyti duomenų...")

        font = cv2.FONT_HERSHEY_SIMPLEX # Sriftas
        res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                          color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA) # Paskutinej img rodamas "text"; jo vieta sriftas; srifto dydis; spalva linijos storis ir tipas
        res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3) # Numeriai apibreziami staciakampiu; kampu kordinates; spalva; linijos storis
        plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
        plt.show()

    elif len(raides) == 2 and len(skaiciai) == 4:

        print("--LIETUVOS RESPUBLIKA--")
        print("--ELEKTROMOBILIS--")
        print(">>>NUMERIS TINKA<<<")
        print("****************************")
        info.configure(foreground='white', text="--LIETUVOS RESPUBLIKA--\n\n--ELEKTROMOBILIS--\n\n>>>NUMERIS TINKA<<<")
        date = datetime.datetime.now()
        try:
          date = datetime.datetime.now()
          my_sql = 'INSERT INTO lt_numeriai (Numeris, Data_Laikas) VALUES (%s, %s)';
          insert = (text, date)
          cur.execute(my_sql, insert)
          conn.commit();
          print("Duomenis įrašyti sėkmingai..")
        except:
           print("Nepavyko įrašyti duomenų...")

        font = cv2.FONT_HERSHEY_SIMPLEX
        res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                          color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
        plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
        plt.show()

    else:
        print("--NE LIETUVOS RESPUBLIKA--")
        print(">>>NUMERIS NETINKA<<<")
        info.configure(foreground='white', text="--NE LIETUVOS RESPUBLIKA--\n\n>>>NUMERIS NETINKA<<<")
        date = datetime.datetime.now()
        try:
          date = datetime.datetime.now()
          my_sql = 'INSERT INTO ne_lt_numeriai (Numeris, Data_Laikas) VALUES (%s, %s)';
          insert = (text, date);
          cur.execute(my_sql, insert)
          conn.commit();
          print("Duomenis įrašyti sėkmingai..")
        except:
           print("---Klaida! Nepavyko įrašyti duomenų--")
           sys.exit(1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                          color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
        plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
        plt.show()

def show_classify_button(file_path):
    classify_btn = Button(text="Classify Image", command=lambda: classify(file_path), padx=10, pady=5) # Sukuriamas "classifyImage" mygtukas; lambda(anonimine funkcija)
    classify_btn.configure(background='#29313A', foreground='white',font=('verdana',12,'bold'))
    classify_btn.pack() # "pack" priskiria ir rezervuoja vieta butent tik sitam mygtukui
    classify_btn.place(x=490,y=550)

def uploadImage():
  try:
    file_path = filedialog.askopenfilename(initialdir="/", title="Select An Image", filetypes=(("jpeg files", "*.jpg"), ("gif files", "*.gif*"), ("png files", "*.png"))) # Leidzia pasirinkti img initialdir(Pradinis katalogas)
    uploaded = Image.open(file_path) # Uploadinamas img is file_path
    uploaded.thumbnail(((root.winfo_width() / 2.25), (root.winfo_height() / 2.25))) # Thumbnail naudojas dydziui img aprasyti winfo_width(root lango plotis)
    im = ImageTk.PhotoImage(uploaded) # img apdorojimas - vaizdavimas
    sign_image.configure(image=im) # sing_image langui priskiriamas org img dydis
    info.configure(text='')
    number_plate.configure(text='')
    sign_image.image=im # img idedamas i jei skirta vieta
    show_classify_button(file_path)
  except:
    print("---Klaida! Negauta nuotrauka--")
    sys.exit(1)
upload = Button(text="Upload an image", command=uploadImage, padx=10, pady=5) # "Upload an image" mygtukas
upload.configure(background='#29313A', foreground='white',font=('verdana',12,'bold'))
upload.pack()
upload.place(x=210,y=550)

sign_image.pack()
sign_image.place(x=70,y=200)

number_plate.pack()
number_plate.place(x=500,y=250)

info.pack()
info.place(x=550,y=300)

root.mainloop() # Metodas tesias amzinai, laukdamas ivykiu is vartotojo, kol vartotojas iseis is programos ir t.t.




