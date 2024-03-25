# Copyright (c) 2024, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from traccar_integration.traccar.doctype.traccar_settings.traccar_settings import (
    TraccarSettings,
)
import json
import re
import requests
from typing import Any, Callable, List
import datetime


class TraccarException(Exception):
    pass


class TraccarDocument(Document):
    @staticmethod
    def request(
        method: str, path: str, params: dict | None = None, payload: dict | None = None
    ) -> Any:
        cache_key = f"traccar:{path}:{'' if params is None else json.dumps(params, sort_keys=True)}"
        if method == "GET" and (data := frappe.cache.get_value(cache_key)):
            return data

        settings: TraccarSettings = frappe.get_single("Traccar Settings")
        base_url = re.sub(r"\/+$", "", settings.server_url)
        url = f"{base_url}{path}"
        headers = {"Authorization": f"Bearer {settings.token}"}
        r = requests.request(
            method=method, url=url, params=params, json=payload, headers=headers
        )
        if not r.ok:
            frappe.throw(
                f"<code>{r.text}</code>",
                exc=TraccarException,
            )
        if method == "DELETE":
            return

        data = r.json()
        if method == "GET":
            frappe.cache.set_value(cache_key, data, expires_in_sec=3600)
        return data

    def clear_keys(self, path: str):
        frappe.cache.delete_keys(f"traccar:{path}:*")

    @classmethod
    def make_dict(cls, record: dict[str, Any]) -> dict[str, Any]:
        doctype = _get_doctype(cls.__name__)
        fields = frappe.get_meta(doctype).get_permitted_fieldnames()
        attributes = record.get("attributes") or {}
        return frappe._dict(
            {
                "name": str(record.get("id")),
                **{x: record.get(_camel(x)) for x in fields},
                "creation": attributes.get("creation"),
                "modified": attributes.get("modified"),
            }
        )

    def as_record(self, with_id=False) -> dict[str, Any]:
        fields = self.meta.get_permitted_fieldnames()
        d = {_camel(x): self.get(x) for x in fields if x != "name"}
        d.update(
            {
                "attributes": {
                    **self._get_attributes(),
                    "creation": self.creation or self.modified,
                    "modified": self.modified,
                },
            }
        )
        if with_id:
            return {"id": self.get("name"), **d}
        return d

    def _get_attributes(self):
        attributes = self.get("attributes")

        if isinstance(attributes, dict):
            return attributes

        if isinstance(attributes, str):
            try:
                return json.loads(attributes)
            except json.JSONDecodeError:
                return {}

        return {}

    @classmethod
    def transform_list(cls, results: List[dict], args: frappe._dict):
        doctype = _get_doctype(cls.__name__)
        fields = _get_fields(doctype, args.fields)
        _results = [*results]

        if args.filters:
            for dt, fieldname, operator, value in args.filters:
                if dt == doctype and (op := _get_operation(operator)):
                    _results = [x for x in _results if op(x.get(fieldname), value)]

        if args.or_filters:
            _unioned_results = []
            for row in _results:
                for dt, fieldname, operator, value in args.or_filters:
                    if dt == doctype and (op := _get_operation(operator)):
                        if row not in _unioned_results and op(
                            row.get(fieldname), value
                        ):
                            _unioned_results.append(row)
            _results = _unioned_results

        if args.order_by:
            allowed_fields = _get_fields(doctype)
            standard_fields = frappe.get_meta(doctype).default_fields
            for term in [x for x in args.order_by.split(", ") if x.find(doctype) >= 0]:
                _term = term.split(".")[-1]
                _field, _dir = _term.split(" ")
                _field = _field.replace("`", "")
                if _field in standard_fields or _field in allowed_fields:
                    _results = sorted(
                        _results,
                        key=lambda x: x.get(_field) or "",
                        reverse=_dir.lower() == "desc",
                    )

        _results = [{k: row.get(k) for k in fields} for row in _results]

        if args.as_list:
            return [[row.get(k) for k in fields] for row in _results]

        return _results


def _get_fields(doctype: str, fields: List[str] | None = None) -> List[str]:
    allowed_fields = ["name", *frappe.get_meta(doctype).get_permitted_fieldnames()]
    if not fields:
        return allowed_fields

    _fields = [x.split(".")[-1].replace("`", "") for x in fields]
    _fields = [x for x in _fields if x in allowed_fields]
    return _fields


def _camel(text: str) -> str:
    pascal = "".join(x.title() for x in text.split("_"))
    return pascal[0].lower() + pascal[1:]


def _get_doctype(text: str) -> str:
    return " ".join(re.split(r"(?<!^)(?=[A-Z])", text))


def make_datetime(x) -> datetime.datetime:
    from pytz import timezone
    from frappe.utils import get_datetime, get_system_timezone

    tz = get_system_timezone()
    _x = get_datetime(x)
    assert _x is not None

    if not _x.tzinfo:
        return _x.astimezone(timezone(tz))

    return _x


def _get_operation(operand: str) -> Callable[[Any, Any], bool] | None:
    import operator

    def like(x: str, y: str) -> bool:
        return x.lower().find(y.replace("%", "").lower()) >= 0

    def contains(x: str, y: List[str]) -> bool:
        return x.lower() in [term.lower() for term in y]

    operation_map = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
    }

    def compare(x, y) -> bool:
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            return operation_map[operand](x, y)
        if isinstance(x, (str, datetime.date, datetime.datetime)) and isinstance(
            y, (str, datetime.date, datetime.datetime)
        ):
            from frappe.utils import ParserError

            try:
                return operation_map[operand](make_datetime(x), make_datetime(y))
            except ParserError:
                pass

        return False

    def between(x, y) -> bool:
        from frappe.utils import ParserError, add_days

        try:
            _x = make_datetime(x)
            from_date = make_datetime(y[0])
            to_date = make_datetime(add_days(y[1], 1))
            return from_date <= _x < to_date
        except ParserError:
            pass

        return False

    match operand:
        case "=":
            return operator.eq
        case "!=":
            return operator.ne
        case "like":
            return lambda x, y: bool(x) and like(x, y)
        case "not like":
            return lambda x, y: bool(x) and not like(x, y)
        case "in":
            return lambda x, y: bool(x) and contains(x, y)
        case "not in":
            return lambda x, y: bool(x) and not contains(x, y)
        case "is":
            return lambda x, y: x is not None if y == "set" else x is None
        case ">" | ">=" | "<" | "<=":
            return compare
        case "Between":
            return between

    return None
