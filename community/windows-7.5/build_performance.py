"""Build community 7.5 from verified 7.4; remove audited optional baggage."""
import argparse, ctypes, hashlib, json, marshal, os, pathlib, struct, sys, types, zlib
from ctypes import wintypes
from portable_archive import read,raw,script,write
ROOT=pathlib.Path(__file__).resolve().parent
BASE_SHA='933dd971567782bf16aa99244310f628df2548738e3d39a3f4f00d250e6f40e4'
REMOVE={'PyQt6\\Qt6\\bin\\opengl32sw.dll','PyQt6\\Qt6\\bin\\Qt6Pdf.dll',
        'PyQt6\\Qt6\\plugins\\imageformats\\qpdf.dll','Pythonwin\\mfc140u.dll','Pythonwin\\win32ui.pyd'}
HID_SOURCE='''
def factory():
    _se=on_jog=on_key=signals=time=None
    def hid_thread():
        nonlocal _se
        from speed_editor_performance import STOP_EVENT, register_hid_worker
        register_hid_worker()
        clock=time.monotonic
        while not STOP_EVENT.is_set():
            try:
                se=SpeedEditor()
                _se=se
                if STOP_EVENT.is_set():break
                print('[HID] Device connected.')
                signals.device_status.emit('已連線')
                se.on_key=on_key
                se.on_jog=on_jog
                se.authenticate()
                se.run()
            except OSError as error:
                if not STOP_EVENT.is_set():
                    print('[HID] Device not found, retrying in 3s… ('+str(error)+')')
                    signals.device_status.emit('尚未連線 — 正在重試…')
            except Exception as error:
                if not STOP_EVENT.is_set():
                    print('[HID] Error: '+str(error))
                    signals.device_status.emit('錯誤：'+str(error))
            finally:
                try:
                    if _se:_se.close()
                except Exception:pass
                _se=None
            STOP_EVENT.wait(3)
    return hid_thread
'''

def patch_hid(code,replacement,changes):
    if code.co_name in ('_hid_loop','hid_thread'):
        assert code.co_freevars==replacement.co_freevars,(code.co_freevars,replacement.co_freevars)
        changes.append(code.co_name)
        return replacement.replace(co_name=code.co_name,co_qualname=code.co_qualname)
    return code.replace(co_consts=tuple(patch_hid(c,replacement,changes) if isinstance(c,types.CodeType) else c for c in code.co_consts))

def make_icon(items):
    # Reuse the verified package's Qt runtime for deterministic icon rendering.
    # Building therefore needs no private installation or separate PyQt install.
    source=ROOT/'build-qt-runtime-v75';source.mkdir(exist_ok=True)
    for item in items:
        if item[1] in (b'b',b'x'):
            relative=pathlib.PureWindowsPath(item[0])
            assert not relative.is_absolute() and '..' not in relative.parts
            target=source.joinpath(*relative.parts);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw(item))
    os.environ['QT_QPA_PLATFORM']='offscreen'
    os.environ['QT_PLUGIN_PATH']=str(source/'PyQt6/Qt6/plugins')
    handles=[os.add_dll_directory(str(path)) for path in (source,source/'PyQt6/Qt6/bin')]
    package=types.ModuleType('PyQt6');package.__path__=[str(source/'PyQt6')]
    package.__file__=str(source/'PyQt6/__init__.py');sys.modules['PyQt6']=package
    from PyQt6.QtWidgets import QApplication
    from performance_runtime import controller_pixmap,ICON_SIZES
    from PIL import Image
    app=QApplication([]);folder=ROOT/'icon-v75';folder.mkdir(exist_ok=True)
    frames=[]
    for size in ICON_SIZES:
        target=folder/(str(size)+'.png');controller_pixmap(size).save(str(target))
        frames.append(Image.open(target).copy())
    path=ROOT/'SpeedEditorCustomizer-v7.5.ico'
    frames[-1].save(path,format='ICO',sizes=[(s,s) for s in ICON_SIZES],append_images=frames[:-1])
    return path.read_bytes()

