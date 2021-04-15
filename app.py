""" 
Engagement AI
"""

# Import dependencies
from src.engine import reko,Bucket_name,Folder_in_S3,upload_folder_to_s3,s3,facedetect
import os
import glob
import json
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from PIL import Image
from tqdm import tqdm
from random import sample
from src.utils import Videos2Images
from datetime import datetime

now = str(datetime.now())

# Get all the files in directory
rootpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "./")).replace("\\", "/")
ImageCollection= rootpath + '/db/input/videos/OutputDump/'
directory = rootpath+ "/db/input/videos/OutputDump/*.jpg"
outputpath = rootpath+"/out/"
Bucket_name=Bucket_name # Bucket name in AWS S3
Folder_in_S3=Folder_in_S3 # Folder name inside S3 bucket

jsonFileAlias="frame"

Marks=pd.read_csv(rootpath + "/db/input/docs/Marks.csv")
QnA=pd.read_csv(rootpath + "/db/input/docs/QnA.csv")

def EmotionalAnalysis():
    """ Tp do the emotional analysis of the selected images """

    files = glob.glob(directory)

    # Get emotions of all the files present in the folder
    for _,file in enumerate(files):

        _, tail = os.path.split(file)

        savePath = outputpath + tail.split(".jpg")[0] + '/'

        reko(file,savePath)

        print(f"[info...] {tail} processed")

def similarity(image_one, image_two):
    """ To find the cosine siilarity between two images """
    # data1 image
    gray_image1 = cv2.cvtColor(cv2.resize(cv2.imread(image_one), (300, 300)), cv2.COLOR_BGR2GRAY) # Read from disk
    # data2 image
    gray_image2 = cv2.cvtColor(cv2.resize(image_two, (300, 300)), cv2.COLOR_BGR2GRAY) # Read from matrics 
    # Cosine similarity
    similarity = cosine_similarity(gray_image1.reshape(1,-1),gray_image2.reshape(1,-1))[0][0]
    # print(f"[info...] Similarity = {similarity}")
    return(similarity)

algo = lambda x: 0.8*(x["CALM"]+x["HAPPY"])-0.1*(x["SURPRISED"]+x["CONFUSED"]+x["ANGRY"]+x["SAD"]+x["DISGUSTED"]+x["FEAR"])+0.2*(x["Marks Obtained"]+0.1*x["Question Asked"]) # Logic to calculate the Engagement score

def EngagementAnalysis(photo,outputjson_emotion,k,threshold=0.80):
    """ To do the Engagement analysis of the videos """
    img0=np.array(Image.open(photo))
    coordinates_emotions=json.load(open(outputjson_emotion,"r"))
    data = []
    for i,value in enumerate(coordinates_emotions["FaceDetails"]):
        BoundingBox = value["BoundingBox"]
        df=pd.DataFrame(value["Emotions"])
        output=dict(zip(list(df["Type"]),list(df["Confidence"])))
        x1, y1, w_size, h_size= BoundingBox["Left"], BoundingBox["Top"], BoundingBox["Width"],BoundingBox["Height"]
        x_start = round(x1*img0.shape[1])
        y_start = round(y1*img0.shape[0])
        x_end = round(x_start + w_size*img0.shape[1])
        y_end = round(y_start + h_size*img0.shape[0])
        roi=img0.copy()
        similarity_score = [similarity(file, cv2.cvtColor(roi[y_start:y_end, x_start:x_end], cv2.COLOR_BGR2RGB)) for file in ArtifactFiles]

        output["FileName"]=photo

        if max(similarity_score) >= threshold:
            output["Person"]=PersonName[similarity_score.index(max(similarity_score))]
            output["Marks Obtained"] = float(list(Marks[Marks["Person"]==output["Person"]]["Percentage"])[0])
            output["Question Asked"] = float(list(QnA[QnA["Person"]==output["Person"]]["Asked Question"])[0])
            output["Image Link"] = f"https://{Bucket_name}.s3.amazonaws.com/{Folder_in_S3}/{PersonName[similarity_score.index(max(similarity_score))]}_{now}.jpg"
        else:
            output["Person"] = "XXXXX"
            output["Marks Obtained"] = np.nan
            output["Question Asked"] = np.nan
            output["Image Link"] = ''

        del similarity_score

        data.append(output)


    Result= pd.DataFrame(data)
    Result["AI Engagement Score"] = Result.apply(algo,axis=1)
    Result["AI raw data"] = str(coordinates_emotions)
    if not os.path.exists(rootpath+'/out/excel'): os.makedirs(rootpath+'/out/excel')
    Result.to_excel(rootpath+'/out/excel/'+f"ImageAnalysis_{k}.xlsx",index=False)

    print(f"[info...] Analysis {k} completed")

    return(Result)

