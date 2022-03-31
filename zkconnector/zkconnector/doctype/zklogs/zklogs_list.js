frappe.listview_settings['ZKLogs'] = {
    onload: function(listview) {
	console.log("hi")
	listview.page.add_inner_button(__("Sync devices"), function() {
	    frappe.call({
		method: 'zkconnector.api.sync_logs',
		callback: function(r){
		    console.log(r.message)
		}
	    })
	});

    }
}
