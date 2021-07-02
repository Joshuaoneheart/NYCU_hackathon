# -*- coding: utf-8 -*-
import os
from config import *
if os.getenv("DEV") is not None:
    from dotenv import load_dotenv
    
    load_dotenv(dotenv_path='./.env')

import sys
import json

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
)

app = Flask(__name__)

# getting channel secret
#  This would be the preferred approach but it just doesn't work
#  CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
#  CHANNEL_TOKEN = os.getenv('LINE_CHANNEL_TOKEN')

if CHANNEL_SECRET is None:
    print("LINE_CHANNEL_SECRET may be undefined.")
    sys.exit(1)
if CHANNEL_TOKEN is None:
    print("LINE_CHANNEL_TOKEN may be undefined")
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

STATE = "init"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if message == 'flex':
        test_flex = json.load(open("./flex/hospital.json", "r"))
        ret_message = FlexSendMessage(alt_text='hospital', contents=test_flex)
    elif message == "初步診斷" and STATE == "init":
        msg = "請簡述您的症狀"
        STATE = "diagnosis"
        ret_message = TextSendMessage(text=msg)
    elif STATE == "diagnosis":
        msg = "初步分析結果：\n您應該確診了！！！\n\n建議掛科：\n胸腔內科\n\n可能病因：\nCOVID-19"
        STATE = "init"
        ret_message = TextSendMessage(text=msg)
    elif message == "debug":
        ret_message = TextSendMessage(text=STATE)
    else:
        ret_message = TextSendMessage(text="Please leave me alone")
    
    line_bot_api.reply_message(
        event.reply_token,
        ret_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
