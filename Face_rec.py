# -*- coding: utf-8 -*-
#Required Libraries for program
import argparse
import face_recognition
import cv2
import requests
import re
import numpy
import time
import json
import os
import time
import unicodedata
from bs4 import BeautifulSoup
from bottle import get, post, request,run, static_file,route,redirect

#A simple asciify fixer
def py_asciify(text):
    return unicodedata.normalize('NFKD', text.replace(u'\u0131', 'i').replace(u')', '\)').replace(u'(', '\(')).encode('ascii', 'ignore').lower().decode('utf8')


# variables
face_locations = []
face_names = []
name_tags = []
ff_encod = []
main_image = ""
## dictionary
g_dict = {}

def create_sub(url):
    pagetemp = requests.get(url)
    page = pagetemp.content
  #  global soup
    soup = BeautifulSoup(page,"html.parser")
    print( "create_sub done")
    return soup

""" Take soup input and create Twitter name tags from it
    Save name tags to name_tags[] list ArgumentParser
"""
def create_tags(soup):
    global name_tags
    name_tags = soup.select(".name span")
    for i in range(0, len(name_tags)):
        name_tags[i] = name_tags[i].string
        name_tags[i] = name_tags[i][name_tags[i].find("(")+2:name_tags[i].find(")")]
    print( "create_tags done")

""" Create Main dictionary with using name_tags,
    keys are the name_tags like {"cmylmz": {"1","2","3"}, ...}
"""
def create_dict():
    global g_dict
    for i in name_tags:
        if not i in g_dict:
            g_dict[i] = {}
        g_dict[i]["twit"] = "twitter.com/" + i
    print( "create_dict done")

""" Add people name's to g_dict (main dictionary)
    it get's names from soup
"""
def add_names(soup):
    l = soup.select(".name > .item > .acc-placeholder-img img")
    names = [i.attrs['alt'] for i in l]
    for i in range(0,len(names)):
        g_dict[name_tags[i]]["name"] = names[i]
    print( "add_names done")

""" Add followers data to g_dict
    it get's data from soup
"""
def add_followers(soup):
    followers = soup.select(".brand-table-list strong")
    for i in range(0,len(followers)):
        followers[i] = followers[i].get_text().strip().replace('\xa0','')
        g_dict[name_tags[i]]["followers"] = followers[i]
    print("add_followers done")

""" Create Images file if it's not exists
    Create 5 jpg file for each person
    It search bing for images, download it then write it to according jpg file
    jpg file names and image link urls are saved to g_dict
    time.sleep() is important to not banned from website
"""
def create_image_links():
    if not os.path.exists("images"):
        os.makedirs("images")
    t_start = time.time()
    bing_url1 = "https://www.bing.com/images/search?view=detailV2&q="
    bing_url3 = "&selectedIndex=0&qft=+filterui%3aimagesize-large&ajaxhist=0"
    user_agent = {'User-agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))'}
    for i in g_dict:
        if not os.path.isfile(os.path.join("images", i + "1.jpg")):
            t_t = bing_url1 +  g_dict[i]["name"] + bing_url3
            response = requests.get(t_t, headers=user_agent)
            g_dict[i]["get_links"] = response.url
        #    print(g_dict[i]["get_links"] + "  " + g_dict[i]["name"])
            print( g_dict[i]["name"])
            time.sleep(3)
            t_image = re.compile('<div class="item"><a class="thumb" target="_blank" href="([^"]*)"').findall(response.text)
            if (t_image and len(t_image) > 4):
                g_dict[i]["image_links"] = [t_image[0],t_image[1],t_image[2],t_image[3],t_image[4]]
                g_dict[i]["names_jpg"] = [i+"1.jpg",i+"2.jpg",i+"3.jpg",i+"4.jpg",i+"5.jpg" ]
            #    print(g_dict[i]["image_links"] + "   " + g_dict[i]["name"])
                for k in range(0,5):
                    try :
                        imgresponse = requests.get(g_dict[i]["image_links"][k], stream=True)
                        if not os.path.exists(os.path.join("images", g_dict[i]["names_jpg"][k])):
                            with open(os.path.join("images", g_dict[i]["names_jpg"][k]), 'wb') as out_file:
                                out_file.write(imgresponse.content)
                    except:
                        pass
    print("create_image_links done in %d" % (time.time() - t_start))

