from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
import sys
from linebot import LineBotApi
from config import *

if CHANNEL_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_TOKEN)

# Example: https://github.com/line/line-bot-sdk-python#create_rich_menuself-rich_menu-timeoutnone
# Document: https://developers.line.biz/en/reference/messaging-api/#create-rich-menu

rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=1152, height=525),
    selected=False,
    name="Nice richmenu",
    chat_bar_text="Tap here",
    areas=[
    RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=575, height=524),
        action=URIAction(label='location', uri='https://dataportal.asia/dataset/203222207_covid-19-dcii/resource/c60dc5fd-a383-44e0-a357-e547355b1051')),
    RichMenuArea(
        bounds=RichMenuBounds(x=576, y=0, width=1151, height=524),
        action=URIAction(label='department', uri='https://data.zhupiter.com/oddt/11318383/%E8%87%BA%E5%8C%97%E5%B8%82%E5%85%AC%E7%A7%81%E7%AB%8B%E9%86%AB%E9%99%A2%E8%A8%BA%E7%99%82%E7%A7%91%E5%88%A5/'))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open('./default.png', 'rb') as f:
    line_bot_api.set_rich_menu_image('rich_menu_id', "image/png", f)
line_bot_api.set_default_rich_menu(rich_menu_id)