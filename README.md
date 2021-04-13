# EngagementAI

<center><img src="./db/input/images/output.jpg" width="900" height="400"></center>

## Introduction
This project uses AWS Rekognition for the emotion detection. Based on the emotion detected, further analysis is made.
Algorithm working behind Engagement analysis
```
0.8*("CALM"+"HAPPY")-0.1*("SURPRISED"+"CONFUSED"+"ANGRY"+"SAD"+"DISGUSTED"+"FEAR")+0.2*("Marks Obtained"+0.1*"Question Asked")
```
## Workflow Diagram
<center><img src="./db/input/images/EngagementAI.png" width="300" height="200"></center>

## Folder Architecture

                C:.
                │   app.py
                │   README.md
                │   requirements.txt
                │
                ├───.vscode
                │       settings.json
                │
                ├───config
                │       credentials.json
                │
                ├───db
                │   ├───artifact
                │   ├───input
                │   │   ├───docs
                │   │   │       Marks.csv
                │   │   │       QnA.csv
                │   │   │       Research Export for analysis.xlsx
                │   │   │
                │   │   ├───images
                │   │   │       frame33.jpg
                │   │   │       output.jpg
                │   │   │
                │   │   ├───json
                │   │   │       frame33.json
                │   │   │
                │   │   └───videos
                │   │       ├───OutputDump
                │   │       └───SourceDump
                │   └───masterImg
                ├───notebook
                │       analysis.ipynb
                │
                ├───out
                └───src
                    │   engine.py
                    │
                    └───utils
                        │   face_detect.py
                        │   face_similarity.py
                        │   Videos2Images.py
                        │
                        └───models
                                haarcascade_frontalface_default.xml

## How to setup the environment for this project?
1. Install Anaconda from this link https://www.anaconda.com/products/individual#windows and follow the steps mentioned in following link
https://docs.anaconda.com/anaconda/install/windows/

2. After Anaconda installation, go to search and run Anaconda Prompt and create virtual environment using following commands.

    `conda create -n engagementai python=3.7.3`

    `conda activate engagementai`

3. Run Anaconda prompt and change the drive to the location to this directory and run command `python -m pip install -r requirements.txt`. This will install all the packages require for model execution.

## How to use this software?
Step 1:
Modify [./config/credentials.json](./config/credentials.json)
```JSON
    {
        "User name": "ashish_temp",
        "Access key ID": "XXXX",
        "Secret access key": "XXXX",
        "Bucket_name":"rekoengagementai",
        "Folder_in_S3":"artifact"
    }
```
- Modify `Folder_in_S3`
  
Step 2:

Modify *.csv for [Marks](./db/input/docs/Marks.csv) and [QnA](./db/input/docs/QnA.csv)

Step 3:
```bash
Python 3.7.3 (default, Apr 24 2019, 15:29:51) [MSC v.1915 64 bit (AMD64)] :: Anaconda, Inc. on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from src.engine import reset
>>> reset()
```

Step 4:
Download Video from this link "https://www.youtube.com/watch?v=K4GyPYuiLWQ&t=15s&ab_channel=PatrickEagan" and put downloaded files at `./db/input/videos/SourceDump/`
**Modify the file Name**
```python
if __name__=="__main__":

    V2I=int(input("\nDo you want to convert video to image?[Press 1 for Yes and 0 for No or you alread have in OutputDump folder]:"))

    if V2I==1:
        Videos2Images.run(inputpath = rootpath+'/db/input/videos/SourceDump/Finance & Corporate Committee - Zoom Meeting.mp4',fps = 100,imageExt=".jpg",OutputName=jsonFileAlias)
```
**Replace Finance & Corporate Committee - Zoom Meeting.mp4** with your file name

Step 5:
Run following command and follow the prompt instruction
```bash
python app.py
```

## How to convert video to images?
*You should be present at the directory location of [README.md](./README.md)*

Code Location : [Videos2Images.py](./src/utils/Videos2Images.py)

```bash
python src/utils/Videos2Images.py --inputpath C:/Users/imash/Documents/upwork/db/input/videos/SourceDump/sample.mp4 --fps 10 --imageExt .jpg --OutputName frame
```

```bash
python src/utils/Videos2Images.py -i C:/Users/imash/Documents/upwork/db/input/videos/SourceDump/sample.mp4 -f 10 -e .jpg -o frame
```

**Explaination**

- inputpath : Input path of the Sample Video
- fps : Frame per second
- imageExt : File extension. This architecture supports only *.jpg format
- OutputName : Alias of the output file name

If you don't want to involve in complexity of input argument, then just insure that your video should be available at `./db/input/videos/SourceDump` and run below mentioned code. Script will dump your images at `./db/input/videos/OutputDump/frame*.jpg` with an alias of `frame`.

```bash
python src/utils/Videos2Images.py
```
*As of now user are suppose to do the selection of images need to be analyzed.*

## Emotional analysis
Once user will select the images in `./db/input/videos/OutputDump/frame*.jpg`, next step will be to do emotional analysis. To do emotional analysis, We are utilizing [Amazon Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/API_Emotion.html). 

To do analysis, user is suppose to run following command.
```bash
python app.py
```
This execution will create json resonse for Amazon Rekognition emotional analysis at `./out/`. Here we are storing the all the responses in *.json format inside the folder and filename of original file name.

## How to setup the person details?
In this step user is suppose to mask the face from the images. **File name should be the Name of the person**. Code will generate the Alias attached with Each name. It is user responsibility to change the file name as per Person's name.  This code will upload your masked images to AWS S3.

Steps 
- Select the image from [./db/input/videos/OutputDump/frame*.jpg](./db/input/videos/OutputDump/) which contains all the persons with proper visibility of face. From this particular image we will extract the face.
- Run below command
    ```python
    from src.engine import facedetect
    facedetect(photo,outputjson_emotion)
    ```
- Modify *.csv for [Marks](./db/input/docs/Marks.csv) and [QnA](./db/input/docs/QnA.csv).

**Explaination**
- photo : Location of image selected in Step 1. e.g. `./db/input/images/frame33.jpg`
- outputjson_emotion : Amazon Rekognition Emotional analysis file of image selected in step 1. e.g. `./out/frame33.json`

## Create S3 bucket
```python
from src.engine import create_bucket
create_bucket('rekoengagementai')
```

## Upload the images in S3
```python
from src.engine import upload_folder_to_s3
Bucket_name="rekoengagementai"
Directory_name='C:/Users/imash/Documents/upwork/db/artifact/'
Folder_in_S3='artifact'
s3bucket = s3.Bucket(Bucket_name)
upload_folder_to_s3(s3bucket, Directory_name, Folder_in_S3)  
```
## Analysis

- [Notebook](./notebook/analysis.ipynb)
- [Final Excel](./FinalAnalysisReport.xlsx)

## Reset the software
To reset run following python commands. Below command will delete out folder, SourceDump folder, OutputDump folder, artifact folder.

```python
from src.engine import reset
reset()
```

## Extra Code
-   `src\utils\face_detect.py` : To find the Face. In this we are using AWS Rekogination not this.
-   `src\utils\face_similarity.py` : To find the Coine similarity between two images.

## References
[Input Data used for analysis](https://www.youtube.com/watch?v=K4GyPYuiLWQ&t=15s&ab_channel=PatrickEagan)
