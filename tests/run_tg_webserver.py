import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tg_bot.handle_bot import run_tg_bot


run_tg_bot()
