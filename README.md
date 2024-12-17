# ArcGIS Online Blue-Green Deployments

Utility classes that make it easy to perform Blue-Green data deployments to ArcGIS within data pipelines.

Requires 3 services in ArcGIS Online:
1. A backing hosted feature service (blue)
2. A second backing hosted feature service with an identical schema (green)
3. A hosted feature view that currently points to one of those services.

Given those three services, these code classes will determine which service is currently the live service in use by the hosted feature view and which service is available for use
as the staging service. Additionally, it provides a shortcut to promote the staging service, and an arcpy-based upsert functionality for use against the staging service.

![An animated diagram showing a feature view toggling between two backing services as a software package updates the data](/docs/blue_green_data.gif)

## What's a Blue-Green Deployment?
Blue-Green Deployments are a DevOps term for having two working copies of a service that toggle between being the live and staging versions of the service (rather than a long-lived staging service that may get out of sync with the long-lived live service). In common usage, when performing an update, the staging version is updated with new code and/or data, the current live version is demoted to staging and the current staging is promoted to be the live service with the new code and data.

# Status
This library is currently alpha status with API functionality likely to change, possibly in breaking ways. You *may*
start to use it, but please get in touch with us using either the Discussions tab here or by using the "Contact Us" link at the bottom of https://gis.data.ca.gov
to let us know you're using it, and we'll keep you updated on breaking changes.

# Installation

Currently, installation involves downloading the repository and unzipping it into a folder on your computer (where it will
live) - then in a command prompt, activate your Python environment and navigate to the folder where you unzipped the
repository. Then run either `python -m pip install --editable .` if you want to be able to download repository updates
and overwrite the folder, or a standard `python -m pip install .` if you want to do an uninstall before future updates.

Alternatively, newer versions of pip should be able to install it directly from the GitHub URL with the command
`python -m pip install agol_bluegreen@git+https://github.com/Office-of-Digital-Services/cdt-ods-gis-agolbluegreen/`

# Requirements
Requires Python 3.11+ and the `arcgis` package. It does not require a local installation of ArcGIS Desktop or Server,
but the default authentication uses ArcGIS Pro's authentication. To authenticate with portal differently, connect in
your own code and pass the GIS object as the fourth argument to the AGOLBlueGreen constructor (see example below).

# Usage
Usage is currently simple. If you have three service IDs - 2 hosted feature layers and a view that uses one of those
feature layers but not the other:

```python
from agol_bluegreen import AGOLBlueGreen

view_id="4acc926fcd1a4c8792d5435964451b73" # for example
blue_service_id = ""  # also an arcgis ID, but to a hosted feature layer
green_service_id = "" # same

# this next line will load up the view and figure out which of the two service IDs it currently points to
bluegreen = AGOLBlueGreen(view_id, blue_service_id, green_service_id)  # fourth parameter is optional arcgis.GIS connection - it defaults to creating its own using "pro" authentication - your signed in ArcGIS Pro user

print(bluegreen.live.itemid)  # prints out whichever of the two service IDs the view currently uses
print(bluegreen.staging.itemid)  # prints out whichever of the two service IDs isn't in use
# do other work here

bluegreen.promote_staging()  # updates the view, swapping the source to the bluegreen.staging service. It updates its attributes, so bluegreen.live will now return what used to be bluegreen.staging (e.g. it maintains consistency)
```

# Future plans
We plan to support upsert-based workflows so that you can run an upsert on the bluegreen object, and it will correctly
update the current staging layer. Then when you're done, you can call `promote_staging` to swap the source. Currently
you'll need to run your upsert manually on the service in `bluegreen.staging.itemid`

We'll also add full API docs and tests, but that'll be further out.