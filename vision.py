import cv2
import numpy as np
import face_recognition
import math
import pyttsx3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from urllib import request
import urllib.request
from bs4 import BeautifulSoup
import os
import subprocess


appState = ''
curUNI = 'Unknown'
baseUrl = 'http://pawlessprint.herokuapp.com/'
curDoc = None
printer_name = ''


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
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dup, contours, -1, (0, 255, 0), 3)

    value = (35, 35)
    crop_img = mask[100:300, 500:300]
    blurred = cv2.GaussianBlur(mask, value, 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

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


def interpret_gesture(left, right, head_pos, driver):
    global appState
    global curDoc
    global baseUrl
    global curUNI
    if curUNI == 'Unknown':
        return
    global printer_name

    if os.path.exists('to_print.pdf'):
        os.remove('to_print.pdf')
    elif os.path.exists('to_print.jpeg'):
        os.remove('to_print.jpeg')
    elif os.path.exists('to_print.png'):
        os.remove('to_print.pdf')
    elif os.path.exists('to_print.png'):
        os.remove('to_print.pdf')
    elif os.path.exists('to_print.jpg'):
        os.remove('to_print.jpg')

    if head_pos == 'duck':
         instructions = "To select the next file in your queue, hold up a five with your right hand, \
                     To move back up to the previous uploaded file, hold up a five with your left hand, \
                     To print out the selected file, jump, \
                     To enter preview mode, lean left, \
                     To scroll down through a document, hold up your right hand, \
                     To scroll up through a document, hold up your left hand, \
                     To exit preview mode and return to the queue, lean right \
                     To logout, just walk away"
         engine = pyttsx3.init()
         engine.say(instructions)
         engine.runAndWait()
         engine.stop()

    if appState == 'notLoggedIn' and left == '5' and right == '5':  # send uni to login
        appState = 'fileList'
        curDoc = 1
        driver.get(baseUrl + 'user/' + curUNI + '/1/')
        time.sleep(2)

    elif appState == 'fileList':  # move left, move right, select for preview
        if left == '5' and curDoc != 1:
            driver.get(baseUrl + 'user/' + curUNI + '/' + str(curDoc - 1))
            time.sleep(2)
            s = (driver.current_url.split(curUNI + '/'))[1]
            curDoc = int(s[:-1])
        elif right == '5':
            driver.get(baseUrl + 'user/' + curUNI + '/' + str(curDoc + 1))
            time.sleep(2)
            s = (driver.current_url.split(curUNI + '/'))[1]
            curDoc = int(s[:-1])
        elif head_pos == 'lean_left':
            appState = 'preview'
            driver.get(baseUrl + 'user/' + curUNI +
                       '/' + str(curDoc) + '/view')
            time.sleep(2)

        elif head_pos == 'jump':
            print('PRINTING')
            url = "http://pawlessprint.herokuapp.com/user/" + \
                curUNI + '/' + str(curDoc) + "/view"

            response1 = urllib.request.urlopen(url)
            response = response1.read()

            soup = BeautifulSoup(response)
            links = soup.find_all("embed")

            url = links[0]['src']

            request.urlretrieve(url, "to_print.pdf")
            time.sleep(2)

            os.system("lpr -P %s to_print.pdf" % printer_name)
    elif appState == 'preview':  # scroll, print, back out
        if head_pos == 'lean_right':
            appState = 'fileList'
            driver.get(baseUrl + 'user/' + curUNI + '/' + str(curDoc))
            time.sleep(2)
        elif left == '5':  # left analagous to up
            x = driver.find_element_by_xpath("//body")
            x.click()
            for i in range(0, 20):
                x.send_keys(Keys.UP)
            time.sleep(2)
        elif right == '5':  # right to down
            x = driver.find_element_by_xpath("//body")
            x.click()
            for i in range(0, 20):
                x.send_keys(Keys.DOWN)
            time.sleep(2)

        elif head_pos == 'jump':
            print('PRINTING')
            url = "http://pawlessprint.herokuapp.com/user/" + \
                curUNI + '/' + str(curDoc) + "/view"

            response1 = urllib.request.urlopen(url)
            response = response1.read()

            soup = BeautifulSoup(response)
            links = soup.find_all("embed")

            url = links[0]['src']

            request.urlretrieve(url, "to_print.pdf")
            time.sleep(2)

if __name__ == "__main__":

    print("Welcome to PawlessPrint. Here is a list of your valid printers:")
    output = subprocess.check_output("lpstat -p -d", shell=True)
    output = str(output)
    printer_list = output.split(" ")

    num_to_printer = {}
    index = 1
    up_next = False
    for i in printer_list:
        if up_next:
            num_to_printer[index] = i
            index += 1
        if "printer" in i:
            up_next = True
        else:
            up_next = False
    if len(num_to_printer) == 0:
        print("No printers found!")
        exit(1)
    for i in num_to_printer:
        print(i, " ", num_to_printer[i])
    while True:
        printer_num = input(
            "Please enter the number corresponding to the printer you'd like to connect to: ")
        if int(printer_num) in num_to_printer:
            break
    printer_name = num_to_printer[int(printer_num)]

    video_capture = cv2.VideoCapture(0)
    driver = webdriver.Firefox()

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

    confirmed = 'Unconfirmed'
    has_confirmed = False

    login = False
    logout = False

    prev_y_pos = 0
    prev_x_pos = 0
    logout_counter = 5
    while True:
        # Grab a single frame of video
        ret, frame1 = video_capture.read()
        frame = cv2.flip(frame1, 1)
        frame_gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        # Only process every other frame of video to save time
        rgb_small_frame = small_frame[:, :, ::-1]
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)

            if len(face_encodings) == 0 and appState == 'fileList':
                logout_counter -= 1
                if logout_counter == 0:
                    # log out
                    appState = ''
                    prev_y_pos = 0
                    prev_x_pos = 0
                    logout_counter = 5
                    login = False
                    driver.get(baseUrl)
            else:
                logout_counter = 5
            if len(face_encodings) == 1 and appState == '':  # someone entered frame
                appState = 'notLoggedIn'
                driver.get(baseUrl)
                time.sleep(.5)
                driver.maximize_window()
            if not login:
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
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
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            face_center = left + ((right - left) / 2), top + \
                ((bottom - top) / 2)

            curUNI = name
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)
            if name != 'Unknown':
                login = True

            if login:
                clone = frame.copy()

                # get the height and width of the frame

                (h, w) = frame.shape[:2]

                # HAND REGIONS
                hand_regionL = frame1[40: 600,
                                      int(face_center[0]) + 100: w].copy()

                hand_regionR = frame1[40: 600,
                                      0: int(face_center[0]) - 100].copy()

                cv2.rectangle(
                    frame, (int(face_center[0]) + 75, 40), (w, 440), (0, 255, 0), 2)  # left
                cv2.rectangle(frame, (0, 40), (int(
                    face_center[0]) - 75, 440), (0, 255, 0), 2)  # right

                cv2.imwrite('hands/left.jpg', hand_regionL)
                cv2.imwrite('hands/right.jpg', hand_regionR)

                leftHand = find_gesture('hands/left.jpg')
                rightHand = find_gesture('hands/right.jpg')
                head_pos = ""

                if prev_y_pos == 0:
                    prev_y_pos = face_center[1]
                else:
                    if prev_y_pos - face_center[1] > 100:
                        head_pos = "jump"
                    if face_center[1] - prev_y_pos > 50:
                        head_pos = "duck"

                if prev_x_pos == 0:
                    prev_x_pos = face_center[0]
                else:
                    if prev_x_pos - face_center[0] > 100:
                        head_pos = "lean_left"
                    if face_center[0] - prev_x_pos > 100:
                        head_pos = "lean_right"
                interpret_gesture(leftHand, rightHand, head_pos, driver)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
