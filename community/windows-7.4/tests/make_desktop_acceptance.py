"""Replace only main in the portable candidate; retain its real bootloader and all startup/runtime files."""
import pathlib,struct,marshal,zlib,hashlib,sys,argparse
work=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--main',default='native_desktop_acceptance.py');parser.add_argument('--out',default='portable acceptance v5');parser.add_argument('--name',default='Portable Test.exe');parser.add_argument('--exe',default='SpeedEditorCustomizer-Portable.exe');args=parser.parse_args()
exe=(work/args.exe).read_bytes()
at=exe.rfind(b'MEI\x0c\x0b\x0a\x0b\x0e');magic,length,toc_off,toc_size,version,lib=struct.unpack('!8sIIII64s',exe[at:at+88]);start=at+88-length
source=(work/args.main).read_text(encoding='utf8').replace('__SOURCE_SHA256__',hashlib.sha256(exe).hexdigest())
code=marshal.dumps(compile(source,'main.py','exec'))
items=[];table=[];offset=0;cursor=start+toc_off
while cursor<start+toc_off+toc_size:
    size,pos,compressed,rawsize,flag,kind=struct.unpack('!iIIIBc',exe[cursor:cursor+18]);name=exe[cursor+18:cursor+size].split(b'\0',1)[0]
    payload=exe[start+pos:start+pos+compressed]
    if name==b'main':payload=zlib.compress(code);rawsize=len(code);flag=1
    if name==b'_context_upgrade':
        original=zlib.decompress(payload) if flag else payload
        wrapped='import os,marshal\nos.environ["SPEED_EDITOR_OFFLINE_TEST"]="1"\nexec(marshal.loads(bytes.fromhex('+repr(original.hex())+')),globals())'
        raw=marshal.dumps(compile(wrapped,'_context_upgrade.py','exec'));payload=zlib.compress(raw);rawsize=len(raw);flag=1
    if name in (b'main',b'_localization_zh_tw',b'_usability_upgrade',b'_editing_tools',b'_application_catalog',b'_context_upgrade',b'_desktop_upgrade',b'_expanded_upgrade'):
        original=zlib.decompress(payload) if flag else payload
        wrapped='import marshal,sys,pathlib,traceback\ntry:\n    exec(marshal.loads(bytes.fromhex('+repr(original.hex())+')),globals())\nexcept Exception:\n    pathlib.Path(sys.executable).with_name("acceptance-bootstrap-error.txt").write_text(traceback.format_exc(),encoding="utf8")\n    sys.exit(1)'
        raw=marshal.dumps(compile(wrapped,name.decode()+'.py','exec'));payload=zlib.compress(raw);rawsize=len(raw);flag=1
    table.append(struct.pack('!iIIIBc',size,offset,len(payload),rawsize,flag,kind)+name+b'\0'*(size-18-len(name)));items.append(payload);offset+=len(payload);cursor+=size
target=work/args.out;target.mkdir(exist_ok=True)
assert not (target/'_internal').exists()
table=b''.join(table)
path=target/args.name;path.write_bytes(exe[:start]+b''.join(items)+table+struct.pack('!8sIIII64s',magic,offset+len(table)+88,offset,len(table),version,lib))
print(str(path))