"""
    It fill images to i_dict[] with using face_recognition load_image_file function
    then it returns i_dict
"""
def fill_images():
    i_dict = {}
    for i in g_dict:
        i_dict[i] = []
        if "names_jpg" in g_dict[i]:
            for j in  g_dict[i]["names_jpg"]:
                try:
                    i_dict[i].append(face_recognition.load_image_file(os.path.join("images",j)))
                except :
                    pass
    print("fill_images done")
    return i_dict


""" It fill image encodings to g_dict, image encodings will be used for face_recognition algorithms
    It takes images dictionary to create image encodings from it
"""
def create_image_encodings(i_dict):
    for i in i_dict.keys():
        l =[]
        for j in i_dict[i]:
            f_l = face_recognition.face_locations(j)
            if f_l:
                l.append(face_recognition.face_encodings(j,f_l)[0].tolist())
        if len(l) >0:
            g_dict[i]["image_encodings"] = l
        print(i)
    print("create_image_encodings done")

""" Write g_dict dictionary to dump.json
"""
def fill_json():
    f = open("dump.json", "w")
    global g_dict
    json.dump(g_dict, f, indent=2, sort_keys=True)
    f.close()
    print("fill_json done")

""" Load dump.json json data to g_dict dictionary
"""
def load_json():
    if( os.path.exists("./dump.json")):
        f = open("dump.json")
        global g_dict
        g_dict = json.load(f)
        f.close()
        print("load_json done")

""" This function is used for questioning
    It take a jpg url string then it download image
    with using face recognition library it find faces from given image and encode them
    After this process, it compare image encodings with database encodings(g_dict)
    then if it find a match it write name(it get name from g_dict)
"""
def query_image(url):
    #url den gelen resim
    response = requests.get( url, stream = True)
    with open("query.jpg", 'wb') as out_file:
        out_file.write(response.content)
    del response
    global main_image
    Rmain_image = face_recognition.load_image_file("query.jpg")
    main_image = cv2.cvtColor(Rmain_image, cv2.COLOR_BGR2RGB)
    global face_locations
    global face_names
    face_locations = face_recognition.face_locations(main_image)
    face_encodings = face_recognition.face_encodings(main_image, face_locations)
    face_names = []
    for faces_from_main_image in face_encodings:
        name = "Unknown"
        print(len(face_encodings))
        print(g_dict.keys())
        for i in g_dict:
            print(i)
            if "image_encodings" in g_dict[i]:
                matchs = face_recognition.compare_faces( [numpy.array(g_dict[i]['image_encodings'])], faces_from_main_image)
                #bool listesinden true d�nenin name ni ekliyor
                if matchs[0] == True:
                    name = i
                    #print(name + "---" + faces_from_main_image)
        face_names.append(name)
    print("query_image done")
