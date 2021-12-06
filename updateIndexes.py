#!/usr/bin/env python3
"""Generates new manifest and icon indexes."""

import hashlib
import os
import plistlib
from datetime import datetime
from glob import glob


def main():
    """Main process."""

    # Path to the ProfileManifests repo
    repo_path = os.path.dirname(__file__)

    # Iterate through index types
    file_types = {"Icons": "png", "Manifests": "plist"}
    for index_type, ext in file_types.items():
        index = {"date": datetime.utcnow()}

        # Get all matching files in the desired subfolder
        file_list = glob("%s/%s/*/*.%s" % (repo_path, index_type, ext))
        for path in sorted(file_list, key=lambda x: x.lower()):
            rel_path = os.path.relpath(path, repo_path)
            _, category, file_name = rel_path.split("/")

            # Add placeholder for category subfolders
            if category not in index:
                index[category] = {}

            if index_type == "Icons":
                # Generate index information for icons
                domain = file_name.replace("." + ext, "")
                with open(path, "rb") as f:
                    hash = hashlib.md5(f.read()).hexdigest()
                index[category][domain] = {
                    "hash": hash,
                    "path": rel_path,
                }

            elif index_type == "Manifests":
                # Generate index information for manifests
                with open(path, "rb") as f:
                    manifest = plistlib.load(f)
                domain = manifest.get("pfm_domain")
                if "pfm_subdomain" in manifest:
                    domain += "-%s" % (manifest.get("pfm_subdomain"))
                index[category][domain] = {
                    "modified": manifest.get("pfm_last_modified"),
                    "version": manifest.get("pfm_version"),
                    "path": rel_path,
                }

        # Write the new index file
        with open(os.path.join(repo_path, index_type, "index"), "wb") as f:
            f.write(plistlib.dumps(index))


if __name__ == "__main__":
    main()
