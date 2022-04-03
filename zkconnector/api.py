import frappe
from threading import Thread
from .zkconnect import ZKConnect, post_req, attendance_to_json, get_headers
from dateutil import parser

connections = {}
api_key = None
api_secret = None
url = frappe.utils.get_url()
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
            # print(f"\n\n\n\n\n\n\n\n\n\n\n\n{conn}\n\n\n\n\n\n\n\n\n\n\n\n")

            last = frappe.get_list('ZKLogs', filters={'device_name':conn},\
                               order_by='date desc, time desc', limit=1)[0]
            last_saved_log = frappe.get_doc('ZKLogs', last) #last log in frappe
            
            logs = connections[conn].get_logs()
            last_log = logs[-1] # last log on the device
            last_log_date, last_log_time = last_log.timestamp.isoformat().split("T")
            # print(f"{last_log_date}  {last_saved_log.date}  ")
            # print(f"{parser.parse(str(last_log_time))}  {parser.parse(str(last_saved_log.time))} ")
            # print("date = ", parser.parse(str(last_log_date)) == parser.parse(str(last_saved_log.date)))
            # print("time = ", parser.parse(str(last_log_time)) == parser.parse(str(last_saved_log.time)))
            if(parser.parse(str(last_log_date)) != parser.parse(str(last_saved_log.date)) or \
               parser.parse(str(last_log_time)) !=  parser.parse(str(last_saved_log.time))):
                
                for log in logs[::-1]:
                    log_d, log_t = log.timestamp.isoformat().split("T")

                    if parser.parse(str(log_d)) == parser.parse(str(last_saved_log.date)) and\
                        parser.parse(str(log_t)) ==  parser.parse(str(last_saved_log.time)):
                        break
                    # print(f"\n\n\n\n\n\n\n\n\n\n\n\n{log}\n\n\n\n\n\n\n\n\n\n\n\n")
                    payload = attendance_to_json(log, conn)
                    headers = get_headers(api_key, api_secret)
                    post_req(f'{url}/api/resource/ZKLogs', headers, payload)
    
    # print(f"\n\n\n\n\n\n\n\n\n\n\n\ndon\n\n\n\n\n\n\n\n\n\n\n\n")
    connect_devices()

@frappe.whitelist()
def connect_devices():
    global api_key
    global api_secret
    global connections

    api_secret = frappe.get_doc("User", 'Administrator').get_password("api_secret")
    api_key = frappe.get_doc("User", 'Administrator').api_key

    devices = frappe.get_all('ZKDevices')
    for device in devices:
        # print(device)
        zk_device = frappe.get_doc('ZKDevices', device)
        if zk_device.name not in connections.keys():
            connections[zk_device.name] = ZKConnect(zk_device.ip, int(zk_device.port),\
                                                    zk_device.password)
    
    for conn in connections:
        try:
            # if not connections[conn].is_connected():
            # print("device connected and conn is ", conn)
            connections[conn].make_connection()
        except:
            frappe.throw(f"Can't connect to device {conn}")
    
    for conn in connections:
        # print("connection live", connections[conn].is_live())
        # print("connection connected", connections[conn].is_connected())

        if connections[conn].is_connected() and not connections[conn].is_live():

            Thread(target=connections[conn].live_capture, args=[conn, api_key, api_secret]).start()
