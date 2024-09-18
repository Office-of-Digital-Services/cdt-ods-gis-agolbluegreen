import arcgis


try:
    import arcpy
    ARCPY_AVAILABLE = True
except ImportError:
    ARCPY_AVAILABLE = False

BLUE = 1
GREEN = 2

class AGOLBlueGreen():
    def init(self, user_facing_item_id, blue_item_id, green_item_id):
        self.user_facing_service = UserFacingService(user_facing_item_id)
        self.blue = BackingService(blue_item_id)
        self.green = BackingService(green_item_id)

        self._staging = None
        self._live = None

    def _determine_staging_live_split(self):
        """
        Figure out which service is currently live and which one is currently staging, and set
        the private variables so that self.staging and self.live point to the correct services.
        Then a user can do something like Truncate/Append on the services
        """

    @property
    def staging(self):
        if self._staging == BLUE:
            return self.blue
        elif self._staging == GREEN:
            return self.green
        else:
            return None
    
    @property
    def live(self):
        if self._live == BLUE:
            return self.blue
        elif self._staging == GREEN:
            return self.green
        else:
            return None

class UserFacingService():
    pass


class BackingService():

    def upsert(self, path):
        """
            Execute a truncate/append on the service, appending the rows from the dataset found at the
            provided path.

            As currently implemented, requires arcpy, though an arcgis package-only implementation is doable (with fewer GP checks)

        Args:
            path (_type_): _description_
        """

        if not ARCPY_AVAILABLE:
            raise NotImplementedError("The upsert method this package uses currently requires arcpy. You'll need to empty and reload data \
                                      via another method for now.")