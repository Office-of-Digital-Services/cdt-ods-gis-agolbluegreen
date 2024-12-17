blue_id = "593eda518c9a4ca0ac2f413085066359"
green_id = "fcf5e73dcdcc4131adc3e094fb4ea95b"
view_id = "4acc926fcd1a4c8792d5435964451b73"

import arcgis
from arcgis import features
import os
from agol_bluegreen import AGOLBlueGreen




def test_basic(id=green_id):
    gis = arcgis.GIS("pro")
    view_item = gis.content.get(view_id)
    view = arcgis.features.FeatureLayerCollection.fromitem(view_item)
    update_layer = gis.content.get(id).layers[0]
    swap_view(view.manager, view,0, 1, update_layer)

    # service = AGOLBlueGreen(view_id, blue_id, green_id)

def test_bluegreen():
    bluegreen = AGOLBlueGreen(view_id, blue_id, green_id)
    pass


#service.upsert(my_new_features)  # empty staging service and insert new records
#service.promote_staging()  # - swap the services - demote live and promote staging


#import arcpy_metadata as md
#metadata = md.MetadataEditor(path_to_some_feature_class, loglevel="DEBUG")

#from datetime import date
#today = date.today()
#metadata.last_update = today

#metadata.point_of_contact.contact_name = "Nick Santos"
#metadata.point_of_contact.email = "nick.santos@state.ca.gov"