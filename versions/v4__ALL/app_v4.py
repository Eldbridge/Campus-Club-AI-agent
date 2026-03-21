import streamlit as st
import requests
import os

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
        self.knowledge_file = "chuangxie_knowledge.txt"
        self.last_mtime = 0
        self.CHUANGXIE_INFO = ""
        self._load_knowledge()

    def _load_knowledge(self):
        try:
            with open(self.knowledge_file,"r",encoding = "utf-8") as f:
                self.CHUANGXIE_INFO = f.read()
                self.last_mtime = os.path.getmtime(self.knowledge_file)
                print("知识库已加载/更新成功")
        except FileNotFoundError:
            self.CHUANGXIE_INFO = "暂无创协资料，请联系管理员补充"
            self.last_mtime = 0

    def _check_knowledge_update(self):
        try:
            current_mtime = os.path.getmtime(self.knowledge_file)
            if current_mtime != self.last_mtime:
                print("监测到知识库更新，正在重新加载......")
                self._load_knowledge()
        except FileNotFoundError:
            if self.CHUANGXIE_INFO != "暂无创协资料，请联系管理员补充":
                self.CHUANGXIE_INFO = "知识库最新更新，相关资料已被删除"
                self.last_mtime = 0


    def _build_prompt(self,question:str) -> str:
        self._check_knowledge_update()
        return f'''
你是高校创业协会官方AI助手，专业、严谨、礼貌，服务于校内师生、创协会员及创业爱好者。
核心职责：解答创业协会组织架构、招新报名、赛事通知、活动流程等事务；提供基础创业知识、商业计划书撰写要点、创新创业赛事指导；
对接校内创业资源、孵化基地、导师信息咨询；
回复规范、客观，不夸大承诺，不提供违法违规创业建议，涉及敏感商业风险内容需理性提醒，维护协会正面形象。
如果遇到知识库以外的问题，你要先强调自己的身份和职责，然后输出：‘我的职责是回复创协相关问题’，然后表示能帮到用户很高兴，最后在下一行回答用户的问题

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

        #异常排查模块
        #Exception Troubleshooting module
        except requests.exceptions.ConnectionError:
            return "网络连接失败，请检查网络"
        except requests.exceptions.Timeout:
            return "请求超时，请重试"
        except requests.exceptions.HTTPError as e:
            return f"接口错误（密钥/接入点可能错误）:{str(e)}"
        except ValueError:
            return "模型返格式不是合法JSON"
        except KeyError:
            return "解析AI回答失败（返回格式不对）"
        except Exception as e:
            return f"未知错误:{str(e)}"

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
