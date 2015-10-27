python = "c:\\python34\\pythonw.exe"

Dim WinScriptHost
Set WinScriptHost = CreateObject("WScript.Shell")
strPath = Wscript.ScriptFullName
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile) 
WinScriptHost.CurrentDirectory = strFolder
WinScriptHost.Run python & " " & strFolder & "\\randompick.py ", 0
Set WinScriptHost = Nothing