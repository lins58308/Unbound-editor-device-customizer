"""Package the same 7.5 runtime without repeated temporary extraction."""
import argparse,hashlib,json,pathlib
from portable_archive import read,raw,write
ROOT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--exe',type=pathlib.Path,default=ROOT/'SpeedEditorCustomizer-Portable-v75.exe')
parser.add_argument('--out',type=pathlib.Path,default=ROOT/'portable-folder-v75');args=parser.parse_args()
data=args.exe.read_bytes();stub,items,metadata=read(data)
folder=args.out.resolve();folder.mkdir(parents=True,exist_ok=True);internal=folder/'_internal';internal.mkdir(exist_ok=True)
kept=[];files=[]
for item in items:
    if item[1] in (b'b',b'x'):
        relative=pathlib.PureWindowsPath(item[0])
        assert not relative.is_absolute() and '..' not in relative.parts
        path=internal.joinpath(*relative.parts);path.parent.mkdir(parents=True,exist_ok=True)
        payload=raw(item);path.write_bytes(payload)
        files.append({'path':str(path.relative_to(folder)).replace('\\','/'),'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
    else:kept.append(item)
kept.append(('pyi-contents-directory _internal',b'o',0,0,b''))
result=write(stub,kept,metadata);(folder/'SpeedEditorCustomizer.exe').write_bytes(result)
proof={'version':'7.5','standalone_source_sha256':hashlib.sha256(data).hexdigest(),'exe_sha256':hashlib.sha256(result).hexdigest(),
       'exe_bytes':len(result),'runtime_bytes':sum(x['bytes'] for x in files),'runtime_files':files,'repeated_extraction':False}
(folder/'folder-build.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
if args.exe.resolve()==(ROOT/'SpeedEditorCustomizer-Portable-v75.exe').resolve():
    (ROOT/'folder_build.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in proof.items() if k!='runtime_files'}))
