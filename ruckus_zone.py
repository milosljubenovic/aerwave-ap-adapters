from ap import AccessPoint
from wlan import Wlan

class RuckusZone:

    def __init__(self, ra=None, zone_id=None, zone_name=None, db=None):
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.ra = ra
        self.aps = {}
        self.db = db
        self.wlans = {}

        self._ruckus_zone_init()

        
    def _ruckus_zone_init(self):
        aps = self.ra.ap_retrieve_list()
    
        zone_aps = [ap for ap in aps if ap['zoneId'] == self.zone_id]
        wlan_groups = self.ra.wlan_group_retrieve_list(self.zone_id)
        wlans = self.ra.get_wlans(self.zone_id)

        for ap in zone_aps:
            self.aps[ap['mac']] = AccessPoint(self.ra, ap, wlan_groups, self.db)
        
        for wlan in wlans:
            self.wlans[wlan['id']] = Wlan(wlan)

    def create_wlan(self, zone_status, wlan_data):


        wlan_id = self.ra.wlan_create(zone_id = self.zone_id, 
                            wlan_name = wlan_data['wlan_name'], 
                            ssid = wlan_data['ssid'],
                            downlink_rate= wlan_data['rate_mbps'],
                            passphrase=wlan_data['passphrase'],
                            description="Aerwave User WLAN",
                            vlan=wlan_data['vlan'])

        if wlan_id:
            wlan_data = self.ra.wlan_retrieve(self.zone_id, wlan_id)
            self.wlans[wlan_id] = Wlan(wlan_data)
            rv =  wlan_id

            self.db.assign_wlan_id_to_zone(self.zone_id, wlan_id, wlan_data)
        else:
            # EMAIL THAT WE FAILED
            print ('We failed man..')
            rv = False
        zone_status[self.zone_id] = rv
        return rv

    def delete_wlan(self, zones_status, zone_id, wlan_id):
        ret = self.ra.wlan_delete(zone_id=self.zone_id, wlan_id=wlan_id)
        zones_status[zone_id] = ret



        

