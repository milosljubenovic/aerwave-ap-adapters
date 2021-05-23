from requests.sessions import session
from sqlalchemy import create_engine, or_
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from db.models import *
# from utils import Utils


class DatabaseAPI:
    def __init__(self, cfg):
        self.cfg = cfg
        self.engine = self.create_engine()
        
        print ('.')
        self.session_maker = sessionmaker(bind=self.engine)
        #FIXME: https://cloud.google.com/sql/docs/mysql/manage-connections
    def create_engine(self):
        """
        This method will create DB Engine
        that will be used during life cycle of current obj.
        """
        db_cfg = self.cfg['db']
        return create_engine('mysql://{}:{}@{}/{}'.format(
                db_cfg['user'],
                db_cfg['password'],
                db_cfg['host'],
                db_cfg['database']),
                pool_recycle=1800,
                connect_args={'connect_timeout': 10000})

    @staticmethod
    def _wlan_dict(obj):
        rv = { 
                'user_first_name': obj.usr.usr_firstname,
                'user_last_name' : obj.usr.usr_lastname,
                'speedrate': obj.usr.subp.subp_speed if getattr(obj,'subp', None) else '',
                'ap_mac' : obj.usr.uni.uni_ap_mac,
                'wlan_name' : obj.usr_id,
                'wlan_ssid': obj.wlan_ssid,
                'wlan_passphrase': obj.wlan_passphrase,
             }
        
        if getattr(obj, 'wfp', None):
            rv.update( {
                'filtering_policy': {
                    'wfp_bockedurls': obj.wfp.wfp_blockedurls,
                    'wfp_primaryip': obj.wfp.wfp_primaryip,
                    'wfp_secondaryip': obj.wfp.wfp_secondaryip, 
                }  
            })
        if getattr(obj, 'wdp', None):
            rv.update ( {
                'dhcp_pool' : {
                    'wdp_description' : obj.wdp.wdp_description,
                    'wdp_id' : obj.wdp.wdp_id,
                    'wdp_leasetime_hours' : obj.wdp.wdp_leasetime_hours,
                    'wdp_leasetime_minutes' : obj.wdp.wdp_leasetime_minutes,
                    'wdp_pool_end_ip' : obj.wdp.wdp_pool_end_ip,
                    'wdp_pool_start_ip' : obj.wdp.wdp_pool_start_ip,
                    'wdp_primarydns_ip' : obj.wdp.wdp_primarydns_ip,
                    'wdp_secondarydns_ip' : obj.wdp.wdp_secondarydns_ip,
                    'wdp_subnetmas' : obj.wdp.wdp_subnetmask,
                    'wdp_subnetnetwork_ip' : obj.wdp.wdp_subnetnetwork_ip
                    }
            })
            
        return { obj.usr_id : rv }
    
    def _users_dict(self, obj):
        """
        :param user:    Users collection object
        :return:    {id: '',
                     wlan_name: ''
                     ssid:'',
                     passphrase:'',
                    'blocked_urls',
                    'primary_ip',
                    'secondary_ip'}
        """
        return {'id' : obj.usr.usr_id,
                'wlan_name' : str(obj.usr.usr_id),
                'ssid' : obj.wlan_ssid,
                'passphrase' : obj.wlan_passphrase,
                'vlan' : obj.usr.uni.uni_vlan,
                'rate_mbps': '',
                'blocked_urls' : '',
                'primary_ip' : '',
                'secondary_ip': ''
                }
    
    def get_wlans_data(self):
        """
        Return {AP_MAC: [self._ssid_dict_from_obj],
                *: [...]}
        :return:    dict
        """
        session = self.session_maker()
        import time
        s = time.time()
        objs = session.query(Wlan).join(User).join(Unit).filter(User.usr_status != None).all()
        print ("taken {}".format(time.time() -s ))
        data = {}
        [data.update(self._wlan_dict(obj)) for obj in objs]
        session.close()
        return data
    
    def get_static_wlans_data(self):
        """
        Return {AP_MAC: [self._ssid_dict_from_obj],
                *: [...]}
        :return:    dict
        """
        session = self.session_maker()
    
        objs = session.query(User).join(Unit).filter(User.usr_status != None).all()

        data = {}
        
        for obj in objs:
            if obj.uni.uni_ap_mac not in data.keys():
                data[obj.uni.uni_ap_mac] =  [obj.usr_id]
            else:
                data[obj.uni.uni_ap_mac].append(obj.usr_id)      
        session.close()
        return data   
    

    def users(self):
        session = self.session_maker()
        active_users = session.query(Wlan).join(User).filter(User.usr_status != None).all()
        rv =  [self._users_dict(us) for us in active_users]
        session.close()
        return rv
    
    def get_user_by_id(self, usr_id=None):
        session = self.session_maker()
        usr = session.query(User).filter(User.usr_status != None, User.usr_id == usr_id).first()
        session.close()
        return usr

    def asign_zone_wg(self, ap_info):
        session = self.session_maker()
        unit = session.query(Unit).filter(Unit.uni_ap_mac == ap_info['mac']).first()
        rwg_50 =None
        rwg_24 = None
        if not unit:
            return False

        if not unit.rwg_24_id:
            rwg_24 = RuckusWg24(wg24_name=ap_info['wlanGroup24']['name'],
                                wg24_id=ap_info['wlanGroup24']['id'])
            session.add(rwg_24)
            session.commit()

        if not unit.rwg_50_id:
            rwg_50 = RuckusWg50(wg50_name=ap_info['wlanGroup50']['name'],
                                wg50_id=ap_info['wlanGroup50']['id'])

        
            session.add(rwg_50)
            session.commit()


        unit.uni_zoneid = ap_info['zoneId']
        if rwg_50 and rwg_24:
            unit.rwg_24_id = rwg_24.rwg_24_id
            unit.rwg_50_id = rwg_50.rwg_50_id

        session.commit()
        session.close()

        return True

    def get_wg(self, ap_mac):
        session = self.session_maker()

        rv = {}
        unit = session.query(Unit).filter(Unit.uni_ap_mac == ap_mac).first()
        if unit:
            rv = {'wlanGroup24_id' : unit.rwg_24.wg24_id,
                  'wlanGroup50_id' : unit.rwg_50.wg50_id}
            
        session.close()   
        return rv

    def create_ruckus_wlan(self, usr_data, ruckus_id, zone_id):
        session = self.session_maker()
        rw = session.query(User).join(Wlan).join(RuckusWlan).filter(User.usr_id == int(usr_data['wlan_name'])).first()
        if not rw:
            wl_obj = session.query(Wlan).join(User).filter(User.usr_id == int(usr_data['wlan_name'])).first()

            rw = RuckusWlan(rw_ruckid = int(ruckus_id), rwl_zoneid=zone_id, wlan_id = wl_obj.wlan_id)

            session.add(rw)
            session.commit()
            
        

        print ('x')
        
    def get_wlan_id_by_wlan_name_per_zone(self, zone_id, wlan_name):
        session = self.session_maker()

        wl_obj = session.query(RuckusWlan).join(Wlan).join(User).filter(User.usr_id == int(wlan_name) , RuckusWlan.rwl_zoneid == zone_id).first()

        if not wl_obj:
            rv = None
        else:
            rv = wl_obj.wlan_id

        session.close()
        return rv
        
    def update_zoneid(self, zone_id, zone_name):
        session = self.session_maker()

        zone_id_obj = session.query(Property).filter(Property.pro_zone_name==zone_name).first()

        if not zone_id_obj:
            print ("Missing db name in database for {}".format(zone_name))
            return None
        
        zone_id_obj.pro_zone_id = zone_id

        session.commit()
        session.close()

        return True
    
    def assign_wlan_id_to_zone(self, zone_id=None, wlan_id=None, user=None):
        session = self.session_maker()
        wlan = session.query(Wlan).join(User).filter(User.usr_email == user['name']).first()
        ruckus_wlan = RuckusWlan(wlan_id=wlan.wlan_id,
                                rwl_zoneid = zone_id,
                                rwl_ruckid=wlan_id)

        session.add(ruckus_wlan)
        session.commit()

if __name__ == '__main__':
    import yaml
    cfg = yaml.load(open('ruckus/config.yml', 'rb'), Loader=yaml.FullLoader)
    dba = DatabaseAPI(cfg=cfg)
    rv = dba.get_wlans_data()
    print (rv)
    rv = dba.get_static_wlans_data()
    print (rv)
