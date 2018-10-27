# Face-Reg
Face Recognition Application.

This simple application can detect faces in the given photo and it can find the names of the people in the photo. For now, we trained it with turkish celebrities photos but you can easily train it with your own photo.

## Prerequisities

- Python 3

## Installing

Ideally you want to create an virtualenv and run it there but this is not an obligotary.

- You can install required python libraries with this command
```
pip install -r requirements.txt
```

## Using

You want to run it and see the result directly!
Run it from console
```
python Face_reg.py -ss true
```

Go to and give an jpg url to it
```
http://127.0.0.1:8080/login
```
Application will find faces on the photo and if it's trained for that faces it will print the name of the faces below(remember we trained it for turkish celebrities for example: Cem Yılmaz)

Better go to and add your photo(or your friends photos)
```
http://127.0.0.1:8080/new
```
Then give a group picture program will find your friends faces.



