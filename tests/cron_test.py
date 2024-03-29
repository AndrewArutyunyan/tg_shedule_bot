import os
import sys
import unittest
import logging
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.cron import add_cron_job, list_cron_jobs, remove_cron_job


class TestXlsParser(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def test_add_list_and_remove_cron_job(self):
        """
        Add sample cron job.
        Test passed if telegram user have received a message.
        """
        cron_time = "* * * * *"
        chat_id = 468614030 # put your telegram chat_id
        notification_id  = 777
        add_cron_job(cron_time, chat_id, "test message", notification_id)
        sleep(60)  # Wait 1 min
        l = list_cron_jobs(notification_id=notification_id)
        print(l)
        remove_cron_job(notification_id)
        self.assertEqual(len(l), 1)

if __name__ == '__main__':
    unittest.main()