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


STATE = {}
DEPARTMENT = {}
# state: 0(init), 1(diagnosis), 2(hospital), 3(covid-19), 4(knowledge), 5(knowledge_disease)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global STATE
    user = event.source.user_id
    if user not in STATE:
        STATE[user] = 0
    message = event.message.text
    if message == "初步診斷" and STATE[user] == 0:
        msg = "請簡述您的症狀"
        STATE[user] = 1
        ret_message = TextSendMessage(text=msg)

    elif STATE[user] == 1 and (("胸悶" and "疲累") in message):
        msg =  '''初步分析結果：\n
        心臟、肺臟、其他\n\n
        建議掛科：\n
        心臟科、胸腔科\n\n
        可能病因：\n
        感染\n\n
        建議：\n
        若為心臟方面疾病，需盡快就醫檢查
        初步分析結果：\n心肌炎\n\n建議掛科：\n胸腔內科\n\n可能病因：\n壓力過大'''
        STATE[user] = 0
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="相關疾病查詢", text="相關疾病查詢")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="查詢附近的內科醫院", text="查詢附近的內科醫院")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="其他服務", text="其他服務")
                        )
                    ]))
    elif STATE[user] == 1 and ((("呼吸" and "困難") or "嘨喘") in message):
        STATE[user] = 0
        msg =  '''初步分析結果：\n
                  氣管阻塞、氣喘、慢性阻塞性肺病(COPD)、肺栓塞\n"
                  近期covid19疫情嚴重，若仍有發燒、咳嗽等症狀同時出現，可能為新冠肺炎之感染!\n\n"
                  建議掛科：\n
                  胸腔科、感染科\n
                  COVID-19患者請前往急診篩檢\n\n
                  可能病因：\n
                  肺部感染、心衰竭'''
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=URIAction(label='Covid19篩檢站', uri='https://antiflu.cdc.gov.tw/ExaminationCounter')
                        )
                    ]))
    elif STATE[user] == 0 and message == "醫療小知識":
        STATE[user] = 4
        msg = "請問要詢問那一科呢？"
        qr = [QuickReplyButton(action=MessageAction(label=department, text=department)) for department in DEPARTMENTS]
        ret_message = TextSendMessage(
            text=msg,
            quick_reply=QuickReply(items=qr)
        )
    elif STATE[user] == 4:
        STATE[user] = 5
        msg = f"請問想了解{message}的什麼疾病呢？"
        ret_message = TextSendMessage(text=msg)
    elif STATE[user] == 6:
        STATE[user] = 0
        msg = "提供以下資訊給您參考：\nhttps://www.cdc.gov.tw/En"

        ret_message = TextSendMessage(text=msg)

    elif STATE[user] == 0 and message == "查詢附近的採檢站":
        STATE[user] = 3
        msg = "請提供您的位置"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(     
                            action=LocationAction(label="查詢附近的採檢站")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="其他服務", text="其他服務")
                        )
                    ]))

    elif STATE[user] == 0 and message == "查詢附近的醫院":
        STATE[user] = 2
        qr = [QuickReplyButton(action=MessageAction(label=department, text=department)) for department in DEPARTMENTS]
        
        ret_message = TextSendMessage(
                text="要看哪一科呢?",
                quick_reply=QuickReply(items=qr))
    elif STATE[user] == 2:
        msg = "請提供您的位置"
        DEPARTMENT[user] = message
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(     
                            action=LocationAction(label="查詢附近的醫院")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="其他服務", text="其他服務")
                        )
                    ]))
    else:
        STATE[user] = 0
        ret_message = TextSendMessage(text='你好！！我是 Kompanion，您的智慧醫療小助手！請問我能夠幫您什麼呢？')

    
    line_bot_api.reply_message(event.reply_token, ret_message)

LATITUDE = None
LONGITUDE = None
ADDRESS = None

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):

    global STATE
    global DEPARTMENT
    user = event.source.user_id
    LATITUDE = event.message.latitude
    LONGITUDE = event.message.longitude
    if STATE[user] == 3:
        pcr_name = get_nearby_PCR((LATITUDE, LONGITUDE))
        msg = f"離您最近的採檢站為：\n{pcr_name}\n\n打開google map以查詢位置：\nhttps://www.google.com.tw/maps/search/{pcr_name}"
        ret_message = TextSendMessage(text=msg)
    elif STATE[user] == 2:
        # get_hospital_by_department DEPARTMENT[user]
        test_flex = json.load(open("./flex/hospital.json", "r"))
        ret_message = FlexSendMessage(alt_text='hospital', contents=test_flex)
    STATE[user] = 0
    line_bot_api.reply_message(event.reply_token, ret_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
