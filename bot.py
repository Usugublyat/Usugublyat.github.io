#!/usr/bin/env python3
import json
import logging
import os
from dotenv import load_dotenv
from typing import Optional, Tuple

from telegram import Chat, ChatMember, ChatMemberUpdated, MenuButtonWebApp, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, ChatMemberHandler, filters
from telegram import User, KeyboardButton, ReplyKeyboardRemove, Update, WebAppInfo
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MenuButtonDefault
)
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from utils import validate as validate_web_app_data


load_dotenv()
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", None)
BOT_CHANNEL_ID = -1002105255563

WEB_APP_URL = 'https://strongly-powerful-muskox.ngrok-free.app/tg-webapp/'
WEB_APP_URL = 'https://durger-king-tg-bot-v2.onrender.com/tg-webapp/'
# WEB_APP_URL = 'https://blowfish-model-cricket.ngrok-free.app/tg-webapp/'


PRODUCT_ITEMS = {
    1: {'title': 'Burger', 'price': 459},
    2: {'title': 'Fries', 'price': 137},
    3: {'title': 'Hotdog', 'price': 321},
    4: {'title': 'Tako', 'price': 367},
    5: {'title': 'Pizza', 'price': 735},
    6: {'title': 'Donut', 'price': 137},
    7: {'title': 'Popcorn', 'price': 183},
    8: {'title': 'Coke', 'price': 137},
    9: {'title': 'Cake', 'price': 1011},
    10: {'title': 'Icecream', 'price': 551},
    11: {'title': 'Cookie', 'price': 367},
    12: {'title': 'Flan', 'price': 735}
}



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("httpx").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            logger.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif not was_member and is_member:
        logger.info("%s added the bot to the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
    elif was_member and not is_member:
        logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)


# Define a `/start` command handler.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    web_app = WebAppInfo(url=WEB_APP_URL)

    keyboard = [[InlineKeyboardButton("Меню", web_app=web_app)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp('Меню', web_app)
    )
    # await context.bot.set_chat_menu_button(
    #     chat_id=update.effective_chat.id,
    #     menu_button=MenuButtonDefault()
    # )
    await update.message.reply_text(
        """Начнем 🍟

Нажмите меню, чтобы заказать идеальный обед!""",
        reply_markup=None,
        # ReplyKeyboardMarkup.from_button(
        #     KeyboardButton(
        #         text="Меню 444",
        #         web_app=web_app,
        #     )
        # ),
    )
    return

    await update.message.reply_text(
        """Начнем 🍟

Нажмите меню, чтобы заказать идеальный обед!""",
        # reply_markup=InlineKeyboardMarkup.from_button(
        #     MenuButtonWebApp('Заказать еду', web_app)
        # )
        # reply_markup=reply_markup
        reply_markup=ReplyKeyboardMarkup.from_button(
            MenuButtonWebApp('Меню', web_app)
        ),
    )

    # await context.bot.set_chat_menu_button(
    #     chat_id=update.effective_chat.id,
    #     menu_button=MenuButtonWebApp('Заказать еду', web_app)
    # )

    return
    
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            MenuButtonWebApp('Меню 3', web_app)
        ),
    )
    """

    """
    return
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp('Меню 3', web_app)
    )

# Define a `/start` command handler.
async def start_v0(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open the color picker!",
                web_app=WebAppInfo(url="https://strongly-powerful-muskox.ngrok-free.app/tg-webapp"),
            )
        ),
    )

# Handle incoming WebAppData
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button.
    Only InlineKeyboardMarkup/InlineKeyboardButton supports callback_data.
    """
    data = json.loads(update.effective_message.web_app_data.data)
    print('web_app_data', data)

    """
    {
        'order_data': [{'id': 3, 'count': 1}],
        'comment': 'dsadsad',
        'initData': 'query_id=AAF_bC1tAgAAAH9sLW0buZ3F&user=%7B%22id%22%3A6126660735%2C%22first_name%22%3A%22Alexey%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22alkorobkov%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1699109051&hash=380c3901e03578417ed0c4628c74f20a03b206ce4ddad017bb4233eefa6ced25',
        'method': 'makeOrder'
    }
    """
    if data['method'] == 'makeOrder':
        # {'order_data': [{'id': 2, 'count': 1}]
        hash_str = data['initDataUnsafeHash']

        if not validate_web_app_data(hash_str, data['initData'], bot_token):
            raise Exception('Bad data: %r' % data)
        
        order_data = data['order_data']

        if BOT_CHANNEL_ID:
            cause_name = update.message.from_user.mention_markdown()
            cart = make_shop_cart(order_data)

            msg = 'Новый заказ от %s\n%s\nСумма: %d ₽' % (cause_name, cart, cart.total_sum())
            if data['comment']:
                msg += '\nКомментарий: %s' % data['comment']

            await app.bot.send_message(
                BOT_CHANNEL_ID,
                msg,
                parse_mode=ParseMode.MARKDOWN,
            )

    await update.message.reply_html(
        text=(
            f'Ваш заказ принят и ожидает обработки'
        ),
        reply_markup=ReplyKeyboardRemove()
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_ids = ", ".join(str(cid) for cid in context.bot_data.setdefault("channel_ids", set()))
    print('reply to /hello:', channel_ids)
    # await context.bot.send_message(
    #     chat_id=BOT_CHANNEL_ID, text='Hello', parse_mode=ParseMode.HTML
    # )
    print(update.message.from_user.mention_markdown()) # [Alexey](tg://user?id=6126660735)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


class ShopCart(object):

    def __init__(self) -> None:
        self._items = dict()

    def add_item(self, item_id, items_count):
        items_count = int(items_count)
        assert items_count
        self._items[int(item_id)] = items_count

    def total_sum(self):
        return sum(
            [v['price'] * self._items[item_id] for item_id,v in PRODUCT_ITEMS.items() if item_id in self._items]
        )

    def __str__(self):
        return 'Заказ:\n%s' % (
            '\n'.join([
                '• %s %dx – %s ₽' % (
                    PRODUCT_ITEMS[item_id]['title'], self._items[item_id], PRODUCT_ITEMS[item_id]['price']*self._items[item_id]
                ) for item_id, item in self._items.items()
            ])
        )


def make_shop_cart(order_data):
    # {'order_data': [{'id': 2, 'count': 1}]
    cart = ShopCart()
    [cart.add_item(item['id'], item['count']) for item in order_data]

    return cart


if bot_token:
    app = Application.builder().token(bot_token).build()

    app.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
else:
    app = None

if __name__ == '__main__':
    cart = make_shop_cart([
        {'id': 2, 'count': 1},
        {'id': 5, 'count': 3},
        {'id': 8, 'count': 2}
    ])
    print(
        cart,
        'Сумма: %d ₽' % cart.total_sum()
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    # asyncio.run(main())
