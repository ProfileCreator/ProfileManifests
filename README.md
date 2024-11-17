# ProfileManifests
Manifest repository for the ProfilePayloads framework that powers [ProfileCreator](https://github.com/ProfileCreator/ProfileCreator) and [iMazing Profile Editor](https://imazing.com/profile-editor).

If you have questions or need any help whatsoever in contributing to this repository, join the [#profilemanifests](https://macadmins.slack.com/messages/profilemanifests) channel in the [MacAdmins Slack](https://www.macadmins.org/).

## Contributing
This repository is meant to provide administrators with a central, common framework which makes it possible to easily configure and manage any available settings in Apple products and supporting third-party software.  By contributing to this repo, you are helping make the lives of all members of the Mac Admin community easier and lowering the barrier to entry for those who are new to managing Apple devices in the process.

Before contributing, please review the [Getting Started](https://github.com/ProfileManifests/ProfileManifests/wiki/Getting-Started) and [Contributing to an existing manifest](https://github.com/ProfileManifests/ProfileManifests/wiki/Contribute-to-an-Existing-Manifest) wiki pages.

### ProfileManifestsMirror

All changes and improvements made here are also immediately converted into [Jamf's JSON Schema](https://docs.jamf.com/technical-papers/jamf-pro/json-schema/10.26.0/Understanding_the_Structure_of_a_JSON_Schema_Manifest.html) in the [ProfileManifestsMirror repository](https://github.com/Jamf-Custom-Profile-Schemas/ProfileManifestsMirror) for use with Jamf. This provides an intuitive interface for managing payloads and preferences not natively supported in Jamf.

A debt of gratitude is owed to [Elliot Jordan](https://www.elliotjordan.com/posts/profilemanifestsmirror/) for his efforts in extending the functionality of this framework!

## Manifest Format
The payload manifest files are using Apple's Preference Manifest File format to describe the payloads and their keys.

Link: [Preference Manifest Files for Managed Clients Overview](https://developer.apple.com/library/archive/documentation/MacOSXServer/Conceptual/Preference_Manifest_Files/Preface/Preface.html)


To meet all required functionality that format has been extended with more keys and options. Use this reference to create manifests for the ProfilePayloads framework and ProfileCreator.

Link: [ProfileManifest Format](https://github.com/ProfileManifests/ProfileManifests/wiki/Manifest-Format)

## Create your own manifest

If you want to create your own manifest read the [Getting Started](https://github.com/ProfileManifests/ProfileManifests/wiki/Getting-Started) wiki page for a quick start guide.
