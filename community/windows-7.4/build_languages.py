"""Add offline 12-language UI to the verified 7.3, preserving every payload."""
import argparse, hashlib, json, marshal, pathlib, struct, zlib
ROOT = pathlib.Path(__file__).resolve().parent
BASE_SHA = '12e605d8f568489e033fb25f8ba1d627d0deec8431aecb75fc37c2609e830991'
parser = argparse.ArgumentParser()
parser.add_argument('--baseline', type=pathlib.Path, default=ROOT/'SpeedEditorCustomizer-Portable-v73.exe')
parser.add_argument('--output', type=pathlib.Path, default=ROOT/'SpeedEditorCustomizer-Portable-v74.exe')
parser.add_argument('--development', action='store_true')
args = parser.parse_args()
data = args.baseline.read_bytes()
assert hashlib.sha256(data).hexdigest() == BASE_SHA, 'The verified 7.3 baseline is required.'
source = (ROOT/'language_runtime.py').read_text(encoding='utf8')
public = json.loads((ROOT/'locales/source.json').read_text(encoding='utf8'))
catalogs = {}
for code in ('zh-CN','en','ja','ko','es','fr','de','pt','it','ru','id'):
    path = ROOT/'locales'/(code+'.json')
    dictionary = json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
    if not args.development:
        assert all(isinstance(dictionary.get(key), str) and dictionary[key] for key in public), code+' catalog is incomplete'
    catalogs[code] = dictionary
guide = ('介面語言', '語言 language English 日本語 한국어 離線',
    '<h1>選擇你熟悉的語言。</h1><p>到「語言」頁選擇介面語言，按「立即套用」。主視窗、浮動鍵盤、使用說明及系統匣選單會立即更新，重新啟動也會保留。</p>'
    '<p>12 種語言均可離線使用。按鍵配置、快捷鍵與 OBS 來源名稱保持原值。</p>')
loader = ('import sys,types,json\n'
    'mod=types.ModuleType("speed_editor_languages")\n'
    'mod.__file__="language_runtime.py"\n'
    'sys.modules[mod.__name__]=mod\n'
    f'exec(compile({source!r},mod.__file__,"exec"),mod.__dict__)\n'
    f'mod.CATALOGS=json.loads({json.dumps(catalogs,ensure_ascii=False)!r})\n'
    'from speed_editor_glass_help import SECTIONS\n'
    f'SECTIONS.append({guide!r})\n'
    'mod.install()\n')
raw = marshal.dumps(compile(loader, '_language_upgrade.py', 'exec'))
addon = ('_language_upgrade', b's', 1, len(raw), zlib.compress(raw))
at = data.rfind(b'MEI\x0c\x0b\x0a\x0b\x0e')
magic, length, toc_offset, toc_size, version, lib = struct.unpack('!8sIIII64s', data[at:at+88])
start = at + 88 - length
cursor = start + toc_offset
entries = []
while cursor < start + toc_offset + toc_size:
    size, offset, compressed, original, flag, kind = struct.unpack('!iIIIBc', data[cursor:cursor+18])
    name = data[cursor+18:cursor+size].split(b'\0', 1)[0].decode()
    cursor += size
    if name == 'main': entries.append(addon)
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
args.output.write_bytes(data[:start] + b''.join(payload) + table
    + struct.pack('!8sIIII64s', magic, offset+len(table)+88, offset, len(table), version, lib))
proof = {'version':'7.4', 'baseline_sha256':BASE_SHA,
    'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'portable_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
    'portable_bytes':args.output.stat().st_size, 'original_payloads_unchanged':True,
    'catalog_counts':{key:len(value) for key,value in catalogs.items()},
    'public_strings':len(public), 'development':args.development}
(ROOT/'language_build.json').write_text(json.dumps(proof, indent=2), encoding='utf8')
print(json.dumps(proof))
