from .utils import *

import re
import zipfile
import json
import urllib.request
import logging
import concurrent.futures
import mobase  # type: ignore
import PyQt6.QtGui as QtGui  # type: ignore
import PyQt6.QtWidgets as QtWidgets  # type: ignore

from PyQt6.QtCore import Qt, qCritical, qWarning, qDebug, qInfo  # type: ignore
from typing import List, Optional, Dict, Any
from pathlib import Path


class PluginWindow(QtWidgets.QDialog):
    def __init__(self, organizer: mobase.IOrganizer, parent=None):
        self.organizer = organizer
        self.current_vs_version = normalize_version(
            self.organizer.managedGame().gameVersion()
        )
        self.sample_label = QtWidgets.QLabel("Test")
        # Base vintage story Mod DB API url
        self.base_url = "https://mods.vintagestory.at/api"
        # Keys are mod ids, value is an object of each mods' JSON
        self.mods_data = {}
        self.mod_updates = []

        super(PluginWindow, self).__init__(parent)

        # TODO: Set window icon
        self.resize(500, 500)

        # Left layout
        left_vertical_layout = QtWidgets.QVBoxLayout()
        test_btn = QtWidgets.QPushButton("Test", self)
        test_btn.clicked.connect(self.test_btn)
        check_updates_btn = QtWidgets.QPushButton("Check for Updates", self)
        check_updates_btn.clicked.connect(self.check_for_updates)

        left_vertical_layout.addWidget(test_btn)
        left_vertical_layout.addWidget(check_updates_btn)

        # Right layout
        right_vertical_layout = QtWidgets.QVBoxLayout()

        right_vertical_layout.addWidget(self.sample_label)

        # Main layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_vertical_layout)
        main_layout.addLayout(right_vertical_layout)

        self.setLayout(main_layout)

    def test_btn(self):
        logging.info("CURRENT VERSION: " + self.current_vs_version)

    def check_for_updates(self):
        """Checks for updates for all mods in MO2."""
        self.populate_mods_data()
        if not self.mods_data:
            qWarning("No mods found in MO2. Please add some mods first.")
            return

        # Clear previous updates
        self.mod_updates.clear()

        def safe_check(mod_id):
            try:
                self.check_mod_for_update(mod_id)
            except Exception as ex:
                qCritical(f"Error checking mod {mod_id}: {ex}")

        # Run checks in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(safe_check, self.mods_data.keys()))

        if not self.mod_updates:
            qInfo("All mods are up to date.")
        else:
            qInfo(f"Found {len(self.mod_updates)} mod updates.")

        logging.info(str(self.mod_updates))

    def check_mod_for_update(self, mod_id: str):
        mod_db_info = self.get_mod_info_from_api(mod_id)
        current_mod_version = parse_version(self.mods_data[mod_id]["version"])
        # Getting latest mod release that supports current VS version
        latest_mod_version = parse_version("0.0.0")
        latest_mod_release = {}
        for release in mod_db_info["mod"]["releases"]:
            if self.current_vs_version in release["tags"]:
                latest_mod_version = parse_version(release["modversion"])
                latest_mod_release = release
                break

        # If current = latest, there is no need to update
        if current_mod_version >= latest_mod_version:
            return
        else:
            self.mod_updates.append(
                {
                    "mod_id": mod_id,
                    "name": mod_db_info["mod"]["name"],
                    "current_version": current_mod_version,
                    "latest_version": latest_mod_version,
                    "latest_release": latest_mod_release,
                    "changelog": self.generate_changelog(
                        mod_db_info, current_mod_version
                    ),
                }
            )

    def generate_changelog(self, mod_db_info: dict, current_mod_version: tuple) -> str:
        """Generates a changelog between the current and latest release."""
        changelog = ""
        for release in mod_db_info["mod"]["releases"]:
            release_version = parse_version(release["modversion"])
            valid_release = (
                self.current_vs_version in release["tags"]
                and release_version > current_mod_version
            )
            if valid_release:
                release_changelog = (
                    f"{release["modversion"]}\n{release["changelog"]}\n\n"
                )
                changelog += release_changelog
            # Assuming releases list is always descending from latest
            elif release_version == current_mod_version:
                break
        return changelog

    def populate_mods_data(self):
        """Populates mods_data for each mod in MO2 from their modinfo.json file."""
        mods_path = Path(self.organizer.modsPath())

        # Looking through each mod folder
        for folder in mods_path.iterdir():
            # Check if item is a folder
            if folder.is_dir():
                # Looking for the mod zip file
                for file in folder.iterdir():
                    # If zip file
                    if file.suffix.lower() == ".zip":
                        mod_info = self.get_mod_info_from_zip(file)

                        # If not empty
                        if mod_info:
                            self.mods_data[mod_info["modid"]] = mod_info
                        break

    def get_latest_game_version(self):
        """Returns the latest game version from the ModDB API."""
        try:
            with urllib.request.urlopen(f"{self.base_url}/gameversions") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["gameversions"][-1]["name"]
                else:
                    qCritical(f"Error: HTTP {response.status}")
                    return None
        except Exception as ex:
            qCritical(f"Error fetching game versions: {ex}")
            raise

    def get_mod_info_from_zip(self, zip_path: Path) -> dict:
        """Returns modinfo.json from mod zip as a dictionary."""
        mod_info = {}
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Check if modinfo.json exists in the zip
                if "modinfo.json" in zip_ref.namelist():
                    # Read and parse the JSON file
                    with zip_ref.open("modinfo.json") as json_file:
                        # Use fix_json_string to ensure the JSON is valid
                        json_str = json_file.read().decode("utf-8")
                        json_str = fix_json_string(json_str)
                        mod_info = json.loads(json_str)
                        mod_info = {k.lower(): v for k, v in mod_info.items()}
                        json_file.close()
                else:
                    qCritical(f"Warning: modinfo.json not found in {zip_path.name}")

                zip_ref.close()

        except zipfile.BadZipFile:
            qCritical(f"Error: {zip_path.name} is not a valid zip file")
        except json.JSONDecodeError:
            qCritical(
                f"Error: Invalid JSON in modinfo.json from {zip_path.name}; could not update the mod. Report this to the mod author."
            )
        except Exception as ex:
            qCritical(f"Error processing {zip_path.name}: {ex}")

        return mod_info

    def get_mod_info_from_api(self, mod_id: str) -> dict:
        """Returns all data from ModDB page"""
        data = {}
        try:
            with urllib.request.urlopen(f"{self.base_url}/mod/{mod_id}") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                else:
                    qCritical(f"Error: HTTP {response.status}")
        except Exception as ex:
            qCritical(f"Error fetching mod info: {ex}")
            raise
        return data


class VSUpdaterPlugin(mobase.IPluginTool):

    def __init__(self):
        self.__window = None
        # self.organizer = None
        self.__parentWidget = None

        super(VSUpdaterPlugin, self).__init__()

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.organizer = organizer
        return True

    def name(self) -> str:
        return "VS Mod Updater"

    def author(self):
        return "mo_shark"

    def description(self):
        return "Update mods in MO2's virtual file system"

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 0, 0)

    def settings(self) -> List[mobase.PluginSetting]:
        return [mobase.PluginSetting("enabled", "Enable this plugin", True)]

    def display(self):
        self.__window = PluginWindow(self.organizer)
        self.__window.setWindowTitle(self.name())
        self.__window.exec()

        self.organizer.refresh()

    def displayName(self) -> str:
        return self.name()

    def icon(self):
        # TODO: Set icon
        return QtGui.QIcon("test")

    def tooltip(self):
        return self.description()
