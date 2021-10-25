# FFXV Blender GFXBin Import Add-on

This fork is simply a refactor of the original add-on to ensure the script registers as an add-on in Blender and to make it more readable for other developers that wish to learn from it.

# Code Editing

It is recommended to use VSCode to edit the code as it is able to provide autocompletion, intellisense, and can automatically detect PEP8 specification errors and correct them on save.

The settings.json under .vscode already provides the required settings, you simply need the following tools:

- VSCode
- Python Extension for VSCode
- Python itself (author uses 3.5.3 as this is the version Blender 2.79b uses)
- pystylecode
- autopep8
- Optional: Fake bpy modules for bpy autocomplete
