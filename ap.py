
from wlan_group import WlanGroup

class AccessPoint:


    def __init__(self, ra, ap_info, wlan_groups):
        
        self.ra = ra
        self.name = ap_info['name']
        self.mac = ap_info['mac']
        self.serial = ap_info['serial']
        self.ap_group_id = ap_info['apGroupId']
        self.zone_id = ap_info['zoneId']
        self.wg_24 = None
        self.wg_50 = None
        self.wlan_groups = wlan_groups
        self._init_ap()

    def _init_ap(self):

        wg_24_name = "wg_24_{}".format(self.mac)
        wlan_group_24 = [wg for wg in self.wlan_groups if wg['name'] == wg_24_name]
        wg_50_name = "wg_50_{}".format(self.mac)
        wlan_group_50 = [wg for wg in self.wlan_groups if wg['name'] == wg_50_name]

        if not wlan_group_24:
            print ("Creating WG 24 for {}".format(self.mac))
            wlan_group_24 = [self.ra.wlan_group_create(self.zone_id, wg_24_name, "Custom WG")]


            if 'errorCode' in wlan_group_24[0]:
                if wlan_group_24[0]['errorCode'] == 302:
                    wgs = self.ra.wlan_group_retrieve_list(self.zone_id)
                    wg = [wg for wg in wgs if wg['name'] == wg_24_name]
                    wg_24_id = wg[0]['id']

            else:
                wg_24_id = wlan_group_24[0]['id']

            self.ra.ap_modify(
                    ap_mac=self.mac,
                    data={'wlanGroup{}'.format('24'): {'id': wg_24_id,
                                                        'name': wg_24_name}})
        
        else:
            self.wg_24 = WlanGroup(self.ra, wlan_group_24[0])
        
        if not wlan_group_50:
            print ("Creating WG 50 for {}".format(self.mac))
            wlan_group_50 = [self.ra.wlan_group_create(self.zone_id, wg_50_name, "Custom WG")]

            if 'errorCode' in wlan_group_50[0]:
                if wlan_group_50[0]['errorCode'] == 302:
                    wgs = self.ra.wlan_group_retrieve_list(self.zone_id)
                    wg = [wg for wg in wgs if wg['name'] == wg_50_name]
                    wg_50_id = wg[0]['id']

            else:
                wg_50_id = wlan_group_50[0]['id']

            self.ra.ap_modify(
                    ap_mac=self.mac,
                    data={'wlanGroup{}'.format('50'): {'id': wg_50_id,
                                                        'name': wg_50_name }})

        else:
            self.wg_50 = WlanGroup(self.ra, wlan_group_50[0])  

    def assign_static(self, wlan_id, wlan_obj):
        

        
        resp24 = self.ra.wlan_group_add_member(self.zone_id, self.wg_24.wg_id, wlan_id)
        resp50 = self.ra.wlan_group_add_member(self.zone_id, self.wg_50.wg_id, wlan_id)

        self.wg_24.wl_members[wlan_id] = wlan_obj
        self.wg_50.wl_members[wlan_id] = wlan_obj
        
        return resp24, resp50