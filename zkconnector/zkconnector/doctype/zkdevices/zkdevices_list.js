frappe.listview_settings['ZKDevices'] = {
    add_fields: ["Status"],
    get_indicator: function (doc) {
	return [__(doc.status), {
	    "Disconnected": "red",
	    "Connected": "green",
	}[doc.status], "status,=," + doc.status];
    },
    before_render: function(listview) {
	frappe.call({
	    method: 'zkconnector.api.check_status',
	    callback: function(r){}
	});
    },
    onload: function(listview) {

	
	listview.page.add_inner_button(__("Connect ALL"), function() {
	    frappe.call({
		method: 'zkconnector.api.connect_devices',
		callback: function(r){}
	    })
	});

	listview.page.add_inner_button(__("Disconnect ALL"), function() {
	    frappe.call({
		method: 'zkconnector.api.disconnect_devices',
		callback: function(r){}
	    })
	});
    }
}
