import psycopg2
from configparser import ConfigParser
import logging
import sys
import os

logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_config(filename, section='postgresql')->dict:
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        exc = Exception('Section {0} not found in the {1} file'.format(section, filename))
        logger.exception(exc)
        raise exc

    return config


def execute_query(query, config=None, writeonly=False):
    """ Run query on the PostgreSQL database server, return result """
    result = None
    conf_file = 'config/database.ini'
    if config is None:
        try:
            config = load_config(conf_file)
        except (Exception) as error:
            logger.exception("Error connecting to DB: ")
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            logger.debug('Connected to the PostgreSQL server.')
            cursor_obj = conn.cursor()
            cursor_obj.execute(query)
            if not writeonly:
                result = cursor_obj.fetchall()
            logger.debug(query)

    except (psycopg2.DatabaseError, Exception) as error:
        logger.exception("Error in postgres SQL: ")

    return result
