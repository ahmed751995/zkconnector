import frappe
from zk import ZK, const
from threading import Thread
import time
from multiprocessing import Process
import json, requests

@frappe.whitelist()
def connect_devices():
    api_secret = frappe.get_doc("User", 'Administrator').get_password("api_secret")
    api_key = frappe.get_doc("User", 'Administrator').api_key
    
    connections = {}
    devices = frappe.get_all('ZKDevices')
    for device in devices:
        d = frappe.get_doc('ZKDevices', device)
        if d.name not in connections.keys():
            connections[d.name] = ZKConnect(d.ip, int(d.port), d.password)
    
    for conn in connections:
        try:
            if not connections[conn].is_connected():
                print("device connected and conn is ", conn)
                connections[conn].make_connection()
        except:
            frappe.throw(f"Can't connect to device {conn}")
    
    for conn in connections:
        # print("connection", connections)

        if connections[conn].is_connected() and not connections[conn].is_live():

            Thread(target=connections[conn].live_capture, args=[conn, api_key, api_secret]).start()

def post_req(url, headers, payload):
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    
class ZKConnect:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.conn = None
        self.close = False
        self.live = False

    def set_default(self):
        self.ip = '192.168.1.201'
        self.port = 4370
        self.password = 0
        print("default setted")

    def make_connection(self):
        try:
            zk = ZK(
                self.ip,
                self.port,
                timeout=5,
                password=self.password,
                force_udp=True,
                ommit_ping=False)
            self.conn = zk.connect()
            self.close = False

        except BaseException:
            raise Exception("can't connect")

    def kill_connection(self):
        self.close = True
        while(self.live):
            time.sleep(.1)
        self.conn.disconnect()

    def is_connected(self):
        if self.conn == None:
            return False
        return self.conn.is_connect

    
    def is_live(self):
        return self.live

        
    def live_capture(self, device_name, api_key='', api_secret=''):
        self.live = True
        for attendance in self.conn.live_capture():
            print("tracking in progress")
            if self.close or not self.is_connected():
                break

            if attendance:
                print("got device here")
                payload = {}
                payload["user_id"] = attendance.user_id
                date, time = attendance.timestamp.isoformat().split("T")
                payload["date"] = date
                payload["time"] = time
                payload["punch"] = attendance.punch
                payload["status"] = attendance.status
                payload["uid"] = attendance.uid
                
                payload_json = json.dumps({"data": payload})

                headers = {
                    'Authorization': f'token {api_key}:{api_secret}',
                    'Content-Type': 'application/json',
                }
                
                res = post_req('http://develop.test:8000/api/resource/ZKLogs', headers, payload_json)

                
        self.live = False
