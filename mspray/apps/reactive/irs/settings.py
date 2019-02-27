"""Reactive IRS settings module"""
from django.conf import settings

# buffer radius for CommunityHealthWorker bgeom field
MSPRAY_REACTIVE_IRS_CHW_BUFFER = 0.0005
# code prefix for CommunityHealthWorker
MSPRAY_REACTIVE_IRS_CHW_CODE_PREFIX = "CHW-"
# Should we create a location object from a CommunityHealthWorker object?
MSPRAY_REACTIVE_IRS_CREATE_CHW_LOCATION = True
# Which level should the location object be, default is target area
MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL = getattr(
    settings, "MSPRAY_TA_LEVEL", "ta")
# Which level should the location parent object be, default is district
MSPRAY_REACTIVE_IRS_CHW_LOCATION_PARENT_LEVEL = getattr(
    settings, "MSPRAY_DISTRICT_LEVEL", "district")
