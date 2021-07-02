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
LAST_STATE = "init"
DISEASE = None

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global STATE
    global DISEASE
    print(event)
    message = event.message.text
    
    if message == "初步診斷" and STATE == "init":
        msg = "請簡述您的症狀"
        STATE = "diagnosis"
        ret_message = TextSendMessage(text=msg)

    elif STATE == "diagnosis" and (("胸悶" and "疲累") in message):
        STATE = "diagnosis_complete"
        DISEASE = "heart"
        msg =  "初步分析結果：\n"
        msg += "心臟、肺臟、其他\n\n"
        msg += "建議掛科：\n"
        msg += "心臟科、胸腔科\n\n"
        msg += "可能病因：\n"
        msg += "感染\n\n"
        msg += "建議：\n"
        msg += "若為心臟方面疾病，需盡快就醫檢查"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="相關疾病查詢", text="相關疾病查詢")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="醫療小知識", text="醫療小知識")
                        )
                    ]))
    elif STATE == "diagnosis" and ((("呼吸" and "困難") or "嘨喘") in message):
        STATE = "init"
        DISEASE = None
        msg =  "初步分析結果：\n"
        msg += "氣管阻塞、氣喘、慢性阻塞性肺病(COPD)、肺栓塞\n"
        msg += "近期covid19疫情嚴重，若仍有發燒、咳嗽等症狀同時出現，可能為新冠肺炎之感染!\n\n"
        msg += "建議掛科：\n"
        msg += "胸腔科、感染科\n"
        msg += "COVID-19患者請前往急診篩檢\n\n"
        msg += "可能病因：\n"
        msg += "肺部感染、心衰竭"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=URIAction(label='Covid19篩檢站', uri='https://antiflu.cdc.gov.tw/ExaminationCounter')
                        )
                    ]))
        
    elif STATE == "diagnosis_complete" and DISEASE == "heart" and message == "相關疾病查詢":
        msg =  "1. 心肌炎\n"
        msg += "2. 心絞痛(反覆胸痛)\n"
        msg += "3. 急性心肌梗塞(重壓、極度疼痛)\n"
        msg += "4. 氣胸\n"
        msg += "5. 消化潰瘍\n"
        msg += "～～請點選您想要查詢的疾病～～"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="心肌炎", text="心肌炎")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="心絞痛", text="心絞痛")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="急性心肌梗塞", text="急性心肌梗塞")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="氣胸", text="氣胸")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="消化潰瘍", text="消化潰瘍")
                        )
                    ]))
        STATE = "init"
        LAST_STATE = "init"
        DISEASE = None
    elif message == "心肌炎":
        STATE = "init"
        LAST_STATE = "init"
        DISEASE = None
        msg =  "心肌炎介紹\n"
        msg += "注意! Covid19可能增加心臟疾病風險，若原本有心臟疾病的患者可能因感染covid19 加重症狀，須密切注意。\n\n"
        msg += "心肌炎的臨床表現多種多樣，從亞臨床疾病到疲勞、胸痛、心力衰竭（HF）、心源性休克、心律失常和猝死。 由於症狀與其他疾病相似，並缺乏安全且靈敏度高的非侵入性檢查，因此可能被忽視，延誤治療。"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=URIAction(label='Covid19相關資訊', uri='https://www.cdc.gov.tw/En')
                        )
                    ]))
    elif STATE == "diagnosis_complete" and DISEASE == "heart" and message == "醫療小知識":
        STATE = "init"
        DISEASE = None
        msg = "提供以下資訊給您參考：\nhttps://www.cdc.gov.tw/En"

        ret_message = TextSendMessage(text=msg,)
    
    elif STATE == "init" and DISEASE == None and message == "醫療小知識":
        STATE = "info_disease"
        msg = "請問是什麼樣的疾病呢？"
        ret_message = TextSendMessage(text=msg)
    
    elif STATE == "info_disease":
        STATE = "init"
        msg = "提供以下資訊給您參考：\nhttps://www.cdc.gov.tw/En"

        ret_message = TextSendMessage(text=msg,)

    elif STATE == "init" and message == "查詢附近的採檢站":
        STATE = "Station"
        msg = "點選下方按鈕輸入您的位置"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=LocationAction(label="點選這裡輸入您的位置")
                        )
                    ]))

    elif STATE == "init" and message == "查詢附近的醫院":
        STATE = "Hospital"
        msg = "點選下方按鈕輸入您的位置"
        ret_message = TextSendMessage(
                text=msg,
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=LocationAction(label="點選這裡輸入您的位置")
                        )
                    ]))

    else:
        STATE = "init"
        LAST_STATE = "init"
        ret_message = TextSendMessage(text='請點選以下您要查詢的資訊',)
    
    line_bot_api.reply_message(event.reply_token, ret_message)

LATITUDE = None
LONGITUDE = None
ADDRESS = None

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    global LATITUDE
    global LONGITUDE
    global ADDRESS
    global STATE

    LATITUDE = event.message.latitude
    LONGITUDE = event.message.longitude
    ADDRESS = event.message.address
    #msg = "您的位置為："+str(ADDRESS)+"\n\n您的緯度為：\n"+str(LATITUDE)+"\n\n您的經度為：\n"+str(LONGITUDE)

    
    if STATE == "Station":
        msg = "離您最近的採檢站為：\n台大醫院\n\n打開google map以查詢位置：\nhttps://www.google.com.tw/maps/search/%E8%87%BA%E5%A4%A7%E9%86%AB%E9%99%A2/@25.0424548,121.5071815,16z/data=!3m1!4b1?hl=zh-TW"


    elif STATE == "Hospital":
        msg = "離您最近的醫院為：\n台大醫院\n\n打開google map以查詢位置：\nhttps://www.google.com.tw/maps/search/%E8%87%BA%E5%A4%A7%E9%86%AB%E9%99%A2/@25.0424548,121.5071815,16z/data=!3m1!4b1?hl=zh-TW"
    else:
        pass
    STATE = "init"
    ret_message = TextSendMessage(text=msg)
    line_bot_api.reply_message(event.reply_token, ret_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
