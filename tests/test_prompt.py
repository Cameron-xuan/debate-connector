import unittest

from debate_connector.prompt import (
    build_debate_prompt,
    build_interim_judge_prompt,
    build_judge_prompt,
)


class InterimJudgePromptTests(unittest.TestCase):
    def test_interim_judge_prompt_separates_current_round_from_context(self):
        msg = {
            "topic": "开源AI是否更有利于社会发展",
            "roundLabel": "评委点评（第二回合）",
            "secs": 75,
            "history": [
                {
                    "slot": "pro_1",
                    "roundLabel": "正方立论",
                    "agentName": "pro-a",
                    "content": "正方第一轮",
                },
                {
                    "slot": "con_1",
                    "roundLabel": "反方立论",
                    "agentName": "con-a",
                    "content": "反方第一轮",
                },
                {
                    "slot": "judge",
                    "roundLabel": "评委点评（第一回合）",
                    "agentName": "judge-a",
                    "content": "第一轮点评",
                },
                {
                    "slot": "pro_2",
                    "roundLabel": "正方二辩质询反方",
                    "agentName": "pro-b",
                    "content": "正方第二轮",
                },
                {
                    "slot": "con_2",
                    "roundLabel": "反方二辩质询正方",
                    "agentName": "con-b",
                    "content": "反方第二轮",
                },
            ],
        }

        prompt = build_interim_judge_prompt(msg)

        current_start = prompt.index("=== 本回合发言")
        previous_start = prompt.index("=== 此前发言记录")
        current_section = prompt[current_start:previous_start]
        previous_section = prompt[previous_start:]

        self.assertIn("[#4] 正方二辩质询反方", current_section)
        self.assertIn("[#5] 反方二辩质询正方", current_section)
        self.assertNotIn("[#1] 正方立论", current_section)
        self.assertIn("[#1] 正方立论", previous_section)
        self.assertIn("[#3] 评委点评（第一回合）", previous_section)
        self.assertIn("严格按发言编号和发言顺序判断回应义务", prompt)

    def test_debater_prompt_constrains_unverified_real_world_facts(self):
        prompt = build_debate_prompt({
            "topic": "开源AI是否更有利于社会发展",
            "slot": "pro_2",
            "roundLabel": "正方二辩质询反方",
            "roundId": "rebut_pro2",
            "secs": 180,
            "history": [],
            "opponentLast": "反方观点",
        })

        self.assertIn("不得虚构现实案例、年份、国家、公司、数字、伤亡或损失后果", prompt)
        self.assertIn("无法确认真实性的外部事实不得使用", prompt)
        self.assertIn("必须省略该案例", prompt)
        self.assertNotIn("假设场景", prompt)
        self.assertIn("输出语言必须与辩题主要语言一致", prompt)

    def test_final_judge_prompt_marks_unsupported_facts_as_unproven(self):
        prompt = build_judge_prompt({
            "topic": "开源AI是否更有利于社会发展",
            "transcript": [
                {
                    "slot": "pro_1",
                    "roundLabel": "正方立论",
                    "agentName": "pro-a",
                    "content": "具体案例主张",
                },
            ],
        })

        self.assertIn("待证事实", prompt)
        self.assertIn("不得作为已经成立的胜负依据", prompt)
        self.assertIn("comment 必须使用中文", prompt)


if __name__ == "__main__":
    unittest.main()
