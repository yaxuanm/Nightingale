#!/usr/bin/env python3
"""
固定测试数据 - 30个预设的prompt和对应的音频文件
用于用户测试，不进行随机生成
"""

FIXED_PROMPTS = [
    {
        "id": "test_001",
        "prompt": "A peaceful forest at dawn with gentle bird songs and rustling leaves",
        "category": "nature",
        "description": "清晨森林的宁静氛围"
    },
    {
        "id": "test_002", 
        "prompt": "Ocean waves crashing on a sandy beach with seagulls in the distance",
        "category": "nature",
        "description": "海浪拍打沙滩的声音"
    },
    {
        "id": "test_003",
        "prompt": "Rain falling softly on a tin roof with distant thunder",
        "category": "weather",
        "description": "雨滴落在屋顶的声音"
    },
    {
        "id": "test_004",
        "prompt": "A cozy coffee shop with espresso machine sounds and soft jazz music",
        "category": "urban",
        "description": "咖啡店的温馨氛围"
    },
    {
        "id": "test_005",
        "prompt": "A mountain stream flowing over rocks with water droplets",
        "category": "nature", 
        "description": "山间溪流的声音"
    },
    {
        "id": "test_006",
        "prompt": "A crackling campfire with wood burning and embers popping",
        "category": "nature",
        "description": "篝火燃烧的声音"
    },
    {
        "id": "test_007",
        "prompt": "A library with pages turning and soft footsteps on carpet",
        "category": "urban",
        "description": "图书馆的安静氛围"
    },
    {
        "id": "test_008",
        "prompt": "A thunderstorm with heavy rain and lightning strikes",
        "category": "weather",
        "description": "雷雨交加的天气"
    },
    {
        "id": "test_009",
        "prompt": "A zen garden with wind chimes and flowing water",
        "category": "meditation",
        "description": "禅意花园的宁静"
    },
    {
        "id": "test_010",
        "prompt": "A busy train station with announcements and footsteps",
        "category": "urban",
        "description": "繁忙的火车站"
    },
    {
        "id": "test_011",
        "prompt": "A meadow with buzzing bees and butterfly wings",
        "category": "nature",
        "description": "草地上的昆虫声音"
    },
    {
        "id": "test_012",
        "prompt": "A fireplace in a cabin with wind howling outside",
        "category": "home",
        "description": "木屋中的壁炉声"
    },
    {
        "id": "test_013",
        "prompt": "A waterfall cascading into a deep pool below",
        "category": "nature",
        "description": "瀑布倾泻的声音"
    },
    {
        "id": "test_014",
        "prompt": "A busy kitchen with pots clanging and food sizzling",
        "category": "home",
        "description": "忙碌厨房的声音"
    },
    {
        "id": "test_015",
        "prompt": "A gentle breeze through bamboo forest",
        "category": "nature",
        "description": "竹林中的微风"
    },
    {
        "id": "test_016",
        "prompt": "A meditation room with Tibetan singing bowls",
        "category": "meditation",
        "description": "冥想室的颂钵声"
    },
    {
        "id": "test_017",
        "prompt": "A city park with children playing and birds singing",
        "category": "urban",
        "description": "城市公园的活力"
    },
    {
        "id": "test_018",
        "prompt": "A snowstorm with wind blowing through trees",
        "category": "weather",
        "description": "暴风雪的声音"
    },
    {
        "id": "test_019",
        "prompt": "A vintage record player with vinyl crackling",
        "category": "music",
        "description": "黑胶唱片机的声音"
    },
    {
        "id": "test_020",
        "prompt": "A tropical rainforest with exotic birds and insects",
        "category": "nature",
        "description": "热带雨林的生机"
    },
    {
        "id": "test_021",
        "prompt": "A clock tower chiming at midnight",
        "category": "urban",
        "description": "午夜钟楼的钟声"
    },
    {
        "id": "test_022",
        "prompt": "A gentle stream flowing through a meadow",
        "category": "nature",
        "description": "草地中的小溪"
    },
    {
        "id": "test_023",
        "prompt": "A busy marketplace with vendors calling out",
        "category": "urban",
        "description": "繁忙的市场声音"
    },
    {
        "id": "test_024",
        "prompt": "A gentle rain on a wooden deck",
        "category": "weather",
        "description": "雨滴落在木甲板上"
    },
    {
        "id": "test_025",
        "prompt": "A cat purring by a warm radiator",
        "category": "home",
        "description": "猫咪在暖气旁打呼噜"
    },
    {
        "id": "test_026",
        "prompt": "A distant church bell ringing on a Sunday morning",
        "category": "urban",
        "description": "周日早晨的教堂钟声"
    },
    {
        "id": "test_027",
        "prompt": "A gentle wind through tall grass",
        "category": "nature",
        "description": "风吹过高草的声音"
    },
    {
        "id": "test_028",
        "prompt": "A bubbling hot spring in the mountains",
        "category": "nature",
        "description": "山中温泉的冒泡声"
    },
    {
        "id": "test_029",
        "prompt": "A quiet study room with pencil scratching on paper",
        "category": "home",
        "description": "安静书房中的书写声"
    },
    {
        "id": "test_030",
        "prompt": "A gentle lullaby with soft humming",
        "category": "music",
        "description": "轻柔的摇篮曲"
    }
]

def get_fixed_prompts():
    """返回固定的30个prompt"""
    return FIXED_PROMPTS

def save_fixed_prompts_to_file(output_file):
    """将固定prompt保存到文件"""
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(FIXED_PROMPTS, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    save_fixed_prompts_to_file("fixed_test_prompts.json")
    print(f"已保存 {len(FIXED_PROMPTS)} 个固定prompt到 fixed_test_prompts.json") 