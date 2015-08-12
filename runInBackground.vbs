Dim WinScriptHost
Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run Chr(34) & "D:\projects\random-wallpaper\setWallPaper.cmd" & Chr(34), 0
Set WinScriptHost = Nothing