#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import urllib3
import json
import plistlib
import re
import datetime

domain = "com.apple.touristd"
touristd_url = "https://help.apple.com/macOS/config.json"
manifests_subfolder = os.path.join( "Manifests", "ManagedPreferencesApple" )

path_component_to_title = {
	"whats-new": "What's New",
	"mac-basics": "New to Mac"
}

product_casing = {
	"Macbook": "MacBook",
	"Mini": "mini",
	"Imac": "iMac"
}

def main():
	# Work from the script's own folder
	script_folder_path = os.path.dirname( os.path.realpath( __file__ ) )
	os.chdir( script_folder_path )

	# Get path to repository root
	popen_args = [ "git", "rev-parse", "--show-toplevel" ]
	repo_root_process: subprocess.Popen = subprocess.Popen(
		popen_args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT
		)
	( stdout, stderr ) = repo_root_process.communicate()

	if repo_root_process.returncode != 0:
		print( "Getting repo root path errored out:\n" + stdout )
		exit( 1 )

	repo_root_path = stdout.decode( sys.stdout.encoding ).strip()
	manifest_path = os.path.join( repo_root_path, manifests_subfolder, domain + ".plist" )

	# Load existing manifest
	manifest_file = open( manifest_path, 'rb' )
	manifest = plistlib.load( manifest_file )
	manifest_file.close()

	# Get touristd config.json
	http = urllib3.PoolManager()
	r = http.request('GET', touristd_url)

	# Verify successful data acquisition
	if r.status != 200:
		print(("Something went wrong with the request. \n \
			HTTP Status code: {}.").format(r.status))

	# Parse json
	touristd_config = json.loads( r.data.decode( 'utf-8' ) )
	# Get tours
	tours = touristd_config["tours"]

	# Create a new subkeys list
	new_subkeys = list()

	# Add common payload keys
	for subkey in manifest[ "pfm_subkeys" ]:
		if ( "pfm_name" in subkey ) and ( isinstance( subkey[ "pfm_name" ], str) == True ) and ( subkey[ "pfm_name" ].startswith( "Payload" ) == True ):
			new_subkeys.append( subkey )

	# Initialize a manifest segments dictionary
	manifest_segments = {}
	# Get the existing segmented control key to serve as template
	segmented_control_key = next( filter( lambda preference_key: ( "pfm_name" in preference_key and preference_key[ "pfm_name" ] == "PFC_SegmentedControl_0"), manifest[ "pfm_subkeys" ] ), None )
	if segmented_control_key is not None and "pfm_range_list_titles" in segmented_control_key:
		for manifest_segment_title in segmented_control_key[ "pfm_range_list_titles" ]:
			manifest_segments[ manifest_segment_title ] = list()

	new_subkeys.append( segmented_control_key )

	# Write tour preference dictionaries
	for tour in tours:

		# Create a new subkey
		new_subkey = dict()

		new_subkey[ "pfm_name" ] = "seed-viewed-" + tour[ "id" ]
		new_subkey[ "pfm_type" ] = "date"
		new_subkey[ "pfm_date_allow_past" ] = True

		tour_url = tour[ "url" ].rstrip( "/" )
		new_subkey[ "pfm_description" ] = tour_url

		# Parse title model/type
		url_model_type = tour_url.split( "/" )[ -1 ]

		if url_model_type in path_component_to_title:
			model_type = path_component_to_title[ url_model_type ]
		else:
			model_type = url_model_type.replace( "-", " " ).title()
			# Correct product casing
			for product_casing_key in product_casing:
				model_type = model_type.replace( product_casing_key, product_casing[ product_casing_key ] )

		# Parse title version
		if "osVersion" in tour:
			parsed_os_versions = list()
			for os_version_item in tour[ "osVersion" ]:
				os_version_fragments = os_version_item.split( "\\." )
				if len( os_version_fragments ) > 1:
					# Version pattern is formatted like 10\\.15\\.[0-9]*
					os_version_fragments = list( filter( lambda fragment: ( fragment.isdigit() ), os_version_fragments ) )
					parsed_os_versions.append( ".".join( os_version_fragments ) )
				else:
					# Version pattern is formatted like 10.15.* / 11.0*
					os_version_fragments = os_version_item.rstrip( "*" ).split( "." )
					os_version_fragments = list( filter( lambda fragment: ( fragment.isdigit() ), os_version_fragments ) )
					parsed_os_versions.append( ".".join( os_version_fragments ) )

			title_os_version = " - ".join( parsed_os_versions )

		new_subkey[ "pfm_title" ] = model_type + ": " + title_os_version

		# Add the new subkey to the new subkeys list
		new_subkeys.append( new_subkey )

		# Add the new subkey to its segment by iterating on a reverse-sorted list, so values like "MacBook Pro" will be caught before "MacBook"
		subkey_segment_found = False
		for title in sorted( list( manifest_segments.keys() ), key = str.casefold, reverse = True ):
			if model_type.startswith( title ):
				manifest_segments[ title ].append( new_subkey[ "pfm_name" ] )
				subkey_segment_found = True
				break

		# Default to macOS segment if not found
		if subkey_segment_found == False:
			manifest_segments[ "macOS" ].append( new_subkey[ "pfm_name" ] )

	# Add keys to segmented control dictionary
	if segmented_control_key is not None:
		segmented_control_key[ "pfm_segments" ] = manifest_segments

	# Replace old subkeys with new ones
	manifest[ "pfm_subkeys" ] = new_subkeys

	# Update last modification time
	manifest["pfm_last_modified"] = datetime.datetime.utcnow()

	# Increment pfm_version by one based on manifest_version
	if "pfm_version" in manifest and isinstance( manifest[ "pfm_version" ], int ):
		manifest[ "pfm_version" ] = manifest[ "pfm_version" ] + 1

	# Write-out
	manifest_file = open( manifest_path, 'wb' )
	plistlib.dump( manifest, manifest_file )
	manifest_file.close()
			

main()
