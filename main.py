import os

if os.getenv("DEV") is not None:
    from dotenv import load_dotenv
    
    load_dotenv(dotenv_path='./.env')

import sys

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, flex_message, 
)

import sys

app = Flask(__name__)

# getting channel secret
CHANNEL_SECRET='fc8cc9fe10d8ff1fab2b2eee096fe07a'
CHANNEL_TOKEN='1uyGxBSEz3dN3GACCh7X2RJR+96zxZyb/NYnFrw0DfsWy72ZxbRpqAiLRMLbtXOetskvNi4xQVfqOxWeBnopb5crdJ3SgXGAwncOBMvlsKasnLI+lpsejB9l86k34B28RZMV1dXQAo/gbY2thp1HGQdB04t89/1O/w1cDnyilFU='
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if message == 'flex':
        import json
        with open("./flex.json") as json_file:
            test_flex = json.load(json_file)
            ret_message = FlexSendMessage(contents=test_flex)
    else:
        ret_message = TextSendMessage(text="Please leave me alone")
    
    line_bot_api.reply_message(
        event.reply_token,
        ret_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
