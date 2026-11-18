# -*- coding: utf-8 -*-
"""打发布包：把「本机运行目录」压成 MaaBH2-v<版本>-win-x64.zip，并在压之前做完整自检。

为什么需要它：`resource/model/`（OCR + 光环分类器，35 MB）被 .gitignore 排除，
从 git 仓库克隆出来是**不含模型的**；一旦漏带，用户端 459 个 OCR 节点全废，
而且报错很隐晦。本脚本把「模型在不在」变成硬性检查，缺一个就拒绝出包。

用法：
    python _build/make_zips.py                 # 自检 + 打包，版本号取自 interface.json
    python _build/make_zips.py --check-only    # 只自检，不出包
    python _build/make_zips.py --out D:\\release  # 指定输出目录（默认 <项目上级>\\_release）
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile

DEFAULT_SRC = r'C:\MaaFramework\MaaScript'

# 这些永远不进包
JUNK = re.compile(r'(\.bak|(^|/)_bak/|__pycache__|~$|\.tmp$|(^|/)logs?/)')

# 本机草稿，不随包发布（仓库里也没有）
EXCLUDE = {'resource/Changelog.md'}

REQUIRED_MODEL = [
    'resource/model/ocr/det.onnx',
    'resource/model/ocr/rec.onnx',
    'resource/model/ocr/keys.txt',
]

ok_all = True


def say(ok, msg, detail=''):
    global ok_all
    if not ok:
        ok_all = False
    print('  %s %s%s' % ('✓' if ok else '✗', msg, ('  ' + detail) if detail else ''))


def load_json(p):
    return json.load(io.open(p, encoding='utf-8'))


def check_interface(src, want_ver):
    p = os.path.join(src, 'interface.json')
    if not os.path.isfile(p):
        say(False, 'interface.json 存在')
        return None
    d = load_json(p)
    ver = d.get('version')
    say(ver == want_ver, 'interface.json 版本 = %s' % ver,
        '' if ver == want_ver else '（期望 %s）' % want_ver)
    for key in ('icon', 'welcome'):
        rel = d.get(key)
        if rel:
            say(os.path.isfile(os.path.join(src, rel)), '%s 指向的文件存在' % key, rel)
    return d


def check_pipeline(src, expect_nodes):
    p = os.path.join(src, 'resource', 'pipeline', 'main.json')
    if not os.path.isfile(p):
        say(False, 'main.json 存在')
        return None
    d = load_json(p)
    say(True, 'main.json 合法', '%d 个节点' % len(d))
    if expect_nodes:
        say(len(d) == expect_nodes, '节点数 = %d' % len(d),
            '' if len(d) == expect_nodes else '（期望 %d）' % expect_nodes)
    return d


def check_models(src, pipeline):
    for rel in REQUIRED_MODEL:
        p = os.path.join(src, rel.replace('/', os.sep))
        size = os.path.getsize(p) if os.path.isfile(p) else 0
        say(size > 1024, '模型 %s' % rel.split('/')[-1], '%.1f MB' % (size / 1048576.0))
    # pipeline 里显式引用的 .onnx（分类器/检测器），按 MFA 约定放在 model/classify|detect 下
    need = set()
    for name, node in (pipeline or {}).items():
        rec = node.get('recognition') or {}
        param = rec.get('param') or {}
        model = param.get('model')
        if not model or not str(model).endswith('.onnx'):
            continue
        kind = {'NeuralNetworkClassify': 'classify',
                'NeuralNetworkDetect': 'detect'}.get(rec.get('type'))
        if kind:
            need.add('resource/model/%s/%s' % (kind, model))
    for rel in sorted(need):
        p = os.path.join(src, rel.replace('/', os.sep))
        size = os.path.getsize(p) if os.path.isfile(p) else 0
        say(size > 1024, '分类器 %s' % rel.split('/')[-1], '%.1f MB' % (size / 1048576.0))


def check_templates(src, pipeline):
    if not pipeline:
        return
    root = os.path.join(src, 'resource', 'image')
    dirs = set(os.listdir(root)) if os.path.isdir(root) else set()
    files = set()
    for dp, dn, fn in os.walk(root):
        for f in fn:
            files.add(os.path.relpath(os.path.join(dp, f), root).replace('\\', '/'))
    miss, used = [], set()
    for name, node in pipeline.items():
        s = json.dumps(node, ensure_ascii=False)
        for m in re.finditer(r'"template":\s*(\[[^\]]*\]|"[^"]*")', s):
            raw = m.group(1)
            names = json.loads(raw) if raw.startswith('[') else [json.loads(raw)]
            for t in names:
                t = t.replace('\\', '/')
                if t in files or t in dirs or any(f.startswith(t.rstrip('/') + '/') for f in files):
                    used.add(t)
                else:
                    miss.append((name, t))
    say(not miss, '模板引用 %d 个全部有图' % len(used),
        '' if not miss else '缺 %d 个：%s' % (len(miss), miss[:5]))


def collect(src):
    """返回 [(磁盘路径, 包内路径)]"""
    out = []
    for rel in ('interface.json', 'icon.png'):
        p = os.path.join(src, rel)
        if os.path.isfile(p):
            out.append((p, rel))
    for top in ('announcements', 'resource'):
        base = os.path.join(src, top)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if not JUNK.search(d + '/')]
            for f in fn:
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, src).replace('\\', '/')
                if JUNK.search(rel) or rel in EXCLUDE:
                    continue
                out.append((p, rel))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(DEFAULT_SRC), '_release'))
    ap.add_argument('--version')
    ap.add_argument('--expect-nodes', type=int, default=None,
                    help='要求 main.json 的节点数正好等于这个值（防止误打旧文件）')
    ap.add_argument('--check-only', action='store_true')
    args = ap.parse_args()

    src = args.src
    if not os.path.isdir(src):
        sys.exit('源目录不存在：%s' % src)

    print('=' * 60)
    print('源目录：', src)

    p_itf = os.path.join(src, 'interface.json')
    if not os.path.isfile(p_itf):
        sys.exit('找不到 interface.json：%s' % p_itf)
    itf = load_json(p_itf)
    ver = args.version or itf.get('version')
    if not ver:
        sys.exit('interface.json 里没有 version 字段')

    print('\n【1/5】interface.json')
    check_interface(src, ver)

    print('\n【2/5】pipeline')
    pipeline = check_pipeline(src, args.expect_nodes)

    print('\n【3/5】模型文件（git 里没有，必须本地带）')
    check_models(src, pipeline)

    print('\n【4/5】模板图')
    check_templates(src, pipeline)

    print('\n【5/5】打包清单')
    items = collect(src)
    bad = [r for _, r in items if JUNK.search(r)]
    say(not bad, '%d 个文件待打包' % len(items), '' if not bad else '混入垃圾：%s' % bad[:5])
    total = sum(os.path.getsize(p) for p, _ in items)
    print('  · 未压缩合计 %.1f MB' % (total / 1048576.0))
    say(any(r.startswith('resource/model/ocr/rec.onnx') for _, r in items),
        '清单里包含 OCR 识别模型')

    if not ok_all:
        print('\n' + '=' * 60)
        print('✗ 自检未通过，拒绝打包。修好上面标 ✗ 的项再跑一次。')
        sys.exit(1)
    if args.check_only:
        print('\n' + '=' * 60)
        print('✓ 自检全部通过（--check-only，未出包）')
        return

    os.makedirs(args.out, exist_ok=True)
    name = 'MaaBH2-v%s-win-x64.zip' % ver
    dst = os.path.join(args.out, name)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p, rel in items:
            z.write(p, rel)

    # 回读校验：包里真的带着模型、接口、节点数对得上
    with zipfile.ZipFile(dst) as z:
        names = set(z.namelist())
        must = {'interface.json', 'resource/pipeline/main.json'} | set(REQUIRED_MODEL)
        miss = sorted(must - names)
        inside_nodes = len(json.loads(z.read('resource/pipeline/main.json').decode('utf-8')))
    size_mb = os.path.getsize(dst) / 1048576.0

    print('\n' + '=' * 60)
    print('已出包：%s' % dst)
    print('  大小 %.1f MB / %d 个文件 / 包内节点数 %d' % (size_mb, len(items), inside_nodes))
    if miss:
        print('  ✗ 回读发现缺失：%s' % miss)
        sys.exit(1)
    print('  ✓ 回读通过：interface.json、main.json、OCR 三件套都在包里')
    if args.expect_nodes and inside_nodes != args.expect_nodes:
        print('  ✗ 包内节点数 %d ≠ 期望 %d' % (inside_nodes, args.expect_nodes))
        sys.exit(1)


if __name__ == '__main__':
    main()
