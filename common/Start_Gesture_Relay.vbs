Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\monar"
WshShell.Run "pythonw.exe gesture_relay.py", 0, False