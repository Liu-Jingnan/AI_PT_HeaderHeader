import time
import os
from dotenv import load_dotenv
from openai import OpenAI

MAX_RETRIES = 5
tempature = 0.5

# 从项目根目录加载 .env 文件
load_dotenv()

if "OPENAI_API_KEY" :
    print("检测到 OPENAI_API_KEY 环境变量，准备初始化客户端...")
else:
    print("未检测到 OPENAI_API_KEY 环境变量，请确保已在 .env 文件中正确设置。")

# 获取 API Key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY 环境变量。")

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

print(f"客户端初始化成功！Key ID: ...{api_key[-4:]} 🚀")

class PTGuide:
    """概率论与数理统计导师"""

    def __init__(self, client):
        self.client = client
        self.system_role = "你是一个严格但耐心的概率论与数理统计导师，擅长用简单易懂的语言解释复杂概念，用语简洁明了。"
        self.system_role = open("Theresa.txt", "r", encoding="utf-8").read()
        # 初始化历史记录，包含系统角色设定
        self.system_prompt = self.system_role
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def RemStreamOut(self, prompt):
        for attempt in range(MAX_RETRIES):
            try:
                """流式输出聊天响应"""
                self.history.append({"role": "user", "content": prompt})

                stream = client.chat.completions.create(
                    temperature= tempature,
                    model="glm-4.5",
                    messages=self.history,
                    stream=True  # <--- 开启流模式
                )

                ai_pieces = []

                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if isinstance(content, list):
                        for item in content:
                            text = item.get("text") if isinstance(item, dict) else None
                            if text:
                                print(text, end="", flush=True)
                                ai_pieces.append(text)
                    # 若直接为字符串，则直接打印
                    elif isinstance(content, str):
                        print(content, end="", flush=True)
                        ai_pieces.append(content)
                print("\n")

                ai_reply = "".join(ai_pieces)
                self.history.append({"role": "assistant", "content": ai_reply})
                self.forget()  # 清理记忆

                break

            except Exception as e:
                print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2) # 等待两秒后重试
                else:
                    return "❌ 服务暂时不可用，请稍后再试。"

    def forget (self):
        """清除超出十轮的上下文记忆"""
        if len(self.history) > 20:
            self.history = self.history[-19:]

    def show_memory(self):
        """调试用：查看当前上下文积累了多少"""
        print(f"\n🧠 当前记忆长度: {len(self.history)} 条消息")
        for msg in self.history:
            print(f"[{msg['role']}]: {msg['content'][:20]}...")

    def explain_defintion(self, definition: str) -> str:
        """解释概率论与数理统计定义"""

        prompt = f"""你好，特蕾西娅！
    请详细解释以下概率论与数理统计定义：
        {definition}
```

        输出要求：
        1. 定义：给出定义的详细解释。
        2. 例子：提供相关的例子帮助理解。
        
        """
        print ("您的AI小导师正在努力解释中...\n")
        self.RemStreamOut( prompt )

    def analyze_question(self, question: str) -> str:
        """分析概率论与数理统计问题并给出解答"""

        prompt = f"""你好，特蕾西娅！
        请详细解答以下概率论与数理统计问题：
        {question}
```

        输出要求：
        1. 题解思路：使用清晰的逻辑表明思考经过。
        2. 具体题解步骤：逐步展示解题过程。
        3. 最终答案：明确给出最终结果。
        """

        print ("您的AI小导师正在努力解题中...\n")
        self.RemStreamOut( prompt )

    def create_training(self, topic: str, sum : int = 5 ) -> str:
        """提供概率论与数理统计的练习题"""

        prompt = f"""你好，特蕾西娅！
            请以{topic}为核心知识点创建练习题：
    ```

            输出要求：
            1. 题目：涵盖该主题的核心概念，难度梯度明显，涵盖各层次，适于初学者练习。
            """
        print ("您的AI小导师正在努力出题中...\n")
        self.RemStreamOut( prompt )

    def check_training(self, training: str,  ) -> str:
        """检查概率论与数理统计的练习题"""

        prompt = f"""你好，特蕾西娅！
            请检查以下概率论与数理统计练习题的正确性：
            {training}
    ```

            输出要求：
            1. 正误：指出题目的正确性或错误性。
            2. 详解：提供详细的解答和解释。
            """

        print ("您的AI小导师正在努力批改中...\n")
        self.RemStreamOut( prompt )

    def chat (self, task_kind: int , user_input: str) -> str:
        """根据用户输入自动判断任务类型并执行相应操作"""

        switch = {
            1: self.explain_defintion,
            2: self.analyze_question,
            3: self.create_training,
            4: self.check_training
        }

        task_function = switch.get(task_kind, None)
        if task_function:
            return task_function(user_input)
        else:
            print("❌ 未识别的任务类型，请输入有效的任务编号（1-4）。")


tutor = PTGuide(client)

while True:

    task = int(input ("请选择任务类型（输入对应数字）：\n1. 概念解释\n2. 例题讲解\n3. 生成练习题\n4. 检查答案 \n5. 退出\n"))
    if task == 5:
        print("感谢使用，再见！👋")
        break
    user_input = input("请输入您的问题（输入 'exit' 退出）：\n")
    if user_input.lower() == 'check memory':
        tutor.show_memory()
        continue
    if user_input.lower() == 'exit':
        print("感谢使用，再见！👋")
        break

    tutor.chat( task, user_input )
