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

#####
# INCREMENT ME
manifest_version = 5
####

domain = "com.apple.touristd"
touristd_url = "https://help.apple.com/macOS/config.json"
manifests_subfolder = os.path.join( "Manifests", "ManagedPreferencesApple" )
# vv need a mechanism for matching model names from the config.json "url" key
# with the manifest_segment_titles below vv
manifest_segment_titles = [
	"iMac",
	"iMac Pro",
	"MacBook",
	"MacBook Air",
	"MacBook Pro",
	"Mac Pro",
	"Mac mini",
	"macOS",
]
manifest_segments = {}
pref_dict = {}

tour_pref_template = {
	"pfm_date_allow_past": True,
	"pfm_description": "",
	"pfm_name": "",
	"pfm_title": "",
	"pfm_type": "date",
}

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

	# Recursively populate manifest_segments 
	for segment in manifest_segment_titles:
		manifest_segments[segment] = []

	# Create a new subkeys list
	new_subkeys = list()

	# Add common payload keys
	for subkey in manifest[ "pfm_subkeys" ]:
		if ( "pfm_name" in subkey ) and ( isinstance( subkey[ "pfm_name" ], str) == True ) and ( subkey[ "pfm_name" ].startswith( "Payload" ) == True ):
			new_subkeys.append( subkey )

	# Replace old subkeys with new ones
	manifest[ "pfm_subkeys" ] = new_subkeys

	# Write tour preference dictionaries
	for tour in tours:

		# Create a new subkey
		new_subkey = dict()

		new_subkey[ "pfm_description" ] = tour[ "url" ]
		new_subkey[ "pfm_name" ] = "seed-viewed-" + tour[ "id" ]
		new_subkey[ "pfm_type" ] = "date"

		# Add the new subkey to the new subkeys list
		new_subkeys.append( new_subkey )

	# Add keys to segmented control dictionary
	segmented_control_key = next( filter( lambda preference_key: ( "pfm_name" in preference_key and preference_key[ "pfm_name" ] == "PFC_SegmentedControl_0" ), new_subkeys ), None )
	if segmented_control_key is not None and "pfm_segments" in segmented_control_key:
		segments = segmented_control_key[ "pfm_segments" ]
		for title in manifest_segment_titles:
			# Create segment arrays
			segments[ title ] = []

			if title in segments:
				for key_name in pref_dict:
					if key_name not in segments[ title ]:
						segments[ title ].append(key_name[ "pfm_name" ])
						# Add preference dictionary to manifest subkeys
						new_subkeys.append( key_name )

	# Update last modification time
	manifest["pfm_last_modified"] = datetime.datetime.utcnow()

	# Increment pfm_version by one based on manifest_version 
	manifest["pfm_version"] = manifest_version + 1

	# Write-out
	manifest_path = os.path.join( repo_root_path, manifests_subfolder, domain + ".plist" )
	manifest_file = open( manifest_path, 'wb' )
	plistlib.dump( manifest, manifest_file )
	manifest_file.close()
			

main()
