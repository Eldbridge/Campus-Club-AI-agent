# ==============================================
# 创协 AI 咨询助手
# ==============================================
import streamlit as st
import requests

# ----------------------
# 1. 网页基础设置
# ----------------------
st.set_page_config(
    page_title="创协 AI 助手",
    page_icon="🎓",
    layout="centered"
)
st.title("🎓 学校创新创业协会 AI 咨询助手")
st.caption("我可以回答：招新、比赛、报名、活动、组队等问题")

# ----------------------
# 2. 从 Streamlit Secrets 安全读取密钥
# ----------------------
try:
    API_KEY = st.secrets["API_KEY"]
    ENDPOINT_ID = st.secrets["ENDPOINT_ID"]
except:
    pass

MODEL_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# ----------------------
# 3. 创协专属知识库（你可以随便改）
# ----------------------
CHUANGXIE_INFO = """
你是学校创业协会AI助手，只根据以下信息回答，简洁、礼貌、口语化，不要编造：

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
"""

# ----------------------
# 4. AI Agent 核心函数
# ----------------------
def ai_agent_answer(question):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 给大模型的指令
    prompt = f"""
    你是学校创业协会AI助手。
    只允许使用下面的资料回答，不许编造内容。
    回答简短、友好、口语化。

    资料：
    {CHUANGXIE_INFO}

    用户问题：{question}
    回答：
    """

    data = {
        "model":  ENDPOINT_ID,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post(
            MODEL_URL,
            headers=headers,
            json=data,
            timeout=10
        )
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI 暂时无法回答，可直接咨询创协部长。\n错误：{str(e)[:30]}"

# ----------------------
# 5. 用户交互界面
# ----------------------
user_question = st.text_input(
    "请问你想咨询什么？",
    placeholder="例如：怎么加入创协？有什么比赛？"
)

if user_question:
    with st.spinner("AI 正在思考..."):
        answer = ai_agent_answer(user_question)
        st.markdown(f"💡 **AI 回答：**\n\n{answer}")

st.divider()
st.caption(" 基于 Streamlit + 大模型| 创协专属 AI Agent")