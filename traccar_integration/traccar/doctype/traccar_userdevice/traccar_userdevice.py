# Copyright (c) 2024, Libermatic and contributors
# For license information, please see license.txt

import frappe
from typing import List
import pypika

from traccar_integration.traccar.database import MysqlDatabase
from traccar_integration.traccar.traccar_document import TraccarDocument


class TraccarUserDevice(TraccarDocument):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        device: DF.Link
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types

    def db_insert(self, *args, **kwargs):
        pass

    def load_from_db(self):
        pass

    def db_update(self):
        pass

    def delete(self, *args, **kwargs):
        pass

    @staticmethod
    def get_list(args) -> List[dict]:
        _args = frappe._dict(args)
        UserDevice = pypika.Table("tc_user_device")
        q = pypika.Query.from_(UserDevice).select(
            UserDevice.userId.as_("parent"),
            UserDevice.deviceId.as_("device"),
        )
        if _args.filters:
            for dt, fieldname, operator, value in _args.filters:
                if dt == "Traccar UserDevice":
                    if fieldname == "parent" and operator == "=":
                        q = q.where(UserDevice.userId == int(value))
                    elif fieldname == "device" and operator == "=":
                        q = q.where(UserDevice.deviceId == int(value))
        result = MysqlDatabase.run(q)
        return [frappe._dict(x) for x in result]

    @staticmethod
    def get_count(args):
        pass

    @staticmethod
    def get_stats(args):
        pass
