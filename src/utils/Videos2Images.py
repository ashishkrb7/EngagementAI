'''
Python code to extract the images from videos based on custom fps

python Videos2Images.py --inputpath C:/Users/imash/Documents/upwork/db/input/videos/SourceDump/sample.mp4 --fps 10 --imageExt .jpg --OutputName sample
'''
# Importing all necessary libraries 
import cv2 
import os 
import argparse

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")).replace("\\", "/") # To get current working path

def run(inputpath,fps,imageExt=".jpg",OutputName="frame"):
    '''Main function to run the program'''
    inputIMG = cv2.VideoCapture(inputpath) # Read the video from specified path 
    if not os.path.exists(path+'/db/input/videos/OutputDump'): os.makedirs(path+'/db/input/videos/OutputDump') # creating a folder named data 

    def getFrame(sec,imageExt,count,filename):
        ''' Function to create the images from videos'''
        inputIMG.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
        # Reading from frame 
        ret,frame = inputIMG.read()
        if ret: 
            name = path+f'/db/input/videos/OutputDump/{filename}_'+ str(count) + imageExt
            print ('[Creating...]' + name) 
            cv2.imwrite(name, frame) 
        return ret

    sec = 0
    count=1
    success = getFrame(sec,imageExt,count,OutputName+'_'+str(count/fps))
    print(success)
    while success:
        count = count + 1
        sec = sec + fps
        sec = round(sec, 2)
        success = getFrame(sec,imageExt,count,OutputName+'_'+str(count/fps))

    inputIMG.release() 
    cv2.destroyAllWindows() 

  
if __name__=="__main__":

    parser=argparse.ArgumentParser()
    
    parser.add_argument("-i","--inputpath",type=str,default=path+'/db/input/videos/SourceDump/sample.mp4',help='File name of the input video')
    parser.add_argument("-f","--fps",type=float,default=10,help='Frame per second, Default=10 sec')
    parser.add_argument("-e","--imageExt",type=str,default='.jpg',help='Output file extension, Default=".jpg"')
    parser.add_argument("-o","--OutputName",type=str,default='frame',help='Output file name, Default="frame"')
    args=parser.parse_args()
    run(
        inputpath=args.inputpath,
        fps=args.fps,
        imageExt=args.imageExt,
        OutputName=args.OutputName,
    )