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


        self._determine_staging_live_split()

    def _determine_staging_live_split(self):
        """
        Figure out which service is currently live and which one is currently staging, and set
        the private variables so that self.staging and self.live point to the correct services.
        Then a user can do something like Truncate/Append on the services.

        WARNING - this function may not work as intended. I'm not sure that we get the item ID of the backing service
        from the properties dictionary. Worth another look
        """
        live_service_id = self.user_facing_service.backing_service.itemid
        if live_service_id == self.blue.itemid:
            self._live = BLUE
            self._staging = GREEN
        elif live_service_id == self.green.itemid:
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
        elif self._live == GREEN:
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
        layer_id = self.user_facing_service.layer_id
        py_layer_id = 0  # right now this will always be 0 - the code only supports layers with one service, so it'll always be the first
        self.user_facing_service.switch_to(self.staging.itemid, layer_id, py_layer_id)

        self._determine_staging_live_split()  # run the full determination rather than a manual split. This makes sure that we're synced up with the API in the event of a silent failure


class UserFacingService():
    def __init__(self, itemid, gis_connection):
        self.itemid = itemid

        self._gis = gis_connection
        self._service = self._gis.content.get(self.itemid)
        self._view = arcgis.features.FeatureLayerCollection.fromitem(self._service) # this is what we need to use
        self._manager = self._view.manager
        self.properties = self._service.layers[0].properties

    @property
    def layer_id(self):
        return self.backing_service.layers[0].properties["id"]  # this always uses the first layer, but our swapping doesn't support multiple right now, so this should be OK.

    @property
    def backing_service(self):
        # TODO: Is this always safe to take the first item??
        return self._service.related_items(rel_type="Service2Data")[0]

    def switch_to(self, agol_service_id, agol_layer_id, py_layer_id=0):

        # how do we get that index below?
        update_layer = self._gis.content.get(agol_service_id).layers[py_layer_id]

        # need to figure out how we get and pass the indexes below
        swap_view(self._manager, self._view, agol_layer_id, py_layer_id, update_layer)


class BackingService():

    def __init__(self, itemid):

        self.itemid = itemid

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
        

