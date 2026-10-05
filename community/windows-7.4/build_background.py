"""Append a tray addon to the delivered v7.2 without changing any baseline payload."""
import hashlib, json, marshal, pathlib, struct, types, zlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
BASE_SHA = '104412c6ca47568c95b6e9d0f3e4e72598dd26c6d4a893899b1632fecc92b3d7'
baseline = pathlib.Path(sys.argv[1])
data = baseline.read_bytes()
assert hashlib.sha256(data).hexdigest() == BASE_SHA
source = (ROOT / 'background_runtime.py').read_text(encoding='utf8')
guide = ('背景執行與系統匣', '背景 最小化 關閉 系統匣 圖示 結束 啟動',
         '<h1>收起視窗，控制器繼續運作。</h1><p>按主視窗右上角關閉或最小化，程式會收至右下角系統匣。自動切換、固定滑鼠與浮動面板保持運作，未儲存的編輯也會保留。</p>'
         '<p>單擊或雙擊 Speed Editor 圖示可重新開啟；右鍵可顯示浮動按鍵面板、調整滑鼠穿透及查看說明。若看不到圖示，請展開右下角「︿」。</p>'
         '<p>到「背景執行」調整關閉、最小化及下次啟動直接在背景執行。這些設定立即儲存。</p>'
         '<p>要完全停止程式，請在系統匣右鍵選「結束程式」。若有未儲存的按鍵編輯，仍會先提示儲存、捨棄或取消。背景執行不代表 Windows 開機自動啟動。</p>')
loader = ('import sys,types\n'
          'mod=types.ModuleType("speed_editor_background")\n'
          'mod.__file__="background_runtime.py"\n'
          'sys.modules[mod.__name__]=mod\n'
          f'exec(compile({source!r},mod.__file__,"exec"),mod.__dict__)\n'
          'from speed_editor_glass_help import SECTIONS\n'
          f'SECTIONS.insert(2,{guide!r})\n'
          'mod.install()\n')
# Keep the mouse guide's existing index (1) and all previous contents intact.
raw = marshal.dumps(compile(loader, '_background_upgrade.py', 'exec'))
addon = ('_background_upgrade', b's', 1, len(raw), zlib.compress(raw))
at = data.rfind(b'MEI\x0c\x0b\x0a\x0b\x0e')
magic, length, toc_offset, toc_size, version, lib = struct.unpack('!8sIIII64s', data[at:at+88])
start = at + 88 - length
cursor = start + toc_offset
entries = []
while cursor < start + toc_offset + toc_size:
    size, offset, compressed, original, flag, kind = struct.unpack('!iIIIBc', data[cursor:cursor+18])
    name = data[cursor+18:cursor+size].split(b'\0', 1)[0].decode()
    cursor += size
    if name == 'main':
        entries.append(addon)
    entries.append((name, kind, flag, original, data[start+offset:start+offset+compressed]))
payload, table, offset = [], [], 0
for name, kind, flag, original, blob in entries:
    encoded = name.encode() + b'\0'
    size = (18 + len(encoded) + 15) // 16 * 16
    table.append(struct.pack('!iIIIBc', size, offset, len(blob), original, flag, kind)
                 + encoded + b'\0' * (size - 18 - len(encoded)))
    payload.append(blob)
    offset += len(blob)
table = b''.join(table)
target = pathlib.Path(sys.argv[2])
target.write_bytes(data[:start] + b''.join(payload) + table
                   + struct.pack('!8sIIII64s', magic, offset+len(table)+88,
                                 offset, len(table), version, lib))
proof = {'version':'7.3', 'baseline_sha256':BASE_SHA,
         'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
         'portable_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
         'portable_bytes':target.stat().st_size, 'original_payloads_unchanged':True}
(ROOT/'background_build.json').write_text(json.dumps(proof, indent=2), encoding='utf8')
print(json.dumps(proof))
