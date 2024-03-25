import pypika
import pymysql
from pymysql.cursors import DictCursor
import frappe


class TraccarDbNotSetup(Exception):
    pass


class MysqlDatabase:
    @classmethod
    def _connect(cls):
        config = frappe.get_site_config()
        args = {
            "host": config.get("traccar_db_host"),
            "database": config.get("traccar_db_name"),
            "user": config.get("traccar_db_user"),
            "password": config.get("traccar_db_password"),
            "cursorclass": DictCursor,
        }
        if not args.get("host"):
            raise TraccarDbNotSetup

        return pymysql.connect(**args)

    @classmethod
    def run(cls, query: pypika.Query, **kwargs):
        try:
            with cls._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query.get_sql(quote_char="`"))
                    result = cursor.fetchall()
                    if pluck := kwargs.get("pluck"):
                        return [x.get(pluck) for x in result]

                    return result
        except TraccarDbNotSetup:
            return []
