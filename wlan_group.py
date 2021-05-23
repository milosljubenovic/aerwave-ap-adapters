from wlan import Wlan




class WlanGroup:

    def __init__(self, ra, wg_data):
        self.ra = ra
        self.wg_id = wg_data['id']
        self.zone_id = wg_data['zoneId']
        self.name = wg_data['name']
        self.description = wg_data['description']
        self.members = wg_data['members']
        self.wl_members = {}
        self._wlangroup_init()


    def _wlangroup_init(self):
        pass