# FFXV Blender GFXBin Add-on

This fork is a largely rewritten version of the Blender add-on that has been updated to include functionality that was missing previously. The Maya plugin has not been changed and is currently not planned to be updated or maintained.

## Contributions

* Huge thanks to AmpersandAsterisk (https://github.com/AsteriskAmpersand) for an incredibly generous amount of work on the armature transformations and help with understanding parts of the file formats
* Thanks to impatient-traveler for a huge amount of assistance in understanding the model formats, applying the data, and debugging issues
* Thanks to sai for the fixes to the original add-on to get it working in Blender 2.8+

## Features

* Full import of Mesh, UV Maps, etc
* Full import of Armature (currently uses a heuristic to determine bone lengths, won't be quite 100% true to the original in places)
* Full import of Vector Colors

## Installation

You will need the contents of the **FFXV Native Importers > Blender** folder.

One way to do this would be to go to **Code > Download ZIP** at the top of this page.

You can then either copy the Blender folder directly to your Blender add-ons directory, or ZIP the Blender folder and install the add-on as ZIP through the Blender add-ons interface.

## Roadmap

* Update importer so models aren't back-to-front
* Improve armature import to correct final minor inaccuracies
* Write GFXBin exporter