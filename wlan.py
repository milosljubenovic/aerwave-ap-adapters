


class Wlan:

    def __init__(self, wlan_data):

        self.id = wlan_data['id']
        self.wlan_name = wlan_data['wlan_name'] \
                    if 'wlan_name' in wlan_data.keys() else wlan_data['id']
        self.ssid = wlan_data['ssid']
        self.zone_id = wlan_data['prop_zoneid'] \
                    if 'prop_zoneid' in wlan_data.keys() else wlan_data['zoneId']

        self.aps_24_wg = []
        self.aps_50_wg = []

    def _wlan_init(self):
        pass