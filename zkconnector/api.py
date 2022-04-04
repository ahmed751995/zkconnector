import frappe
from threading import Thread
from .zkconnect import ZKConnect, post_req, attendance_to_json, get_headers
from dateutil import parser

connections = {}
api_key = None
api_secret = None
url = frappe.utils.get_url()

@frappe.whitelist()
def check_status():
    global connections
    if len(connections.keys()) == 0:
        devices = frappe.get_all('ZKDevices')
        for device in devices:
            zk_device = frappe.get_doc('ZKDevices', device)
            zk_device.status = "Disconnected"
            zk_device.save()
    else:
        for conn in connections:
            zk_device = frappe.get_doc('ZKDevices', conn)
            if not connections[conn].is_connected():
                zk_device.status = "Disconnected"
                zk_device.save()
    frappe.db.commit()

@frappe.whitelist()
def sync_logs():
    global api_secret
    global api_key
    global connections
    global url

    for conn in connections:
        connections[conn].end_live()
        # print("live ended")
        if connections[conn].is_connected():
            last = frappe.get_list('ZKLogs', filters={'device_name':conn},\
                               order_by='date desc, time desc', limit=1)[0]
            last_saved_log = frappe.get_doc('ZKLogs', last) #last log in frappe
            
            logs = connections[conn].get_logs()
            last_log = logs[-1] # last log on the device
            last_log_date, last_log_time = last_log.timestamp.isoformat().split("T")
            
            if(parser.parse(str(last_log_date)) != parser.parse(str(last_saved_log.date)) or \
               parser.parse(str(last_log_time)) !=  parser.parse(str(last_saved_log.time))):
                
                for log in logs[::-1]:
                    log_d, log_t = log.timestamp.isoformat().split("T")
                    
                    if parser.parse(str(log_d)) == parser.parse(str(last_saved_log.date)) and\
                        parser.parse(str(log_t)) ==  parser.parse(str(last_saved_log.time)):
                        break
                    payload = attendance_to_json(log, conn)
                    headers = get_headers(api_key, api_secret)
                    post_req(f'{url}/api/resource/ZKLogs', headers, payload)
    
    connect_devices()

@frappe.whitelist()
def connect_devices():
    global api_key
    global api_secret
    global connections
    global url
    api_secret = frappe.get_doc("User", 'Administrator').get_password("api_secret")
    api_key = frappe.get_doc("User", 'Administrator').api_key

    devices = frappe.get_all('ZKDevices')
    for device in devices:
        zk_device = frappe.get_doc('ZKDevices', device)
        if zk_device.name not in connections.keys():
            connections[device.name] = ZKConnect(zk_device.ip, int(zk_device.port),\
                                                    zk_device.password)
    
    for conn in connections:
        try:
            if not connections[conn].is_connected():
                connections[conn].make_connection()
            zk_device = frappe.get_doc('ZKDevices', conn)
            zk_device.status = "Connected"
            zk_device.save()
            frappe.db.commit()
            if not connections[conn].is_live():

                Thread(target=connections[conn].live_capture, args=[conn, url, api_key, api_secret]).start()
        except:
            frappe.throw(f"Can't connect to device {conn}")
    
       
       



@frappe.whitelist()
def disconnect_devices():

    for conn in connections:
        try:
            connections[conn].kill_connection()
            zk_device = frappe.get_doc('ZKDevices', conn)
            zk_device.status = "Disconnected"
            zk_device.save()
            frappe.db.commit()
            
        except:
            frappe.throw("Please check your server")
