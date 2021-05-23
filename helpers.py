import math, random
import requests

def otp_gen():

    string = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
    OTP = ""
    length = len(string)
    for i in range(6) :
        OTP += string[math.floor(random.random() * length)]
    return OTP


def send_otp(cfg, dt, otp):
    resp = requests.post(url=cfg['email_service']['url'] + '/send_otp',json=\
        { 'receiver_mail' : dt['usr_email'] ,
        'subject': 'Aerwave OTP', 
        'first_name' : dt['usr_firstname'], 
        'otp' : otp,
        'phone_no' : dt['usr_phone']}
    )

    if resp.status_code == 200:
        return True
    else:
        return False