"""Minimal deterministic reader/writer for the existing PyInstaller package."""
import marshal, struct, zlib
MAGIC = b'MEI\x0c\x0b\x0a\x0b\x0e'

def read(data):
    at = data.rfind(MAGIC)
    cookie = struct.unpack('!8sIIII64s', data[at:at+88])
    magic, length, toc_offset, toc_size, version, library = cookie
    start = at + 88 - length
    items = []; cursor = start + toc_offset
    while cursor < start + toc_offset + toc_size:
        size, offset, packed, raw_size, flag, kind = struct.unpack('!iIIIBc', data[cursor:cursor+18])
        name = data[cursor+18:cursor+size].split(b'\0',1)[0].decode()
        items.append((name,kind,flag,raw_size,data[start+offset:start+offset+packed]))
        cursor += size
    return data[:start], items, (magic,version,library)

def raw(item):
    return zlib.decompress(item[4]) if item[2] else item[4]

def script(name, code):
    blob = marshal.dumps(code)
    return name, b's', 1, len(blob), zlib.compress(blob,9)

def write(stub,items,metadata):
    magic,version,library = metadata
    payload=[];table=[];offset=0
    for name,kind,flag,original,blob in items:
        encoded=name.encode()+b'\0'; size=(18+len(encoded)+15)//16*16
        table.append(struct.pack('!iIIIBc',size,offset,len(blob),original,flag,kind)+encoded+b'\0'*(size-18-len(encoded)))
        payload.append(blob);offset+=len(blob)
    toc=b''.join(table)
    return stub+b''.join(payload)+toc+struct.pack('!8sIIII64s',magic,offset+len(toc)+88,offset,len(toc),version,library)
