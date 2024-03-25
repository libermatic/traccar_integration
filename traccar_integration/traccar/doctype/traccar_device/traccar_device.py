# Copyright (c) 2024, Libermatic and contributors
# For license information, please see license.txt

import frappe
from typing import List
from frappe.model.document import Document
from traccar_integration.traccar.traccar_document import TraccarDocument
import datetime


class TraccarDevice(TraccarDocument):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        attributes: DF.JSON | None
        category: DF.Data | None
        contact: DF.Data | None
        device_name: DF.Data
        disabled: DF.Check
        expiration_time: DF.Datetime | None
        group_id: DF.Data | None
        last_update: DF.Datetime | None
        model: DF.Data | None
        phone: DF.Link
        position_id: DF.Data | None
        status: DF.Data | None
        unique_id: DF.Link
    # end: auto-generated types

    def db_insert(self, *args, **kwargs):
        creation = datetime.datetime.now(datetime.UTC).isoformat()
        attributes = self._get_attributes()
        payload = {
            **self.as_record(),
            "attributes": {**attributes, "creation": creation, "modified": creation},
        }
        data = TraccarDevice.request("POST", "/api/devices", payload=payload)
        self.name = data.get("id")
        self.clear_keys("/api/devices")
        self.reload()

    def load_from_db(self):
        data = TraccarDevice.request("GET", f"/api/devices/{self.name}")
        if data:
            super(Document, self).__init__(TraccarDevice.make_dict(data))
        else:
            raise frappe.exceptions.NotFound

    def db_update(self):
        data = TraccarDevice.request(
            "PUT", f"/api/devices/{self.name}", payload=self.as_record(with_id=True)
        )
        self.name = data.get("id")
        self.clear_keys(f"/api/devices/{self.name}")
        self.reload()

    def delete(self, *args, **kwargs):
        TraccarDevice.request("DELETE", f"/api/devices/{self.name}")
        self.clear_keys("/api/devices")

    @staticmethod
    def get_list(args) -> List[list] | List[dict]:
        data = TraccarDevice.request("GET", "/api/devices", params={"all": True})
        docs = [TraccarDevice.make_dict(x) for x in data]
        return TraccarDevice.transform_list(docs, args=frappe._dict(args))

    @staticmethod
    def get_count(args) -> int:
        data = TraccarDevice.request("GET", "/api/devices")
        return len(data)

    @staticmethod
    def get_stats(args):
        pass

    @classmethod
    def make_dict(cls, record: dict) -> dict:
        d = super().make_dict(record)
        d.update({"device_name": record.get("name")})
        return d

    def as_record(self, with_id=False):
        d = super().as_record(with_id=with_id)
        d.update({"name": d.pop("deviceName")})
        return d
