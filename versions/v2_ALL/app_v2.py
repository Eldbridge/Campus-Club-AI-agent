import streamlit as st
import requests

#Unified management of configuration information: key, interface, and model information
#配置类；统一管理配置信息：密钥，接口，模型信息
class AIConfig:
    def __init__(self):
        self.API_KEY = st.secrets["API_KEY"]
        self.ENDPOINT_ID = st.secrets["ENDPOINT_ID"]
        self.MODEL_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.HEADERS = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content_Type":"application/json"
            }


#Ai Class,Core logic: Responsible for communicating with large models, sending requests,
#processing returns, and catching exceptions
#AI类,核心逻辑:负责与大模型通信，发请求，处理返回，捕获异常


class AIClient:
    def __init__(self):
        self.config = AIConfig()
        self.CHUANGXIE_INFO = '''
知识库：

1. 协会福利：
- 直推高水平双创竞赛（如互联网+、挑战杯）
- 项目孵化平台：与有创业想法的同学组队，共同打磨落地项目
- 创新创业学分认定 & 活动证书
- 366㎡创业苗圃免费使用
- 行业导师一对一指导
- 创业沙龙、尚创季等品牌活动

2. 创协加入方式：
问卷、开学第二周周四周五面试

3. 创协的主要竞赛：大创 triz杯

4. 比赛报名渠道：大创赛创业赛道直推名额

5. 比赛组队渠道：拉群，群里自由组队（拉好了部长会把群二维码发你）

下面是几篇资料文章：
1，大创赛宣传文章

青春敢创｜一篇读懂大创，每个人都能从0到1
大创？其实就是“校园造梦工厂”！
 大创全称「大学生创新创业训练计划」，它不是枯燥的实验，而是把你的奇思妙想变现的绿色通道！
整理了一份不废话干货，建议收藏！
1. 核心价值：
💰 奖金+补贴：国赛特等奖50W！
🎓 保研/复试：升学硬核加分项！
👔 就业/实习：优质项目直通大厂实习。
2. 神仙队友标准：
① 技术硬核组：懂Python、会数据分析的理工大神，负责把想法落地。
② 商业鬼才组：能把“卖矿泉水”讲出纳斯达克上市气势的PPT大师，负责路演忽悠（划掉）征服评委。
③ 财务稳如磐石组：算得清账、能把预算规划得明明白白的细心大佬。
3. 选题红黑榜：
✅ 推荐：校园痛点解决、AI+数学建模、跨境电商新模式、文化数字化。
❌ 避雷：假大空的“未来科技”、没有数据支撑的伪需求、纯理论讨论。
4. 关键节点：
立项答辩：现在（3月），完成申报与团队组建，创协提供一对一指导。
​中期答辩：10-11月，汇报项目进展，完善数据与原型。
​结项答辩：次年6月，最终成果展示与验收。
创协私藏·避坑指南（干货满满）
①拒绝“画大饼”：评委最烦没数据的空谈，一定要做实地调研！
​②善用“武器库”：学校孵化器免费给场地、给资源；创协也有往届获奖秘籍供参考。
​③答辩小技巧：正装是加分项，但自信更重要！咱们学生逻辑强，只要讲清逻辑，赢面很大！
往年学长学姐的比赛经验:
 选题接地气：大多从校园生活、社会痛点、文化传承出发，容易找到真实需求和落地场景。
​  形式多样：既有硬件装置、软件平台，也有商业策划、文化传播类项目，适合不同专业背景的同学参与。
 偏向实践：项目都强调“构建/开发/运营”，注重从想法到可落地成果的转化，符合大创赛“创新创业实践”的核心目标。
 大创不是一个人的战斗，是团队的并肩作战。2026年，愿所有创协人：思路如天马行空，落地如万马奔腾！
'''
    def _build_prompt(self,question:str) -> str:
        return f'''
你的职业是学校创新创业协会AI助手
你也是一个猫娘
例如，你会说：你好，喵
只允许使用下面的资料回答，不许编造内容
回答友好、口语化

资料:
{self.CHUANGXIE_INFO}

用户问题: {question}
   
'''
    def chat(self,question:str) -> str:
        prompt = self._build_prompt(question)
        #请求参数
        data = {
            "model":  self.config.ENDPOINT_ID,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            resp = requests.post(
                url = self.config.MODEL_URL,
                headers = self.config.HEADERS,
                json = data,
                timeout = 15
            )
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except:
            return "出现错误"


# Only responsible for  streamlit_UI
# 只负责前端streamlit渲染
class ChatUI:
    def __init__(self):
        self.ai_client = AIClient()
        self._init_page()

    #Page basic setting;
    #页面基础设置
    def _init_page(self):
        st.set_page_config(page_title = "创协AI智能体")
        st.title("🤝 创新创业协会AI助手")
        st.caption("有任何问题都可以问我<:>")

    def run(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        #History information;
        #历史消息
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        #ueser_input
        #用户输入
        user_input = st.chat_input("请输入你的问题......")
        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            with st.chat_message("user"):
                st.text(user_input)

            with st.chat_message("AI"):
                with st.spinner("思考中......"):
                    ai_response = self.ai_client.chat(user_input)
                    st.text(ai_response)

            st.session_state.messages.append({"role":"AI","content": ai_response})

if __name__ == "__main__":
    app = ChatUI()
    app.run()
