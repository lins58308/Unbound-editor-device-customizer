"""Real Qt/frozen runtime; isolated settings and deliberately slow UIA worker.

No hardware is opened, no external input is sent, and no accounts connect.
"""
import os,sys,pathlib,copy,json,time,threading
import app,config as cfg,auth
from actions import obs
from PyQt6.QtCore import QTimer,QEvent
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import speed_editor_context as context
import speed_editor_usability as ux
import speed_editor_foreground as foreground
ROOT=pathlib.Path(sys.executable).parent
cfg.CONFIG_FILE=str(ROOT/'config.json');auth.is_signed_in=lambda:False;auth.get_user_email=lambda:''
obs.client.connect=lambda *args,**kwargs:False;obs.client.get_scenes=lambda:[]
app.hotkey_action.send=lambda *args:None
from speed_editor_desktop_input import __dict__ as inputs
inputs['OUTPUT']=lambda *args:None
ux.atomic_save(copy.deepcopy(cfg.DEFAULT_CONFIG));application=QApplication([])
application.setStyle('Fusion');application.setFont(QFont('Microsoft JhengHei UI',10))
context.OFFLINE=True
window=app.MainWindow();window.show()
# Avoid inspecting any user application in this reproducible stall test.
monitor=window._context.monitor
started=threading.Event()
def slow_worker():
    started.set();time.sleep(2)
monitor.worker=threading.Thread(target=slow_worker,name='Foreground profiles',daemon=True)
monitor.worker.start()
report={'source_sha256':'__SOURCE_SHA256__','mode':getattr(sys,'_MEIPASS',''),
        'request_seconds':None,'quit_seconds':None,'heartbeat_max_gap':0,'heartbeat_count_after_request':0}
ticks=[];requested=[None]
timer=QTimer(application);timer.setInterval(20)
def heartbeat():
    now=time.monotonic()
    if ticks:report['heartbeat_max_gap']=max(report['heartbeat_max_gap'],now-ticks[-1])
    ticks.append(now)
    if requested[0] is not None:report['heartbeat_count_after_request']+=1
timer.timeout.connect(heartbeat);timer.start()
def quit_now():
    requested[0]=time.monotonic()
    window._background.quit_action.trigger()
    report['request_seconds']=time.monotonic()-requested[0]
QTimer.singleShot(120,quit_now)
def finished():
    report['quit_seconds']=time.monotonic()-requested[0]
    report['all_workers_stopped']=not monitor.worker.is_alive() and not window._expanded_obs.worker.is_alive()
    report['tray_hidden']=not window._background.tray.isVisible()
    report['config_exists']=pathlib.Path(cfg.CONFIG_FILE).is_file()
    report['icon_sizes']=[s.width() for s in window.windowIcon().availableSizes()]
    report['temporary_extraction']='_MEI' in str(getattr(sys,'_MEIPASS',''))
application.aboutToQuit.connect(finished)
code=application.exec();report['exit_code']=code
(ROOT/'performance-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
for top in QApplication.topLevelWidgets():top.deleteLater()
QApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
sys.exit(code)
