#!/usr/bin/env python3
from typing import Union
import os
import json
from urllib.parse import parse_qs
import asyncio
import uvicorn

from fastapi import FastAPI, Request
from fastapi.logger import logger
from fastapi_utils.tasks import repeat_every
from fastapi.staticfiles import StaticFiles
from bot import app as bot_app, Update, bot_token, make_shop_cart, ParseMode
from utils import validate as validate_web_app_data

app = FastAPI()
app.mount("/tg-webapp", StaticFiles(directory="tg-webapp", html=True), name="tg-webapp-static")

BOT_CHANNEL_ID = -1002105255563


@app.get("/")
@app.head("/")
def read_root():
    return {"Hello": "World"}



@app.post("/cafe/api")
async def cafe_api(request: Request):
    data = await request.json()
    print(data)
    """
    order_data: [{"id":2,"count":3},{"id":5,"count":1},{"id":6,"count":1}]
    comment: 323
    _auth: query_id=AAF_bC1tAgAAAH9sLW3u69tY&user=%7B%22id%22%3A6126660735%2C%22first_name%22%3A%22Alexey%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22alkorobkov%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1698940705&hash=948aadeee4f55c9a5861a67c3a94816e0bbdf27da1e64e94bc252fb39fa0a4c2
    method: makeOrder
    """
    
    user_data = json.loads(parse_qs(data['initData'])['user'][0])
    USER_ID = user_data['id']

    if data['method'] == 'makeOrder':
        # {'order_data': [{'id': 2, 'count': 1}]
        hash_str = data['initDataUnsafeHash']

        if not validate_web_app_data(hash_str, data['initData'], bot_token):
            raise Exception('Bad data: %r' % data)
        
        order_data = data['order_data']

        if BOT_CHANNEL_ID:
            # cause_name = update.message.from_user.mention_markdown()
            cause_name = '[%s](tg://user?id=%d)' % (user_data['first_name'], USER_ID)
            cart = make_shop_cart(order_data)

            msg = 'Новый заказ от %s\n%s\nСумма: %d ₽' % (cause_name, cart, cart.total_sum())
            if data['comment']:
                msg += '\nКомментарий: %s' % data['comment']

            await bot_app.bot.send_message(
                BOT_CHANNEL_ID,
                msg,
                parse_mode=ParseMode.MARKDOWN,
            )

    await bot_app.bot.send_message(
        USER_ID,
        'Ваш заказ принят и ожидает обработки',
        parse_mode=ParseMode.MARKDOWN,
    )

    return {'ok': 'ok'}


PORT = int(os.environ.get('PORT', '8000'))


import aiohttp

counter = 0

@app.on_event("startup")
@repeat_every(seconds=60, logger=logger, wait_first=True)
async def periodic():
    global counter
    counter += 1
    async with aiohttp.ClientSession() as session:
        async with session.get('https://durger-king-tg-bot-v2.onrender.com/?i=%d' % counter) as resp:
            # resp.status
            await resp.text()
            # print(resp)



async def main():
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            port=PORT,
            use_colors=False,
            host="0.0.0.0",
        )
    )

    if bot_app:
        async with bot_app:
            await bot_app.initialize()
            await bot_app.start()
            # await bot_app.run_polling(allowed_updates=Update.ALL_TYPES)
            await bot_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            await webserver.serve()
            if bot_app.updater:
                await bot_app.updater.stop()
            await bot_app.stop()
    else:
        await webserver.serve()


if __name__ == "__main__":
    asyncio.run(main())
# or uvicorn web:app --reload
