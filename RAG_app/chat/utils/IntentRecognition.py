"""
    意图识别模块，判断用户提问是否与调查新闻相关
"""
import json
from RAG_app.common.LoadModel import LoadModel

def intent_recognition(question: str, history):
    # 得到本地大模型
    local_model = LoadModel().local_llm
    prompt = f"""
        你是一个专业的新闻领域意图识别专家。你的任务是判断用户的输入属于以下哪一类：【新闻回溯】、【其他】。

        # 输入信息
        - 【近期历史对话】为你提供用户之前几轮问过的问题和助手的回答
        - 【用户当前问题】是你要判断的这句话
        - 【当前时间】是判断相对时间（去年、上个月、3年前）的基准
        - 【近期历史对话】 {history}
        
        # Definition: 什么是"新闻回溯"
        包括但不限于以下范畴：
        1. 询问过去某个具体时间点发生的新闻事件（如"2014年洲际国奥男篮争霸赛"、"2014年世界杯决赛"）
        2. 询问某个新闻事件的详细背景、起因、经过、结果
        3. 询问新闻事件的相关人物、地点、组织（如"杨宪益是谁"、"科比哪年去世的"）
        4. 询问某条新闻的后续进展、影响和评价
        5. 对新闻事件之间的关联性进行追问（如"与这个事件同年发生的还有什么大事"）
        6. 询问过去发生的体育赛事、政治事件、经济危机、科技突破等
        7. 当用户的提问里面包含“新闻”两个字时，判定为【新闻回溯】
        8. **对上一轮新闻话题的追问**——问题中包含"这件事、他、那个人、那次比赛、这个事件"等指代词，且指代对象是历史对话中的新闻事件
        
        # Definition: 什么是"其他"
        1. 纯日常闲聊、个人情感倾诉，不涉及任何具体新闻事件
        2. 纯粹的技术问题（如"Python怎么读取Excel文件"）
        3. 与具体新闻事件无关的常识问答、概念解释
        4. 实时性新闻（如"今天天气怎么样"、"刚才发生了什么"），不属于新闻回溯范畴
        
        # 指代改写规则（重要）
        判断前，先看【近期历史对话】：
        1. 如果当前问题包含指代词（这件事、他、那个人、那次、这个、它、这里），**先根据历史对话把指代词替换成具体事件/人物/时间**，再判断。
        2. 如果历史对话里最近一轮是"新闻回溯"类话题，且当前问题在继续追问（如"后来呢"、"结果如何"、"是谁"），**判定为【新闻回溯】**。
        3. 如果当前问题能独立成立（不依赖历史），**只用当前问题判断**。
        
        # 相对时间处理
        根据【当前时间】把相对时间转成绝对时间：
        - "去年" = 当前年份 - 1
        - "上个月" = 当前月份 - 1
        - "3年前" = 当前年份 - 3
        转换后如果指向过去的具体事件，判定为【新闻回溯】。
        
        # 优先级规则
        当一个问题**同时涉及新闻和其他领域**时（如"2014年医疗事故的法律赔偿标准"），按以下优先级判定：
        - 如果用户的核心诉求是**了解过去发生的具体事件**，判定为【新闻回溯】
        - 如果用户的核心诉求是**寻求建议、解决方案或科普解释**，判定为【其他】
        
        # Output Format
        仅输出一个JSON对象，不要包含任何其他解释文字：
        {{
            "category": "news/other",
            "confidence": "high/medium/low"
        }}
        
        # Examples
        
        ## 基础新闻回溯
        User: "2014年国奥男篮争霸赛的结果是什么"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        User: "2013年世界杯预选赛中国队表现怎么样"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        User: "2008年金融危机是怎么发生的"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        ## 人物/事件问询
        User: "杨宪益先生离开我们多久了"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        User: "科比是哪年去世的"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        ## 指代追问（需要看历史）
        【近期历史对话】
        用户：2014年洲际国奥男篮争霸赛发生了什么
        助手：2014年洲际国奥男篮争霸赛于7月5日至7日在云南曲靖举行...
        User: "这件事的冠军是谁"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        【近期历史对话】
        用户：2014年洲际国奥男篮争霸赛发生了什么
        助手：2014年洲际国奥男篮争霸赛于7月5日至7日在云南曲靖举行...
        User: "那次比赛有几支球队参加"
        Assistant: {{"category": "news", "confidence": "high"}}
        
        ## 其他
        User: "今天北京天气怎么样"
        Assistant: {{"category": "other", "confidence": "high"}}
        
        User: "Python怎么读取Excel文件"
        Assistant: {{"category": "other", "confidence": "high"}}
        
        User: "今天心情好差，感觉活着没意思"
        Assistant: {{"category": "other", "confidence": "high"}}
        
        User: "高血压患者平时应该注意什么"
        Assistant: {{"category": "other", "confidence": "high"}}
        
        User: "2014年医疗事故的法律赔偿标准是什么"
        Assistant: {{"category": "other", "confidence": "medium"}}
        
        ## 无历史时的指代（应判 other）
        【近期历史对话】（空）
        User: "这件事的冠军是谁"
        Assistant: {{"category": "other", "confidence": "medium"}}
"""

    # 意图识别
    rs = local_model.invoke([
        {"role": "system","content": prompt},
        {"role": "user","content": f"请解析用户的问题：{question}"}
    ])
    return json.loads(rs.content)["category"]

if __name__ == "__main__":
    q = "6月20号发生了什么"
    q1 = "这件事因为什么爆发的"
    q2 = "这件事的冠军是谁"
    q3 = "说说有关奥特曼系列汽车的新闻"
    rs = intent_recognition(q3, "2014年洲际国奥男篮争霸赛于7月5日至7日在云南曲靖举行...")
    print(rs)