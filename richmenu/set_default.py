
import sys
from linebot import LineBotApi
from NYCU_hackathon.config import *

if CHANNEL_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_TOKEN)

# Example: https://github.com/line/line-bot-sdk-python#set_default_rich_menuself-rich_menu_id-timeoutnone
# Document: https://developers.line.biz/en/reference/messaging-api/#set-default-rich-menu
rich_menu_id = 'richmenu-4cf0175cb2fb38e008d79387d26eefbe'
line_bot_api.set_default_rich_menu(rich_menu_id)
