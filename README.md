<center>
<h1> Vintage Story Mod Updater for MO2 </h1>

*Update Vintage Story mods installed through Mod Organizer 2, all with a convenient UI!*

<!-- Future Mod DB link: https://mods.vintagestory.at/modupdaterformo2 -->
<img alt="Static Badge" src="https://img.shields.io/badge/%E2%9A%99%EF%B8%8F-VS%20Mod%20DB-%23a6947b?style=flat&labelColor=%237d6b56&link=https%3A%2F%2Fmods.vintagestory.at%2Fmodupdaterformo2">
<img alt="Discord" src="https://img.shields.io/discord/532779726343897104?style=flat&logo=discord&label=Discord&color=%237289da&link=https%3A%2F%2Fdiscord.gg%2FsWVexFEWNZ">
<img alt="Static Badge" src="https://img.shields.io/badge/GitHub-gray?style=flat&logo=github&link=https%3A%2F%2Fgithub.com%2Fmosharky">



</center>


## Requirements
- [Vintage Story](https://www.vintagestory.at/)
- [Mod Organizer 2](https://github.com/ModOrganizer2/modorganizer/releases) - v2.5.2 or higher
- [Mod Organizer 2 Support Tools](https://mods.vintagestory.at/vsmosupportplugin)


## Installation

> [!IMPORTANT]
> Currently unsure of compatibility with platforms other than Windows since Mod Organizer 2 doesn't natively support them.

### Manual
1. Set up [Mod Organizer 2 Support Tools](https://mods.vintagestory.at/vsmosupportplugin) if you haven't already (see their page for instructions)
2. Download the latest version from [VS Mod DB](https://mods.vintagestory.at/) or [GitHub Releases](https://github.com/mosharky/MO2-VS-Mod-Updater/releases)
3. Extract the `vs_mod_updater` folder from the downloaded .zip file into the plugins folder, found in your MO2 install directory
    - The plugins folder will be in the same directory as `ModOrganizer.exe`. For example, assuming MO2 is installed in `C:\MO2`, your plugins folder is `C:\MO2\plugins\`

If you followed the instructions correctly, you should have a `C:\MO2\plugins\vs_mod_updater\` folder with a bunch of `.py` files.

### Plugin Finder
> [!WARNING]
> This plugin has not been approved yet for Kezyma's Plugin Finder. Once it is, I will remove this warning.

You can use [Kezyma's Plugin Finder](https://kezyma.github.io/?p=pluginfinder) to install many plugins, including this one, as well as update them.


## Usage
To open the update menu, go to the Tools button and select 'VS Mod Updater'
![](https://github.com/mosharky/MO2-VS-Mod-Updater/blob/main/assets/plugin_dropdown.png)

From there, you'll be met with this screen:
![](https://github.com/mosharky/MO2-VS-Mod-Updater/blob/main/assets/plugin_ui.png)

You need to press the 'Check for Updates' button to be able to update any mods. If the plugin successfully found updates, you'll see a neat overview of all updates and their changes:
![](https://github.com/mosharky/MO2-VS-Mod-Updater/blob/main/assets/updates_found.png)

The 'Update Mods' button will only update mods with their checkbox marked.

### Updating
> [!WARNING]
> This plugin has not been approved yet for Kezyma's Plugin Finder. Once it is, I will remove this warning.

You can use [Kezyma's Plugin Finder](https://kezyma.github.io/?p=pluginfinder) to install new updates. Otherwise, reinstall the plugin for every update.


## How it works
An update is found if a mod version released after the current version does the following:
- Version number is greater than current version
- Supports currently installed VS version or holds the same minor version as it (ex: Installed version of VS is 1.20.12 and an update for the mod released that supports some 1.20.x version).

It's possible that update detection is flawed; I haven't extensively tested for potential edge cases.


## Future plans
- Improve version checking
- Use custom icons instead of emojis (or existing MO2 icons)


<br>
<br>

***

<br>
<br>


# Contributing

## Preamble
- Using VSCode for the workspace is recommended
- Symlink files in `src` to MO2 plugins folder
    - This is so that you can quickly restart MO2 to refresh the plugin
- Change 'Log Level' to Debug
    - MO2 > Settings > Diagnostics > Log Level

## Prerequisites
- Python 3.12 or newer

## First-Time Setup
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

## Releasing
1. Change version number in `VSModUpdaterPlugin` class
2. Add a new version to `plugin_definitions.json`
3. Upload the release


<br>
<br>

***

<br>
<br>


# Credits
- [MO2 Plugins](https://github.com/deorder/mo2-plugins) by [deorder](https://github.com/deorder) for references on how to initialize an MO2 plugin project and workspace.
- [Mod Organizer 2 Support Tools](https://mods.vintagestory.at/vsmosupportplugin) by [Qwerdo](https://mods.vintagestory.at/show/user/adf3da0e8b6165d9e974) for making this project or even using MO2 for Vintage Story possible.