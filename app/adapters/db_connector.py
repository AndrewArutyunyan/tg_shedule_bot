import psycopg2
from configparser import ConfigParser
import logging


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
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config


def execute_query(config, query):
    """ Run query on the PostgreSQL database server, return result """
    result = None
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            logging.info('Connected to the PostgreSQL server.')
            cursor_obj = conn.cursor()
            cursor_obj.execute(query)
            result = cursor_obj.fetchall()
            logging.info("Result: ", "\n", result)

    except (psycopg2.DatabaseError, Exception) as error:
        logging.exception("Error in postgres SQL: ")

    return result
