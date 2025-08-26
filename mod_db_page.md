<center>
<h1> Vintage Story Mod Updater for MO2 </h1>

<p><i>Update Vintage Story mods installed through Mod Organizer 2, all with a convenient UI!</i></p>

<a href="https://mods.vintagestory.at/modupdaterformodorganizer"><img src="https://img.shields.io/badge/%E2%9A%99%EF%B8%8F-VS%20Mod%20DB-%23a6947b?style=flat&labelColor=%237d6b56" alt="VS Mod DB"></a>
<a href="https://discord.gg/sWVexFEWNZ"><img src="https://img.shields.io/discord/532779726343897104?style=flat&logo=discord&label=Discord&color=%237289da" alt="Discord"></a>
<a href="https://github.com/mosharky"><img src="https://img.shields.io/badge/GitHub-gray?style=flat&logo=github" alt="GitHub"></a>

</center>

<h2>Requirements</h2>
<ul>
    <li><a href="https://www.vintagestory.at/">Vintage Story</a></li>
    <li><a href="https://github.com/ModOrganizer2/modorganizer/releases">Mod Organizer 2</a> - v2.5.2 or higher</li>
    <li><a href="https://mods.vintagestory.at/vsmosupportplugin">Mod Organizer 2 Support Tools</a></li>
</ul>


<h2>Installation</h2>

<blockquote>
<strong>IMPORTANT:</strong><br>
Currently unsure of compatibility with platforms other than Windows since Mod Organizer 2 doesn't natively support them.
</blockquote>

<h3>Manual</h3>
<ol>
    <li>Set up <a href="https://mods.vintagestory.at/vsmosupportplugin">Mod Organizer 2 Support Tools</a> if you haven't already (see their page for instructions)</li>
    <li>Download the latest version from <a href="https://mods.vintagestory.at/modupdaterformodorganizer#tab-files">VS Mod DB</a> or <a href="https://github.com/mosharky/MO2-VS-Mod-Updater/releases">GitHub Releases</a></li>
    <li>Extract the <code>vs_mod_updater</code> folder from the downloaded .zip file into the plugins folder, found in your MO2 install directory
        <ul>
            <li>The plugins folder will be in the same directory as <code>ModOrganizer.exe</code>. For example, assuming MO2 is installed in <code>C:\MO2</code>, your plugins folder is <code>C:\MO2\plugins\</code></li>
        </ul>
    </li>
</ol>

<p>If you followed the instructions correctly, you should have a <code>C:\MO2\plugins\vs_mod_updater\</code> folder with a bunch of <code>.py</code> files.</p>


<h2>Usage</h2>
<p>To open the update menu, go to the Tools button and select 'VS Mod Updater'</p>
<img src="https://raw.githubusercontent.com/mosharky/MO2-VS-Mod-Updater/refs/heads/main/assets/plugin_dropdown.png" alt="Plugin dropdown">

<p>From there, you'll be met with this screen:</p>
<img src="https://raw.githubusercontent.com/mosharky/MO2-VS-Mod-Updater/refs/heads/main/assets/plugin_ui.png" alt="Plugin UI">

<p>You need to press the 'Check for Updates' button to be able to update any mods. If the plugin successfully found updates, you'll see a neat overview of all updates and their changes:</p>
<img src="https://raw.githubusercontent.com/mosharky/MO2-VS-Mod-Updater/refs/heads/main/assets/updates_found.png" alt="Updates found">

<p>The 'Update Mods' button will only update mods with their checkbox marked.</p>

<h3>Updating</h3>

<p>Reinstall the plugin for every update. In the future, I might see if I can update everything within MO2.</p>


<h2>How it works</h2>
<p>An update is found if a mod version released after the current version does the following:</p>
<ul>
    <li>Version number is greater than current version</li>
    <li>Supports currently installed VS version or holds the same minor version as it (ex: Installed version of VS is 1.20.12 and an update for the mod released that supports some 1.20.x version).</li>
</ul>

<p>It's possible that update detection is flawed; I haven't extensively tested for potential edge cases.</p>

<h2>Future plans</h2>
<ul>
    <li>Improve version checking</li>
    <li>Use custom icons instead of emojis (or existing MO2 icons)</li>
</ul>

<br>
<br>

<hr>

<br>
<br>

<h1>Credits</h1>
<ul>
    <li><a href="https://github.com/deorder/mo2-plugins">MO2 Plugins</a> by <a href="https://github.com/deorder">deorder</a> for references on how to initialize an MO2 plugin project and workspace.</li>
    <li><a href="https://mods.vintagestory.at/vsmosupportplugin">Mod Organizer 2 Support Tools</a> by <a href="https://mods.vintagestory.at/show/user/adf3da0e8b6165d9e974">Qwerdo</a> for making this project or even using MO2 for Vintage Story possible.</li>
</ul>