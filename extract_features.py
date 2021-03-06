########################################################################################
# Author: Amrit Singhal, Year: 2018                                                    #
# Emotion Extraction from Images in the Circumplex model: Arousal and Valence values   #
# Details:                                                                             #
# Python Implementation of the paper 'Building Emotion Machines: Recognizing Image     #
# Emotion through Deep Neural Networks' by Hye-Rin Kim, Yeong-Seok Kim, Seon Joo Kim,  #
# and In-Kwon Lee.                                                                     #
# Model from https://github.com/amr4i/EmotionDetection                                 #
########################################################################################

import os
import sys
import cv2
import pickle
import numpy as np
import VGG.vgg16 as vgg 
from lbp.LocalBinaryPatterns import LocalBinaryPatterns


names=[]
gists=[]
sem_features = {}
vgg_features = {}

def load_gistfile(gistFile):
	with open(gistFile, 'r') as g:
		gs = g.readlines()
		for line in gs:
			name, gist = line.split(":")
			names.append(name)
			gists.append(gist)
	
def load_semantic_features(file):
	global sem_features
	with open(file, 'rb') as handle:
		sem_features = pickle.load(handle)

def load_vgg_features(file):
	global vgg_features
	with open(file, 'rb') as handle:
		vgg_features = pickle.load(handle)
	

def get_lbp(image, numPoints=57, radius=4):
	lbpDesc = LocalBinaryPatterns(numPoints, radius)
	hist = lbpDesc.describe(image)
	return hist

def get_gist(imagename):
	ind = names.index(imagename)
	gist = gists[ind].strip().split(" ")
	for i in range(0,len(gist)):
		gist[i] = float(gist[i])
	gist = np.array(gist)
	return gist

def extract_feature_vector(imagepath):
	imagename = imagepath.split("/")[-1]
	print('Extracting feature vector for image {}'.format(imagename))
	image = cv2.imread(imagepath)
	grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	print "Extracting LBP...."
	LBP_Desc = get_lbp(grayImage)
	print "Extracting GIST...."
	GIST_Desc = get_gist(imagename)
	print "Extracting VGG...."
	VGG_Desc = vgg_features[imagename]
	print "Extracting Semantic Features...."
	Sem_Desc = sem_features[imagename]
	
	# Concatenating into a single feature vector	
	feature_vector = np.concatenate((LBP_Desc, VGG_Desc, GIST_Desc, Sem_Desc))
	return feature_vector


""" 
training_file: a document where each line contains the name of the image file, and its corresponding A-V value, separated by a comma. 
directory: path to folder that contains all the image files.
"""
def get_features(training_file ,directory, VGG_feature_file="vgg.pickle", gistFile="gists.txt", semF_file='sematic_features.pickle'):
	features = []
	labels = []
	
	with open(training_file, 'r') as trainFile:
		
		files = trainFile.readlines()
		load_gistfile(gistFile)
		load_semantic_features(semF_file)
		load_vgg_features(VGG_feature_file)
		for file in files:
			filename, file_label = file.split(",")
			filepath = os.path.join(directory, filename)
			if not os.path.isabs(filepath):
				filepath = os.path.join(os.path.dirname(__file__), filepath)
			feature_vector = extract_feature_vector(filepath)
			features.append(feature_vector)
			labels.append(file_label/100.0)
		
		return features, labels


def get_prediction_features(test_file, directory, VGG_feature_file="vgg.pickle", gistFile="gists.txt", semF_file='sematic_features.pickle'):
	features = []
	labels = []
	
	with open(test_file, 'r') as testFile:
		
		files = testFile.readlines()
		load_gistfile(gistFile)
		load_semantic_features(semF_file)
		load_vgg_features(VGG_feature_file)
		for filename in files:
			filepath = os.path.join(directory, filename)
			if not os.path.isabs(filepath):
				filepath = os.path.join(os.path.dirname(__file__), filepath)
			feature_vector = extract_feature_vector(filepath)
			features.append(feature_vector)
		
		return features
	
if __name__ == "__main__":
	imagepath = sys.argv[1]
	load_gistfile(sys.argv[2])
	load_vgg_file(sys.argv[3])
	extract_feature_vector(imagepath)

