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

=== 本回合发言（这是你本次点评的唯一评价对象） ===
{current_transcript}

=== 此前发言记录（仅供理解上下文，不得作为“本回合表现”评价） ===
{previous_transcript}

请做一次真实辩论赛风格的中场点评。要求：
- 输出语言必须与辩题主要语言一致；如果辩题是中文，必须使用中文输出
- 只点评过程表现，不宣布胜负，不给最终比分
- 只评价“本回合发言”中的表现；此前发言只能作为上下文
- 严格按发言编号和发言顺序判断回应义务：一方不能因未回应其发言之后才出现的观点而被扣分
- 指出双方本回合最有效的推进和最明显的漏洞；不要把此前回合的表现说成本回合表现
- 区分“提出了主张/案例”和“完成了证明”：未经支撑或尚未被对方回应的案例，只能评价为攻击方向，不能直接认定为有效实证
- 对具体事实、年份、国家、公司、数字、伤亡或损失后果保持审慎；如果发言中没有给出来源或对方尚未承认，只能标记为“待证”，不能作为已成立优势
- 最后必须给出“下一回合关键看点”，但只能基于双方已经暴露的未决争议，不得引入新事实、新案例或替任一方设计新论点
- 点评要具体，避免“双方都很精彩”这类空话
- 字数控制在 {word_limit} 字以内

请按以下格式输出：
正方本回合优势：
正方需要补强：
反方本回合优势：
反方需要补强：
下一回合关键看点：
"""

JUDGE_PROMPT_TEMPLATE = """你是一位公正的辩论评委。请根据以下辩论记录进行评分。

辩题：{topic}

=== 完整辩论记录 ===
{transcript}

请基于真实辩论赛逻辑评判，并按 100 分制分别给正反双方打分：
1. 立论与标准建立（20分）：是否清楚定义关键概念，建立可用于比较胜负的判断标准
2. 论证质量（25分）：主张、理由、证据/例子、结论是否形成完整逻辑链
3. 反驳与回应（25分）：是否真正回应对方关键论点，是否有效指出对方漏洞
4. 战场控制与推进（15分）：是否把比赛推进到对己方有利且重要的核心争议点
5. 总结陈词与回收（15分）：是否回收全场主要胜负点，比较双方表现，而不是临时提出大量新论点

评分要求：
- 输出 JSON 中的 comment 语言必须与辩题主要语言一致；如果辩题是中文，comment 必须使用中文
- 分数应体现全场表现，不要只看最后一轮
- 中场点评只能作为过程参考，不能替代最终独立判断
- 具体事实案例、年份、国家、公司、数字、伤亡或损失后果若未经文本支撑或双方承认，应视为“待证事实”，不得作为已经成立的胜负依据
- 如果一方把待证事实包装成实证案例，应在论证质量或回应质量中酌情扣分
- 如果双方都没有明显压倒对方，可以判 none
- winner 必须与总分和评语理由一致；若分差很小但一方关键战场更强，也可以给该方小胜

请给出：
1. 胜方（正方 pro / 反方 con / 平局 none）
2. 双方评分（0-100 整数）
3. 200字以内评语，说明决定胜负的 1-2 个核心理由，并点明主要失分项

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

=== 本阶段任务 ===
{stage_task}

=== 辩论历史 ===
{history}

=== 对方最新发言 ===
{opponent_last}

=== 评委上一轮提示 ===
{judge_focus}

