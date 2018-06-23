import cv2
import numpy as np
import math
import webbrowser as wb
import os

print ("Enter full website for")

print ("\n2 fingers")
fingers2=input()

print ("\n3 fingers")
fingers3=input()

print ("\n4 fingers")
fingers4=input()

tabs=0
count=0
cap = cv2.VideoCapture(0)

while(cap.isOpened()):
    # read image
    ret, img = cap.read()

    # get hand data from the rectangle sub window on the screen
    cv2.rectangle(img, (400,400), (100,100), (0,255,0),0)
    crop_img = img[100:400, 100:400]

    # convert to grayscale
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # show thresholded image, not necessary and can be skipped
    cv2.imshow('Thresholded', thresh1)

    # check OpenCV version to avoid unpacking error
    (version, _, _) = cv2.__version__.split('.')

    if version == '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
               cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    elif version == '2':
        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
               cv2.CHAIN_APPROX_NONE)

    # find contour with max area
    cnt = max(contours, key = lambda x: cv2.contourArea(x))

    # create bounding rectangle around the contour (can skip below two lines)
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt)

    # drawing contours
    drawing = np.zeros(crop_img.shape,np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt, returnPoints=False)#  return point false to find convexity defects

    # finding convexity defects
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)# to draw all contours pass -1

    # applying Cosine Rule to find angle for all defects (between fingers)
    # with angle > 90 degrees and ignore defects
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0] #[ start point, end point, farthest point, approximate distance to farthest point ]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])

        # find length of all sides of triangle
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

        # apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

        # ignore angles > 90 and highlight rest with red dots
        if angle <= 90:
            count_defects += 1
            cv2.circle(crop_img, far, 1, [0,0,255], -1)
        #dist = cv2.pointPolygonTest(cnt,far,True)

        # draw a line from start to end i.e. the convex points (finger tips)
        # (can skip this part)
        cv2.line(crop_img,start, end, [0,255,0], 2)
        #cv2.circle(crop_img,far,5,[0,0,255],-1)
    if count==0:
        cv2.putText(img,"Wait for it :p", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, 3)
    # define actions required
    if count_defects == 1 and count!=2 and tabs<=8:
        wb.open_new_tab('http://www.'+fingers2+'.com')
        tabs=tabs+1
        cv2.putText(img,"2."+fingers2, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,0,0), 3)
        count=2    
    elif count_defects == 2 and count!=3 and tabs<=8:
        wb.open_new_tab('http://www.'+fingers3+'.com')
        tabs=tabs+1
        cv2.putText(img, "3."+fingers3, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 3)
        count=3
    elif count_defects == 3 and count!=4 and tabs<=8:
        wb.open_new_tab('http://www.'+fingers4+'.com')
        cv2.putText(img, "4."+fingers4, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,165,0), 3)
        tabs=tabs+1
        count=4
    elif count_defects == 4 and count!=5:
        cv2.putText(img,"5.Close Web browser", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 3, 3)
        os.system("taskkill /im chrome.exe /f")
        tabs=0
        count=5
    else:
        cv2.putText(img,"", (50, 100),\
                    cv2.FONT_HERSHEY_SIMPLEX, 3, 3)
        
        
    if count==2:
        cv2.putText(img, "2."+fingers2, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,0,0), 3)
    elif count==3:
        cv2.putText(img, "3."+fingers3, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 3)
    elif count==4:
        cv2.putText(img, "4."+fingers4, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,165,0), 3)
    elif count==5:
        cv2.putText(img, "5.WebBrowser close", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, 3)



    # show appropriate images in windows
    cv2.imshow('Gesture', img)
    all_img = np.hstack((drawing, crop_img))
    #not necessary to show contours and can be skipped
    cv2.imshow('Contours', all_img)

    k = cv2.waitKey(10)
    if k == 27:
        break