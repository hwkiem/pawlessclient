import cv2
import numpy as np
import face_recognition
import os
import math
from selenium import webdriver
import time

driver = webdriver.Firefox()
appState = ''
curUNI = 'Unknown'


def get_coords(p1):
    try:
        return int(p1[0][0][0]), int(p1[0][0][1])
    except:
        return int(p1[0][0]), int(p1[0][1])


def head_movement(frame, first_frame):
    gesture = 'Unconfirmed'
    x_movement = 0
    y_movement = 0

    p0 = np.array([[face_center]], np.float32)
    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    while True:
        ret, frame = video_capture.read()
        old_gray = first_frame.copy()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        cv2.circle(frame, get_coords(p1), 4, (0, 0, 255), -1)
        cv2.circle(frame, get_coords(p0), 4, (255, 0, 0))

        # get the xy coordinates for points p0 and p1
        a, b = get_coords(p0), get_coords(p1)
        x_movement += abs(a[0] - b[0])
        y_movement += abs(a[1] - b[1])

        # print(y_movement)
        if y_movement > 50:
            gesture = 'Yes'

        if gesture == 'Yes':
            return "Confirmed"
        else:
            return "Unconfirmed"


def find_gesture(filename):
    # read image
    src = cv2.imread(filename, cv2.IMREAD_UNCHANGED)

    if src is None:
        return 'None'

    dup = src

    # extract red channel
    red_channel = src[:, :, 2]

    # create empty image with same shape as that of src image
    red_img = np.zeros(src.shape)

    # assign the red channel of src to empty image
    red_img[:, :, 2] = red_channel

    # set RGB color bounds
    lower = (0, 0, 0)
    upper = (0, 0, 150)
    mask = cv2.inRange(red_img, lower, upper)

    # flip binary bits --> white blob
    mask = cv2.bitwise_not(mask)
    # cv2.imwrite('binary.jpeg', mask)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=4)

    # get contours of new binary image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dup, contours, -1, (0, 255, 0), 3)

    value = (35, 35)
    crop_img = mask[100:300, 500:300]
    blurred = cv2.GaussianBlur(mask, value, 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    cv2.imwrite('yuh.jpg', blurred)

    max_area = -1
    if contours:
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if (area > max_area):
                max_area = area
                ci = i
        cnt = contours[ci]

        # check if gesture is a fist
        hull = cv2.convexHull(cnt)
        areaHull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)
        areaRatio = areacnt / areaHull
        if areaRatio > .85:
            return "Fist"
    else:
        return 'None'


    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(dup, (x, y), (x + w, y + h), (0, 0, 255), 0)
    hull = cv2.convexHull(cnt)

    # area and ratio calculations, addition
    areaHull = cv2.contourArea(hull)
    areacnt = cv2.contourArea(cnt)
    areaRatio = ((areaHull - areacnt) / areacnt) * 100

    # drawing = np.zeros(dup.shape,np.uint8)
    # cv2.drawContours(drawing,[cnt],0,(0,255,0),0)
    # cv2.drawContours(drawing,[hull],0,(0,0,255),0)
    hull = cv2.convexHull(cnt, returnPoints=False)
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
        if angle <= 90:
            count_defects += 1
            cv2.circle(crop_img, far, 1, [0, 0, 255], -1)
        cv2.line(crop_img, start, end, [0, 255, 0], 2)

    symbol = 'None'
    if count_defects == 0:
        if areaRatio < 15:
            symbol = 'Fist'
        else:
            symbol = '1'
    elif count_defects == 1:
        symbol = '2'
    elif count_defects == 2:
        symbol = '3'
    elif count_defects == 3:
        symbol = '4'
    elif count_defects == 4:
        symbol = '5'
    return symbol


def build_face_lists():
    encodings = []
    names = []

    directory = os.fsencode('faces')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        name = filename.split('.')[0]

        path = 'faces/' + filename
        img = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(img)
        if len(encoding) < 1:
            print('No faces found in ' + filename)
        else:
            names.append(name)
            encodings.append(encoding[0])

    return encodings, names


