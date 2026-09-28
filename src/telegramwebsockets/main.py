import asyncio
import json
import os
import time

import websockets
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

last_sent_time = 0
load_dotenv()
dp = Dispatcher()
binance_url = (
    "wss://stream.binance.com:9443/stream?streams=btcusdt@aggTrade/ethusdt@aggTrade"
)
tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
tg_id = os.getenv("USER_ID")
bot = Bot(token=tg_token)
crypto = {}


@dp.message(CommandStart())
async def get_start(message: Message):
    user_id = message.from_user.id
    await message.answer(text=f"{user_id=}")


async def fetch_binance_trades(url: str):
    global last_sent_time
    async with websockets.connect(url) as ws:
        async for msg in ws:
            root_data = json.loads(msg)
            data = root_data["data"]
            price = float(data["p"])
            name = data["s"]
            crypto[name] = price
            if time.time() - last_sent_time > 5:
                sorted_crypto = dict(
                    sorted(crypto.items(), key=lambda item: item[1], reverse=True)
                )
                msg_lines = ["**Последние цены криптовалют:**"]
                for coin_name, coin_price in sorted_crypto.items():
                    msg_lines.append(f"• {coin_name}: ${coin_price:,.2f}")
                await send_message_to_tg(msg="\n".join(msg_lines))
                last_sent_time = time.time()


async def send_message_to_tg(msg: str):
    await bot.send_message(chat_id=tg_id, text=msg)


async def main():
    async with asyncio.TaskGroup() as task_group:
        (task_group.create_task(fetch_binance_trades(binance_url)),)
        task_group.create_task(dp.start_polling(bot, handle_signals=False))


if __name__ == "__main__":
    asyncio.run(main())
