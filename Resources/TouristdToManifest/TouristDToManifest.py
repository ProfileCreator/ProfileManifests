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

# Initialize manifest dictionary
manifest = {
	"pfm_description": '"New to Mac" notification settings',
	"pfm_documentation_url": 'https://help.apple.com/macOS/config.json',
	"pfm_domain": 'com.apple.touristd',
	"pfm_format_version": 1,
	"pfm_last_modified": '',
	"pfm_platforms": [ "macOS" ],
	"pfm_targets": [ "system", "user" ],
	"pfm_title": 'New to Mac / Tours',
	"pfm_unique": True,
	"pfm_version": manifest_version,
	"pfm_subkeys": [
		{
			"pfm_default": '"New to Mac" tour notification settings',
			"pfm_description": 'Description of the payload.',
			"pfm_description_reference": 'Optional. A human-readable description of this payload. '
				'This description is shown on the Detail screen.',
			"pfm_name": 'PayloadDescription',
			"pfm_title": 'Payload Description',
			"pfm_type": 'string'
		},
		{
			"pfm_default": 'New to Mac',
			"pfm_description": 'Name of the payload.',
			"pfm_description_reference": 'Optional. A human-readable name for the profile payload. '
				'This description is shown on the Detail screen. It does not have to be unique.',
			"pfm_name": 'PayloadDisplayName',
			"pfm_require": 'always',
			"pfm_title": 'Payload Display Name',
			"pfm_type": 'string'
		},
		{
			"pfm_default": 'com.apple.touristd',
			"pfm_description": 'A unique identifier for the payload, dot-delimited.  '
				'Usually root PayloadIdentifier+subidentifier',
			"pfm_description_reference": 'A reverse-DNS-style identifier for the specific payload. '
				'It is usually the same identifier as the root-level PayloadIdentifier value with '
				'an additional component appended.',
			"pfm_name": 'PayloadIdentifier',
			"pfm_require": 'always',
			"pfm_title": 'Payload Identifier',
			"pfm_type": 'string'
		},
		{
			"pfm_default": 'com.apple.touristd',
			"pfm_description": 'The type of the payload, a reverse dns string.',
			"pfm_description_reference": 'The payload type.',
			"pfm_name": 'PayloadType',
			"pfm_require": 'always',
			"pfm_title": 'Payload Type',
			"pfm_type": 'string'
		},
		{
			"pfm_description": 'Unique identifier for the payload '
				'(format 01234567-89AB-CDEF-0123-456789ABCDEF)',
			"pfm_description_reference": 'A globally unique identifier for the payload. '
				'The actual content is unimportant, but it must be globally unique. In macOS, '
				'you can use uuidgen to generate reasonable UUIDs.',
			"pfm_name": 'PayloadUUID',
			"pfm_require": 'always',
			"pfm_title": 'Payload UUID',
			"pfm_type": 'string'
		},
		{
			"pfm_default": 1,
			"pfm_description": 'The version of the whole configuration profile.',
			"pfm_description_reference": 'The version number of the individual payload. '
				'A profile can consist of payloads with different version numbers. '
				'For example, changes to the VPN software in iOS might introduce a new payload '
				'version to support additional features, but Mail payload versions would not '
				'necessarily change in the same release.',
			"pfm_name": 'PayloadVersion',
			"pfm_require": 'always',
			"pfm_title": 'Payload Version',
			"pfm_type": 'integer'
		},
		{
			"pfm_description": 'This value describes the issuing organization of the profile, '
				'as displayed to the user',
			"pfm_name": 'PayloadOrganization',
			"pfm_title": 'Payload Organization',
			"pfm_type": 'string'
		},
		{
			"pfm_name": 'PFC_SegmentedControl_0',
			"pfm_range_list_titles": [ manifest_segment_titles ],
			"pfm_require": 'always',
			"pfm_segments": {},
			"pfm_type": 'string',
		},
		# 		<key>iMac</key>
		# 		<array>
		# 			<string>seed-viewed-+trJt2VsTvK1yfPGwOySDw</string>
		# 			<string>seed-viewed-EeEFv8cyS0CVe3ia2UEehA</string>
		# 			<string>seed-viewed-KwUoo0fRRM2VPmIm0V67xg</string>
		# 			<string>seed-viewed-UhiR1M79RWmXLIQr4M0AWw</string>
		# 			<string>seed-viewed-WEyaCPMVRB6HbnmRq9EnNQ</string>
		# 			<string>seed-viewed-aytyxqEmTIOvEz3iS4IbkA</string>
		# 			<string>seed-viewed-catalina_imac</string>
		# 			<string>seed-viewed-catalina_imac-21a</string>
		# 			<string>seed-viewed-catalina_mid-2020_imac</string>
		# 			<string>seed-viewed-d+gfl8CNTNeauANKjf9WqA</string>
		# 			<string>seed-viewed-pDWyREoARJm5V1mJYr9GKg</string>
		# 		</array>
		# 		<key>iMac Pro</key>
		# 		<array>
		# 			<string>seed-viewed-40reAuuYTHOsx4oGcx4qrA</string>
		# 			<string>seed-viewed-APhNaYV1RxSS41lC7ZJJ9Q</string>
		# 			<string>seed-viewed-catalina_imac-pro</string>
		# 		</array>
		# 		<key>MacBook</key>
		# 		<array>
		# 			<string>seed-viewed-FQrkbNP9ThKQQtpqx2saFg</string>
		# 			<string>seed-viewed-Pa88nesPSO6POlutVN4/Sg</string>
		# 			<string>seed-viewed-SdV08ZZQRxOCWq6JBEXmfg</string>
		# 			<string>seed-viewed-We59wh+OTa6c1yas/yppwg</string>
		# 			<string>seed-viewed-b/dLke8ZTQaN9KKrxfwDQw</string>
		# 			<string>seed-viewed-hP2OZh+MTEKeFcjgec2gZw</string>
		# 		</array>
		# 		<key>MacBook Air</key>
		# 		<array>
		# 			<string>seed-viewed-SkI/dLAkQu6k/qpzSOG6Iw</string>
		# 			<string>seed-viewed-Tu81gKhDTvmNkjyqcPBfKA</string>
		# 			<string>seed-viewed-catalina_early-2020_macbook-air</string>
		# 			<string>seed-viewed-catalina_macbook-air</string>
		# 		</array>
		# 		<key>MacBook Pro</key>
		# 		<array>
		# 			<string>seed-viewed-/+vP78HsSh+Yeb4xJnUT9A</string>
		# 			<string>seed-viewed-2+LvxAVyT6qnV1sDMZT0NA</string>
		# 			<string>seed-viewed-B70mVuHeT0WUgKh/VdUuZQ</string>
		# 			<string>seed-viewed-EBFV2ZqnQiaqrZhvyifLeQ</string>
		# 			<string>seed-viewed-ETJeJ9/1QmmWUde7uK8fDg</string>
		# 			<string>seed-viewed-EWfaSdJwR/6f1BYGiyLpcQ</string>
		# 			<string>seed-viewed-GZAJdmpdSqmfH2PkCr8ebw</string>
		# 			<string>seed-viewed-JTecrrXDSVut2tSfltty9Q</string>
		# 			<string>seed-viewed-MM3ne3nTR9eXFyVwZ5gN7Q</string>
		# 			<string>seed-viewed-catalina_early-2020_macbook-pro-13</string>
		# 			<string>seed-viewed-catalina_late-2019_macbook-pro</string>
		# 			<string>seed-viewed-catalina_macbook-pro</string>
		# 			<string>seed-viewed-catalina_macbook-pro-13</string>
		# 			<string>seed-viewed-fWRpNw7IR3S3qxX63nmvMw</string>
		# 			<string>seed-viewed-krdWS8DSQIqJSqQFXW1/pw</string>
		# 			<string>seed-viewed-kti4ZkMKQFyCL2kbgCY23A</string>
		# 			<string>seed-viewed-lEDfW5O+SZe8KTQ93HGOPA</string>
		# 			<string>seed-viewed-n87FVu1TSwGzble8vqBvsg</string>
		# 			<string>seed-viewed-srluh6uOQiuWCzxguqhDNw</string>
		# 		</array>
		# 		<key>Mac Pro</key>
		# 		<array>
		# 			<string>seed-viewed-catalina_mac-pro</string>
		# 		</array>
		# 		<key>Mac mini</key>
		# 		<array>
		# 			<string>seed-viewed-baXokbqsQ/2KLkzIZrR6ng</string>
		# 			<string>seed-viewed-catalina_mac-mini</string>
		# 		</array>
		# 		<key>macOS</key>
		# 		<array>
		# 			<string>seed-viewed-LR2P9+rnQ2q9xSUy1ZgWOw</string>
		# 			<string>seed-viewed-bydF6fX5Sp6aBYdEXD0VwQ</string>
		# 			<string>seed-viewed-catalina_mac_basics</string>
		# 			<string>seed-viewed-catalina_whats_new</string>
		# 			<string>seed-viewed-f/Pn3F4RScOh+GUBKO9sRA</string>
		# 			<string>seed-viewed-lQlm1yrMS0GPVyAL44id+A</string>
		# 		</array>
		# 	</dict>
		# 	<key>pfm_type</key>
		# 	<string>string</string>
		# </dict>
	],

}

