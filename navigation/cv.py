import numpy as np
import cv2
import imutils
import time

import threading

class CVThread (threading.Thread):
 def __init__(self ):
   threading.Thread.__init__(self)
   self._active = 1
   self._cvOut = [[[0, 0], [0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0], [0, 0]]]
   
 def stop(self) :
   self._active = 0

 def getCVOut(self) :
   try:
       return self._cvOut
   except:
       print("no coordinates were found")

 def run(self):

     video = cv2.VideoCapture('gateC.mp4')
     width = int(video.get(4))
     height = int(video.get(3))

     # Downscale the image to a reasonable size to reduce compute
     scale = 0.5 
     dim = (int(height*scale), int(width*scale))
     
     # Minimize false detects by eliminating contours less than a percentage of the image
     area_threshold = 10

     print 'h' + ' ' + str(height) + ' ' + 'w' + ' ' + str(width)
     
     while(self._active):
      
        ret, orig_frame = video.read()
        if not ret:
            break
        
        orig_frame = cv2.resize(orig_frame, dim, interpolation = cv2.INTER_AREA)
        frame = cv2.GaussianBlur(orig_frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask0 = cv2.inRange(hsv,(0, 0, 20), (25, 255, 255) )
        mask1 = cv2.inRange(hsv,(160, 0, 20), (179, 255, 255) )
        # join masks
        mask = mask0 + mask1

        ret, thresh = cv2.threshold(mask, 127, 255,0)
    #Erosions and dilations
    #erosions are apploed to reduce the size of foreground objects
        kernel = np.ones((3,3),np.uint8)
        eroded = cv2.erode(thresh, kernel, iterations=1)	
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        #cv2.imshow("dilated", dilated)
        #cv2.imshow("Edged", edged)

        cnts,hierarchy = cv2.findContours(dilated,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(orig_frame, cnts, -1, (0, 255, 0), 3)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:3]

        boundingBoxes = np.empty((0, 4), float)
        if len(cnts) > 0:

                M = cv2.moments(cnts[0])
                i = 0
                for c in cnts:
                        rect = cv2.minAreaRect(c)
                        #print("rect: {}".format(rect))

                        # the order of the box points: bottom left, top left, top right,
                        # bottom right
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)

                        #print("bounding box: {}".format(box))
                        cv2.drawContours(orig_frame, [box], 0, (0, 0, 255), 2)
                        #x,y,w,h = cv2.boundingRect(c)

                        #boundingBoxes = np.append(boundingBoxes, np.array([[x,y,x+w,y+h]]), axis = 0)
                        #cv2.rectangle(orig_frame,(x,y), (x+w, y+h), (255,0,0), 2)
                        #cv2.imshow("bounding rectangle",orig_frame)
                        
                        #print(str(x/width) + " " + str(y/height) + " " + str((x+w)/width) + " " +  str((y+h)/height))

                        #print(box)

                        if i == 0 :
                            self._cvOut[i]=box

                        if i == 1 :
                            if box[0][0] > self._cvOut[0][0][0] :
                                self._cvOut[i]=box
                            else :
                                self._cvOut[i]=self._cvOut[i-1]
                                self._cvOut[i-1]=box

                        if i == 2 :
                            if box[0][0] > self._cvOut[1][0][0] :
                                self._cvOut[i]=box
                            elif box[0][0] < self._cvOut[0][0][0] :
                                self._cvOut[i]=self._cvOut[i-1]
                                self._cvOut[i-1]=self._cvOut[i-2]
                                self._cvOut[i-2]=box
                            else :
                                self._cvOut[i]=self._cvOut[i-1]
                                self._cvOut[i-1]=box
                        
                        '''
                        if i == 0 :

                            self.cvOut[i]=box
                        if i == 1 :

                            if box[0][0] < self._cvOut[0][0][0]:
                            self._cvOut[i]=box
                        '''
                        i = i+1
                        
                        '''if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                        else:
                                cX, cY = 0,0
                        print(cX/width, cY/height)'''
                
        key = cv2.waitKey(1)
        if key == 27:
            break
        time.sleep(0.1)

     video.release()
     cv2.destroyAllWindows()

