
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
import sys
from linebot import LineBotApi
from linebot.models import *
from NYCU_hackathon.config import *
if CHANNEL_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_TOKEN)

# Example: https://github.com/line/line-bot-sdk-python#create_rich_menuself-rich_menu-timeoutnone
# Document: https://developers.line.biz/en/reference/messaging-api/#create-rich-menu

rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1560),
    selected=False,
    name="Nice richmenu",
    chat_bar_text="Tap here",
    areas=[
        # covid-19
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=1250, height=780),
        action=MessageAction(label="初步診斷", text="初步診斷")),
        # knowledge
        RichMenuArea(
        bounds=RichMenuBounds(x=1251, y=0, width=1250, height=780),
        action=MessageAction(label="查詢附近的醫院", text="查詢附近的醫院")),
        # diagnosis
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=781, width=1250, height=780),
        action=MessageAction(label="查詢附近的採檢站", text="查詢附近的採檢站")),
        # hospital
        RichMenuArea(
        bounds=RichMenuBounds(x=1251, y=781, width=1250, height=780),
        action=MessageAction(label="醫療小知識", text="醫療小知識"))
        ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
print(rich_menu_id)


