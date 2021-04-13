import cv2
import os
import argparse

def FaceDetect(imagePath,savePath,cascPath):
    """ To get the face from the image """
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    # Read the image
    image = cv2.imread(imagePath)
    roi=image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=2,minSize=(10, 10))

    print("[info...] Found {0} faces!".format(len(faces)))

    # Draw a rectangle around the faces
    if not os.path.exists(savePath): os.makedirs(savePath)
    for i,(x, y, w, h) in enumerate(faces): 
        cv2.imwrite(savePath+"image.jpg",cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 1)) # Save images
        cv2.imwrite(savePath+f"/face_{str(i)}.jpg",roi[y:y+h, x:x+w]) # Save face

if __name__=="__main__":

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")).replace("\\","/")
    cascPath = path + "/src/utils/models/haarcascade_frontalface_default.xml"
    # Get user supplied values
    parser=argparse.ArgumentParser(description='Face Detection Tool')
    parser.add_argument("-i","--imagePath",type=str,default=path+'/db/input/images/frame33.jpg',help='Input image')
    parser.add_argument("-s","--savePath",type=str,default=path+'/db/output/',help='Image output path')
    args=parser.parse_args()
    
    FaceDetect(args.imagePath,args.savePath,cascPath)

    
