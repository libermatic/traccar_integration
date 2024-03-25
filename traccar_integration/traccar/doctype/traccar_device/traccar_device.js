// Copyright (c) 2024, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Traccar Device", {
  setup(frm) {
    frm.set_query('unique_id', { filters: { item_group: 'Tracker' } });
    frm.set_query('phone', { filters: { item_group: 'SIM' } });
  },
});