def dirFile(root,pattern):
    """ Extract all the files present on provided root directory with particular extention"""
    filelist = []
    for path, _, files in os.walk(root):
        for name in files:
            file=os.path.join(path, name)
            if file.endswith(pattern):
                filelist.append(file)
    return(filelist)

def EngagementAnalysisBatch(threshold):
    """ Batch analyis of all the files selected for Analysis in Outputump folder """

    photo_dir_files = dirFile(rootpath+'/db/input/videos/OutputDump/',".jpg") # Selected image for analysis
    outputjson_emotion_dir_root = rootpath+'/out/'

    for k,filedir in enumerate(photo_dir_files):
        _,filename = os.path.split(filedir)
        EngagementAnalysis(filedir,outputjson_emotion_dir_root+filename.split(".jpg")[0]+"/"+jsonFileAlias+".json",k,threshold)

    print(f"[info...] Congratulations all the analysis completed")

def dfs_tabs(df_list, sheet_list, file_name):
    """ To combine multiple excel into one """
    writer = pd.ExcelWriter(file_name,engine='xlsxwriter')   
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0)   
    writer.save()

def ExcelCombine():
    df = pd.DataFrame()
    files = dirFile(rootpath+'/out/excel','.xlsx')
    for file in tqdm(files):
        df = df.append(pd.read_excel(file),ignore_index=True)
    
    df = df[df["Person"]!="XXXXX"]
    df1 = pd.DataFrame(df.groupby(['Person','Image Link'])['AI Engagement Score'].mean()).reset_index(drop=False)
    df1 = df1[df1["Person"]!="XXXXX"]
    # list of dataframes and sheet names
    dfs = [df, df1]
    sheets = ['raw data combined','AI Engagement Score','df2']  

    # run function
    dfs_tabs(dfs, sheets, 'FinalAnalysisReport.xlsx')

    print(f"[info...] All analysis Excel combined for analyis")

if __name__=="__main__":

    V2I=int(input("\nDo you want to convert video to image?[Press 1 for Yes and 0 for No or you alread have in OutputDump folder]:"))

    if V2I==1:
        filename=input("\nEnter video file name [e.g. Finance & Corporate Committee - Zoom Meeting.mp4 ]:")
        Videos2Images.run(inputpath = rootpath+f'/db/input/videos/SourceDump/{filename}',fps = 100,imageExt=".jpg",OutputName=jsonFileAlias)

        selection=int(input("\nDo you want to automatically select the images? [Press 1 for Yes and 0 for No]:"))
        try:
            if selection==1:
                retainNo= int(input("\nHow many images do you want to retain?[Type number e.g. 10]:"))
                files = os.listdir(ImageCollection)
                for file in sample(files,len(files)-retainNo):
                    os.remove(ImageCollection+file)
            else:
                print(f"\nPlease delete the images at {ImageCollection} manually which you not want to analyze:")
        except:
            print(f"\nPlease delete the images at {ImageCollection} which you not want to analyze:")

    else:
        print("Proceeding to next step...")



    uploadIn=int(input("\nDo you want to automatically create master images? [Press 1 for Yes and 0 for No]:"))

    if uploadIn==1:

        permission = int(input(f"Please confirm you have transfered one representable file from {ImageCollection} to {rootpath}/db/masterImg/ manually ! [Press 1 for Yes and 0 for No]" ))
        
        try:

            reko(dirFile(rootpath+"/db/masterImg/",".jpg")[0],rootpath+"/db/masterImg/")
            facedetect(dirFile(rootpath+"/db/masterImg/",".jpg")[0],dirFile(rootpath+"/db/masterImg/",".json")[0])
            upload_folder_to_s3(s3.Bucket(Bucket_name), rootpath+'/db/artifact/',Folder_in_S3) 

        except:
            print(f"Error Occured !! it may be due to slow internet or you have not transfered the file from {ImageCollection} to {rootpath}/db/masterImg/ manually") 
    else:
        print("Manually upload the master face image in S3 refer README.md")

    entry = int(input("\nDo you want to proceed for Emotional analysis using AWS? [Type 1 for yes and 0 for No]"))
    
    if entry==1:
        print(f"[info...] Emotional Analysis initiated")
        EmotionalAnalysis() # Uses Amazon Rekogination
    else:
        print("Proceeding to next step...")

    entry2 = int(input("\nDo you want to proceed for Engagement analysis ? [Type 1 for yes and 0 for No]"))

    if entry2==1:
        ArtifactFiles = glob.glob(rootpath+ "/db/artifact/Person_*.jpg") # get all the file name with directory ends with *.jpg
        PersonName = list(map(lambda x: os.path.split(x)[1].split(".")[0],ArtifactFiles)) # To get the name of the persons
        print(f"[info...] Analysis of images initiated")
        EngagementAnalysisBatch(threshold=0.8) # Individual analysis generation
        ExcelCombine() # Combine the individual Spreadsheet
    else:
        print("\nThank you for using this app")
