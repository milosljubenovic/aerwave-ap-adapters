from flask import Flask, jsonify, request
from ruckus_server import RuckusServer
from ruckus_api import RuckusAPI

from db.database_api import DatabaseAPI
from threading import Thread
import yaml

app = Flask(__name__)
cfg = yaml.load(open('config.yml', 'rb'), yaml.FullLoader)
ruckus_api = RuckusAPI(cfg)
database_api = DatabaseAPI(cfg)

ruckus_server = RuckusServer(ruckus_api = ruckus_api, db=database_api)
print ("finished server worker init.")
@app.route('/create_wlan', methods=['POST'])
def create_wlan():

    data = request.json

    zones_status = {}
    threads = {}
    
    for zone_name, zone in ruckus_server.zones.items():
        threads[zone_name] = Thread(target=zone.create_wlan, args=(zones_status, data))
        threads[zone_name].start()
    
    for zone_name in ruckus_server.zones.keys():
        threads[zone_name].join()

    if False not in [status for _, status in zones_status.items()]:
        zone = ruckus_server.zones[data['prop_zoneid']]
        ap = zone.aps[data['ap_mac']]
        wlan_id = zones_status[data['prop_zoneid']]
        wlan_obj = zone.wlans[wlan_id]
        resp24, resp50 = ap.assign_static(wlan_id, wlan_obj)

        if not resp24 and not resp50:
            return jsonify(msg="Wlan created succesfuly", ruckus = zones_status), 200
        else:
            return jsonify(msg="Failed on assign to AP"), 200
    else:
        return jsonify(msg="Failed on wlan creation...", ruckus = zones_status), 302

@app.route('/assign_static', methods=['POST'])
def assign_static():
    data = request.json

    zone =  ruckus_server.zones[data['zone_id']]
    ap = zone.aps[data['ap_mac']]
    wlan_id  = data['wlan_id']
    wlan_obj = zone.wlans[wlan_id]

    resp24, resp50 = ap.assign_static(wlan_id, wlan_obj)
    
    if not resp24 and not resp50:
        return jsonify(msg="Yay, Assigned ;)"), 200
    else:
        return jsonify(msg="Error occured..."), 302

@app.route('/delete_wlan', methods=['DELETE'])
def delete_wlan():
    
    data = request.json

    threads = {}
    zones_status = {}

    for zone_id, wlan_id in data['ruckus'].items():
        zone = ruckus_server.zones[zone_id]
        threads[zone_id] = Thread(name=zone_id, target = zone.delete_wlan, 
                    args=(zones_status, zone_id, wlan_id))
        threads[zone_id].start()

    for _, t in threads.items():
        t.join()

    if False not in [status for _, status in zones_status.items()]:
        return jsonify(msg="Wlan created succesfuly", ruckus = zones_status), 200
    else:
        return jsonify(msg="Failed on wlan creation...", ruckus = zones_status), 302




        

if __name__ == "__main__":

    import yaml
    import time
    cfg = yaml.load(open('config.yml', 'rb'), yaml.FullLoader)
    
    s = time.time()
    ruckus_api = RuckusAPI(cfg)
    database_api = DatabaseAPI(cfg)

    ruckus_server = RuckusServer(ruckus_api = ruckus_api, db=database_api)
    print (time.time() -s )
    # s = time.time()
    # ruckus_server.refresh()
    # print (time.time() -s )

    app.run(host=cfg['flask']['host'],
            port=cfg['flask']['port'])