# ArcGIS Online Blue-Green Deployments

Utility classes that make it easy to perform Blue-Green data deployments to ArcGIS within data pipelines.

Requires 3 services in ArcGIS Online:
    1. A backing hosted feature service (blue)
    2. A second backing hosted feature service with an identical schema (green)
    3. A hosted feature view that currently points to one of those services.

Given those three services, these code classes will determine which service is currently the live service in use by the hosted feature view and which service is available for use
as the staging service. Additionally, it provides a shortcut to promote the staging service, and an arcpy-based upsert functionality for use against the staging service.

![An animated diagram showing a feature view toggling between two backing services as a software package updates the data](https://github.com/Office-of-Digital-Services/cdt-ods-gis-agolbluegreen/blob/docs/blue_green_data.gif?raw=true)

## What's a Blue-Green Deployment?
Blue-Green Deployments are a DevOps term for having two working copies of a service that toggle between being the live and staging versions of the service (rather than a long-lived staging service that may get out of sync with the long-lived live service). In common usage, when performing an update, the staging version is updated with new code and/or data, the current live version is demoted to staging and the current staging is promoted to be the live service with the new code and data.