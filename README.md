<h1 align="center">Программа для подсчета времени работы приложений.</h1>

<p><b>setting_console.py - запуск и остановка программы регулируется только в этой консоли</b>.</p>

<h3>Файл с записанным временем имеет следующий вид (пример):</h3>


<p><br>
==============  LOOKING  ===============<br>
<br>
PyCharm                             01:06:09<br>
Telegram                            02:05:59<br>
Chrome                              01:50:59<br>
<br>
================  ALL  =================<br>
<br>
py.exe                              00:54:34<br>
DCv2.exe                            02:38:52<br>
backgroundTaskHost.exe              00:00:56<br>
CalculatorApp.exe                   00:32:49<br>
BackgroundDownload.exe              00:01:01<br>
ms-teamsupdate.exe                  00:00:08<br>
pycharm64.exe                       01:06:09<br>
notepad.exe                         00:09:54<br>
<br>
</p>

<h2>Настройка отслеживаемых приложений (LOOKING):</h2><br>
<p><b>data/apps.json</b>  ->  добавить в словарь необходжимое приложение<br>
<b>пример:</b> "pycharm64.exe": "PyCharm"<br></p>

<h2>Настройка игнорируемых процессов (не будут записаны нигде):</h2><br>
<p><b>data/process_ignore.json</b>  ->  добавить в список необходжимый процесс<br>
<b>пример:</b> "System Idle Process", "System", "Registry"<br></p>
<br>

<h2>Настройки конфигов</h2>

<p>файл:  configs/config.ini<br>

<b>path</b> - путь сохранения файла с записями (по умолчанию - .)<br>
<b>pause</b> - временой интервал между записью в файл в сек (по умолчанию - 10)<br>

<b>остальное настраивается программой</b><br>
(при сбоях все переменные в **[STATUS]** установить на **0**)</p>
  
