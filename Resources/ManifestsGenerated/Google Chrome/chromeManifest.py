#!/usr/bin/python
# # -*- coding: utf-8 -*-

import plistlib
import os
from subprocess import call
import datetime


manifestpath = os.path.abspath('/Applications/Google Chrome.app/Contents/Resources/com.google.Chrome.manifest/Contents/Resources/com.google.Chrome.manifest')
manifest = plistlib.readPlist(manifestpath)
Localizable = os.path.abspath('/Applications/Google Chrome.app/Contents/Resources/com.google.Chrome.manifest/Contents/Resources/en.lproj/Localizable.strings')
call(["/usr/bin/plutil", "-convert", "xml1", Localizable])
strings = plistlib.readPlist(Localizable)
chromeinfo = plistlib.readPlist(
    os.path.abspath("/Applications/Google Chrome.app/Contents/Info.plist"))

for dict in manifest["pfm_subkeys"]:
    dict["pfm_title"] = strings[dict["pfm_name"]+".pfm_title"]

    # UPDATE
    # Put the "raw" description in a new key pfm_description_reference which will hold the full description of a key
    dict["pfm_description_reference"] = strings[dict["pfm_name"]+".pfm_description"].strip('\n')

    # UPDATE
    # Only set the string before the first double newlines to the actual description, as this seem to be how they consistantly structure it.
    description = strings[dict["pfm_name"]+".pfm_description"].split('\n\n')[0]

    # UPDATE
    # Remove pfm_targets as it's only user-managed anyway and it will be read from the manifest root
    try:
        del dict['pfm_targets']
    except KeyError:
        pass

    # UPDATE
    # Loop through each pfm_range_list when available and add the descriptions for the keys.
    if 'pfm_range_list' in dict:
        description_new = description
        range_list = dict['pfm_range_list']
        range_list_titles = []
        for item in range_list:
            for line in description.splitlines():
                if line.startswith(str(item) + ' '):
                    range_list_titles.append(line.split(' - ')[1])
                    description_new = description_new.replace(line + '\n','')
        
        if range_list_titles and len(range_list_titles) == len(range_list):
            dict['pfm_range_list_titles'] = range_list_titles
            if description_new:
                description = description_new

    # UPDATE
    # Set the description last as it might have been modified
    dict["pfm_description"] = description.strip('\n')

def payloadSubkey(name, typeString, title, description, description_reference=None, default=None):
    payloadSubkey = {}
    payloadSubkey["pfm_name"] = str(name)
    payloadSubkey["pfm_type"] = str(typeString)
    payloadSubkey["pfm_title"] = str(title)
    payloadSubkey["pfm_description"] = str(description)
    if description_reference is not None:
        payloadSubkey["pfm_description_reference"] = description_reference
    if default is not None:
        payloadSubkey["pfm_default"] = default
    return payloadSubkey

# UPDATE
# This is unfortunately still required, I'm working on making this simpler in the manifests, but currently these six dicts are required to be at the top of each manifest.
subkeys = manifest["pfm_subkeys"]

payloadVersion = payloadSubkey("PayloadOrganization", "string", "Payload Organization", "This value describes the issuing organization of the profile, as displayed to the user.", "Optional. A human-readable string containing the name of the organization that provided the profile. The payload organization for a payload need not match the payload organization in the enclosing profile.")
payloadVersion["pfm_require"] = "always"
subkeys.append(payloadVersion)

payloadVersion = payloadSubkey("PayloadVersion", "integer", "Payload Version", "The version of the whole configuration profile.", "The version number of the individual payload. A profile can consist of payloads with different version numbers. For example, changes to the VPN software in iOS might introduce a new payload version to support additional features, but Mail payload versions would not necessarily change in the same release.", 1)
payloadVersion["pfm_require"] = "always"
subkeys.append(payloadVersion)

payloadUUID = payloadSubkey("PayloadUUID", "string", "Payload UUID", "Unique identifier for the payload (format 01234567-89AB-CDEF-0123-456789ABCDEF).", "A globally unique identifier for the payload. The actual content is unimportant, but it must be globally unique. In macOS, you can use uuidgen to generate reasonable UUIDs.", "")
payloadUUID["pfm_require"] = "always"
payloadUUID["pfm_format"] = "^[0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12}$"
subkeys.append(payloadUUID)

payloadType = payloadSubkey("PayloadType", "string", "Payload Type", "The type of the payload, a reverse dns string.", "The payload type.", "com.google.Chrome")
payloadType["pfm_require"] = "always"
subkeys.append(payloadType)

payloadIdentifier = payloadSubkey("PayloadIdentifier", "string", "Payload Identifier", "A unique identifier for the payload, dot-delimited.  Usually root PayloadIdentifier+subidentifier.", "A reverse-DNS-style identifier for the specific payload. It is usually the same identifier as the root-level PayloadIdentifier value with an additional component appended.", "com.google.Chrome")
payloadIdentifier["pfm_require"] = "always"
subkeys.append(payloadIdentifier)

payloadDisplayName = payloadSubkey("PayloadDisplayName", "string", "Payload Display Name", "Name of the payload.", "A human-readable name for the profile payload. This name is displayed on the Detail screen. It does not have to be unique.", "Google Chrome")
payloadDisplayName["pfm_require"] = "always"
subkeys.append(payloadDisplayName)

payloadDescription = payloadSubkey("PayloadDescription", "string", "Payload Description", "Description of the payload.", "Optional. A human-readable description of this payload. This description is shown on the Detail screen.", "Configures Google Chrome settings")
subkeys.append(payloadDescription)

manifest["pfm_subkeys"] = subkeys

newmanifest = manifest
#newmanifest["pfm_version"] = chromeinfo["CFBundleShortVersionString"]
newmanifest["pfm_title"] = "Google Chrome"
newmanifest["pfm_description"] = "Google Chrome Managed Settings"
newmanifest["pfm_app_url"] = "https://enterprise.google.com/chrome/chrome-browser/"

# UPDATE
# This key has changed from pfm_documentation to pfm_documentation_url
newmanifest["pfm_documentation_url"] = "http://dev.chromium.org/administrators/policy-list-3"
newmanifest["pfm_format_version"] = 1

# UPDATE
# Removed .isoformat() as this key needs to be a true date and not a string.
newmanifest["pfm_last_modified"] = datetime.datetime.now()

# UPDATE
# Add pfm_targers at the root
newmanifest["pfm_targets"] = ["user", "system"]

# UPDATE
# Add pfm_unique
newmanifest["pfm_unique"] = False

# UPDATE
# add pfm_platforms
newmanifest["pfm_platforms"] = ["macOS"]

# UPDATE
# Add pfm_interaction
newmanifest["pfm_interaction"] = "combined"

plistlib.writePlist(manifest,
    os.path.abspath(os.path.expanduser("~/Desktop/GoogleChrome_{}.plist".format(chromeinfo["CFBundleShortVersionString"]))))
