import arcgis


try:
    import arcpy
    ARCPY_AVAILABLE = True
except ImportError:
    ARCPY_AVAILABLE = False

BLUE = 1
GREEN = 2

class AGOLBlueGreen():
    def init(self, user_facing_item_id, blue_item_id, green_item_id, portal="https://arcgis.com"):
        self.user_facing_service = UserFacingService(user_facing_item_id)
        self.blue = BackingService(blue_item_id)
        self.green = BackingService(green_item_id)
        self.portal = portal

        self._staging = None
        self._live = None

        self.gis = arcgis.GIS(portal)

    def _determine_staging_live_split(self):
        """
        Figure out which service is currently live and which one is currently staging, and set
        the private variables so that self.staging and self.live point to the correct services.
        Then a user can do something like Truncate/Append on the services
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

class UserFacingService():
    def __init__(self, item_id, gis_connection):
        self.item_id = item_id

        self._gis = gis_connection
        self._service = self._gis.content.get(self.item_id)
        self.properties = self._service.layers[0].properties

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
        


from __future__ import annotations
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, FeatureLayerCollection, Table
import concurrent.futures

# code below via https://github.com/Esri/arcgis-python-api/issues/1731
def swap_view(
    view: FeatureLayerCollection,
    index: int,
    new_source: FeatureLayer | Table,
    future: bool = False,
) -> dict | concurrent.futures.Future:
    """
    Swaps the Data Source Layer with a different parent layer.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    view                   Required FeatureLayerCollection. The view feature layer collection
                           to update.
    ------------------     --------------------------------------------------------------------
    index                  Required int. The index of the layer on the view to replace.
    ------------------     --------------------------------------------------------------------
    new_source             Requred FeatureLayer or Table. The layer to replace the existing
                           source with.
    ------------------     --------------------------------------------------------------------
    future                 Optional Bool. When True, a Future object will be returned else a
                           JSON object.
    ==================     ====================================================================


    """
    keys: list[str] = [
        'currentVersion',
        'id',
        'name',
        'type',
        'displayField',
        'description',
        'copyrightText',
        'defaultVisibility',
        'editingInfo',
        'isDataVersioned',
        'hasContingentValuesDefinition',
        'supportsAppend',
        'supportsCalculate',
        'supportsASyncCalculate',
        'supportsTruncate',
        'supportsAttachmentsByUploadId',
        'supportsAttachmentsResizing',
        'supportsRollbackOnFailureParameter',
        'supportsStatistics',
        'supportsExceedsLimitStatistics',
        'supportsAdvancedQueries',
        'supportsValidateSql',
        'supportsCoordinatesQuantization',
        'supportsLayerOverrides',
        'supportsTilesAndBasicQueriesMode',
        'supportsFieldDescriptionProperty',
        'supportsQuantizationEditMode',
        'supportsApplyEditsWithGlobalIds',
        'supportsMultiScaleGeometry',
        'supportsReturningQueryGeometry',
        'hasGeometryProperties',
        'geometryProperties',
        'advancedQueryCapabilities',
        'advancedQueryAnalyticCapabilities',
        'advancedEditingCapabilities',
        'infoInEstimates',
        'useStandardizedQueries',
        'geometryType',
        'minScale',
        'maxScale',
        'extent',
        'drawingInfo',
        'allowGeometryUpdates',
        'hasAttachments',
        'htmlPopupType',
        'hasMetadata',
        'hasM',
        'hasZ',
        'objectIdField',
        'uniqueIdField',
        'globalIdField',
        'typeIdField',
        'dateFieldsTimeReference',
        'preferredTimeReference',
        'types',
        'templates',
        'supportedQueryFormats',
        'supportedAppendFormats',
        'supportedExportFormats',
        'supportedSpatialRelationships',
        'supportedContingentValuesFormats',
        'supportedSyncDataOptions',
        'hasStaticData',
        'maxRecordCount',
        'standardMaxRecordCount',
        'standardMaxRecordCountNoGeometry',
        'tileMaxRecordCount',
        'maxRecordCountFactor',
        'capabilities',
        'url',
        'adminLayerInfo',
    ]

    if isinstance(new_source, FeatureLayer):
        flc_lyr_info: FeatureLayer = view.layers[index]
    elif isinstance(new_source, Table):
        flc_lyr_info: Table = view.tables[index]

    props: dict = {
        key: new_source.properties[key]
        for key in keys
        if key in new_source.properties
    }

    if new_source._con.token:
        props['url'] = new_source.url + f"?token={new_source._con.token}"
    else:
        props['url'] = new_source.url

    if "viewLayerDefinition" in flc_lyr_info.manager.properties['adminLayerInfo']:
        props['adminLayerInfo'] = {}
        props['adminLayerInfo']['viewLayerDefinition'] = flc_lyr_info.manager.properties['adminLayerInfo']['viewLayerDefinition']
        props['adminLayerInfo']['viewLayerDefinition']['sourceServiceName'] = new_source.manager.properties['name']
        props['adminLayerInfo']['viewLayerDefinition'].pop("sourceId", None)
    if isinstance(new_source, FeatureLayer):
        delete_json: dict = {"layers": [{"id": index}], "tables": []}
        add_json: dict = {"layers": [props]}
    elif isinstance(new_source, Table):
        delete_json: dict = {"layers": [], "tables": [{"id": index}]}
        add_json: dict = {"tables": [props]}
    view.manager.delete_from_definition(delete_json)
    if future:
        return view.manager.add_to_definition(add_json, future=True)
    else:
        return view.manager.add_to_definition(add_json, future=False)
