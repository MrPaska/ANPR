import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import datetime
import re
import sys
try:
 img = cv2.imread('C:\\Users\pauli\Downloads\ANPRwithPython-main\ANPRwithPython-main\image5.jpg') # Nuskaito is failo img
 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Spalvos keitimas spalvos kodas: cv2.COLOR_BGR2GRAY
 plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)) # Kovertuojams per koda cv2.COLOR_BGR2RGB i RGB, nes matplotlib reikia RGB
 plt.show() # img rodimas naudojant matplotlib
except:
    print("KLAIDA! Negauta Nuotrauka...")
    sys.exit(1)

bfiler = cv2.bilateralFilter(gray, 11, 17, 17) # Triuksmo mazinimas padaro img svaresne, dailesne; islyginimo parametrai: 11, 17, 17
edged = cv2.Canny(bfiler, 30, 200) # Krastu aptikimas(is img krastu istraukimas)
plt.imshow(cv2.cvtColor(edged, cv2.COLOR_BGR2RGB))
plt.show()

keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # suranda konturus(figura); TREE grazina ivairaus lygio konturus; CHAIN sudeda taskus tik ant figuros kampu(galu)
contours = imutils.grab_contours(keypoints) # paima konturus
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10] # surusiuoja konturus pagal konturo plota(key=cv2.contourArea), mazejanciai(revesre=True), grazina 10 didziausiu konturu

location = None
try:
 for contour in contours: # is konturu saraso "contours"
    approx = cv2.approxPolyDP(contour, 5, True) # sudaro apytikslio daugiakampio koordinates(pasiima konturu sarasa; is kiek tasku gali but sudarytas(max))
    if len(approx) == 4: # jei taskai 4 tai greiciausiai numeriu remelis
        location = approx
        break # loop end
except:
    print("KLAIDA! Numeris nerastas...")
    sys.exit(1)
print(location)

mask = np.zeros(gray.shape, np.uint8) # sukuriama matrica su 0 reiksmem(np.uint8) same formos kaip gray img(gray.shape)
new_image = cv2.drawContours(mask, [location], 0, 255, -1) # piesiami konturai pagal numeriu remelius; mask(blank img);[location](numeriu remeliu kampu koordinates); Parametrai draw
new_image = cv2.bitwise_and(img, img, mask=mask) # ant org img uzdedamas mask
plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
plt.show()

(x,y) = np.where(mask == 255) # kintamieji remeliu pozicijai
(x1, y1) = (np.min(x), np.min(y)) # min x, y
(x2, y2) = (np.max(x), np.max(y)) # max x, y
cropped_image = gray[x1:x2+1, y1:y2+1] # sucropinama is gray img; +1 kad susvelninti pacius remus
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
text = re.sub(pattern, '', text) # panaikina rasta - (\W) is "text"

if len(text) != 0:
   print("****************************")
   print("VALSTYBINIS NUMERIS: " + text)
   print("****************************")

else:
  print(">>>NUMERIS NERASTAS<<<")

raides = "".join(re.split("[^a-zA-Z]*", text)) # splitina i raides nuo a-z ir A-Z
skaiciai = "".join(re.split("[^0-9]*", text)) # splitina i skaicius nuo 0-9
print ("# Raidės:", str(raides))
print ("# Skaičiai:", str(skaiciai))
print("****************************")

if len(raides) == 3 and len(skaiciai) == 3:

    print("--LIETUVOS RESPUBLIKA--")
    print(">>>NUMERIS TINKA<<<")
    print("****************************")

    date = datetime.datetime.now() # data laikas now
    f = open("LT_Numeriai.txt", "a") # atidaromas failas txt
    f.write(str(text)) # irasomi numeriai
    f.write("|" + str(date)) # irasoma data kada nuskaityti numeriai
    f.write("\n")
    f.close() # failo uzdarymas

    font = cv2.FONT_HERSHEY_SIMPLEX # sriftas
    res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                      color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA) # paskutinej img rodamas "text"; jo vieta sriftas; srifto dydis; spalva linijos storis ir tipas
    res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3) # numeriai apibreziami staciakampiu; kampu kordinates; spalva; linijos storis
    plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
    plt.show()

elif len(raides) == 2 and len(skaiciai) == 4:

    print("--LIETUVOS RESPUBLIKA--")
    print("--ELEKTROMOBILIS--")
    print(">>>NUMERIS TINKA<<<")
    print("****************************")

    date = datetime.datetime.now()
    f = open("LT_Numeriai.txt", "a")
    f.write(str(text))
    f.write("|" + str(date))
    f.write("\n")
    f.close()

    font = cv2.FONT_HERSHEY_SIMPLEX
    res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                      color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
    plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
    plt.show()

else:
    print("--NE LIETUVOS RESPUBLIKA--")
    print(">>>NUMERIS NETINKA<<<")
    date = datetime.datetime.now()
    f = open("Ne_LT_Numeriai.txt", "a")
    f.write(str(text))
    f.write("|" + str(date))
    f.write("\n")
    f.close()

    font = cv2.FONT_HERSHEY_SIMPLEX
    res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                      color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)
    plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
    plt.show()



