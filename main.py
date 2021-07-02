# -*- coding: utf-8 -*-
import os
from config import *
if os.getenv("DEV") is not None:
    from dotenv import load_dotenv
    
    load_dotenv(dotenv_path='./.env')

import sys
import json
from hospital import *

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

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
    global STATE
    message = event.message.text
    if STATE == "init" and message == 'flex':
        test_flex = json.load(open("./flex/hospital.json", "r"))
        ret_message = FlexSendMessage(alt_text='hospital', contents=test_flex)
    elif message == "初步診斷" and STATE == "init":
        msg = "請簡述您的症狀"
        STATE = "diagnosis"
        ret_message = TextSendMessage(text=msg)
    elif STATE == "diagnosis":
        msg = "初步分析結果：\n心肌炎\n\n建議掛科：\n胸腔內科\n\n可能病因：\n壓力過大"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="初步診斷", text="初步診斷")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="查詢附近的採檢站/醫院")
                        )
                    ]))
        STATE = "init"
    elif STATE == "init" and message == "醫療小知識":
        STATE = "info_department"
        msg = "請問要詢問那一科呢？"
        ret_message = TextSendMessage(text=msg)
    elif STATE == "info_department":
        STATE = "info_disease"
        msg = "請問是什麼樣的疾病呢？"
        ret_message = TextSendMessage(text=msg)
    elif STATE == "info_disease":
        STATE = "init"
        msg = "提供以下資訊給您參考：\nhttps://www.cdc.gov.tw/En"

        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="初步診斷", text="初步診斷")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="查詢附近的採檢站/醫院")
                        )
                    ]))

    elif STATE == "init" and message == "查詢附近的採檢站":
        pcr_name = get_nearby_PCR((LATITUDE, LONGITUDE))
        msg = f"離您最近的採檢站為：\n{pcr_name}\n\n打開google map以查詢位置：\nhttps://www.google.com.tw/maps/search/{pcr_name}"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="初步診斷", text="初步診斷")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="查詢附近的採檢站/醫院")
                        )
                    ]))

    elif STATE == "init" and message == "查詢附近的醫院":
        msg = "離您最近的醫院為：\n台大醫院\n\n打開google map以查詢位置：\nhttps://www.google.com.tw/maps/search/%E8%87%BA%E5%A4%A7%E9%86%AB%E9%99%A2/@25.0424548,121.5071815,16z/data=!3m1!4b1?hl=zh-TW"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="初步診斷", text="初步診斷")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="查詢附近的採檢站/醫院")
                        )
                    ]))
    else:
        STATE = "init"
        ret_message = TextSendMessage(
                text='請點選以下您要查詢的資訊',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="初步診斷", text="初步診斷")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="查詢附近的採檢站/醫院")
                        )
                    ]))
    
    line_bot_api.reply_message(event.reply_token, ret_message)

LATITUDE = None
LONGITUDE = None
ADDRESS = None

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    global LATITUDE
    global LONGITUDE
    global ADDRESS

    LATITUDE = event.message.latitude
    LONGITUDE = event.message.longitude
    ADDRESS = event.message.address

    ret_message = TextSendMessage(
                text="您的位置為："+str(ADDRESS)+"\n\n您的緯度為：\n"+str(LATITUDE)+"\n\n您的經度為：\n"+str(LONGITUDE),
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="查詢附近的採檢站", text="查詢附近的採檢站")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="查詢附近的醫院", text="查詢附近的醫院")
                        )
                    ]))
    line_bot_api.reply_message(event.reply_token, ret_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
