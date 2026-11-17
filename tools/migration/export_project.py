"""Export this project's recoverable Codex records and portable working files.

Read-only access to the original databases. Does not overwrite Codex state,
publish files, modify game assets, or run Blender authoring scripts.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import time
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HOME = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
OUT = ROOT.parent / (ROOT.name + '-迁移包-20261116')
CHAT = OUT / 'codex-chats'
SETUP = OUT / 'setup'
TZ = dt.timezone(dt.timedelta(hours=8))
PROJECT_IDS = {'40435890-ad29-4db7-ac87-37cbfd27b1d5', '4506d5ed-4b16-4b75-9ef2-0dd164887952'}
LATEST_DIRS = {
    'layered-island-build', 'local-camera-review', 'spatial-foundation-review',
    'left-finish-review', 'beach-swash-review', 'hd2d-space-diagnosis',
    'bamboo-west-extension-review',
}
SKIP_DIRS = {'.git', '.godot', 'node_modules', '__pycache__', '.venv', 'venv'}
REPORT = {}
SECRETS = set()
REDACTIONS = collections.Counter()


def public_record(value):
    """Keep project messages/tools while removing private runtime internals."""
    if isinstance(value, list):
        return [public_record(v) for v in value]
    if not isinstance(value, dict):
        return value
    kind = value.get('type')
    if kind in {'reasoning', 'agent_reasoning', 'agent_reasoning_raw_content', 'compacted', 'turn_context'} or value.get('role') in {'system', 'developer'} or value.get('channel') == 'analysis':
        return {k: value[k] for k in ['type', 'id', 'timestamp'] if k in value} | {'omitted': 'private_runtime_context'}
    private_keys = {'base_instructions', 'developer_instructions', 'system_instructions', 'encrypted_content', 'reasoning_content', 'raw_reasoning', 'chain_of_thought'}
    return {k: public_record(v) for k, v in value.items() if k not in private_keys}


def norm(s):
    return str(s or '').removeprefix('\\\\?\\').replace('\\', '/').rstrip('/').casefold()


TARGETS = {norm(ROOT), norm(ROOT.anchor + ROOT.name)}


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def jsonline(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'


def readonly(path):
    c = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    c.execute('BEGIN')
    return c


def gather_secrets(value, key=''):
    if isinstance(value, dict):
        for k, v in value.items():
            gather_secrets(v, k)
    elif isinstance(value, list):
        for v in value:
            gather_secrets(v, key)
    elif isinstance(value, str) and re.search(r'(?i)api.?key|bearer.?token|access.?token|refresh.?token|secret|password|authorization', key):
        if len(value) >= 12:
            SECRETS.add(value)


def redact(s):
    for secret in SECRETS:
        if secret in s:
            REDACTIONS['configured_credential'] += s.count(secret)
            s = s.replace(secret, '[REDACTED_CREDENTIAL]')
    patterns = [
        ('api_key_format', r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}'),
        ('github_token', r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'),
        ('bearer_token', r'(?i)(?<=Bearer )[A-Za-z0-9._~+/-]{24,}'),
    ]
    for name, pattern in patterns:
        s, n = re.subn(pattern, '[REDACTED_CREDENTIAL]', s)
        REDACTIONS[name] += n
    return s


def files_under(base, skip=SKIP_DIRS):
    if not base.exists():
        return
    for dp, dns, fns in os.walk(base):
        dns[:] = sorted(d for d in dns if d not in skip)
        for name in sorted(fns):
            p = Path(dp) / name
            if p.is_file():
                yield p


def git_capture(args):
    r = subprocess.run(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT, capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8', errors='replace'))
    return r.stdout


def time_text(ms):
    if ms is None:
        return ''
    return dt.datetime.fromtimestamp(ms / 1000, TZ).isoformat(timespec='seconds')


def user_content(item):
    out = []
    for c in item.get('content', []):
        if isinstance(c, str):
            out.append(c)
        elif c.get('type') in ('text', 'input_text', 'output_text'):
            out.append(c.get('text', ''))
        elif c.get('type') in ('localImage', 'input_image', 'image'):
            out.append('[图片附件：' + (c.get('path') or c.get('image_url', '')[:100] or '保存在完整事件档案') + ']')
    return '\n'.join(out)


def export_chats():
    CHAT.mkdir(parents=True, exist_ok=True)
    SETUP.mkdir(parents=True, exist_ok=True)
    cfg = tomllib.loads((HOME / 'config.toml').read_text(encoding='utf-8'))
    gather_secrets(cfg)
    # Only a sanitized reference is exported; authentication files are never copied.
    (SETUP / 'codex-config-reference.redacted.toml').write_text(redact((HOME / 'config.toml').read_text(encoding='utf-8')), encoding='utf-8')
    meta = {}
    edges = []
    for path in [HOME / 'state_5.sqlite', HOME / 'sqlite/state_5.sqlite']:
        if not path.exists():
            continue
        c = readonly(path)
        for r in c.execute('SELECT * FROM threads'):
            meta.setdefault(r['id'], dict(r))
        edges += [dict(r) for r in c.execute('SELECT * FROM thread_spawn_edges')]
        c.close()
    index_titles = {}
    ip = HOME / 'session_index.jsonl'
    if ip.exists():
        for line in ip.read_text(encoding='utf-8').splitlines():
            if line.strip():
                x = json.loads(line)
                index_titles[x['id']] = x.get('thread_name')
    selected = {i for i, r in meta.items() if norm(r.get('cwd')) in TARGETS or r.get('project_id') in PROJECT_IDS}
    reasons = {i: ['thread_metadata_project_or_cwd'] for i in selected}
    gp = HOME / '.codex-global-state.json'
    if gp.exists():
        g = json.loads(gp.read_text(encoding='utf-8'))
        for i, v in g.get('thread-project-assignments', {}).items():
            if isinstance(v, dict) and v.get('projectId') in PROJECT_IDS:
                selected.add(i)
                reasons.setdefault(i, []).append('desktop_project_assignment')
        for key, value in g.items():
            if 'thread-writable-roots' in key and isinstance(value, dict):
                for i, roots in value.items():
                    if isinstance(roots, list) and any(norm(p) in TARGETS for p in roots):
                        selected.add(i)
                        reasons.setdefault(i, []).append('desktop_workspace_root')
    raw = {}
    for folder in ['sessions', 'archived_sessions']:
        for p in (HOME / folder).rglob('*.jsonl'):
            with p.open(encoding='utf-8') as f:
                first = f.readline()
            try:
                x = json.loads(first).get('payload', {})
            except json.JSONDecodeError:
                continue
            i = x.get('id') or x.get('session_id')
            if not i:
                continue
            raw[i] = p
            if norm(x.get('cwd')) in TARGETS:
                selected.add(i)
                reasons.setdefault(i, []).append('raw_session_cwd')
                meta.setdefault(i, {'id': i, 'cwd': x.get('cwd'), 'source': x.get('source'), 'cli_version': x.get('cli_version'), 'metadata_recovered_from': 'session_meta'})
    history = readonly(HOME / 'thread_history_1.sqlite')
    for r in history.execute("SELECT DISTINCT thread_id,json_extract(item_json,'$.cwd') AS cwd FROM thread_items WHERE item_type='commandExecution'"):
        if norm(r['cwd']) in TARGETS:
            selected.add(r['thread_id'])
            reasons.setdefault(r['thread_id'], []).append('historical_command_cwd')
    while True:
        before = len(selected)
        for e in edges:
            if e['parent_thread_id'] in selected:
                selected.add(e['child_thread_id'])
                reasons.setdefault(e['child_thread_id'], []).append('spawned_from_project_thread')
        for i, r in meta.items():
            if r.get('attached_thread_parent_id') in selected:
                selected.add(i)
                reasons.setdefault(i, []).append('attached_project_child')
        if len(selected) == before:
            break
    database = sqlite3.connect(CHAT / 'chat_archive.sqlite')
    database.execute('PRAGMA secure_delete=ON')
    database.executescript('CREATE TABLE IF NOT EXISTS threads(id TEXT PRIMARY KEY, metadata_json TEXT); CREATE TABLE IF NOT EXISTS turns(thread_id TEXT, turn_id TEXT, data_json TEXT, PRIMARY KEY(thread_id,turn_id)); CREATE TABLE IF NOT EXISTS items(thread_id TEXT,item_id TEXT,rollout_ordinal INTEGER,item_type TEXT,data_json TEXT,PRIMARY KEY(thread_id,item_id));')
    coverage = []
    attachments = {}
    messages_total = 0
    items_total = 0
    for n, i in enumerate(sorted(selected)):
        m = meta.get(i, {'id': i, 'metadata_recovered_from': 'history_items_or_project_assignment'})
        rows = history.execute('SELECT * FROM thread_items WHERE thread_id=? ORDER BY rollout_ordinal,item_id', (i,)).fetchall()
        title = m.get('title') or index_titles.get(i)
        if not title:
            first_user = next((user_content(json.loads(r['item_json'])).strip() for r in rows if r['item_type'] == 'userMessage'), '')
            title = first_user or '历史会话（无存留标题）'
            m['title_origin'] = 'first_user_message_fallback'
        m['export_title'] = title
        m['selection_reasons'] = sorted(set(reasons.get(i, [])))
        m['exported_at'] = dt.datetime.now(TZ).isoformat(timespec='seconds')
        thread_dir = CHAT / 'threads' / i
        thread_dir.mkdir(parents=True, exist_ok=True)
        dump(thread_dir / 'metadata.json', json.loads(redact(json.dumps(m, ensure_ascii=False))))
        database.execute('INSERT OR REPLACE INTO threads VALUES (?,?)', (i, redact(json.dumps(m, ensure_ascii=False))))
        readable = ['# ' + title.replace('\n', ' '), '', '会话ID：`' + i + '`', '', '以下为本机存留的用户与agent消息，工具调用及实际存留输出另见完整事件档案。', '']
        turns = history.execute('SELECT * FROM thread_turns WHERE thread_id=? ORDER BY rollout_ordinal', (i,)).fetchall()
        with (thread_dir / 'turns.jsonl').open('w', encoding='utf-8') as f:
            for r in turns:
                x = dict(r)
                f.write(redact(jsonline(x)))
                database.execute('INSERT OR REPLACE INTO turns VALUES (?,?,?)', (i, r['turn_id'], redact(json.dumps(x, ensure_ascii=False))))
        message_count = 0
        with (thread_dir / 'items.jsonl').open('w', encoding='utf-8') as f:
            for r in rows:
                x = dict(r)
                item = public_record(json.loads(x.pop('item_json')))
                x['item'] = item
                text = redact(jsonline(x))
                f.write(text)
                database.execute('INSERT OR REPLACE INTO items VALUES (?,?,?,?,?)', (i, r['item_id'], r['rollout_ordinal'], r['item_type'], text.rstrip()))
                kind = item.get('type')
                if kind in ('userMessage', 'agentMessage'):
                    label = '用户' if kind == 'userMessage' else 'Agent'
                    phase = item.get('phase', '')
                    readable += ['## ' + label + (' · ' + phase if phase else '') + (' · ' + time_text(r['created_at_ms']) if r['created_at_ms'] else ''), '', redact(user_content(item) if kind == 'userMessage' else item.get('text', '')), '']
                    message_count += 1
                if kind == 'userMessage':
                    for part in item.get('content', []):
                        if isinstance(part, dict) and part.get('type') == 'localImage' and part.get('path'):
                            attachments.setdefault(part['path'], set()).add(i)
        p = raw.get(i)
        if not p and m.get('rollout_path') and Path(m['rollout_path']).exists():
            p = Path(m['rollout_path'])
        raw_count = 0
        raw_error = None
        if p:
            size = p.stat().st_size
            consumed = 0
            with p.open('rb') as source, (thread_dir / 'rollout.jsonl').open('w', encoding='utf-8', newline='\n') as dest:
                while consumed < size:
                    line = source.readline(size - consumed)
                    consumed += len(line)
                    if not line.endswith(b'\n'):
                        raw_error = 'Active file ended in an incomplete line; trailing partial line excluded.'
                        break
                    value = line.decode('utf-8')
                    try:
                        event = json.loads(value)
                    except json.JSONDecodeError:
                        raw_error = 'Invalid source line excluded at snapshot boundary.'
                        break
                    dest.write(redact(jsonline(public_record(event))))
                    raw_count += 1
                    # Fallback for a raw record not yet projected into thread_items.
                    if not rows and event.get('type') == 'response_item':
                        payload = event.get('payload', {})
                        if payload.get('type') == 'message' and payload.get('role') in ('user', 'assistant'):
                            readable += ['## ' + ('用户' if payload['role'] == 'user' else 'Agent'), '', redact(user_content(payload)), '']
                            message_count += 1
            dump(thread_dir / 'raw_source.json', {'original_path': str(p), 'source_snapshot_bytes': size, 'exported_lines': raw_count, 'note': raw_error})
        (thread_dir / 'conversation.md').write_text('\n'.join(readable), encoding='utf-8')
        status = 'raw_and_history' if p and rows else ('history_database_only' if rows else ('raw_only' if p else 'metadata_only'))
        coverage.append({'id': i, 'title': title, 'title_origin': m.get('title_origin', 'stored_title'), 'coverage': status, 'messages': message_count, 'items': len(rows), 'turns': len(turns), 'raw_lines': raw_count, 'raw_note': raw_error, 'selection_reasons': m['selection_reasons']})
        messages_total += message_count
        items_total += len(rows)
        if n % 10 == 0:
            print('Exported conversations:', n + 1, '/', len(selected), flush=True)
    history.close()
    database.commit()
    integrity = database.execute('PRAGMA integrity_check').fetchone()[0]
    database.execute('VACUUM')
    database.close()
    attachment_index = []
    for original, ids in sorted(attachments.items()):
        p = Path(original)
        record = {'source_path': original, 'thread_ids': sorted(ids), 'exists': p.exists()}
        if p.is_file() and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}:
            ident = hashlib.sha256(norm(original).encode()).hexdigest()[:16]
            target = CHAT / 'attachments' / (ident + '-' + p.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            record['export_path'] = str(target.relative_to(CHAT)).replace('\\', '/')
            record['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        attachment_index.append(record)
    dump(CHAT / 'attachment-index.json', attachment_index)
    dump(CHAT / 'coverage.json', coverage)
    dump(CHAT / 'spawn-edges.json', [e for e in edges if e['parent_thread_id'] in selected or e['child_thread_id'] in selected])
    coverage_counts = collections.Counter(r['coverage'] for r in coverage)
    lines = ['# Codex项目聊天索引', '', '导出时间：' + dt.datetime.now(TZ).isoformat(timespec='seconds'), '', f'共识别 {len(selected)} 个项目相关会话，存留 {messages_total} 条用户/Agent消息、{items_total} 个历史事件记录。', '', '导出范围是项目沟通、工具事件与实际存留输出；内部推理、系统/开发者指令及凭据已排除或脱敏。保留被省略事件的ID与顺序，不把档案描述为逐字节原始运行上下文。', '', '早期日志已不在原路径的会话从本地聊天数据库提取；工具输出只保留源文件/数据库实际存留内容，已在源端截断或未保存的输出不补造。覆盖与缺失逐项见 coverage.json；附件来源与是否存在见 attachment-index.json。', '', '每个会话的 conversation.md 便于阅读；items.jsonl、turns.jsonl 保留结构化事件。rollout.jsonl 仅在找到原日志时存在，应用同样的导出范围。chat_archive.sqlite 是独立查询档案，不能直接覆盖新机Codex数据库。', '', '| 会话（存留标题） | 用户/Agent消息 | 历史事件 | 来源 |', '| --- | ---: | ---: | --- |']
    for r in coverage:
        title = r['title'].replace('\n', ' ').replace('|', '\\|')
        lines.append(f"| [{title}](threads/{r['id']}/conversation.md) | {r['messages']} | {r['items']} | {r['coverage']} |")
    (CHAT / 'INDEX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    REPORT['chat'] = {'threads': len(selected), 'messages': messages_total, 'items': items_total, 'coverage_counts': dict(coverage_counts), 'sqlite_integrity': integrity, 'attachment_total': len(attachment_index), 'attachment_copied': sum('export_path' in r for r in attachment_index), 'credential_redactions': dict(REDACTIONS)}
    print('Chat export:', json.dumps(REPORT['chat'], ensure_ascii=True), flush=True)


def export_setup():
    for name in ['jeff-hd2d-modeling', 'minimax-h3-walk']:
        p = HOME / 'skills' / name
        if p.exists():
            shutil.copytree(p, SETUP / 'skills' / name, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    addon = Path.home() / 'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons/blender_mcp.py'
    if addon.exists():
        (SETUP / 'blender-mcp').mkdir(parents=True, exist_ok=True)
        shutil.copy2(addon, SETUP / 'blender-mcp/blender_mcp.py')
    setup_text = '''# 新电脑环境与外部依赖

## 可以直接续的部分

第一包含工程全部运行资源、最新与旧岛Blender源，以及Godot 4.7.2 Windows便携版。运行游戏无需Blender、MiniMax或旧机Codex登录状态。首次解压导入会重建 .godot 缓存。

登录新电脑Codex后添加工程目录，在新聊天读 project/handoff/START_HERE.md 即可续上项目记录。完整聊天档案在 codex-chats/，无需依赖旧会话ID能够远程打开。

## 建模

本机Blender实际程序：C:/软件/blender/blender.exe；插件来自Blender 5.1用户插件目录。迁移包 setup/blender-mcp/blender_mcp.py 保存本机副本。新机安装兼容Blender，安装并启用插件，打开当前 .blend，启动MCP连接（旧机分层场景端口19887），在Codex检查连接后再建模。插件含网络服务配置，启用时按新机需求设置；安装文件不自动启动外部服务。

项目相关个人skill在 setup/skills/：jeff-hd2d-modeling、minimax-h3-walk。复制到新机Codex skills目录后检查其中写死的旧机路径。项目剧情skill已包含于 project/.claude/skills/wuxia-prose/。

Blender作者脚本、贴图制作脚本、个人skill与 .blend 外部图像可能保存旧绝对路径。推荐恢复同路径 D:/自己做着玩的/孤屿霜尘；换路径时先检查副本中的引用，不能批量替换运行资产或直接重跑已完成脚本。Blender有打包图像也仍需检查当前依赖。

## 角色动作生成

第三包保存 D:/AI/minimax-h3-minimal 的 action-batches、walk-batches、jobs、walk-kit、sources、results，以及根目录流程/说明/脚本。完成、失败、中止批次都保留，不能当成待执行任务重交。包内未包含大型 ComfyUI_windows_portable、模型权重、runtime-vulkan、下载缓存与显卡运行环境。继续生成前按 README/PROGRESS/models.json 和 minimax-h3-walk skill恢复环境，匹配新机显卡。既有帧、审阅与游戏运行不需要这些模型权重。

## 参考游戏与额外外部原件

工程内 artifacts 的研究、抽取与审阅资料在第一/第二包。外部安装游戏（Wandering Sword、I Just Wanted to Fish Demo、古龙风云录）、Steam程序、全量外部分析库、WorkBuddy原视频文件夹和其他未复制的下载目录并不作为软件安装包迁移。聊天中仍存在的本地图像附件已另行复制并建立索引，缺失项明确记录。若以后需要重新提取某个参考游戏，需新机具备对应游戏；当前建模/游戏运行资源已在工程中。

## Codex配置与登录

codex-config-reference.redacted.toml 仅为脱敏参照，包含旧机绝对路径。不要整体覆盖新机 config.toml；重新登录账号或配置原供应商，重装所需插件，合并必要设置。auth、密钥、浏览器登录态、其他项目聊天未作为环境配置复制。迁移没有云端上传。

本次没有改写任何新/旧Codex数据库，chat_archive.sqlite 是离线查询档案。它保存本机可找回的项目历史，不能保证还原同一个侧栏聊天或供应商内部的响应链；新聊天读取短交接文件是确定可用的续接入口。

## Git

旧机分支、HEAD、远端、完整状态和两个已有改动资源的patch在 setup/git/。本项目 .git 历史对象约15.6GB，主要包含早期大资料，未加入迁移压缩包；最新工作区文件已全部另行打包，未跟踪文件也包含。旧Git历史仍在原机和原仓库。不要只拉远端替换这份工作区。需要原提交历史时从远端按记录恢复；需要原机全部本地历史时另复制旧 .git 目录。
'''
    (SETUP / 'ENVIRONMENT.md').write_text(setup_text, encoding='utf-8')
    git_dir = SETUP / 'git'
    git_dir.mkdir(parents=True, exist_ok=True)
    for name, args in [
        ('status.txt', ['status', '--short', '--branch']),
        ('status-porcelain-v2.txt', ['status', '--porcelain=v2', '--branch']),
        ('tracked-working-tree.patch', ['diff', '--binary']),
        ('staged.patch', ['diff', '--cached', '--binary']),
        ('head.txt', ['rev-parse', 'HEAD']),
        ('branch.txt', ['branch', '--show-current']),
        ('refs.txt', ['show-ref']),
        ('remote.txt', ['remote', '-v']),
    ]:
        (git_dir / name).write_bytes(git_capture(args))
    records = []
    for p in files_under(ROOT / 'artifacts'):
        if p.suffix.lower() == '.md':
            text = p.read_text(encoding='utf-8', errors='replace')
            records.append({'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'title': text.splitlines()[0] if text else '', 'modified_at': time_text(p.stat().st_mtime * 1000), 'bytes': p.stat().st_size})
    dump(OUT / 'progress-index.json', records)
    (OUT / 'README.md').write_text('''# 孤屿霜尘迁移包

先解压 `01-project-and-chats.zip`，阅读 `project/handoff/START_HERE.md`。这包包含当前未提交工程、可编辑Blender源、便携Godot、最新实机验证、全部研究说明与可找回的项目聊天。

`02-project-history.zip` 解压到同一目录补齐 project/artifacts 历史研究、录像、备份与审阅素材。`03-animation-workfiles.zip` 补齐外部MiniMax批次与流程，继续动作制作时使用。

各包内部文件清单和SHA256在 manifests/；整包校验在 SHA256SUMS.txt。导出统计与覆盖检查在 export-report.json、codex-chats/coverage.json。新机工具配置和未打包大型运行依赖见 setup/ENVIRONMENT.md。不要把本档案SQLite覆盖到新机Codex目录。

最直接的续接方式：把 project 内容复制到工程目录，登录新机Codex，添加该目录，在新聊天粘贴 START_HERE.md 的启动语。双击工程的试玩脚本即可查看当前分层孤岛；默认 F5 仍启动旧岛。
''', encoding='utf-8')


def plan_packages():
    core, historical, animation = [], [], []
    for p in files_under(ROOT):
        rel = p.relative_to(ROOT)
        entry = (p, 'project/' + rel.as_posix())
        if rel.parts[0] != 'artifacts':
            core.append(entry)
        elif p.name == '.gdignore' or p.suffix.lower() == '.md' or (len(rel.parts) > 1 and rel.parts[1] in LATEST_DIRS and p.suffix.lower() != '.avi'):
            core.append(entry)
        else:
            historical.append(entry)
    # Current launch script already prefers this relative location.
    godot = Path(ROOT.anchor + ROOT.name) / 'tools/godot'
    present = {a for _, a in core}
    if godot.exists():
        for p in files_under(godot):
            arc = 'project/tools/godot/' + p.relative_to(godot).as_posix()
            if arc not in present:
                core.append((p, arc))
    for base in [CHAT, SETUP]:
        core += [(p, base.name + '/' + p.relative_to(base).as_posix()) for p in files_under(base)]
    core += [(OUT / n, n) for n in ['README.md', 'progress-index.json']]
    h3 = Path('D:/AI/minimax-h3-minimal')
    if h3.exists():
        for p in sorted(h3.iterdir()):
            if p.is_file() and p.suffix.lower() in {'.py', '.ps1', '.cmd', '.md', '.json', '.txt'}:
                if p.name == 'comfy.pid':
                    continue
                animation.append((p, 'animation/minimax-h3-minimal/' + p.name))
        for folder in ['action-batches', 'walk-batches', 'jobs', 'walk-kit', 'sources', 'results']:
            animation += [(p, 'animation/minimax-h3-minimal/' + p.relative_to(h3).as_posix()) for p in files_under(h3 / folder)]
    plans = [('01-project-and-chats.zip', core), ('02-project-history.zip', historical), ('03-animation-workfiles.zip', animation)]
    dump(OUT / 'package-plan.json', {name: {'files': len(entries), 'source_bytes': sum(p.stat().st_size for p, _ in entries)} for name, entries in plans})
    return plans


def pack(name, entries):
    target = OUT / name
    if target.exists():
        raise RuntimeError('Archive already exists: ' + str(target))
    records = []
    total = sum(p.stat().st_size for p, _ in entries)
    done = 0
    last = time.monotonic()
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as z:
        for n, (p, arc) in enumerate(entries):
            initial = p.stat()
            digest = hashlib.sha256()
            with p.open('rb') as src, z.open(arc, 'w', force_zip64=True) as dest:
                while True:
                    data = src.read(1024 * 1024)
                    if not data:
                        break
                    digest.update(data)
                    dest.write(data)
            after = p.stat()
            if initial.st_size != after.st_size or initial.st_mtime_ns != after.st_mtime_ns:
                raise RuntimeError('Source changed while archiving: ' + str(p))
            records.append({'path': arc, 'source_path': str(p), 'bytes': initial.st_size, 'sha256': digest.hexdigest(), 'modified_at': time_text(initial.st_mtime * 1000)})
            done += initial.st_size
            if time.monotonic() - last > 25:
                print(name, 'files', n + 1, '/', len(entries), 'MiB', round(done / 2**20), '/', round(total / 2**20), flush=True)
                last = time.monotonic()
        manifest = ''.join(jsonline(r) for r in records)
        z.writestr('_migration/file-manifest.jsonl', manifest)
    manifest_path = OUT / 'manifests' / (name + '.jsonl')
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest, encoding='utf-8')
    REPORT.setdefault('packages', {})[name] = {'files': len(entries), 'source_bytes': total, 'archive_bytes': target.stat().st_size}
    print('Packed', name, 'bytes', target.stat().st_size, flush=True)


def verify_packages():
    sums = []
    coverage = json.loads((CHAT / 'coverage.json').read_text(encoding='utf-8'))
    REPORT.setdefault('chat', {}).update({'threads': len(coverage), 'messages': sum(r['messages'] for r in coverage), 'items': sum(r['items'] for r in coverage), 'coverage_counts': dict(collections.Counter(r['coverage'] for r in coverage))})
    for name in ['01-project-and-chats.zip', '02-project-history.zip', '03-animation-workfiles.zip']:
        p = OUT / name
        print('Verifying CRC:', name, flush=True)
        with zipfile.ZipFile(p) as z:
            broken = z.testzip()
            if broken:
                raise RuntimeError('ZIP CRC failure: ' + broken)
            manifest = [json.loads(line) for line in z.read('_migration/file-manifest.jsonl').decode('utf-8').splitlines()]
            if len({r['path'] for r in manifest}) != len(manifest):
                raise RuntimeError('Duplicate archive paths: ' + name)
            for r in manifest:
                if z.getinfo(r['path']).file_size != r['bytes']:
                    raise RuntimeError('ZIP size mismatch: ' + r['path'])
            if name.startswith('01-'):
                required = ['project/assets/layered_island/layered_island.blend', 'project/assets/layered_island/layered_island.glb', 'project/assets/layered_island/layout.json', 'project/assets/island_blender/nameless_island.blend', 'project/scenes/layered_island.tscn', 'project/scripts/layered_island.gd', 'project/试玩分层孤岛.cmd', 'project/tools/godot/Godot_v4.7.2-stable_win64.exe', 'project/handoff/START_HERE.md', 'project/AGENTS.md', 'project/artifacts/.gdignore', 'codex-chats/chat_archive.sqlite', 'codex-chats/INDEX.md', 'setup/blender-mcp/blender_mcp.py', 'project/artifacts/bamboo-west-extension-review/review-motion.mp4']
                missing = [n for n in required if n not in z.namelist()]
                if missing:
                    raise RuntimeError('Missing core files: ' + repr(missing))
        digest = hashlib.sha256()
        with p.open('rb') as f:
            for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
                digest.update(data)
        value = digest.hexdigest()
        sums.append(value + '  ' + name)
        REPORT.setdefault('packages', {}).setdefault(name, {}).update({'files': len(manifest), 'source_bytes': sum(r['bytes'] for r in manifest), 'archive_bytes': p.stat().st_size, 'crc_verified': True, 'sha256': value})
        print('Verified:', name, flush=True)
    (OUT / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', encoding='ascii')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['export', 'pack', 'pack-core', 'verify', 'all'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / 'export-report.json'
    if report_path.exists():
        REPORT.update(json.loads(report_path.read_text(encoding='utf-8')))
    REPORT.update({'project_root': str(ROOT), 'export_directory': str(OUT), 'date_timezone': 'Asia/Shanghai', 'generated_at': dt.datetime.now(TZ).isoformat(timespec='seconds')})
    if args.mode in ('export', 'all'):
        export_chats()
        export_setup()
        plan_packages()
        dump(report_path, REPORT)
    if args.mode in ('pack', 'pack-core', 'all'):
        plans = plan_packages()
        if args.mode == 'pack-core':
            plans = plans[:1]
        for name, entries in plans:
            pack(name, entries)
            dump(report_path, REPORT)
    if args.mode in ('verify', 'all'):
        verify_packages()
        dump(report_path, REPORT)
    print('Completed:', args.mode, str(OUT), flush=True)


if __name__ == '__main__':
    main()
