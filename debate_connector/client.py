import asyncio
import json
import subprocess
import sys
from urllib.parse import urlencode

import websockets

from .prompt import build_debate_prompt, build_judge_prompt


def run_ai(cmd: str, prompt: str, timeout: int = 90) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True,
            input=prompt, capture_output=True,
            text=True, timeout=timeout,
        )
        output = result.stdout.strip()
        if not output and result.stderr:
            print(f"\n[warn] AI stderr: {result.stderr[:200]}", file=sys.stderr)
        return output
    except subprocess.TimeoutExpired:
        print("\n[warn] AI command timed out", file=sys.stderr)
        return ''
    except Exception as e:
        print(f"\n[error] AI command failed: {e}", file=sys.stderr)
        return ''


def parse_judge_output(raw: str) -> dict | None:
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


async def connect(host: str, room: str, slot: str, name: str, cmd: str):
    params = urlencode({'slot': slot, 'name': name})
    clean_host = host.removeprefix('https://').removeprefix('http://')
    is_local = clean_host.startswith('localhost') or clean_host.startswith('127.')
    proto = 'ws' if is_local else 'wss'
    url = f"{proto}://{clean_host}/ws/{room}?{params}"

    print(f"  连接: {url}")
    print(f"  身份: {slot} ({name})")
    print(f"  命令: {cmd}")
    print("─" * 50)

    async for ws in websockets.connect(url, ping_interval=30, ping_timeout=10):
        try:
            await ws.send(json.dumps({'event': 'join', 'slot': slot, 'name': name}))
            print(f"[✓] 已连接，等待辩论开始...")

            async for raw in ws:
                msg = json.loads(raw)
                event = msg.get('event')

                if event == 'roster':
                    connected = sum(1 for v in msg['slots'].values() if v.get('connected'))
                    print(f"[roster] {connected}/5 已连接", end='\r')

                elif event == 'debate_started':
                    print(f"\n[✓] 辩论开始！辩题：{msg['topic']}")

                elif event == 'round_start':
                    print(f"\n[round {msg['roundIndex']+1}/8] {msg['roundLabel']} — 发言方：{msg['slot']} — {msg['secs']}秒")

                elif event == 'your_turn':
                    print(f"\n[▶] 轮到你了！{msg['roundLabel']} ({msg['secs']}秒)")
                    prompt = build_debate_prompt(msg)
                    print(f"[~] 正在调用 AI...")
                    content = run_ai(cmd, prompt, timeout=msg['secs'] - 5)
                    if content:
                        await ws.send(json.dumps({'event': 'speech', 'content': content}))
                        preview = content[:80].replace('\n', ' ')
                        print(f"[✓] 已发言: {preview}{'...' if len(content) > 80 else ''}")
                    else:
                        print("[!] AI 未返回内容，跳过本轮")

                elif event == 'speech':
                    if msg['slot'] != slot:
                        preview = msg['content'][:60].replace('\n', ' ')
                        print(f"[{msg['roundLabel']}] {msg['slot']}({msg['agentName']}): {preview}...")

                elif event == 'judge_now':
                    print(f"\n[▶] 评审时间！请对辩论进行评分...")
                    prompt = build_judge_prompt(msg)
                    print(f"[~] 正在调用 AI 评分...")
                    raw_score = run_ai(cmd, prompt, timeout=60)
                    score = parse_judge_output(raw_score)
                    if score:
                        await ws.send(json.dumps({'event': 'score', **score}))
                        print(f"[✓] 评分已提交: 胜方={score.get('winner')}")
                    else:
                        print(f"[!] 无法解析评分输出: {raw_score[:100]}")

                elif event == 'debate_ended':
                    winner = msg.get('winner', '')
                    label = '正方获胜' if winner == 'pro' else '反方获胜' if winner == 'con' else '平局'
                    print(f"\n[✓] 辩论结束！结果：{label}")
                    if msg.get('comment'):
                        print(f"    评语：{msg['comment']}")
                    return

                elif event == 'error':
                    print(f"[!] 错误: {msg.get('message')}")
                    return

        except websockets.ConnectionClosed as e:
            if e.code == 4001:
                print(f"\n[!] 该 slot ({slot}) 已被占用")
                return
            print(f"\n[~] 连接断开，3秒后重连...")
            await asyncio.sleep(3)
