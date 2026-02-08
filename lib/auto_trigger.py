#!/usr/bin/env python3
"""
MemU Auto-Trigger Detection Module
自动检测需要存储到长期记忆的关键信息
"""
import re
import sys
import json
from typing import List, Tuple, Optional

# 自动触发词模式 (按类别)
TRIGGER_PATTERNS = {
    "preference": [
        r"我喜欢\s*(.+?)[。，!！]",
        r"我讨厌\s*(.+?)[。，!！]",
        r"我偏好\s*(.+?)[。，!！]",
        r"我习惯\s*(.+?)[。，!！]",
        r"我不喜欢\s*(.+?)[。，!！]",
    ],
    "health": [
        r"我有\s*(.+?)(?:病|症|问题)?[，。！,]",
        r"我(?:对|有)\s*(.+?)过敏",
        r"我患有\s*(.+?)[。，]",
        r"我正在服用\s*(.+?)[。，]",
    ],
    "personal": [
        r"我的\s*(.+?)\s*是\s*(.+?)[。，!！]",
        r"我(?:的)?\s*(?:名字|姓名|职业|职位)\s*(?:是|叫)\s*(.+?)[。，]",
        r"我在\s*(.+?)\s*工作",
        r"我是\s*(.+?)(?:的|，)",
    ],
    "explicit": [
        r"记住[这|那]个[：:]?\s*(.+)",
        r"请记住[：:]?\s*(.+)",
        r"记下来[：:]?\s*(.+)",
    ]
}

def detect_triggers(message: str) -> List[Tuple[str, str]]:
    """
    检测消息中的记忆触发词
    
    Returns:
        List of (category, extracted_content) tuples
    """
    triggers = []
    
    for category, patterns in TRIGGER_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 多组匹配，合并
                    content = " ".join(m.strip() for m in match if m)
                else:
                    content = match.strip()
                
                if content and len(content) >= 2:  # 过滤过短内容
                    triggers.append((category, content))
    
    return triggers

def format_memory(category: str, content: str, user_id: str = "master") -> dict:
    """格式化记忆内容"""
    category_names = {
        "preference": "偏好",
        "health": "健康",
        "personal": "个人信息",
        "explicit": "重要信息"
    }
    
    return {
        "content": f"[{category_names.get(category, '信息')}] {content}",
        "user_id": user_id,
        "category": category,
        "source": "auto_trigger"
    }

def should_memorize(message: str, min_confidence: float = 0.7) -> Optional[dict]:
    """
    判断是否应该存储到 MemU
    
    Returns:
        Memory dict if should memorize, None otherwise
    """
    triggers = detect_triggers(message)
    
    if not triggers:
        return None
    
    # 按优先级排序：explicit > health > preference > personal
    priority = {"explicit": 4, "health": 3, "preference": 2, "personal": 1}
    triggers.sort(key=lambda x: priority.get(x[0], 0), reverse=True)
    
    # 返回最高优先级的
    category, content = triggers[0]
    return format_memory(category, content)

# 测试
def test_detection():
    """测试触发词检测"""
    test_cases = [
        "我喜欢简洁的回复风格",
        "我有前庭性偏头痛",
        "我的职业是游戏发行商",
        "记住这个：明天要检查gateway",
        "我讨厌等待",
        "我对花生过敏",
        "这是一个普通句子",  # 不应触发
    ]
    
    print("=" * 50)
    print("MemU Auto-Trigger Detection Test")
    print("=" * 50)
    
    for msg in test_cases:
        result = should_memorize(msg)
        status = "📝 存储" if result else "⏭️ 跳过"
        print(f"\n{status}: {msg}")
        if result:
            print(f"   → Category: {result['category']}")
            print(f"   → Content: {result['content']}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    # 如果通过管道接收输入
    if not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()
        result = should_memorize(input_text)
        if result:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(json.dumps({"skip": True}))
    else:
        # 运行测试
        test_detection()
