#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import plistlib
import re
import datetime

brave_domain = "com.brave.Browser"
chrome_domain = "com.google.Chrome"
manifest_replacements = {
    "pfm_app_url": "https://brave.com/",
    "pfm_description": "Brave Browser Managed Settings",
    "pfm_domain": "com.brave.Browser",
    "pfm_title": "Brave Browser",
    "pfm_documentation_url": "https://support.brave.com/hc/en-us/articles/360039248271-Group-Policy",
}
manifests_subfolder = os.path.join( "Manifests", "ManagedPreferencesApplications" )

def main():
    # Work from the script's own folder
    script_folder_path = os.path.dirname( os.path.realpath( __file__ ) )
    os.chdir( script_folder_path )

    # Get path to repository root
    popen_args = [ "git", "rev-parse", "--show-toplevel" ]
    repository_root_process: subprocess.Popen = subprocess.Popen( popen_args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    ( stdout, stderr ) = repository_root_process.communicate()

    if repository_root_process.returncode != 0:
        print( "Getting repo root path errored out:\n" + stdout )
        exit( 1 )

    repository_root_path = stdout.decode( sys.stdout.encoding ).strip()
    chrome_manifest_path = os.path.join( repository_root_path, manifests_subfolder, chrome_domain + ".plist" )

    # Load the Chrome manifest
    try:
        chrome_manifest_file = open( chrome_manifest_path, 'rb' )
        manifest = plistlib.load( chrome_manifest_file )
    except Exception as error:
        print( "Could not load " + chrome_manifest_path )
        print( "Exception message: " + str( error ) )
        exit( 2 )
    chrome_manifest_file.close()

    # Root replacements
    for subkey in manifest_replacements:
        manifest[ subkey ] = manifest_replacements[ subkey ]

    subkeys = manifest[ "pfm_subkeys" ]

    # Known subkey replacements
    known_top_subkeys = [
        {
            "name": "PayloadDescription",
            "property": "pfm_default",
        },
        {
            "name": "PayloadDisplayName",
            "property": "pfm_default"
        },
        { 
            "name": "PayloadIdentifier",
            "property": "pfm_default",
            "old_string": chrome_domain,
            "new_string": brave_domain,
        },
        {
            "name": "PayloadType",
            "property": "pfm_default",
            "old_string": chrome_domain,
            "new_string": brave_domain,
        },
    ]
    for known_top_subkey in known_top_subkeys:
        replace_in_known_top_key( subkeys, known_top_subkey )

    # General replacement in keys
    manifest[ "pfm_subkeys" ] = replace_in_keys_recursively( subkeys )

    # Add domain specific keys
    domain_specific_keys_path = os.path.join( script_folder_path, brave_domain + "-specific.plist" )
    domain_specific_keys = None
    try:
        domain_specific_keys_file = open( domain_specific_keys_path, 'rb' )
        domain_specific_keys = plistlib.load( domain_specific_keys_file )
        domain_specific_keys_file.close()
    except Exception as error:
        print( "Could not load domain specific keys plist" )
        print( "Exception message: " + str( error ) )

    if domain_specific_keys is not None:
        subkeys.extend( domain_specific_keys )

        # Add domain specific keys to segmented control under "Misc."
        segmented_control_key = next( filter( lambda preference_key: ( "pfm_name" in preference_key and preference_key[ "pfm_name" ] == "PFC_SegmentedControl_0" ), subkeys ), None )
        if segmented_control_key is not None and "pfm_segments" in segmented_control_key:
            segments = segmented_control_key[ "pfm_segments" ]
            if "Misc." in segments:
                misc_segment = segments[ "Misc." ]
                for specific_key in domain_specific_keys:
                    if "pfm_name" in specific_key:
                        misc_segment.append( specific_key[ "pfm_name" ] )

    # Update last modification time
    manifest[ "pfm_last_modified" ] = datetime.datetime.utcnow()

    # Write-out
    brave_manifest_path = os.path.join( repository_root_path, manifests_subfolder, brave_domain + ".plist" )
    brave_manifest_file = open( brave_manifest_path, 'wb' )
    plistlib.dump( manifest, brave_manifest_file )
    brave_manifest_file.close()

    print( "Brave manifest successfully created at " + brave_manifest_path + "." )

def replace_in_keys_recursively( keys: list ):
    for key in keys:
        # Replace in titles
        if "pfm_title" in key:
            key[ "pfm_title" ] = key[ "pfm_title" ].replace( "Google Chrome", "Brave Browser" )
            key[ "pfm_title" ] = key[ "pfm_title" ].replace( "Chrome", "Brave Browser" )

        # Replace in descriptions
        if "pfm_description" in key:
            key[ "pfm_description" ] = re.sub( r"Google Chrome( version \d+)", r"Chromium\1", key[ "pfm_description" ] )
            key[ "pfm_description" ] = re.sub( r"Google Chrome( \d+)", r"Chromium\1", key[ "pfm_description" ] )
            key[ "pfm_description" ] = re.sub( r"Chrome( \d+)", r"Chromium\1", key[ "pfm_description" ] )
            key[ "pfm_description" ] = key[ "pfm_description" ].replace( "Google Chrome", "Brave Browser" )
            key[ "pfm_description" ] = re.sub( r"Chrome(?! Web Store)", r"Brave Browser", key[ "pfm_description" ] )

        if "pfm_description_reference" in key:
            key[ "pfm_description_reference" ] = re.sub( r"Google Chrome( version \d+)", r"Chromium\1", key[ "pfm_description_reference" ] )
            key[ "pfm_description_reference" ] = re.sub( r"Google Chrome( \d+)", r"Chromium\1", key[ "pfm_description_reference" ] )
            key[ "pfm_description_reference" ] = re.sub( r"Chrome( \d+)", r"Chromium\1", key[ "pfm_description_reference" ] )
            key[ "pfm_description_reference" ] = key[ "pfm_description_reference" ].replace( "Google Chrome", "Brave Browser" )
            key[ "pfm_description_reference" ] = re.sub( r"Chrome(?! Web Store)", r"Brave Browser", key[ "pfm_description_reference" ] )

        # Replace in notes
        if "pfm_note" in key:
            key[ "pfm_note" ] = re.sub( r"Google Chrome( version \d+)", r"Chromium\1", key[ "pfm_note" ] )
            key[ "pfm_note" ] = re.sub( r"Google Chrome( \d+)", r"Chromium\1", key[ "pfm_note" ] )
            key[ "pfm_note" ] = re.sub( r"Chrome( \d+)", r"Chromium\1", key[ "pfm_note" ] )
            key[ "pfm_note" ] = key[ "pfm_note" ].replace( "Google Chrome", "Brave Browser" )
            key[ "pfm_note" ] = re.sub( r"Chrome(?! Web Store)", r"Brave Browser", key[ "pfm_note" ] )

        # When subkeys are encountered, they should be recursed into
        if "pfm_subkeys" in key:
            replace_in_keys_recursively( key[ "pfm_subkeys" ] )

    return keys

def replace_in_known_top_key( keys: list, key_replacement: dict ):
    if not ( "name" in key_replacement and "property" in key_replacement ):
        return

    name = key_replacement[ "name" ]
    property = key_replacement[ "property" ]

    known_key = next( filter( lambda preference_key: ( "pfm_name" in preference_key and preference_key[ "pfm_name" ] == name ), keys ), None )
    if known_key is None:
        return

    old_string = key_replacement.get( "old_string" ) or "Google Chrome"
    new_string = key_replacement.get( "new_string" ) or "Brave Browser"

    known_key[ property ] = known_key[ property ].replace( old_string, new_string )

main()
