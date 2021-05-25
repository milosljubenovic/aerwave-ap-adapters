import urllib3
urllib3.disable_warnings()
import requests
import json
import ruckus_helpers as helpers


class RuckusAPI:

    def __init__(self, cfg):
        self.cfg = cfg
        self.base_url = cfg['ruckus']['url']
        self.headers_template = {'Content-Type': "application/json;charset=UTF-8"}
        self.session = requests.session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=cfg['ruckus']['max_connections'],
                                                pool_maxsize=cfg['ruckus']['max_connections'])
        self.session.mount('https://', adapter)

        login_status = self._ruckusapi_init().status_code
        print ("Ruckus Login: {}".format(login_status))
        self.req_listsize = cfg['ruckus']['req_listsize']

    def _ruckusapi_init(self):
        payload = {'username': self.cfg['ruckus']['username'],
        'password': self.cfg['ruckus']['password']}
        
        login = self.session.post(
            url="{}/{}/{}".format(self.base_url, 'v6_0', 'session'),
            headers=self.headers_template,
            data=json.dumps(payload),
            verify=False)
            
        self.headers_template['Cookie'] = 'JSESSIONID={}'.format(login.cookies['JSESSIONID'])

        return login

    def request(self, method, url, data=None, params=None, decoding="UTF-8"):
        """

        :param method:      [post, get, delete, patch]
        :param url:         string
        :param data:   dictionary
        :param params:   dictionary
        :return:
        """
        response = getattr(self.session, method)(
            '{}/{}?listSize={}'.format(self.base_url, url, self.req_listsize),
            headers=self.headers_template,
            data=json.dumps(data) if data is not None else '',
            params=json.dumps(params) if params is not None else '',
            verify=False)
        
        if not response:
            # TODO: Reinit RuckusAPI
            resp_msg = json.loads(response.text)
            if resp_msg['errorType'] == 'No active session':

                self.logger.info(self.login())
                self.request(method,url,data,params,decoding)

            
            else:
                print(resp_msg)

        content = response.content.decode('UTF-8')

        return json.loads(content) if content else None

    def retrieve_list(self, url, method='get', data=None, params=None):
        """
        For functions which retrieve List
        :param url:
        :param method:
        :param data:
        :param params:
        :return:
        """
        # TODO: check totalCount, hasMore, firstIndex - ignore for now
        # TODO: Check if request is executed
        response = self.request(
            method=method, url=url, data=data, params=params)
        
        if not response:
            # TODO: Reinit RuckusAPI
            return []

        return response.get('list') if 'list' in response else []

    # zone
    def get_zones(self):
        """

        :return:    list -> {id, name}
        """
        return self.retrieve_list(url='v8_2/rkszones', method='get')

    def ap_retrieve_list(self):
        """

        :return:    dict -> {mac, zoneId, apGroupId, name}
        """
        return self.retrieve_list(url='v8_2/aps', method='get')

    def ap_modify(self, ap_mac, data):
        self.request(
            method='patch',
            url='v6_0/aps/{}'.format(ap_mac),
            data=data)

    def wlan_group_create(self, zone_id, name, description):
        response = self.request(
            method='post',
            url='v8_2/rkszones/{}/wlangroups'.format(zone_id),
            data={'name': name, 'description': description})
        return response['id']

    def wlan_group_retrieve_list(self, zone_id):
        return self.retrieve_list(
            url='v8_2/rkszones/{}/wlangroups'.format(zone_id), method='get', params={'listSize' : 1000})


    def wlan_group_create(self, zone_id, name, description):
        response = self.request(
            method='post',
            url='v8_2/rkszones/{}/wlangroups'.format(zone_id),
            data={'name': name, 'description': description})
        return response
    
    def wlan_group_add_member(self, zone_id, wg_id, wlan_id):
        resp = self.request(
            method='post',
            url='/v8_2/rkszones/{}/wlangroups/{}/members'.format(zone_id,
                                                                 wg_id),
            data={'id': wlan_id})
        
        return resp


    def ap_summary(self, ap_mac):
        """

        :param ap_mac:
        :return:
        """
        return self.request(
            method='get',
            url='v8_2/aps/{}/operational/summary'.format(ap_mac)
        )
        
    def get_wlans(self, zone_id):
        return self.retrieve_list(
            url='v8_2/rkszones/{}/wlans'.format(zone_id), method='get')

    def wlan_create(self,
                zone_id,
                wlan_name,
                ssid,
                downlink_rate,
                fp=None,
                passphrase='',
                description='Aerwave User WLAN',
                vlan=1,
                ):

        data = helpers.generate_wlan_data(
            wlan_name=wlan_name,
            ssid=ssid,
            downlink_rate=downlink_rate,
            fp=fp,
            passphrase=passphrase,
            description=description,
            vlan=vlan)

        response = self.request(
            method='post',
            url='/v8_2/rkszones/{}/wlans'.format(zone_id),
            data=data
        )

        if 'id' not in response.keys():
            rv = None
        else:
            rv = response['id'] 
        return rv

    def wlan_delete(self, zone_id, wlan_id):
        resp = self.request(
            method='delete',
            url='/v8_2/rkszones/{}/wlans/{}'.format(zone_id, wlan_id))
        return resp

    def wlan_retrieve(self, zone_id, wlan_id):
        return self.request(
            method='get',
            url='/v8_2/rkszones/{}/wlans/{}'.format(zone_id, wlan_id))