subkeys = manifest["pfm_subkeys"]

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

	# Get touristd config.json
	http = urllib3.PoolManager()
	r = http.request('GET', touristd_url)

	# Verify successful data acquisition
	if r.status != 200:
		print(("Something went wrong with the request. \n \
			HTTP Status code: {}.").format(r.status))

	# Parse json
	touristd_config = r.json()
	# Get tours
	tours = touristd_config["tours"]
	#print(tours)

	# Recursively populate manifest_segments 
	for segment in manifest_segment_titles:
		manifest_segments[segment] = []

	# Write tour preference dictiories
	for tour in tours:
		tour_id = tour["id"]
		# vv don't believe this is right vv
		pref_dict[tour_id] = tour_pref_template
		# ^^ don't believe this is right ^^
		# Add prelim values
		pref_dict[tour_id]["pfm_name"] = 'seed-viewed-' + tour_id
		pref_dict[tour_id]["pfm_description"] = tour["url"]

	### << STUCK BEYOND THIS POINT >> ###

		# Need to parse urls for pfm_titles

		# Also need to parse to determine if url contains
		# imac, macbook pro, etc. in order to write to

		if tour["type"] == 0:
			# New to Mac / Mac Basics

			# If mac-basics and high-sierra
			# "New to Mac: 10.13"

			# If mac-basics and mojave
			# "New to Mac: 10.14"

			# If mac-basics and catalina
			# "New to Mac: 10.15"

			# ^^^^^^ Need to determine this formatting & logic ^^^^^^

			# Need to write pfm_name to s
			subkeys.append()

		elif tour["type"] == 1:
			# What's New

			# If whats-new and high-sierra
			# "What's New: 10.13"

			# If whats-new and mojave
			# "What's New: 10.14"

			# If whats-new and catalina
			# "What's New: 10.15"

			# ^^^^^^ Need to determine this formatting & logic ^^^^^^
			subkeys.append()
		elif tour["type"] == 2:
			# Mac Hardware

			# Need to parse url to get Mac hardware
			# to write pfm_title

			subkeys.append()
		else:
			print(("Don't know what to do with key {} given type of {}.")
			.format(id, tour["type"]))

		#subkeys.extend()
	
	# << Taken from ChromeToBrave, but since we're not pulling from a 
	# domain-specific .plist, not sure how best to address writing out
	# the segments. >>

	# Add keys to segmented control dictionary
	segmented_control_key = next( filter( lambda preference_key: ( "pfm_name" in preference_key and preference_key[ "pfm_name" ] == "PFC_SegmentedControl_0" ), subkeys ), None )
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
						subkeys.append( key_name )

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
