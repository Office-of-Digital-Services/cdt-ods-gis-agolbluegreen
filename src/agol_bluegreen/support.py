import os

import arcgis
from arcgis import features

def swap_view(manager,
              view,
              py_index,
              esri_index,
              new_source,
              future=False,
              ):
    """
    Modified version of Esri's built-in swap_view function that can handle an item that's not the 0-index layer (e.g.
    a view with one layer that has a layer id of 1 or 2).

    In practice, we're going to wrap this function, but this keeps it very close to Esri's builtin function
    so that we can update it with new versions of the API.

    Usage:

        view_item = gis.content.get(view_id)
        view = arcgis.features.FeatureLayerCollection.fromitem(view_item)
        update_layer = gis.content.get(update_layer_id).layers[0]
        swap_view(view.manager, view,0, 1, update_layer)

    Swaps the Data Source Layer with a different parent layer.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    view                   Required FeatureLayerCollection. The view feature layer collection
                           to update.
    ------------------     --------------------------------------------------------------------
    py_index               Required int. The Python 0-based index of the layer on the view to replace.
                            Basically, where in the python list of layers for this view is the layer
                            you want to replace? It must be in the same data source as the others then.
    ------------------     --------------------------------------------------------------------
    esri_index             Required int. The Esri numerical-index of the layer on the view to replace.
                            This is the layer ID that is in feature service URLs, in ArcGIS Pro, etc.
                            It often is not the same as the python index, which is why this function
                            separates it out.
    ------------------     --------------------------------------------------------------------
    new_source             Requred FeatureLayer or Table. The layer to replace the existing
                           source with.
    ------------------     --------------------------------------------------------------------
    future                 Optional Bool. When True, a Future object will be returned else a
                           JSON object. This parameter is only honored for the ArcGIS Online
                           platform.
    ==================     ====================================================================

    :return: dict | concurrent.futures.Future
    """
    keys: list[str] = [
        "currentVersion",
        "id",
        "name",
        "type",
        "displayField",
        "description",
        "copyrightText",
        "defaultVisibility",
        "editingInfo",
        "isDataVersioned",
        "hasContingentValuesDefinition",
        "supportsAppend",
        "supportsCalculate",
        "supportsASyncCalculate",
        "supportsTruncate",
        "supportsAttachmentsByUploadId",
        "supportsAttachmentsResizing",
        "supportsRollbackOnFailureParameter",
        "supportsStatistics",
        "supportsExceedsLimitStatistics",
        "supportsAdvancedQueries",
        "supportsValidateSql",
        "supportsCoordinatesQuantization",
        "supportsLayerOverrides",
        "supportsTilesAndBasicQueriesMode",
        "supportsFieldDescriptionProperty",
        "supportsQuantizationEditMode",
        "supportsApplyEditsWithGlobalIds",
        "supportsMultiScaleGeometry",
        "supportsReturningQueryGeometry",
        "hasGeometryProperties",
        "geometryProperties",
        "advancedQueryCapabilities",
        "advancedQueryAnalyticCapabilities",
        "advancedEditingCapabilities",
        "infoInEstimates",
        "useStandardizedQueries",
        "geometryType",
        "minScale",
        "maxScale",
        "extent",
        "drawingInfo",
        "allowGeometryUpdates",
        "hasAttachments",
        "htmlPopupType",
        "hasMetadata",
        "hasM",
        "hasZ",
        "objectIdField",
        "uniqueIdField",
        "globalIdField",
        "typeIdField",
        "dateFieldsTimeReference",
        "preferredTimeReference",
        "types",
        "templates",
        "supportedQueryFormats",
        "supportedAppendFormats",
        "supportedExportFormats",
        "supportedSpatialRelationships",
        "supportedContingentValuesFormats",
        "supportedSyncDataOptions",
        "hasStaticData",
        "maxRecordCount",
        "standardMaxRecordCount",
        "standardMaxRecordCountNoGeometry",
        "tileMaxRecordCount",
        "maxRecordCountFactor",
        "capabilities",
        "url",
        "adminLayerInfo",
    ]
    if isinstance(new_source, features.FeatureLayer):
        flc_lyr_info: features.FeatureLayer = view.layers[py_index]
    elif isinstance(new_source, features.Table):
        flc_lyr_info: features.Table = view.tables[py_index]
    props: dict = {
        key: new_source.properties[key]
        for key in keys
        if key in new_source.properties
    }
    if new_source._con.token:
        props["url"] = new_source.url + f"?token={new_source._con.token}"
    else:
        props["url"] = new_source.url
    if "viewLayerDefinition" in flc_lyr_info.manager.properties["adminLayerInfo"]:
        props["adminLayerInfo"] = {}
        props["adminLayerInfo"]["viewLayerDefinition"] = (
            flc_lyr_info.manager.properties["adminLayerInfo"]["viewLayerDefinition"]
        )
        props["adminLayerInfo"]["viewLayerDefinition"]["sourceServiceName"] = (
            os.path.basename(os.path.dirname(os.path.dirname(new_source.url)))
        )
        props["adminLayerInfo"]["viewLayerDefinition"].pop("sourceId", None)
    if isinstance(new_source, features.FeatureLayer):
        delete_json: dict = {"layers": [{"id": esri_index}], "tables": []}
        add_json: dict = {"layers": [props]}
    elif isinstance(new_source, features.Table):
        delete_json: dict = {"layers": [], "tables": [{"id": esri_index}]}
        add_json: dict = {"tables": [props]}
    view.manager.delete_from_definition(delete_json)
    if future and manager._gis._is_arcgisonline:
        return view.manager.add_to_definition(add_json, future=True)
    else:
        if future and manager._gis._is_arcgisonline == False:
            print(
                "Enterprise does not support asynchronous view swap, using synchronous method."
            )
        return view.manager.add_to_definition(add_json, future=False)