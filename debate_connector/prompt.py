SLOT_LABELS = {
    'pro_1': '正方一辩',
    'pro_2': '正方二辩',
    'con_1': '反方一辩',
    'con_2': '反方二辩',
    'judge': '评委',
}

SIDE_LABELS = {
    'pro_1': '正方（支持辩题）',
    'pro_2': '正方（支持辩题）',
    'con_1': '反方（反对辩题）',
    'con_2': '反方（反对辩题）',
}

INTERIM_JUDGE_PROMPT_TEMPLATE = """你是一位公正的辩论评委，正在主持一场 2v2 辩论。本场比赛共 4 个回合，每个回合双方各发言一次后由你做中场点评，第 4 回合结束后你将给出最终胜负。

辩题：{topic}
当前点评阶段：{round_label}
时间限制：{secs} 秒（约 {word_limit} 字以内）

=== 截至目前的完整发言记录 ===
{transcript}

请对正反双方本回合的表现做一次简洁的中场点评。要求：
- 分别点评正方与反方本回合的逻辑、论据、攻防表现
- 指出值得肯定之处与可以改进之处
- 不要在此阶段宣布胜负，仅做过程性评价
- 字数控制在 {word_limit} 字以内
- 直接输出点评内容，不要加任何前缀、标题或 JSON
"""

JUDGE_PROMPT_TEMPLATE = """你是一位公正的辩论评委。请根据以下辩论记录进行评分。

辩题：{topic}

=== 完整辩论记录 ===
{transcript}

请给出你的评判：
1. 评选胜方（正方 pro / 反方 con / 平局 none）
2. 双方评分（0-100 整数）
3. 评语（200字以内）

严格按以下 JSON 格式输出，不要有任何多余内容：
{{
  "winner": "pro",
  "scores": {{"pro": 85, "con": 78}},
  "comment": "评语内容"
}}"""

DEBATE_PROMPT_TEMPLATE = """你正在参加一场正式辩论比赛。

辩题：{topic}
你的身份：{slot_label}（{side_label}）
当前阶段：{round_label}
时间限制：{secs} 秒（约 {word_limit} 字以内）

=== 辩论历史 ===
{history}

=== 对方最新发言 ===
{opponent_last}

请给出你的辩论发言。要求：
- 紧扣辩题，逻辑清晰，观点鲜明
- 字数控制在 {word_limit} 字以内
- 直接输出发言内容，不要加任何前缀或说明
"""


def build_debate_prompt(msg: dict) -> str:
    slot = msg['slot']
    history_lines = []
    for s in msg.get('history', []):
        label = SLOT_LABELS.get(s['slot'], s['slot'])
        history_lines.append(f"[{s['roundLabel']}] {label} ({s['agentName']}):\n{s['content']}\n")

    return DEBATE_PROMPT_TEMPLATE.format(
        topic=msg['topic'],
        slot_label=SLOT_LABELS.get(slot, slot),
        side_label=SIDE_LABELS.get(slot, ''),
        round_label=msg['roundLabel'],
        secs=msg['secs'],
        word_limit=msg['secs'] * 4,
        history='\n'.join(history_lines) if history_lines else '（暂无历史发言）',
        opponent_last=msg.get('opponentLast') or '（对方尚未发言）',
    )


def build_interim_judge_prompt(msg: dict) -> str:
    lines = []
    for i, s in enumerate(msg.get('history', []), 1):
        label = SLOT_LABELS.get(s['slot'], s['slot'])
        lines.append(f"[{i}] {s['roundLabel']} | {label} ({s['agentName']}):\n{s['content']}\n")
    return INTERIM_JUDGE_PROMPT_TEMPLATE.format(
        topic=msg['topic'],
        round_label=msg['roundLabel'],
        secs=msg['secs'],
        word_limit=msg['secs'] * 4,
        transcript='\n'.join(lines) if lines else '（暂无发言）',
    )


def build_judge_prompt(msg: dict) -> str:
    lines = []
    for i, s in enumerate(msg.get('transcript', []), 1):
        label = SLOT_LABELS.get(s['slot'], s['slot'])
        lines.append(f"[{i}] {s['roundLabel']} | {label} ({s['agentName']}):\n{s['content']}\n")
    return JUDGE_PROMPT_TEMPLATE.format(
        topic=msg['topic'],
        transcript='\n'.join(lines),
    )
