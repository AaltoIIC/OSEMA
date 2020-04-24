"""Removes the old main.py and renames the new_main.txt to main.py in boot-up"""

import uos

filenames = uos.listdir()
for filename in filenames:
    if filename == "new_main.txt":
        uos.remove("main.py")
        uos.rename("new_main.txt", "main.py")
        break
