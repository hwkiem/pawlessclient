# pawlessclient

This repo is dedicated to the PawlessPrint Client and uses a live video feed of a user's hand gestures and head movements to navigate pawlessprint.herokuapp.com and print out queued documents.
PawlessClient will run persistently on the computer connected to a printer.
To use the client, first create an account at pawlessprint.herokuapp.com and then upload an image of your face saved as '[YOUR ACCOUNT USERNAME].jpeg' to the faces directory.


### How to run
Must install the dependencies in requirements.txt. On top of this, must install geckodriver fromhttps://github.com/mozilla/geckodriver/releases . Once this is downloaded and the geckodriver is moved to a directory in your path, you will be able to run Selenium. You will also need to add a well-cropped photo of yourself to the /faces directory, named the same as your PawlessPrint profile username; for example, user 'jpr2158' on PawlessPrint must add their face to /faces and name it 'jpr2158.jpeg'. Finally, you could run into trouble previewing pdf's using Firefox. If this happens, the likely fix is Settings > Preferences > Files and Applications > change PDF action to preview in Firefox.  

To run: python3 vision.py


### Connecting to Printer

The system first finds all of the possible printers your computer can connect to and asks you to select one for printing. If no printers are available, the system stops. 

### Logging in

The client will track for faces. When the user face is found it will use facial recognition against the faces directory. The user will use their hands to signal they are trying to log in by holding out a five gesture with both hands. This will navigate to pawlessprint.herokuapp.com/user/[uni]/1/ which will display a list of the user's queued files.
  
### Selecting previous or next document

A five gesture with the left or right hand will control selecting the previous or next document

### Switching between preview mode and queued list view

If the user leans to the left or right, they can switch between previewing the selected document and then back to seeing the entire queue of documents.

### Scrolling

A five gesture with the left or right hand will control scrolling up or down for the currently previewed document

### Printing

If a user jumps, the currently selected file will be downloaded and printed

### Hearing the instructions

At any point, if the user squats, the system will speak the instructions aloud 

### Logging out

To log out, the user just walks away and leaves the frame and the system returns to the camera view where it is tracking for faces
