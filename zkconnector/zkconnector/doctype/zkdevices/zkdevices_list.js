frappe.listview_settings['ZKDevices'] = {
    onload: function(listview) {
	console.log("hi")
	listview.page.add_inner_button(__("connect"), function() {
	    frappe.call({
		method: 'zkconnector.api.connect_devices',
		callback: function(r){
		    console.log('done')
		}
	    })
	})
    }
}
