import sys
import asyncio
from app.tg_bot.handle_bot import send_message

if __name__ == '__main__':

    args = sys.argv[1:]
    chat_dest = int(args[0])
    chat_msg = args[1]

    asyncio.run(send_message(chat_dest, chat_msg))
