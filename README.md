# pawlessclient

This repo is dedicated to the pawlessprint client.
pawlessclient will run persistently on the computer connected to a printer.

1) The client will track for faces. When the user face is found it will be encoded and sent to pawlessprint.herokuapp.com via a file POST request.
2) pawlessprint.herokuapp.com will respond with a username (uni).
3) The user will be asked to confirm their identity with a NOD or a SHAKE.
  3.1) A NOD action will generate a GET request to pawlessprint.herokuapp.com/[uni] which will return all associated files.
  3.2) A SHAKE action will return the client to its start state in which it is searching for a face.
4) The files will be loaded into the curfiles directory. The first file will be opened. The filename will be printed at the top.
  4.1) Ideally the appropriate commands key is listed somewhere.
5) A RIGHT action will close the current file and load the next file in the directory. If we are at the end of the directory nothing happens.
6) A LEFT action will close the current file and load the previous file in the directory. If we are at the beginning of the directory nothing happens.
7) A NOD action (or some alternative indication gesture - grammar to be decided) will print the current file.
8) If print action is successful a DELETE request is sent to pawlessprint.herokuapp.com/delete/filename (or some equivalent url) such that the file is removed from the print server.
9) If print action is successful the file is removed from the curfiles directory and the next file is open.
10) If no files are in the current directory display "no files"
11) If user waves goodbye (???) the client displays "goodbye" and returns to the camera view where it is tracking for faces.

ADDITIONAL PRINT COMMANDS... (ADD HERE GUYS)
