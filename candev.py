from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import cv2
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
from pytesseract import Output
import imutils
from tqdm import tqdm
import os


def extract_csv(src_path):
    
    year_list = [str(i) for i in range(2018,2050)]
    
    doc = convert_from_path(src_path,poppler_path=r'\app\vendor\poppler-0.1.0\bin')
    a = 0
    
    try:
        os.mkdir('images')
        os.mkdir('static/output_csv')
    except:
        pass
    
    f_name = os.path.basename(src_path).split('.')[0]
        
    for page in tqdm(doc):
        
        im_path = os.path.join('images',f"{f_name}_page_{a}.jpg" )
        page.save(im_path, "JPEG")
        
        image = cv2.imread(im_path)
        
        rotated = pytesseract.image_to_osd(im_path,config='--psm 0 -c min_characters_to_try=5',output_type=pytesseract.Output.DICT)

        image = imutils.rotate_bound(image, angle=rotated["rotate"])

        flag = False
        if rotated['rotate'] != 0:
            flag = True

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9,9), 0)
        thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
        dilate = cv2.dilate(thresh, kernel, iterations=4)

        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]

        line_items_coordinates = []
        for c in contours:
            area = cv2.contourArea(c)
            x,y,w,h = cv2.boundingRect(c)
            
            if flag:
                if y >= 50 and x <= 400 :
                    if area > 10000:
                        image = cv2.rectangle(image, (x,y), (2100, y+h), color=(255,0,255), thickness=3)
                        line_items_coordinates.append([(x,y), (2100, y+h)])
            else:
                if y >= 50 and x <= 400 :
                    if area > 10000:
                        image = cv2.rectangle(image, (x,y), (1600, y+h), color=(255,0,255), thickness=3)
                        line_items_coordinates.append([(x,y), (1600, y+h)])

        line_items_coordinates.reverse()
        
        txt=[]

        for c in line_items_coordinates:
  
            img = image[c[0][1]:c[1][1], c[0][0]:c[1][0]] 

            ret,thresh1 = cv2.threshold(img,120,255,cv2.THRESH_BINARY)

            text = str(pytesseract.image_to_string(thresh1, config='--psm 6',lang='eng'))
            if flag:
                text = re.sub('[^A-Za-z0-9\n\- ()%]+', '', text)
            else:
                text = re.sub('[^A-Za-z0-9\n\- ()%.]+', '', text)
            txt.append(text)
            
            c = 0
            d = 0
            for i in text.split('\n'):
                for j in i.split('\n'):
                    for k in j.split():
                        if k.isalpha():
                            c+=1
                        if k.isdigit():
                            d+=1
                            
            if c>25 and d<4:
                txt.pop(-1) 
            

        d = {}
        f = 0
        for t in txt:
            for i in t.split('\n'):
                
                j = i.split()
                j.insert(0,' ')
                j.append(' ')
                x = j.copy()
                
                if '-' in j:
                    idx = j.index('-')
                    
                    if len(set(j)) == 2 and j[1] == '-':
                        continue
                    
                    if j[idx-1].isalpha() and j[idx+1].isalpha(): 
                        j.pop(idx)
                        j.pop(0)
                        j.pop(-1)
                        
                    else:
                        j = i.split()
                        
                else:
                    j = i.split()
                
                strings = []
                dig = []
                
        
                
                for k in j:
                    
                    if k.isalpha() == True:
                        strings.append(k) 
                        
                    elif k.isdigit() == True:
                        if int(k)>100 and k not in year_list:
                            dig.append(k)
                        else:
                            strings.append(k)
                            
                    elif k == '-':
                        dig.append(k)
                       
                            
                    elif k[0] == '(' and k[-1] == ')':
                        if re.sub('[()]','',k).isdigit():
                            dig.append(str(int(k[1:-1])*-1))
                        else:
                            strings.append(k)
                            
                    else:
                        strings.append(k)
                
                
                
                if len(strings)!= 0:      
                    key = ' '.join(strings)
                    
                    if key.split()[0] in year_list:
                        dig = key.split()
                        key = 'Year:'
                        
                    if key.split()[0] == 'Budget' or key.split()[0] == 'Actual' :
                        dig = key.split()
                        key = ' '
                        
                    if key.isupper()==True and len(dig)==0:
                        key='TITLE: '+key
                        
                    if key in d:
                        key = key + ' '
                    
                    if (len(set(dig)) == 1 and dig[0] == '-') or (key[0] =='a' and len(set(key))==1):
                        continue
                        
                    d[key] = dig
                    
                elif len(dig)!= 0:
                    key = ' '.join(strings)
                    f+=1
                    if key in d:
                        key = key + (' ')*f
                        
                    if (len(set(dig)) == 1 and dig[0] == '-') :
                        continue
                        
                    d[key] = dig
    

        df = pd.DataFrame.from_dict(d, orient='index').fillna('')
        
        dest_path = os.path.join('static','output_csv', f"{f_name}_page_{a}.csv")
        a+=1 
        if len(df.columns) == 0:
            df = pd.DataFrame()
            continue
        else:
            df.to_csv(dest_path)

if __name__ == '__main__':
    extract_csv()