def interpret_gesture(left, right): # doc list/preview view boolean needed
    if appState == 'notLoggedIn' and left == '5' and right == '5': # send uni to login
        driver.get('http://localhost:8111/login/' + curUNI)
        time.sleep(2)
    elif appState == 'fileList': # move left, move right, select for preview
        if left == '5' and right == 'Fist':
            driver.get('http://localhost:8111/prevDoc/')
        elif left == 'Fist' and right == '5':
            driver.get('http://localhost:8111/nextDoc/')
        elif left == '5' and right == '5':
            driver.get('http://localhost:8111/getDoc/')
    elif appState == 'preview': # scroll, print, back out
        # if left == '5' and right == '5': # print, path doesn't exist yet
        #     driver.get('http://localhost:8111/prevDoc/') 
        if left == 
    elif appState == 'pageView' # scroll betweeen pages, go back 




    if left == '5' and right == '5' and browserOpen: # give face encoding to app
        driver.get('http://localhost:8111/another')
        time.sleep(2)
    elif left == '5' and right == 'Fist':
        print('going left') # go left
    elif left == '5' and right == 'Fist':
        print('going right') # go right


# def interpret_head(confirmed): # need to use appState to know what moves are legal



if __name__ == "__main__":

    video_capture = cv2.VideoCapture(0)

    known_face_encodings, known_face_names = build_face_lists()

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # initialize num of frames
    num_frames1 = 0
    num_frames2 = 0
    aWeight = 0.5
    browserOpen = False

    confirmed = 'Unconfirmed'
    head_counter = 4
    has_confirmed = False

    login = False
    logout = False
    has_confirmed_print = False
    while True:
        # Grab a single frame of video
        ret, frame1 = video_capture.read()
        frame = cv2.flip(frame1, 1)
        frame_gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if len(face_encodings) > 0 and appState == '':
                appState = 'notLoggedIn'
                driver.get('http://localhost:8111/')
            if not login:
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            face_center = left + ((right - left) / 2), top + ((bottom - top) / 2)
            # print(face_center)

            if not has_confirmed:
                if confirmed == 'Unconfirmed':
                    confirmed = head_movement(frame, frame_gray1)
                    head_counter = 3
                else:
                    next_check = head_movement(frame, frame_gray1)
                    # print(next_check)
                    if next_check == confirmed:
                        head_counter -= 1
                        if head_counter < 1:
                            if next_check == 'Confirmed':
                                has_confirmed = True
                                name = name + confirmed
                                head_counter = 4

                    else:
                        head_counter = 4
                        confirmed = next_check
            else:
                name = name + confirmed

            curUNI = name
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            if has_confirmed:
                login = True
                confirmed = 'Unconfirmed'
                # log in make the get request

            if login:
                clone = frame.copy()

                # get the height and width of the frame
                (height, width) = frame.shape[:2]

                # HAND REGIONS
                hand_regionL = frame1[int(face_center[1]) - 250: int(face_center[1]) + 250,
                               int(face_center[0]) + 150: int(face_center[0]) + 600].copy()

                hand_regionR = frame1[int(face_center[1]) - 250: int(face_center[1]) + 250,
                               int(face_center[0]) - 600: int(face_center[0]) - 150].copy()

                cv2.imwrite('left.jpg', hand_regionL)
                cv2.imwrite('right.jpg', hand_regionR)

                leftHand = find_gesture('left.jpg')
                rightHand = find_gesture('right.jpg')

                interpret_gesture(leftHand, rightHand)

                if leftHand == '5' and rightHand == '5':
                    print('High Five')
                elif leftHand == '5':
                    print('left')
                elif rightHand == '5':
                    print('right')

                # if leftHand == 'Fist' or rightHand == 'Fist':
                #     logout = True
                #     login = False

                # elif leftHand == '5' and rightHand == '5':
                #     print('High five')

                # elif leftHand == '5':
                #     action = 'moveprev'
                #     print('left')
                # elif rightHand == '5':
                #     action = 'movenext'
                #     print('right')

                if confirmed == 'Unconfirmed':
                    confirmed = head_movement(frame, frame_gray1)
                    head_counter = 3
                else:
                    next_check = head_movement(frame, frame_gray1)
                    # print(next_check)
                    if next_check == confirmed:
                        head_counter -= 1
                        if head_counter < 1:
                            if next_check == 'Confirmed':
                                has_confirmed_print = True
                                # print current pdf
                                confirmed = 'Unconfirmed'
                    else:
                        head_counter = 4
                        confirmed = next_check

        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
