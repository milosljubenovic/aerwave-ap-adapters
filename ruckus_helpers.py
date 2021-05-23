
def generate_wlan_data(wlan_name,
                        ssid,
                        downlink_rate,
                        fp=None,
                        passphrase='',
                        description='Aerwave User WLAN',
                        vlan=1):
    data = {
        'name': wlan_name,
        'ssid': ssid,
        'description': description,
        'vlan': {
            'accessVlan': vlan,
        },
        "advancedOptions": {
            "mgmtTxRateMbps": "6 mbps",
        },
    }
    if downlink_rate:
        data['advancedOptions']['downlinkEnabled'] = True
        data['advancedOptions']['downlinkRate'] = min(int(downlink_rate), 200)
    else:
        data['advancedOptions']['downlinkEnabled'] = False
    # encryption
    if passphrase:
        data['encryption'] = {
            'method': 'WPA2',
            'algorithm': 'AES',
            'passphrase': passphrase,
            'mfp': "disabled",
            'support80211rEnabled': True,
            'mobilityDomainId': 3
        }
    else:
        data['encryption'] = {
            'method': 'None',
            'mfp': "disabled",
            'support80211rEnabled': True,
            'mobilityDomainId': 3
        }
    # filtering policy
    if fp is not None:
        # Disabled due licensing issue
        data['advancedOptions']['urlFilteringPolicyEnabled'] = False
        data['advancedOptions']['urlFilteringPolicyId'] = ''
        if fp['dns_enabled']:
            data['dnsServerProfile'] = {
                'id': fp['dns_id'],
                'name': fp['dns_name']
            }
    return data.copy()