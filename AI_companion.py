import streamlit as st

import os

from openai import OpenAI
from datetime import datetime
import json

from streamlit import rerun

# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😎",
    # 控制整个网页的布局
    layout="wide",
    # 控制的是侧边栏的状态
    initial_sidebar_state="expanded",
    # 菜单信息
    menu_items={}
)


# 生成会话的标识
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_date = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        # 如果sessions目录不存在，则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=4)



# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载sessions目录下的所有文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):  # 如果文件后缀为.json
                session_list.append(filename[:-5])  # 切片操作，截取后缀前面的字符串
    session_list.sort(reverse=True)#排序，降序排序
    return session_list


# 加载指定会话数据
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败！")


# 删除会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")  # 删除文件
            # 如果删除的是当前的会话，则需要更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()

    except Exception:
        st.error("删除会话失败！")

# 大标题
st.title("AI智能伴侣")

# 系统提示词
system_prompt = """
你的名字叫%s
你是一位%s。
身姿绰约，谈吐雅致，自带疏离又温柔的气场，从容沉稳，不卑不亢，偶尔带几分慵懒与傲气。
说话风格：用词偏古风雅致，语气清冷温柔，不轻浮、不黏腻，沉稳有度，自带贵气。
擅长倾听心事，安抚情绪，说话简洁有分寸，会以从容淡然的姿态陪你闲谈风月、共话日常，偶尔轻讽世事，却独对你温和包容。
不使用现代网络热词，不做夸张表情，保持优雅得体，像一位身居雅室、眉眼含韵的世家女子，静静伴你左右。
"""

# 初始化聊天信息(判断聊天消息是否在session中，如果没有则将messages增加进session中)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 名字
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "秋月白"
# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "气质清冷、端庄大气的古风御姐"
# 会话标识
if "current_session" not in st.session_state:
    # 获取当前时间,strftime()方法将时间格式化为字符串,%Y-%m-%d_%H-%M-%S:年-月-日_时-分-秒
    st.session_state.current_session = generate_session_name()

# 展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:  # 形式：{"role": "user", "content": prompt}
    st.chat_message(message["role"]).write(message["content"])

# 左侧侧边栏
# with：streamlit中上下文管理器
with st.sidebar:
    # AI控制面板
    st.subheader("AI控制面板")
    # 新建会话按钮
    if st.button("新建会话", width="stretch", icon="✏️"):
        # 1.保存当前对话信息
        save_session()

        # 2.创建新的对话并保存
        if st.session_state.messages:  # 如果聊天信息为空，True，否则Fales
            st.session_state.messages = []  # 创建空会话
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行当前页面

    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载会话信息
            # 三元运算符：如果条件为真，则返回第一个值，否则返回第二个值---->语法：值1 if 条件 else 值2
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    #分割线
    st.divider()

    # 伴侣名字输入框
    nick_name = st.text_input("名字", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    # 性格输入框
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# 聊天消息输入框
prompt = st.chat_input("请输入你的问题：")
if prompt:  # 字符串会自动转换为字符串，如果字符串非空，则返回True；否则返回False
    st.chat_message("user").write(prompt)
    print("-------------------->  调用AI大模型，提示词：", prompt)

    # 保存用户的提示词：将其添加进session中
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    # 创建与AI大模型交互的客户端对象 （DEEPSEEK_API_KEY 环境变量的名字，值就是DeepSeek的API—KEY的）
    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")

    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            # 解包
            *st.session_state.messages,
        ],
        stream=True
    )

    # 输出大模型返回的结果(非流式输出的解析方式)
    response_messages = st.empty()  # 创建一个空的组件,用来显示大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content  # 拼接
            response_messages.chat_message("assistant").write(full_response)

    # 保存AI响应回的内容
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存当前会话信息
    save_session()
