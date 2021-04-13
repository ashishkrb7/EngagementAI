import cv2
import os
import argparse
from sklearn.metrics.pairwise import cosine_similarity

def run(image_one, image_two):
    """ To find the cosine siilarity between two images """
    # data1 image
    gray_image1 = cv2.cvtColor(cv2.resize(cv2.imread(image_one), (300, 300)), cv2.COLOR_BGR2GRAY)
    
    # data2 image
    gray_image2 = cv2.cvtColor(cv2.resize(cv2.imread(image_two), (300, 300)), cv2.COLOR_BGR2GRAY)
    
    # Cosine similarity
    similarity = cosine_similarity(gray_image1.reshape(1,-1),gray_image2.reshape(1,-1))[0][0]

    print(f"[info...] Similarity = {similarity}")
    return(similarity)

if __name__ == '__main__':

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")).replace("\\","/")
    parser = argparse.ArgumentParser(description='Face Comparison Tool')
    parser.add_argument("-i1","--image-one",type=str,default=path+'/db/output/face_0.jpg',help='Input image')
    parser.add_argument("-i2","--image-two",type=str,default=path+'/db/artifact/P5.jpg',help='Image output path')
    args = parser.parse_args()

    run(args.image_one, args.image_two)