""" It prints the image with names appended to it
"""
def show_image():
    for (top, right, bottom, left), name in zip(face_locations, face_names):

        #Draw the rec around face
        cv2.rectangle(main_image, (left,top), (right,bottom), (0,0,255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(main_image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(main_image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Imagek', main_image)
    cv2.waitKey(0)
    print("show_image done")
""" this function do the same job with query_image in basics but it written for bottle(server).
    it also save image details to h_dict dictionary and returns it
"""

def bottle_query(url):
    #url den gelen resim
    response = requests.get( url, stream = True)
    query_name = str(time.time()) + ".jpg"

    if not os.path.exists("query.images"):
        os.makedirs("query.images")

    with open(os.path.join("query.images", query_name), 'wb') as out_file:
        out_file.write(response.content)
    del response

    global main_image

    Rmain_image = face_recognition.load_image_file( os.path.join("query.images", query_name) )
    main_image = cv2.cvtColor(Rmain_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(main_image)
    face_encodings = face_recognition.face_encodings(main_image, face_locations)
    face_names = []
    for faces_from_main_image in face_encodings:
        name = "Unknown"
        #print(len(face_encodings))
        #print(g_dict.keys())
        l = 1
        for i in g_dict:
            #print(i)
            if "image_encodings" in g_dict[i]:
                for k in g_dict[i]["image_encodings"]:
                    #matchs = face_recognition.compare_faces( [numpy.array(g_dict[i]['image_encodings'])], faces_from_main_image)
                    if (face_recognition.face_distance([numpy.array(k)], faces_from_main_image)) < l:
                        l = (face_recognition.face_distance([numpy.array(k)], faces_from_main_image))
                        name = g_dict[i]["name"]
                    #bool listesinden true d�nenin name ni ekliyor
                    """if matchs[0] == True:
                        name = i"""
                        #print(name + "---" + faces_from_main_image)
        print(str(l) + " " + name)
        if l < 0.6:
            face_names.append(name)
        else:
            face_names.append("Unknown")

    h_dict = {}
    datas =[]
    for i in range(0,len(face_locations)):
        datas.append(face_locations[i] + (face_names[i],))
    h_dict["data"] = datas
    h_dict["image"] = query_name
    img = cv2.imread(os.path.join("query.images", query_name))
    height, width, channels = img.shape
    h_dict["width"] = width
    h_dict["height"] = height
    print(h_dict)
    return bottle_show_image(h_dict)
""" it show image with names appended it but it resize rectangle around faces and text size
"""
def bottle_show_image(h_dict):
    for (top, right, bottom, left, name) in h_dict["data"]:
        name = py_asciify(name)
        resize = 1
        font = cv2.FONT_HERSHEY_DUPLEX
        p_h = (bottom-top)/3
        p_w = (right - left)
        t_h = cv2.getTextSize(name, font, 1, 1)[0][1]
        t_w = cv2.getTextSize(name, font, 1, 1)[0][0]

        if p_h < t_h:
            resize = p_h /t_h
        if p_w > t_w:
            resize = p_w / t_w
        #Draw the rec around face
        cv2.rectangle(main_image, (left,top), (right,bottom), (0,0,255), 2)
        # Draw a label with a name below the face
        cv2.rectangle(main_image, (left, bottom + int((bottom - top)/3)), (right, bottom), (0, 0, 255), cv2.FILLED)

        cv2.putText(main_image, name, (left, bottom + int((bottom - top)/3) -1), font, resize, (255, 255, 255), 1)

    final_img = str(time.time()) + ".jpg"
    if not os.path.exists("final.images"):
        os.makedirs("final.images")

    cv2.imwrite(os.path.join("final.images", final_img) ,main_image)
    #return final_img
    return static_file(os.path.join("final.images", final_img), root='./')
""" This function is used for the add new person to data base
    with your friend photo and name you can add it to g_dict database
"""
def add_a_personn(url,name):
    di = str(time.time())
    g_dict[di] ={}
    g_dict[di]["name"] = name
    g_dict[di]["image_links"] = url

    try :
        imgresponse = requests.get(url, stream=True)
        if not os.path.exists(os.path.join("images", di +".jpg")):
            with open(os.path.join("images", di +".jpg"), 'wb') as out_file:
                out_file.write(imgresponse.content)
    except:
        pass

    try:
        a = face_recognition.load_image_file(os.path.join("images",di+".jpg"))
    except :
        pass
    f_l = face_recognition.face_locations(a)
    l = face_recognition.face_encodings(a,f_l)[0].tolist()
    if len(l) >0:
        g_dict[di]["image_encodings"] = []
        g_dict[di]["image_encodings"].append(face_recognition.face_encodings(a,f_l)[0].tolist())
    fill_json()
    return "Succesfully added"
"""it start the bottle"""
def start_bottle():
    @get('/login') # or @route('/login')
    def login():
        return '''
            <form action="/login" method="post">
                Enter your Url: <input name="url" type="text" />
                <input value="Upload" type="submit" />
            </form>
        '''

    @post('/login') # or @route('/login', method='POST')
    def do_login():
        url = request.forms.get('url')
        return bottle_query(url)


    @get('/new')
    def add_a_person():
        return '''
            <p> You can add your self from here </p>
            <form action="/new" method="post">
                Enter your photo Url: <input name="url" type="text" />
                Enter your name: <input name = "name" type : "text" />
                <input value="Upload" type="submit" />
            </form>
        '''
    @post('/new')
    def added():
        url = request.forms.get('url')
        name = request.forms.get('name')
        return add_a_personn(url,name)
    run(reloader = True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", "-d", help="Enter the Social Bankers URL")
    parser.add_argument("--FindURL","-f",  help="Enter the URL of image")
    parser.add_argument("--Images","-i",  help="fill downloaded images")
    parser.add_argument("-Server","-ss", help = "Start the server")
    args = parser.parse_args()
    print(args)
    if(args.download):
        load_json()
        soup = create_sub(args.download)
        create_tags(soup)
        create_dict()
        add_names(soup)
        add_followers(soup)
        create_image_links()
        fill_json()

    if(args.Images):
        load_json()
        images = fill_images()
        create_image_encodings(images)
        fill_json()

    if(args.FindURL):
        load_json()
        query_image(args.FindURL)
        show_image()

    if(args.Server):
        load_json()
        start_bottle()
