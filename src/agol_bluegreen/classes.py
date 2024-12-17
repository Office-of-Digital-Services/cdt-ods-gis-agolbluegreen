import arcgis

from .support import swap_view

try:
    import arcpy
    ARCPY_AVAILABLE = True
except ImportError:
    ARCPY_AVAILABLE = False

BLUE = 1
GREEN = 2

class AGOLBlueGreen:
    def __init__(self, user_facing_item_id, blue_item_id, green_item_id, gis_connection=arcgis.GIS("pro")):
        self.gis = gis_connection

        self.user_facing_service = UserFacingService(user_facing_item_id, gis_connection)
        self.blue = BackingService(blue_item_id)
        self.green = BackingService(green_item_id)

        self._staging = None
        self._live = None


    def _determine_staging_live_split(self):
        """
        Figure out which service is currently live and which one is currently staging, and set
        the private variables so that self.staging and self.live point to the correct services.
        Then a user can do something like Truncate/Append on the services.

        WARNING - this function may not work as intended. I'm not sure that we get the item ID of the backing service
        from the properties dictionary. Worth another look
        """
        live_service_id = self.user_facing_service.properties.serviceItemId
        if live_service_id == self.blue.item_id:
            self._live = BLUE
            self._staging = GREEN
        elif live_service_id == self.green.item_id:
            self._live = GREEN
            self._staging = BLUE
        else:
            raise ValueError(f"Provided view does not use one of the two provided backing services as its live service. Cannot proceed safely (don't want to destroy existing view). Item ID of live service in view is {live_service_id}")

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

    def upsert(self):
        """
            We need a workflow here that calls a truncate and append, but truncate doesn't work if the layers we run
            it against have sync enabled, so we need a fallback that maybe has a flag empty_sync_enabled? or something
            and then it uses an alternative approach to delete the data from the table anyway. Then we can use append
            as normal. We may be able to append over the top, but that seems risky.
        :return:
        """
        pass

    def promote_staging(self):
        # WARNING - THIS REQUIRES THAT WE FIGURE OUT OUR LAYER IDS, ETC
        self.user_facing_service.switch_to(self.staging)


class UserFacingService():
    def __init__(self, item_id, gis_connection):
        self.item_id = item_id

        self._gis = gis_connection
        self._service = self._gis.content.get(self.item_id)
        self._view = arcgis.features.FeatureLayerCollection.fromitem(self._service) # this is what we need to use
        self._manager = self._view.manager
        self.properties = self._service.layers[0].properties

    def switch_to(self, id):

        # how do we get that index below?
        update_layer = self._gis.content.get(id).layers[0]

        # need to figure out how we get and pass the indexes below
        #swap_view(view.manager, view, 0, 1, update_layer)


class BackingService():

    def __init__(self, item_id):

        self.item_id = item_id

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
        

