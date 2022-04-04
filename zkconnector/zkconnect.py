import requests
import json
import time
from zk import ZK, const


class ZKConnect:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.zk = None
        self.close = False
        self.live = False

    def set_default(self):
        self.ip = '192.168.1.201'
        self.port = 4370
        self.password = 0
        print("default setted")

    def make_connection(self):
        try:
            self.zk = ZK(
                self.ip,
                self.port,
                timeout=5,
                password=self.password,
                force_udp=True,
                ommit_ping=False)
            self.zk.connect()
            self.close = False

        except BaseException:
            raise Exception("can't connect")


    def end_live(self):
        self.close = True
        while(self.live):
            time.sleep(.1)
            
    def kill_connection(self):
        self.close = True
        while(self.live):
            time.sleep(.2)
        self.zk.disconnect()

    def is_connected(self):
        try:
            self.zk.connect()
            return True
        except:
            return False

    def get_logs(self):
        return self.zk.get_attendance()
    
    def is_live(self):
        return self.live

        
    def live_capture(self, device_name, url, api_key='', api_secret=''):
        self.live = True
        self.close = False
        for attendance in self.zk.live_capture():
            print("tracking in progress")
            if self.close or not self.is_connected():
                break

            if attendance:
                print("got device here")
                payload = attendance_to_json(attendance, device_name)
                
                headers = get_headers(api_key, api_secret)
                
                res = post_req(f'{url}/api/resource/ZKLogs', headers, payload)

        self.live = False



def post_req(url, headers, payload):
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def attendance_to_json(attendance, device_name):
    payload = {}
    payload["user_id"] = attendance.user_id
    date, time = attendance.timestamp.isoformat().split("T")
    payload["date"] = date
    payload["time"] = time
    payload["punch"] = attendance.punch
    payload["status"] = attendance.status
    payload["uid"] = attendance.uid
    payload["device_name"] = device_name
    payload_json = json.dumps({"data": payload})
    return payload_json


def get_headers(api_key, api_secret):
    headers = {
        'Authorization': f'token {api_key}:{api_secret}',
        'Content-Type': 'application/json',
    }
    return headers
