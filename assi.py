from unittest import case
import win32com.client
import os
import subprocess
inp=input("Enter the application to open (excel/notepad/word): ")
match inp:
    case "notepad":
        os.system("notepad")
    case "chrome":
        os.system("start chrome")
    case "calculator":
        os.system("calc")
    case "excel":
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        workbook = excel.Workbooks.Add()
    case "word":
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        document = word.Documents.Add()
    case "cmd":
     process = subprocess.Popen("cmd.exe", shell=True)