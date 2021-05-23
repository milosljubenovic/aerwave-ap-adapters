# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Building(Base):
    __tablename__ = 'buildings'

    bul_id = Column(INTEGER(10), primary_key=True)
    bul_name = Column(String(255))
    bul_units = Column(String(45))
    pro_id = Column(INTEGER(10), nullable=False, index=True)


class City(Base):
    __tablename__ = 'city'

    cit_id = Column(INTEGER(10), primary_key=True)
    cit_name = Column(String(255))
    cit_zip = Column(String(45))


class ProStatu(Base):
    __tablename__ = 'pro_status'

    pros_id = Column(INTEGER(10), primary_key=True)
    pros_name = Column(String(45))


class Role(Base):
    __tablename__ = 'roles'

    rol_id = Column(INTEGER(10), primary_key=True)
    rol_name = Column(String(255))


class RuckusWg24(Base):
    __tablename__ = 'ruckus_wg24'

    rwg_24_id = Column(INTEGER(11), primary_key=True)
    wg24_name = Column(String(255))
    wg24_id = Column(String(255))
    rwl_id = Column(INTEGER(11))

    rwls = relationship('RuckusWlan', secondary='rwl_rwg24')


class RuckusWg50(Base):
    __tablename__ = 'ruckus_wg50'

    rwg_50_id = Column(INTEGER(11), primary_key=True)
    wg50_name = Column(String(255))
    wg50_id = Column(String(255))
    rwl_id = Column(INTEGER(11))

    rwls = relationship('RuckusWlan', secondary='rwl_rwg50')


class State(Base):
    __tablename__ = 'state'

    sta_id = Column(INTEGER(10), primary_key=True)
    sta_name = Column(String(255))


class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'

    subp_id = Column(INTEGER(10), primary_key=True)
    subp_name = Column(String(255))
    subp_price = Column(String(45))
    subp_duration = Column(INTEGER(11))
    subp_duration_unit = Column(String(100))
    subp_speed = Column(String(105))
    subp_unlimited = Column(INTEGER(11))
    subp_description = Column(Text)


class WlanDhcpPool(Base):
    __tablename__ = 'wlan_dhcp_pool'

    wdp_id = Column(INTEGER(10), primary_key=True)
    wdp_description = Column(String(255))
    wdp_subnetnetwork_ip = Column(String(45))
    wdp_subnetmask = Column(String(45))
    wdp_pool_start_ip = Column(String(45))
    wdp_pool_end_ip = Column(String(45))
    wdp_primarydns_ip = Column(String(45))
    wdp_secondarydns_ip = Column(String(45))
    wdp_leasetime_hours = Column(INTEGER(11))
    wdp_leasetime_minutes = Column(INTEGER(11))


class WlanFilteringPolouse(Base):
    __tablename__ = 'wlan_filtering_police'

    wfp_id = Column(INTEGER(10), primary_key=True)
    wfp_blockedurls = Column(String(255))
    wfp_primaryip = Column(String(225))
    wfp_secondaryip = Column(String(255))


class Property(Base):
    __tablename__ = 'property'

    pro_id = Column(INTEGER(10), primary_key=True, unique=True)
    pro_address = Column(String(255))
    pros_id = Column(ForeignKey('pro_status.pros_id'), nullable=False, index=True)
    pro_lastmodified = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    pro_zone_name = Column(String(255))
    pro_zone_id = Column(String(255))

    pros = relationship('ProStatu')


class Unit(Base):
    __tablename__ = 'units'

    uni_id = Column(INTEGER(10), primary_key=True)
    uni_number = Column(String(45))
    uni_floor = Column(String(45))
    uni_ap_mac = Column(String(100))
    uni_vlan = Column(INTEGER(10), nullable=False)
    bul_id = Column(ForeignKey('buildings.bul_id'), nullable=False, index=True)
    usr_id = Column(INTEGER(11))
    uni_zoneid = Column(String(255))
    rwg_24_id = Column(ForeignKey('ruckus_wg24.rwg_24_id'), index=True)
    rwg_50_id = Column(ForeignKey('ruckus_wg50.rwg_50_id'), index=True)

    bul = relationship('Building')
    rwg_24 = relationship('RuckusWg24')
    rwg_50 = relationship('RuckusWg50')


class ClientEvent(Base):
    __tablename__ = 'client_events'

    cle_id = Column(INTEGER(10), primary_key=True)
    cle_macaddres = Column(String(255))
    cle_event = Column(String(255))
    uni_id = Column(ForeignKey('units.uni_id'), nullable=False, index=True)

    uni = relationship('Unit')


