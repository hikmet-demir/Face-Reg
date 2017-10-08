# Face-Reg
Face Recognition Application.

This is a Face Recognition application. It's based on python. It's using many libraries but the main libraries are [Face Recognition](https://github.com/ageitgey/face_recognition#face-recognition) and [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

**What is it doing?**

The application ﬁnds the human faces in the given image and with using it’s database, it determine who belongs to this face. 
The image may contain multiple humans but application will find all faces and label them. 
If the given human face is not recorded in its database then it will label that face as "Unknown".
The program also create it's database itself. For now it's creating Turkish Celebrities faces database with web scrabbing.

**How is it doing?**

The application have 2 main step: Creating database & Labeling Faces

_Creating database:_
The application needs names and faces of desired people. I used [Social Bankers](https://www.socialbakers.com/statistics/twitter/profiles/turkey/celebrities/page-1-5/) to get a list of Turkish Celebrities
I used a Beautiful Soup 4 python library to get names/followers/twitter hastags datas from Social Bankers website. BS4 is a web scrabbing library in Python. Algorithm saves data to a dictionary then
it search names in bing and again with bs4 library it download the first 5 images of desired humans and saved them to "images" file.

_Labeling Faces:_
After Creating database, Face_recognition library starts to do its magic. It fill images to a temporary dictionary then it pushes this library to image encodings function.
Image Encoding function is find faces in image then it creates [128 byte encoding of faces](https://cdn-images-1.medium.com/max/1600/1*6kMMqLt4UBCrN7HtqNHMKw.png). 
Face recognition algorithm is using this face encodings to match faces. 







