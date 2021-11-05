#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import cv2 as cv
import numpy as np
import time
#
MODEL = "./yolov3-tiny_anchor.weights"
CFG = "./yolov3-tiny_anchor.cfg"
SCALE = 0.00392
CLASS_NAME="./obj.names"
INP_SHAPE = (160,160)
MEAN = 0
RGB = True
# Load a network
net = cv.dnn.readNetFromDarknet(CFG, MODEL)
# set conf & nms
confThreshold = 0.5# Confidence threshold
nmsThreshold = 0.9 # Non-maximum supression threshold
with open(CLASS_NAME) as f:
    class_names = f.read().splitlines()
    print("Class name=",class_names,"Detection")
#
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
#
def postprocess(frame, outs):
    found=0
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    def drawPred(classId, conf, left, top, right, bottom):
        left = int(left)
        top = int(top)
        right = int(right)
        bottom = int(bottom)
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0))
        label = class_names[classId] + '_%.2f' % conf
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine), (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    layerNames = net.getLayerNames()
    lastLayerId = net.getLayerId(layerNames[-1])
    lastLayer = net.getLayer(lastLayerId)
    classIds = []
    confidences = []
    boxes = []
    if lastLayer.type == 'Region':
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = center_x - width / 2
                    top = center_y - height / 2
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])
                    print (center_x,center_y,width)
    else:
        print('Unknown output layer type: ' + lastLayer.type)
        exit()

    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        drawPred(classIds[i], confidences[i], left, top, left + width, top + height)
    return boxes
#-------------------------
def main():
    print( "StartCapture")
    c = cv.VideoCapture(-1)
    c.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    c.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    c.set(cv.CAP_PROP_FPS, 30)
    c.set(cv.CAP_PROP_BUFFERSIZE, 1)
    #
    while True:
        r, frame = c.read()
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        # Create a 4D blob from a frame.
        inpWidth = INP_SHAPE[0]
        inpHeight = INP_SHAPE[1]
        blob = cv.dnn.blobFromImage(frame, SCALE, (inpWidth, inpHeight), MEAN, RGB, crop=False)
        # Run a model
        net.setInput(blob)
        outs = net.forward(getOutputsNames(net))
        print("------")
        boxes = postprocess(frame, outs)
        print (boxes)
        cv.namedWindow('image',cv.WINDOW_NORMAL)
        cv.imshow('image', frame )
        cv.waitKey(1)
    cv.destroyAllWindows()
    cv.mwrite(target_filepath, frame)
#-------------------------
if __name__ == "__main__":
    main()

