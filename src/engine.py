""" 
         .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-.  .-.-. 
        ( E .' ( n .' ( g .' ( a .' ( g .' ( e .' ( m .' ( e .' ( n .' ( t .' ( A .' ( I .'
         `.(    `.(    `.(    `.(    `.(    `.(    `.(    `.(    `.(    `.(    `.(    `.(

Description : Code to call Amazon Rekognition API for Emotional analysis
"""
# Import relevant libraries
import boto3
from boto3.session import Session
import json
import os
import argparse
import shutil
from PIL import Image
import pandas as pd
import numpy as np
import cv2
import json
import random

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./..")).replace("\\","/")

# Import credentials files
credentials=json.load(open(path + '/config/credentials.json','rb'))
access_key_id = credentials["Access key ID"]
secret_access_key = credentials["Secret access key"]
Bucket_name=credentials["Bucket_name"] # Bucket name in AWS S3
Folder_in_S3=credentials["Folder_in_S3"] # Folder name inside S3 bucket

# Activate web services
client = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id = access_key_id, aws_secret_access_key= secret_access_key)
# s3 = boto3.client('s3')
s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
    )


def create_bucket(name):
    """ To create Amazon S3 bucket """
    s3.create_bucket(Bucket=name)

def upload_folder_to_s3(s3bucket, inputDir, s3Path):
    """ To add the files with directory in S3 """
    print("Uploading results to s3 initiated...")
    print("Local Source:",inputDir)
    os.system("ls -ltR " + inputDir)
    print("Dest  S3path:",s3Path)
    try:
        for path, _, files in os.walk(inputDir):
            for file in files:
                dest_path = path.replace(inputDir,"")
                __s3file = os.path.normpath('/' + dest_path + '/' + file).replace("\\","/")
                __local_file = os.path.join(path, file)
                print("upload : ", __local_file, " to Target: ", __s3file, end="")
                s3bucket.upload_file(__local_file, s3Path +__s3file)
                print(" ...Success")
    except Exception as e:
        print(" ... Failed!! Quitting Upload!!")
        print(e)
        raise e    

def printS3items():
    """ To print the list of the items present in S3 """ 
    session = Session(aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key)
    your_bucket = session.resource('s3').Bucket(Bucket_name)
    for s3_file in your_bucket.objects.all():
        print(s3_file.key)

def deleteS3items():
    """ To print the list of the items present in S3 """ 
    session = Session(aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key)
    your_bucket = session.resource('s3').Bucket(Bucket_name)
    for s3_file in your_bucket.objects.all():
        s3.Object(Bucket_name, s3_file.key).delete()
        print(f"{s3_file.key} deleted")

def reko(imagePath,savePath):
    """ To do Emotional analysis of the images stored in respective folder """
    # Load image
    with open(imagePath ,'rb') as source_image:
        source_bytes = source_image.read()

    # Use web services
    print("[info...] Request for Emotion identification initiated")
    response_face_emotion = client.detect_faces(Image={'Bytes':source_bytes},Attributes=['ALL']) # This part can be modify if user need to access the images from S3

    _, tail = os.path.split(imagePath) # To get the file name from path

    # Save response
    if not os.path.exists(savePath): os.makedirs(savePath)
    json.dump(response_face_emotion,open(savePath+tail.split("_")[0]+".json","w")) # Input file name and JSON file will be same
    print("[info...] Emotions successfully dumped")

def reset():
    """ This command will delete the older execution results from the folders and make ready this software for new run """
    try:
        shutil.rmtree(path+"/out/")
        print("[warning...] out folder deleted")
    except:
        pass
    try:
        shutil.rmtree(path+"/db/input/videos/SourceDump/")
        print("[warning...] SourceDump folder deleted")
    except:
        pass
    try:
        shutil.rmtree(path+"/db/input/videos/OutputDump/")
        print("[warning...] OutputDump folder deleted")
    except:
        pass
    try:
        shutil.rmtree(path+"/db/artifact/")
        print("[warning...] artifact folder deleted")
    except:
        pass

    try:
        shutil.rmtree(path+"/db/masterImg/")
        print("[warning...] masterImg's files deleted")
    except:
        pass

    if not os.path.exists(path+"/out/"): os.makedirs(path+"/out/")
    if not os.path.exists(path+"/db/input/videos/SourceDump/"): os.makedirs(path+"/db/input/videos/SourceDump/")
    if not os.path.exists(path+"/db/input/videos/OutputDump/"): os.makedirs(path+"/db/input/videos/OutputDump/")
    if not os.path.exists(path+"/db/artifact/"): os.makedirs(path+"/db/artifact/")
    if not os.path.exists(path+"/db/masterImg/"): os.makedirs(path+"/db/masterImg/")

def facedetect(photo,outputjson_emotion):
    """ To extract face form images """
    img0=np.array(Image.open(photo))
    coordinates_emotions=json.load(open(outputjson_emotion,"r"))

    result = img0.copy()
    for i,value in enumerate(coordinates_emotions["FaceDetails"]):
        BoundingBox = value["BoundingBox"]
        df=pd.DataFrame(value["Emotions"])
        label='%s' % (df["Type"].iloc[df['Confidence'].idxmax()])
        tl = round(0.002 * (img0.shape[0] + img0.shape[1]) / 2) + 1  # line/font thickness
        color = [random.randint(0, 255) for _ in range(3)]
        tf = max(tl - 1, 1)  # font thickness
        x1, y1, w_size, h_size= BoundingBox["Left"], BoundingBox["Top"], BoundingBox["Width"],BoundingBox["Height"]
        x_start = round(x1*img0.shape[1])
        y_start = round(y1*img0.shape[0])
        x_end = round(x_start + w_size*img0.shape[1])
        y_end = round(y_start + h_size*img0.shape[0])
        roi=img0.copy()
        roi = roi[y_start:y_end, x_start:x_end]
        cv2.imwrite(path + f"/db/artifact/Person_{str(i)}.jpg",cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        c1,c2=(x_start, y_start), (x_end, y_end)
        cv2.rectangle(result, c1,c2,color, thickness=tl, lineType=cv2.LINE_AA) 
        cv2.putText(result, label, (c1[0], c1[1] - 2), 0, tl / 5, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    cv2.imwrite(path+"/out/result1.jpg",cv2.cvtColor(result, cv2.COLOR_BGR2RGB))  
    print("[info...] See '.db/artifact/*.jpg'  folder and rename the file as per person name") 


if __name__=="__main__":

    # Get user supplied values
    parser=argparse.ArgumentParser(description='AWS rekognition service utilization tool')
    parser.add_argument("-i","--imagePath",type=str,default=path+'/db/input/images/frame33.jpg',help='Input image')
    parser.add_argument("-s","--savePath",type=str,default=path+'/out/',help='JSON output location')
    args=parser.parse_args()
    
    reko(args.imagePath,args.savePath)