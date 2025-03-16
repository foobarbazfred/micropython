to transfer file

(1)ampy

ampy -p <dev> <cmd>
cmd := 
  get    Retrieve a file from the board.
  ls     List contents of a directory on the board.
  mkdir  Create a directory on the board.
  put    Put a file or folder and its contents on the board.
  reset  Perform soft reset/reboot of the board.
  rm     Remove a file from the board.
  rmdir  Forcefully remove a folder and all its children from the board.
  run    Run a script and print its output.

$ ampy -p /dev/ttyS12 put upysh.py   /lib/upysh.py
$ ampy -p /dev/ttyS12 ls  /lib
/lib/upysh.py