def update_icon(stub,ico):
    path=ROOT/'v75-icon-stub.exe';path.write_bytes(stub)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.BeginUpdateResourceW.argtypes=[wintypes.LPCWSTR,wintypes.BOOL];kernel.BeginUpdateResourceW.restype=wintypes.HANDLE
    kernel.UpdateResourceW.argtypes=[wintypes.HANDLE,ctypes.c_void_p,ctypes.c_void_p,wintypes.WORD,ctypes.c_void_p,wintypes.DWORD];kernel.UpdateResourceW.restype=wintypes.BOOL
    kernel.EndUpdateResourceW.argtypes=[wintypes.HANDLE,wintypes.BOOL];kernel.EndUpdateResourceW.restype=wintypes.BOOL
    handle=kernel.BeginUpdateResourceW(str(path),False);assert handle,ctypes.get_last_error()
    reserved,kind,count=struct.unpack_from('<HHH',ico);group=bytearray(struct.pack('<HHH',reserved,kind,count))
    try:
        for index in range(count):
            w,h,colors,zero,planes,bits,size,offset=struct.unpack_from('<BBBBHHII',ico,6+16*index)
            blob=ico[offset:offset+size];buffer=ctypes.create_string_buffer(blob)
            assert kernel.UpdateResourceW(handle,ctypes.c_void_p(3),ctypes.c_void_p(index+1),0,buffer,size),ctypes.get_last_error()
            group.extend(struct.pack('<BBBBHHIH',w,h,colors,zero,planes,bits,size,index+1))
        buffer=ctypes.create_string_buffer(bytes(group))
        assert kernel.UpdateResourceW(handle,ctypes.c_void_p(14),ctypes.c_void_p(1),0,buffer,len(group)),ctypes.get_last_error()
    except BaseException:
        kernel.EndUpdateResourceW(handle,True);raise
    assert kernel.EndUpdateResourceW(handle,False),ctypes.get_last_error()
    return path.read_bytes()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=pathlib.Path,default=ROOT/'SpeedEditorCustomizer-Portable-v74.exe')
    parser.add_argument('--output',type=pathlib.Path,default=ROOT/'SpeedEditorCustomizer-Portable-v75.exe');args=parser.parse_args()
    assert sys.version_info[:2]==(3,12),'Use Python 3.12, matching the verified application runtime.'
    data=args.baseline.read_bytes();assert hashlib.sha256(data).hexdigest()==BASE_SHA
    stub,items,metadata=read(data);source=(ROOT/'performance_runtime.py').read_text(encoding='utf8')
    loader=('import sys,types\nmod=types.ModuleType("speed_editor_performance")\nmod.__file__="performance_runtime.py"\n'
            'sys.modules[mod.__name__]=mod\n'+f'exec(compile({source!r},mod.__file__,"exec"),mod.__dict__)\nmod.install()\n')
    addon=script('_performance_upgrade',compile(loader,'_performance_upgrade.py','exec'))
    parent=next(c for c in compile(HID_SOURCE,'cooperative_hid.py','exec').co_consts if isinstance(c,types.CodeType))
    replacement=next(c for c in parent.co_consts if isinstance(c,types.CodeType))
    packed=[];removed=[];changes=[];retained=[]
    for item in items:
        if item[0] in REMOVE:
            removed.append({'name':item[0],'compressed':len(item[4]),'original':item[3]});continue
        if item[0]=='main':
            packed.append(addon);item=script('main',patch_hid(marshal.loads(raw(item)),replacement,changes))
        elif item[2]:
            blob=zlib.compress(raw(item),9)
            if len(blob)<len(item[4]):item=(*item[:4],blob)
        packed.append(item);retained.append(item[0])
    assert len(changes)==1,changes
    ico=make_icon(packed);newstub=update_icon(stub,ico)
    result=write(newstub,packed,metadata);args.output.write_bytes(result)
    proof={'version':'7.5','baseline_sha256':BASE_SHA,'baseline_bytes':len(data),'portable_sha256':hashlib.sha256(result).hexdigest(),
           'portable_bytes':len(result),'reduction_bytes':len(data)-len(result),'reduction_percent':round(100*(len(data)-len(result))/len(data),2),
           'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'removed_optional_payloads':removed,'hid_retry_loop_changed':changes,
           'retained_payloads_unchanged_except_hid_loop':all(raw(next(x for x in items if x[0]==name))==raw(next(x for x in packed if x[0]==name)) for name in retained if name!='main'),
           'icon_sha256':hashlib.sha256(ico).hexdigest(),'icon_sizes':[16,20,24,32,40,48,64,128,256]}
    (ROOT/'performance_build.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))

if __name__=='__main__':main()
