# Copyright (c) 2024, Libermatic and contributors
# For license information, please see license.txt

import frappe
from typing import Any, List
from frappe.model.document import Document
from traccar_integration.traccar.doctype.traccar_userdevice.traccar_userdevice import (
    TraccarUserDevice,
)
from traccar_integration.traccar.traccar_document import TraccarDocument
import datetime


class TraccarUser(TraccarDocument):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from traccar_integration.traccar.doctype.traccar_userdevice.traccar_userdevice import (
            TraccarUserDevice,
        )

        administrator: DF.Check
        attributes: DF.JSON | None
        coordinate_format: DF.Data | None
        device_limit: DF.Int
        device_readonly: DF.Check
        devices: DF.TableMultiSelect[TraccarUserDevice]
        disabled: DF.Check
        email: DF.Data
        expiration_time: DF.Datetime | None
        fixed_email: DF.Check
        latitude: DF.Float
        limit_commands: DF.Check
        longitude: DF.Float
        map: DF.Data | None
        phone: DF.Data | None
        poi_layer: DF.Data | None
        readonly: DF.Check
        twelve_hour_format: DF.Check
        user_limit: DF.Int
        user_name: DF.Data
        zoom: DF.Int
    # end: auto-generated types

    def db_insert(self, *args, **kwargs):
        creation = datetime.datetime.now(datetime.UTC).isoformat()
        attributes = self._get_attributes()
        payload = {
            **self.as_record(),
            "attributes": {**attributes, "creation": creation, "modified": creation},
        }
        data = TraccarUser.request("POST", "/api/users", payload=payload)
        self.name = data.get("id")
        self.clear_keys("/api/users")
        self.reload()

    def load_from_db(self):
        data = TraccarUser.request("GET", f"/api/users/{self.name}")
        if data:
            devices = TraccarUserDevice.get_list(
                {"filters": [["Traccar UserDevice", "parent", "=", self.name]]}
            )
            doc = TraccarUser.make_dict({**data, "devices": devices})
            super(Document, self).__init__(doc)
        else:
            raise frappe.exceptions.NotFound

    def db_update(self):
        data = TraccarUser.request(
            "PUT", f"/api/users/{self.name}", payload=self.as_record(with_id=True)
        )
        self.name = data.get("id")
        self.clear_keys(f"/api/users/{self.name}")
        self.reload()

    def delete(self, *args, **kwargs):
        TraccarUser.request("DELETE", f"/api/users/{self.name}")
        self.clear_keys("/api/users")

    @staticmethod
    def get_list(args) -> List[list] | List[dict]:
        data = TraccarUser.request("GET", "/api/users")
        docs = [TraccarUser.make_dict(x) for x in data]
        return TraccarUser.transform_list(docs, args=frappe._dict(args))

    @staticmethod
    def get_count(args) -> int:
        data = TraccarUser.request("GET", "/api/users")
        return len(data)

    @staticmethod
    def get_stats(args):
        pass

    @classmethod
    def make_dict(cls, record: dict[str, Any]) -> dict:
        d = super().make_dict(record)
        d.update({"user_name": record.get("name"), "devices": []})
        for device in record.get("devices") or []:
            d["devices"].append(device)
        return d

    @classmethod
    def transform_list(cls, results: List[dict], args: frappe._dict):
        _results = [*results]
        if args.filters:
            for dt, fieldname, operator, value in args.filters:
                if dt == "Traccar UserDevice":
                    users = [
                        x.get("parent")
                        for x in TraccarUserDevice.get_list(
                            {"filters": [[dt, fieldname, operator, value]]}
                        )
                    ]
                    _results = [x for x in _results if x.get("name") in users]
        _results = super().transform_list(_results, args)
        return _results

    def as_record(self, with_id=False):
        d = super().as_record(with_id=with_id)
        d.update({"name": d.pop("userName")})
        return d