class User(Base):
    __tablename__ = 'users'

    usr_id = Column(INTEGER(10), primary_key=True)
    usr_firstname = Column(String(255))
    usr_lastname = Column(String(255))
    usr_email = Column(String(255), unique=True)
    usr_phonenumber = Column(String(255))
    usr_status = Column(INTEGER(11))
    usr_deleted = Column(INTEGER(11))
    usr_deldate = Column(TIMESTAMP)
    usr_stage = Column(String(255))
    usr_device = Column(String(45))
    subp_id = Column(ForeignKey('subscription_plans.subp_id'), index=True)
    uni_id = Column(ForeignKey('units.uni_id'), index=True)

    subp = relationship('SubscriptionPlan')
    uni = relationship('Unit')


class BillingInfo(Base):
    __tablename__ = 'billing_info'

    bil_id = Column(INTEGER(10), primary_key=True)
    bil_number = Column(INTEGER(11))
    bil_adress = Column(String(255))
    cit_id = Column(ForeignKey('city.cit_id'), nullable=False, index=True)
    sta_id = Column(ForeignKey('state.sta_id'), nullable=False, index=True)
    usr_id = Column(ForeignKey('users.usr_id'), nullable=False, index=True)

    cit = relationship('City')
    sta = relationship('State')
    usr = relationship('User')


class EmergancyWlan(Base):
    __tablename__ = 'emergancy_wlan'

    emw_id = Column(INTEGER(10), primary_key=True)
    emw_aplist = Column(String(255))
    emw_status = Column(String(255))
    emw_comment = Column(Text)
    usr_id = Column(ForeignKey('users.usr_id'), index=True)

    usr = relationship('User')


class OnetimePassword(Base):
    __tablename__ = 'onetime_password'

    otp_id = Column(INTEGER(10), primary_key=True)
    otp_number = Column(String(45), nullable=False)
    otp_confirmed = Column(INTEGER(11))
    otp_created = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    otp_used = Column(INTEGER(11))
    otp_deleted = Column(TIMESTAMP)
    usr_email = Column(ForeignKey('users.usr_email'), nullable=False, index=True)

    user = relationship('User')


class SubscriptionHistory(Base):
    __tablename__ = 'subscription_history'

    sub_id = Column(INTEGER(10), primary_key=True)
    sub_startdate = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    sub_enddate = Column(Date)
    sub_lastmodefieddate = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    sub_paymentdate = Column(TIMESTAMP)
    sub_paymentstatus = Column(String(245))
    sub_active = Column(INTEGER(11))
    usr_id = Column(ForeignKey('users.usr_id'), index=True)

    usr = relationship('User')


class UserDevice(Base):
    __tablename__ = 'user_devices'

    usrd_id = Column(INTEGER(10), primary_key=True)
    usrd_macaddres = Column(String(105))
    usrd_hostname = Column(String(255))
    usrd_ostype = Column(String(255))
    usrd_status = Column(String(235))
    usrd_created = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    usr_id = Column(ForeignKey('users.usr_id'), nullable=False, index=True)

    usr = relationship('User')


class UsrRole(Base):
    __tablename__ = 'usr_roles'

    usr_rol_id = Column(INTEGER(10), primary_key=True)
    usr_id = Column(ForeignKey('users.usr_id'), nullable=False, index=True)
    rol_id = Column(ForeignKey('roles.rol_id'), nullable=False, index=True)

    rol = relationship('Role')
    usr = relationship('User')


class Wlan(Base):
    __tablename__ = 'wlan'

    wlan_id = Column(INTEGER(10), primary_key=True, unique=True)
    wlan_ruckusid = Column(String(255))
    wlan_ssid = Column(String(255))
    wlan_passphrase = Column(String(255))
    wlan_vlan = Column(INTEGER(11))
    wlan_instaces = Column(INTEGER(11))
    usr_id = Column(ForeignKey('users.usr_id'), nullable=False, index=True)
    wfp_id = Column(ForeignKey('wlan_filtering_police.wfp_id'), nullable=False, index=True)
    wdp_id = Column(ForeignKey('wlan_dhcp_pool.wdp_id'), index=True)

    usr = relationship('User')
    wdp = relationship('WlanDhcpPool')
    wfp = relationship('WlanFilteringPolouse')


class RuckusWlan(Base):
    __tablename__ = 'ruckus_wlan'

    rwl_id = Column(INTEGER(11), primary_key=True, unique=True)
    wlan_id = Column(ForeignKey('wlan.wlan_id'), index=True)
    rwl_ruckid = Column(String(255))
    rwl_zoneid = Column(String(45))

    wlan = relationship('Wlan')


t_rwl_rwg24 = Table(
    'rwl_rwg24', metadata,
    Column('rwl_id', ForeignKey('ruckus_wlan.rwl_id'), primary_key=True),
    Column('rwg_24_id', ForeignKey('ruckus_wg24.rwg_24_id'), index=True)
)


t_rwl_rwg50 = Table(
    'rwl_rwg50', metadata,
    Column('rwl_id', ForeignKey('ruckus_wlan.rwl_id'), primary_key=True),
    Column('rwg_50_id', ForeignKey('ruckus_wg50.rwg_50_id'), index=True)
)
