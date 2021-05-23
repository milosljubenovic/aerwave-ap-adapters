
from flask import Flask, jsonify, request, session

import requests
from db_api import DatabaseAPI
from helpers import otp_gen, send_otp
from flask_cors import CORS
import threading

import yaml
import time
import json

config = yaml.load(open('config.yml', 'rb'), yaml.FullLoader)


db = DatabaseAPI(cfg=config)

app = Flask(__name__)
app.config['SECRET_KEY']  = 'p4*@xZ*s+zW4xHrzgrc2Hk5W6NNv!A'
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

CORS(app, resources={r'/*': {'origins': '*'}})

def validate_schema(keys_list=[], data={}):

    if False in [k in data.keys() for k in keys_list]: return False
    if True in [data[k] == "" for k in keys_list]: return False

    return True



@app.route('/properties', methods=['GET'])
def get_properties():
    res = db.get_properties()
    return jsonify({'properties' : res})


@app.route('/register', methods=['POST'])
def register():

    list_of_fields = ['usr_firstname', 'usr_lastname', 'usr_email', 'uni_id', 'usr_phone', 'usr_stage']
    data = json.loads(request.data.decode('UTF-8'))
    
    if not validate_schema(list_of_fields, data):
        return "Error occured!", 302

    rv = db.register_user(data)

    if rv:
        return 'suc', 200
    else:
        return "Please go to login page!", 302


@app.route('/verify_otp', methods=['POST'])

def verify_otp():

    data = json.loads(request.data.decode('UTF-8'))
    
    if not validate_schema(['otp_number', 'usr_email', 'usr_stage'], data):
        return "Error occured!", 302

    rv = db.verify_otp(usr_mail=data['usr_email'],  otp_no=data['otp_number'].upper(), stage=data['usr_stage'])
    
    if rv:
        return 'Ok OTP', 200
    else:
        return 'woops ;) enter correct one!', 302

@app.route('/subsplans', methods=['GET'])
def get_subplans():

    rv = db.get_subsplans()

    if rv:
        return jsonify({'subplans' : rv}) , 200
    
    return "woops!", 302
        
@app.route('/wlan', methods=['POST'])
def set_wlan():

    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['wlan_ssid','wlan_passphrase', 'subp_id', 'usr_email', 'usr_stage'],data):
        return "Something went wrong", 302


    if db.assign_wlan(data):
        return "Yeah baby!",200
    else:
        return 'Nope!', 302

@app.route('/payments', methods=['POST'])
def get_payments():
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email', 'crd_number', 'crd_fullname', 'crd_month', 'crd_year', 'crd_cvv', 'usr_stage'], data):
        return "Something went wrong", 302

    # TODO: Send data to stripe!
    db_resp = db.update_stage(usr_status=None, usr_email=data['usr_email'],
                    usr_stage=data['usr_stage'])

    if db_resp:
        time.sleep(5)
        return "YAY", 200
    else:
        return "WOOOOOPS!", 302

@app.route('/create_wlan', methods=['POST'])
def create_wlan():
    print ("We have {} wlans to create before yours..." .format(threading.active_count()))
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email'], data):
        return "Something went wrong", 302
    response = None

    user_data = db.get_user_data(usr_email=data['usr_email'])

    ap_init_resp = requests.post(url='http://localhost:9091/create_wlan',
                                json=user_data)

    if ap_init_resp.status_code == 200:
        response = json.loads(ap_init_resp.content.decode('UTF-8'))
        
        static_wlan_data = {'zone_id': user_data['prop_zoneid'],
                            'ap_mac': user_data['ap_mac'],
                            'wlan_id': response['ruckus'][user_data['prop_zoneid']]}


        static_status = requests.post(url='http://localhost:9091/assign_static', 
                                    json=static_wlan_data)
    
    # response = json.loads(ap_init_resp.content.decode('UTF-8'))
    if static_status.status_code == 200:
        response = json.loads(ap_init_resp.content.decode('UTF-8'))
        return response, 200
    
    else:
        return jsonify(msg="Failed..."),302
        
@app.route('/confirmed', methods=['POST'])
def confirmed():
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email'], data):
        return "Something went wrong", 302

    user = db.get_user_data(usr_email=data['usr_email'])
    
    if not user:
        return "Where do you live?! :/", 302

    print (user)

    return "YAY", 200

@app.route('/soft_delete_user', methods=['DELETE'])
def soft_delete_user():
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email'], data):
        return "Something went wrong", 302


    user = db.get_user_data(usr_email=data['usr_email'])
    zone_wlanid_map = db.get_users_wlan_id_per_zone(usr_email=data['usr_email'])

    if user:
        dele = requests.delete(url='http://localhost:9091/delete_wlan',
                    json={'wlan_name' : user['wlan_name'],
                        'ruckus' : zone_wlanid_map})

    rv = db.soft_user_delete(usr_email=data['usr_email'])
    if rv:
        return 'Succ', 200
    else:
        return 'dang Dang dang', 302

@app.route('/hard_delete_user', methods=['DELETE'])
def hard_delete_user():
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email'], data):
        return "Something went wrong", 302

    user = db.get_user_data(usr_email=data['usr_email'])
    zone_wlanid_map = db.get_users_wlan_id_per_zone(usr_email=data['usr_email'])

    if user:
        dele = requests.delete(url='http://localhost:9091/delete_wlan',
                    json={'wlan_name' : user['wlan_name'],
                        'ruckus' : zone_wlanid_map})

    rv = db.hard_user_delete(usr_email=data['usr_email'])
    if rv:
        return jsonify(msg='User {} removed.'.format(data['usr_email'])), 200
    
    else:
        return 'dang Dang dang', 302


@app.route('/login_otp', methods=['POST'])
def login_otp():
    data = json.loads(request.data.decode('UTF-8'))
    if not validate_schema(['usr_email'], data):
        return "Something went wrong", 302

    user = db.get_user(usr_email=data['usr_email'])

    if not user:
        return jsonify(msg="He isn't registered yet!"), 302
    else:
        otp = otp_gen()

        while db.check_existing_otp(otp):
            time.sleep(0.5)
            otp = otp_gen()

        dt = {'usr_email' : user['usr_email'],
            'usr_firstname' : user['usr_firstname'],
            'usr_phone' : user['usr_phonenumber']}

        if not send_otp(config, dt, otp):
            return jsonify(msg="OTP Service failed"), 302
        
        db.update_otp(usr_email=data['usr_email'], otp_no=otp)

        return jsonify(msg=True), 200



if __name__=="__main__":

    app.run(host='0.0.0.0',port='9090')

