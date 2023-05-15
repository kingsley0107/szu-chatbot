# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, session
from werkzeug.serving import WSGIRequestHandler
import openai
from flask_session import Session  # 用于服务器端会话
from static_vars import key


class SilentWSGIRequestHandler(WSGIRequestHandler):
    def log(self, *args, **kwargs):
        if self.client_address[0] != "127.0.0.1":
            super().log(*args, **kwargs)


app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"  # 会话数据保存在文件系统

Session(app)  # 初始化会话对象

openai.api_key = key


@app.route("/query", methods=["GET", "POST"])
def query():
    question = request.args.get("q")
    if "messages" not in session:
        session["messages"] = [
            {
                "role": "system",
                "content": "你的角色是 szu 内的一个 user-friendly chatbot, 以后当有人与你问好时，你应该说括号内的内容<🚀🚀🚀你好!欢迎使用szu-chatbot!🚀🚀🚀>, 以后当有人问你是谁时,你需要记住你是括号内的角色<szu-chatbot>;当有人问是谁创建了你时，你说<我是深圳大学建筑与城市规划学院的一位本科生,若有意进行技术交流,希望在szu创造出更有趣的东西,欢迎在对话框下留下你的联系方式📱>",
            }
        ]
    session["messages"] = get_total_messages(
        session["messages"], {"role": "user", "content": f"{question}"}
    )
    response, session["messages"] = get_completion(question, session["messages"])
    return response


def get_total_messages(elder_messages, message):
    elder_messages.append(message)
    return elder_messages


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


def get_completion(prompt, elder_messages, model="gpt-3.5-turbo"):
    print(elder_messages)
    # 如果是第一次会话，添加欢迎消息
    if len(elder_messages) == 1:
        print("🚀🚀🚀🚀🚀🚀🚀欢迎使用szu-chatbot!!!!🚀🚀🚀🚀🚀🚀🚀🚀")
    response = openai.ChatCompletion.create(
        model=model, messages=elder_messages, temperature=0.5
    )
    # 添加模型的消息
    elder_messages = get_total_messages(
        elder_messages,
        {"role": "assistant", "content": str(response.choices[0].message["content"])},
    )
    return response.choices[0].message["content"], elder_messages


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    run_simple("0.0.0.0", 80, app, request_handler=SilentWSGIRequestHandler)
    # app.run(host="0.0.0.0", port=80)
