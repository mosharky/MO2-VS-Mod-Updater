# Vintage Story Mod Updater for MO2

Update vintage story mods installed through Mod Organizer 2.

Currently unsure of compatibility with platforms other than Windows since Mod Organizer 2 doesn't natively support them.

<!-- TODO: Socials links and ModDB page -->


## Requirements
- [Mod Organizer 2 Support Tools](https://mods.vintagestory.at/vsmosupportplugin)


<!-- TODO: Installation guide -->


## How it works
An update is found if a mod version released after the current version does the following:
- Version number is greater than current version
- Supports currently installed VS version or holds the same minor version as it (ex: Installed version of VS is 1.20.12 and an update released that supports some 1.20.x version)

<!-- TODO: Add media to demonstrate (gifs, images) -->

## Future plans
- Improve version checking

## How to contribute

### Recommendations
- Use VSCode for the workspace
- Symlink files in `src` to MO2 plugins folder
    - This is so that you can quickly restart MO2 to refresh the plugin
- Change 'Log Level' to Debug
    - MO2 > Settings > Diagnostics > Log Level

### Prerequisites
- Python 3.12 or newer

### First-Time Setup
1. Open a terminal in the project directory.
2. Create a virtual environment:
   ```
   python3 -m venv .venv
   
   or
   
   C:Path/To/Python3.12/python.exe -m venv .venv
   ```
3. Activate the virtual environment:
   ```
   On Windows:
   .\.venv\Scripts\activate

   On Linux:
   source .venv/bin/activate
   ```
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Credits
- [MO2 Plugins](https://github.com/deorder/mo2-plugins) by [deorder](https://github.com/deorder) for references on how to initialize an MO2 plugin project and workspace
- [Mod Organizer 2 Support Tools](https://mods.vintagestory.at/vsmosupportplugin) by [Qwerdo](https://mods.vintagestory.at/show/user/adf3da0e8b6165d9e974)