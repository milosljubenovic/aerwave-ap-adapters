from flask.globals import session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
from model import *
from benedict import benedict


import requests

from helpers import otp_gen, send_otp

class DatabaseAPI:
    def __init__(self, cfg):
        self.cfg = cfg
        self.engine = self.create_engine()
        self.session_maker = sessionmaker(bind=self.engine)
        # from sqlalchemy.ext.automap import automap_base
        # self.db_base = automap_base()
        # self.db_base.prepare(self.engine, reflect=True)

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
    
    def _buildings_dict(self,obj):
        return {'bul_id' : obj.bul_id,
                'pro_id' : obj.pro.pro_id,
                'pro_address' : obj.pro.pro_address, 
                'pros_id' : obj.pro.pro_id}

    
    def register_user(self, dt):
        session = self.session_maker()

        usr = session.query(User).filter(User.usr_email == dt['usr_email']).first()
        
        if usr:
            return False


        otp = otp_gen()

        while len(otp) != 6:
            otp = otp_gen()

        while self.check_existing_otp(otp):
            time.sleep(0.5)
            otp = otp_gen()

        if not send_otp(self.cfg, dt, otp):
            return False

        new_otp = OnetimePassword(usr_email=dt['usr_email'],
                                  otp_number=otp)

        

        new_usr = User (usr_firstname=dt['usr_firstname'],
                    usr_lastname=dt['usr_lastname'],
                    usr_email=dt['usr_email'],
                    uni_id =dt['uni_id'],
                    usr_phonenumber=dt['usr_phone'],
                    usr_stage=dt['usr_stage'])
                                    
        session.add(new_otp) 
        session.add(new_usr)

        session.commit()
        new_usr_rol = UsrRole(rol_id=2, usr_id=new_usr.usr_id)
        session.add(new_usr_rol)
        session.commit()
        session.close()

        return True

    def check_existing_otp(self, otp_no):
        session = self.session_maker()
        otp = session.query(OnetimePassword).filter(OnetimePassword.otp_number == otp_no).first()
        session.close()
        if not otp:
            return False

        else:
            return True



    def update_otp(self, usr_email=None, otp_no=None, stage='Login stage'):
        
        session = self.session_maker()

        usr = session.query(User).filter(User.usr_email == usr_email).first()

        if not usr:
            return False
        
        otp = session.query(OnetimePassword).join(User).filter(User.usr_email == usr_email).first()

        usr.usr_stage = stage
        otp.otp_number = otp_no
        otp.otp_used = None

        session.commit()
        session.close()

    def verify_otp(self, usr_mail=None, otp_no=None, stage=None):
        session = self.session_maker()
        obj = session.query(OnetimePassword).filter_by(usr_email=usr_mail, otp_used=None).first()
        
        if obj:
            if obj.otp_number == otp_no:
                obj.otp_used = 1
                obj.user.usr_stage = stage
                session.commit()
                return True
        session.close()
        return False
    
    def _subs_plan_dict(self, obj):
        return {
            'subp_id' : obj.subp_id,
            'subp_name' : obj.subp_name,
            'subp_price' : obj.subp_price,
            'subp_duration' : obj.subp_duration,
            'subp_duration_unit' : obj.subp_duration_unit,
            'subp_speed' : obj.subp_speed,
            'subp_unlimited': obj.subp_unlimited,
            'subp_description' : obj.subp_description
        }

    def get_subsplans(self):
        session = self.session_maker()
        objs = session.query(SubscriptionPlan)
        session.close()
        return [self._subs_plan_dict(obj) for obj in objs]


    def get_properties(self):
        session = self.session_maker()

        props = {ob.pro_id : {'address' : ob.pro_address, 'status' : ob.pros_id} for ob in session.query(Property).all()}
        units = session.query(Unit).join(Building).all()

        properties = {}
        data = benedict()
        for unit in units:
            if 'building' not in unit.bul.bul_name.lower():
                continue
            data[props[unit.bul.pro_id]['address'], 'buildings', unit.bul.bul_name, 'units', unit.uni_number] =  {'uni_id' : unit.uni_id }
            data[props[unit.bul.pro_id]['address'], 'pro_id']= unit.bul.pro_id
            data[props[unit.bul.pro_id]['address'], 'pros_id'] = props[unit.bul.pro_id]['status']

        return data

    def assign_wlan(self, data={}):
        session = self.session_maker()

        usr = session.query(User).filter(User.usr_email==data['usr_email']).first()
        
        if not usr:
            return False
        
        usr.usr_stage=data['usr_stage']

        wlan = Wlan(wlan_ssid=data['wlan_ssid'],
                    wlan_passphrase=data['wlan_passphrase'],
                    wfp_id = 1,
                    wdp_id = 1,
                    usr_id=usr.usr_id)

        session.add(wlan)
        session.commit()
        session.close()
        return True

    
    def update_stage(self, usr_stage=None, usr_email=None, usr_status=None):
        
        session = self.session_maker()
        usr = session.query(User).filter(User.usr_email==usr_email).first()

        if not usr:
            return False
        
        usr.usr_stage=usr_stage

        session.commit()
        session.close()

        return True

    def _users_dict(self, obj, prop):
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
        return {'id' : obj.usr_id,
                'wlan_name' : obj.usr.usr_email,
                'ssid' : obj.wlan_ssid,
                'passphrase' : obj.wlan_passphrase,
                'vlan' : obj.usr.uni.uni_vlan,
                'ap_mac' : obj.usr.uni.uni_ap_mac,
                'rate_mbps': '',
                'blocked_urls' : '',
                'primary_ip' : '',
                'secondary_ip': '',
                'prop_zoneid': prop.pro_zone_id,
                'prop_zonename' : prop.pro_zone_name
                }


    def get_user_data(self, usr_email):

        session = self.session_maker()
        rv = session.query(Wlan).join(User).filter(User.usr_email == usr_email).first()
        bul = session.query(Building).join(Unit).filter(Unit.uni_ap_mac == rv.usr.uni.uni_ap_mac).first()
        prop = session.query(Property).filter(Property.pro_id == bul.pro_id).first()
        if rv:
            rv = self._users_dict(rv, prop)
        
        return rv

    def soft_user_delete(self, usr_email):
        session = self.session_maker()
        user = session.query(User).filter(User.usr_email == usr_email).first()
        if not user:
            return True
        else:
            user.usr_status = None
        
        session.commit()
        session.close()
        return True


    def hard_user_delete(self, usr_email):
        session = self.session_maker()
        otp = session.query(OnetimePassword).join(User).filter(User.usr_email==usr_email).first()
        wlan = session.query(Wlan).join(User).filter(User.usr_email == usr_email).first()
        user = session.query(User).filter(User.usr_email == usr_email).first()
        ruckus_wlan = session.query(RuckusWlan).filter(RuckusWlan.wlan_id == wlan.wlan_id).all()
        usr_roles = session.query(UsrRole).join(User).filter(User.usr_email == usr_email).first()

        if otp:
            session.delete(otp)
        if wlan:
            if ruckus_wlan:
                for obj in ruckus_wlan:
                    session.delete(obj)
            session.delete(wlan)

        if usr_roles:
            session.delete(usr_roles)

        session.delete(user)
        session.commit()
        session.close()
        
        user = session.query(User).filter(User.usr_email == usr_email).first()

        if not user:
            return True
        
        return False
    
    def get_user(self,usr_email=None):
        rv = None
        session = self.session_maker()
        user = session.query(UsrRole).join(User).filter(User.usr_email==usr_email).first()

        if user:
            rv = {  'usr_email' : user.usr.usr_email,
                    'usr_phonenumber' : user.usr.usr_phonenumber,
                    'usr_firstname' : user.usr.usr_firstname,
                    'usr_role' : user.rol_id}

        session.close()
        return rv
    
    def get_users_wlan_id_per_zone(self, usr_email=None):
        session = self.session_maker()
        wlans = session.query(RuckusWlan).join(Wlan).join(User).filter(User.usr_email == usr_email).all()

        rv = {w.rwl_zoneid : w.rwl_ruckid for w in wlans}

        return rv


if __name__ == "__main__":
    # read config
    import yaml
    import time
    import json
    config = yaml.load(open('config.yml', 'rb'), yaml.FullLoader)

    db = DatabaseAPI(cfg=config)

    data = db.get_buildings_unit_map()

    #buildings = db.get_buildings()    
    
    print (":")