请给出你的辩论发言。要求：
- 输出语言必须与辩题主要语言一致；如果辩题是中文，必须使用中文输出
- 必须回应对方最新发言中的一个关键论点，不要自说自话
- 如果有评委提示，要在策略上处理该关键看点；不要生硬地说“评委刚才说”
- 围绕 1-2 个最重要战场推进，不要平均铺开所有问题
- 不要编造对方没有说过的观点
- 不得虚构现实案例、年份、国家、公司、数字、伤亡或损失后果
- 无法确认真实性的外部事实不得使用；不要把不确定信息改写成“某公司/某国家/某年份/某事故”等模糊案例
- 具体事实案例必须来自辩论历史、用户提供材料、给定事实库，或属于你高度确信的公开常识；不满足时必须省略该案例，改用不含具体事实细节的原则性论证或机制推理
- 不要使用“综上所述，我们应该理性看待”等空泛结尾
- 字数控制在 {word_limit} 字以内
- 直接输出发言内容，不要加标题、项目符号或解释你如何完成任务
"""


def _format_history(history: list[dict]) -> str:
    lines = []
    for s in history:
        label = SLOT_LABELS.get(s['slot'], s['slot'])
        lines.append(f"[{s['roundLabel']}] {label} ({s['agentName']}):\n{s['content']}\n")
    return '\n'.join(lines) if lines else '（暂无历史发言）'


def _format_numbered_speeches(items: list[tuple[int, dict]], empty_text: str) -> str:
    lines = []
    for number, s in items:
        label = SLOT_LABELS.get(s['slot'], s['slot'])
        lines.append(f"[#{number}] {s['roundLabel']} | {label} ({s['agentName']}):\n{s['content']}\n")
    return '\n'.join(lines) if lines else empty_text


def _split_current_judge_scope(history: list[dict]) -> tuple[list[tuple[int, dict]], list[tuple[int, dict]]]:
    numbered = list(enumerate(history, 1))
    last_judge_index = -1
    for index, s in enumerate(history):
        if s.get('slot') == 'judge':
            last_judge_index = index

    previous = numbered[:last_judge_index + 1]
    current = [
        item for item in numbered[last_judge_index + 1:]
        if item[1].get('slot') != 'judge'
    ]
    return previous, current


def _last_judge_focus(history: list[dict]) -> str:
    for s in reversed(history):
        if s.get('slot') == 'judge':
            return s.get('content') or '（暂无评委提示）'
    return '（暂无评委提示）'


def _stage_task(round_id: str, slot: str) -> str:
    if round_id in ('open_pro1', 'open_con1'):
        return (
            "这是立论阶段。你的目标是建立己方的判断标准、定义关键概念，并提出 2-3 条核心论证链。"
            "如果对方已经发言，先回应其最关键的标准或定义，再展开己方框架。"
        )
    if round_id in ('rebut_pro2', 'rebut_con2'):
        return (
            "这是攻防/质询阶段。你的目标不是重新立论，而是抓住对方上一轮最脆弱的一环进行拆解，"
            "提出追问式压力，并补强己方最容易被攻击的论点。"
        )
    if round_id in ('free_1', 'free_2'):
        return (
            "这是自由辩论阶段。你的发言要短促、有针对性，优先回应对方最近观点和评委提示中的关键战场。"
            "不要铺陈长篇背景，不要重写立论稿。"
        )
    if round_id in ('close_con1', 'close_pro1'):
        return (
            "这是总结陈词阶段。你的目标是回收全场最重要的 1-2 个胜负标准，比较双方在这些标准下谁更充分，"
            "回应对方最后的关键攻击。不要依赖全新论点取胜。"
        )
    if slot == 'judge':
        return "你是评委，请根据双方刚完成的本回合攻防做过程性点评。"
    return "请根据当前阶段推进己方论证，并回应对方最新发言。"


def _word_limit(round_id: str, secs: int) -> int:
    if round_id in ('open_pro1', 'open_con1'):
        return 700
    if round_id in ('rebut_pro2', 'rebut_con2'):
        return 550
    if round_id in ('free_1', 'free_2'):
        return 400
    if round_id in ('close_con1', 'close_pro1'):
        return 650
    return secs * 4


def build_debate_prompt(msg: dict) -> str:
    slot = msg['slot']
    history = msg.get('history', [])
    round_id = str(msg.get('roundId', ''))
    secs = int(msg['secs'])

    return DEBATE_PROMPT_TEMPLATE.format(
        topic=msg['topic'],
        slot_label=SLOT_LABELS.get(slot, slot),
        side_label=SIDE_LABELS.get(slot, ''),
        round_label=msg['roundLabel'],
        secs=secs,
        word_limit=_word_limit(round_id, secs),
        stage_task=_stage_task(round_id, slot),
        history=_format_history(history),
        opponent_last=msg.get('opponentLast') or '（对方尚未发言）',
        judge_focus=_last_judge_focus(history),
    )


def build_interim_judge_prompt(msg: dict) -> str:
    previous, current = _split_current_judge_scope(msg.get('history', []))
    return INTERIM_JUDGE_PROMPT_TEMPLATE.format(
        topic=msg['topic'],
        round_label=msg['roundLabel'],
        secs=msg['secs'],
        word_limit=300,
        current_transcript=_format_numbered_speeches(current, '（暂无本回合发言）'),
        previous_transcript=_format_numbered_speeches(previous, '（暂无此前发言）'),
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
