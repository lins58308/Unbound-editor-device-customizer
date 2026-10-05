"""Cooperative controller shutdown and consistent high-DPI Windows icons.

Keep the existing dispatch, configuration, UI and language code. Never wait for
HID, UI Automation or OBS on the Qt GUI thread; keep Qt alive until they stop.
"""
import ctypes, json, pathlib, queue, sys, threading, time, weakref
from ctypes import wintypes
from PyQt6.QtCore import QObject, QTimer, Qt, QRectF
from PyQt6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

STOP_EVENT = threading.Event()
HID_WORKERS = weakref.WeakSet()
ICON_SIZES = (16,20,24,32,40,48,64,128,256)

def controller_pixmap(size):
    """Render every icon resolution separately, with no font or scaling blur."""
    pixmap=QPixmap(size,size);pixmap.fill(Qt.GlobalColor.transparent)
    painter=QPainter(pixmap);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size/64,size/64)
    gradient=QLinearGradient(0,0,64,64)
    gradient.setColorAt(0,QColor('#7668f7'));gradient.setColorAt(1,QColor('#4937c6'))
    painter.setPen(Qt.PenStyle.NoPen);painter.setBrush(gradient)
    painter.drawRoundedRect(QRectF(1,1,62,62),14,14)
    painter.setBrush(QColor('#f4f2ff'))
    for x,y in ((11,15),(24,15),(11,29),(24,29)):
        painter.drawRoundedRect(QRectF(x,y,9,9),2.5,2.5)
    # A solid center and complete ring stay readable in the 16 px tray icon.
    painter.setBrush(QColor('#25175f'));painter.drawEllipse(QRectF(37,21,21,21))
    painter.setBrush(Qt.BrushStyle.NoBrush);painter.setPen(QPen(QColor('#f4f2ff'),2.5))
    painter.drawEllipse(QRectF(41,25,13,13))
    painter.setPen(QPen(QColor('#f4f2ff'),2.5,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
    painter.drawLine(47,26,47,30)
    painter.end();return pixmap

def controller_icon():
    image=QIcon()
    for size in ICON_SIZES:image.addPixmap(controller_pixmap(size))
    return image

def native_icon(path,size=64):
    """Recover alpha reliably, including older icons with an empty alpha plane.

    Draw the HICON on black and white. The difference gives its real coverage,
    without uninitialized DIB memory or the black boxes of legacy AND masks.
    """
    from PyQt6.QtGui import QImage
    shell=ctypes.WinDLL('shell32');user=ctypes.WinDLL('user32');gdi=ctypes.WinDLL('gdi32')
    shell.ExtractIconExW.argtypes=[wintypes.LPCWSTR,ctypes.c_int,ctypes.POINTER(wintypes.HICON),ctypes.POINTER(wintypes.HICON),ctypes.c_uint]
    shell.ExtractIconExW.restype=ctypes.c_uint
    user.DrawIconEx.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.HICON,ctypes.c_int,ctypes.c_int,ctypes.c_uint,wintypes.HBRUSH,ctypes.c_uint]
    user.DestroyIcon.argtypes=[wintypes.HICON]
    gdi.CreateCompatibleDC.argtypes=[wintypes.HDC];gdi.CreateCompatibleDC.restype=wintypes.HDC
    gdi.CreateDIBSection.argtypes=[wintypes.HDC,ctypes.c_void_p,ctypes.c_uint,ctypes.POINTER(ctypes.c_void_p),wintypes.HANDLE,ctypes.c_uint];gdi.CreateDIBSection.restype=wintypes.HBITMAP
    gdi.SelectObject.argtypes=[wintypes.HDC,wintypes.HANDLE];gdi.SelectObject.restype=wintypes.HANDLE
    gdi.DeleteObject.argtypes=[wintypes.HANDLE];gdi.DeleteDC.argtypes=[wintypes.HDC]
    class Header(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('width',wintypes.LONG),('height',wintypes.LONG),('planes',wintypes.WORD),('bits',wintypes.WORD),('compression',wintypes.DWORD),('image',wintypes.DWORD),('x',wintypes.LONG),('y',wintypes.LONG),('used',wintypes.DWORD),('important',wintypes.DWORD)]
    large=wintypes.HICON();small=wintypes.HICON()
    # Request the actual display size, rather than enlarging a default 32 px
    # shell icon. Windows selects the best image in the executable's icon group.
    extract=shell.SHDefExtractIconW
    extract.argtypes=[wintypes.LPCWSTR,ctypes.c_int,ctypes.c_uint,ctypes.POINTER(wintypes.HICON),ctypes.POINTER(wintypes.HICON),ctypes.c_uint]
    extract.restype=ctypes.c_long
    result=extract(str(path),0,0,ctypes.byref(large),ctypes.byref(small),size|(size<<16))
    if result!=0 or not large:
        for stale in (large,small):
            if stale:user.DestroyIcon(stale)
        large=wintypes.HICON();small=wintypes.HICON()
        if not shell.ExtractIconExW(str(path),0,ctypes.byref(large),ctypes.byref(small),1):return None
    handle=small if size<=24 and small else large or small
    dc=gdi.CreateCompatibleDC(None);bitmap=None;old=None
    try:
        header=Header(40,size,-size,1,32,0,0,0,0,0,0);bits=ctypes.c_void_p()
        bitmap=gdi.CreateDIBSection(dc,ctypes.byref(header),0,ctypes.byref(bits),None,0)
        if not bitmap or not bits.value:return None
        old=gdi.SelectObject(dc,bitmap);planes=[]
        for background in (0,255):
            fill=bytes((background,background,background,255))*(size*size)
            ctypes.memmove(bits.value,fill,len(fill))
            if not user.DrawIconEx(dc,0,0,handle,size,size,0,None,3):return None
            planes.append(ctypes.string_at(bits.value,len(fill)))
        black,white=planes;result=bytearray(len(black))
        for offset in range(0,len(black),4):
            alpha=255-max(max(0,white[offset+i]-black[offset+i]) for i in range(3))
            result[offset:offset+4]=bytes((*[min(alpha,black[offset+i]) for i in range(3)],alpha))
        image=QImage(bytes(result),size,size,QImage.Format.Format_ARGB32_Premultiplied).copy()
        return QIcon(QPixmap.fromImage(image))
    finally:
        if old:gdi.SelectObject(dc,old)
        if bitmap:gdi.DeleteObject(bitmap)
        if dc:gdi.DeleteDC(dc)
        for handle in (large,small):
            if handle:user.DestroyIcon(handle)

def monitor_stop(monitor):
    """Signal only: an active COM transaction must finish on its own worker."""
    monitor.stop_event.set()
    # Wake a queue wait without issuing a player action.
    try:monitor.commands.put_nowait((0,{},'',lambda *args:None,False))
    except queue.Full:pass

def register_hid_worker():
    HID_WORKERS.add(threading.current_thread())

def release_inputs(bridge):
    if bridge is None:return
    with bridge.lock:
        # Use the original release path, so hold actions and temporary layers
        # unwind exactly as they do on a physical button release.
        bridge.key_callback([])
        bridge.release_mouse()
        import app
        toggles=bridge.cells['_toggle_holds'].cell_contents
        for keys in list(toggles.values()):app.hotkey_action.release_keys(keys)
        toggles.clear()

class Shutdown(QObject):
    def __init__(self,owner):
        super().__init__(owner);self.owner=owner;self.started=False;self.finished=False
        self.started_at=0;self.release_worker=None;self.elapsed=0;self.polls=0
        self.timer=QTimer(self);self.timer.setInterval(20);self.timer.timeout.connect(self.poll)

    def request_mouse_release(self):
        bridge=self.owner._context.bridge
        if bridge is not None and bridge.lock.acquire(blocking=False):
            try:bridge.release_mouse()
            finally:bridge.lock.release()
        # A busy callback is released by the shutdown worker, never joined here.

    def begin(self):
        if self.started:return
        self.started=True;self.started_at=time.monotonic();STOP_EVENT.set()
        owner=self.owner;owner._context.monitor.stop()
        owner._expanded_discovery.active=False;owner._expanded_obs.stop()
        def release():
            try:release_inputs(owner._context.bridge)
            except (RuntimeError,OSError):pass
        self.release_worker=threading.Thread(target=release,name='Controller input release',daemon=True)
        self.release_worker.start();self.timer.start()

    def workers(self):
        result=list(HID_WORKERS)
        for candidate in (self.owner._context.monitor.worker,self.owner._expanded_obs.worker,self.release_worker):
            if candidate is not None:result.append(candidate)
        # Discovery owns no device callback, but finish its COM apartment before
        # interpreter finalization. This does not wait or poll busy on the GUI.
        result.extend(t for t in threading.enumerate() if t.name=='Startup application discovery')
        return [t for t in result if t is not threading.current_thread() and t.is_alive()]

    def poll(self):
        if self.finished:return
        self.polls+=1
        if self.workers():return
        self.finished=True;self.timer.stop();self.elapsed=time.monotonic()-self.started_at
        QApplication.instance().quit()

def install():
    import app, speed_editor_background as background, speed_editor_context_icons as icons
    import speed_editor_foreground as foreground, hid_layer
    if getattr(app,'_performance_installed',False):return
    app._performance_installed=True
    # Use the same artwork in Explorer, the main window, floating guide and tray.
    previous_icon=icons.icon;previous_vector=icons.vector_icon
    icons.native_icon=native_icon
    def icon(identifier):
        if identifier=='controller':
            if identifier not in icons._CACHE:icons._CACHE[identifier]=controller_icon()
            return icons._CACHE[identifier]
        return previous_icon(identifier)
    icons.icon=icon
    icons.vector_icon=lambda identifier,size=128:controller_pixmap(size) if identifier=='controller' else previous_vector(identifier,size)
    icons._CACHE.clear()
    # Modules imported the original icon function by value. Its existing cache
    # now contains the correct shared icon; custom app native extraction also
    # calls the replacement through the original function's globals.
    icons._CACHE['controller']=controller_icon() if QApplication.instance() else None
    if icons._CACHE['controller'] is None:icons._CACHE.pop('controller')
    foreground.ForegroundMonitor.stop=monitor_stop
    original_device_init=hid_layer.SpeedEditor.__init__
    original_auth=hid_layer.SpeedEditor.authenticate
    original_device_close=hid_layer.SpeedEditor.close
    def device_init(device,*args,**kwargs):
        device._shutdown_io_lock=threading.RLock()
        return original_device_init(device,*args,**kwargs)
    def authenticate(device):
        with device._shutdown_io_lock:
            if not STOP_EVENT.is_set():return original_auth(device)
    def device_close(device):
        with device._shutdown_io_lock:
            if getattr(device,'dev',None) is not None:return original_device_close(device)
    def run(device):
        handlers={3:device._handle_03,4:device._handle_04,7:device._handle_07}
        while not STOP_EVENT.is_set():
            report=device.dev.read(64,100)
            if STOP_EVENT.is_set():break
            if report:
                handler=handlers.get(report[0])
                if handler:handler(report)
                else:print('[unhandled]',bytes(report[:8]).hex())
    hid_layer.SpeedEditor.__init__=device_init
    hid_layer.SpeedEditor.authenticate=authenticate
    hid_layer.SpeedEditor.close=device_close
    hid_layer.SpeedEditor.run=run
    old_init=app.MainWindow.__init__
    # The final existing close wrapper owns the tray decision. Retain its full
    # earlier chain, including the original save/discard/cancel dialog.
    close_cells=dict(zip(app.MainWindow.closeEvent.__code__.co_freevars,app.MainWindow.closeEvent.__closure__))
    earlier_close=close_cells['old_close'].cell_contents
    def init(owner,*args,**kwargs):
        old_init(owner,*args,**kwargs)
        owner._shutdown=Shutdown(owner);owner._desktop_release_mouse=owner._shutdown.request_mouse_release
        image=controller_icon();icons._CACHE['controller']=image
        owner.setWindowIcon(image);QApplication.instance().setWindowIcon(image)
        owner._background.tray.setIcon(image);owner._expanded_overlay.setWindowIcon(image)
        owner.setWindowTitle(owner.windowTitle().replace('7.4','7.5'))
    def close(owner,event):
        tray=owner._background
        if owner._shutdown.started:
            event.accept();return
        if (not tray.exiting and not QApplication.instance().isSavingSession()
                and background.preferences(owner._config)['close_to_tray'] and tray.available()):
            event.ignore();tray.hide_window();return
        earlier_close(owner,event)
        if event.isAccepted():
            tray.cleanup();owner._shutdown.begin()
    def quit(tray,checked=False):
        if tray.exiting or tray.stopped:return
        tray.show_window();tray.exiting=True
        try:tray.owner.close()
        finally:tray.exiting=False
    original_refresh=background.Background.refresh
    def refresh(tray):
        original_refresh(tray)
        if not tray.stopped:tray.tray.setToolTip(tray.tray.toolTip().replace('Speed Editor 7.4','Speed Editor 7.5'))
    app.MainWindow.__init__=init;app.MainWindow.closeEvent=close
    background.Background.quit=quit;background.Background.refresh=refresh
    # Qt widgets use the CPU raster painter; none of this program uses OpenGL.
    # Do not request a bundled software OpenGL fallback on startup.
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL,False)
    try:
        shell=ctypes.WinDLL('shell32')
        shell.SetCurrentProcessExplicitAppUserModelID.argtypes=[wintypes.LPCWSTR]
        shell.SetCurrentProcessExplicitAppUserModelID('SpeedEditorCustomizer.Community')
    except OSError:pass
