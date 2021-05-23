
from ruckus_zone import RuckusZone
from db.database_api import DatabaseAPI

class RuckusServer:

    def __init__(self, ruckus_api, db):

        self.ra = ruckus_api
        self.db = db
        self.zones = {}
        self._server_init()
        self.refresh = self._server_init

    
    def _server_init(self):
        zones = self.ra.get_zones()

        for zone in zones:
            self.db.update_zoneid(zone_name=zone['name'], zone_id=zone['id'])
            self.zones[zone['id']] = RuckusZone(ra=self.ra, 
                                                zone_id=zone['id'], 
                                                zone_name=zone['name'],
                                                db=self.db)



