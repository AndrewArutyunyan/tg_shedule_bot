import os
import sys
import unittest
import logging
import subprocess
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tg_bot.handle_bot import WEB_SERVER_HOST, WEB_SERVER_PORT


class TestTelegramBot(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def test_webserver(self):
        """
        Start Telegram webserver, test connection.
        Run sample request.
        """
        tg_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_tg_webserver.py')
        # Here we start the server
        p = subprocess.Popen([sys.executable, tg_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        sleep(5)
        try:
            # output, errors = p.communicate()
            # self.logger.warning(errors)
            # If the process was terminated - test failed
            is_server_running = p.poll()
            # Execute sample querry to the server
            result = subprocess.run(["curl", "--tlsv1.2", "-v", "-k", f"https://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}/"], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        finally:
            # Kill server
            p.kill()
            sleep(1)
        self.assertIsNone(is_server_running)
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()