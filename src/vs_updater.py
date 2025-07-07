import zipfile
import json
import urllib.request
import logging
import mobase  # type: ignore
import PyQt6.QtGui as QtGui  # type: ignore
import PyQt6.QtWidgets as QtWidgets  # type: ignore

from PyQt6.QtCore import Qt, qCritical, qWarning, qDebug, qInfo  # type: ignore
from typing import List, Optional, Dict, Any
from pathlib import Path


# TODO: use qCritical(string) instead of print(string)
class PluginWindow(QtWidgets.QDialog):
    def __init__(self, organizer: mobase.IOrganizer, parent=None):
        self.organizer = organizer
        self.sample_label = QtWidgets.QLabel("Test")
        # Keys are mod ids, value is an object of each mods' JSON
        self.mods_data = {}
        # Base vintage story Mod DB API url
        self.base_url = "https://mods.vintagestory.at/api"
        
        super(PluginWindow, self).__init__(parent)

        self.resize(500, 500)
        # TODO: Set window icon

        mainLayout = QtWidgets.QHBoxLayout()
        leftVerticalLayout = QtWidgets.QVBoxLayout()
        rightVerticalLayout = QtWidgets.QVBoxLayout()

        someButton = QtWidgets.QPushButton("Test", self)
        someButton.clicked.connect(self.test_btn)
        leftVerticalLayout.addWidget(someButton)

        rightVerticalLayout.addWidget(self.sample_label)

        mainLayout.addLayout(leftVerticalLayout)
        mainLayout.addLayout(rightVerticalLayout)

        self.setLayout(mainLayout)

    def test_btn(self):
        logging.debug("LATEST VERSION: " + str(self.get_latest_game_version()))

    # Adds mod info from installed mods' modinfo.json file
    def populate_mod_data(self):
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
                        self.mods_data[mod_info["modid"]] = mod_info
                        break
        
    def get_latest_game_version(self):
        try:
            with urllib.request.urlopen(f"{self.base_url}/gameversions") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data['gameversions'][-1]['name']
                else:
                    qCritical(f"Error: HTTP {response.status}")
                    return None
        except Exception as ex:
            qCritical(f"Error fetching game versions: {ex}")
            raise
        
    def get_mod_info_from_zip(self, zip_path: Path) -> dict:
        mod_info = {}
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check if modinfo.json exists in the zip
                if 'modinfo.json' in zip_ref.namelist():
                    # Read and parse the JSON file
                    with zip_ref.open('modinfo.json') as json_file:
                        mod_info = json.load(json_file)
                        json_file.close()
                else:
                    qCritical(f"Warning: modinfo.json not found in {zip_path.name}")
                
                zip_ref.close()
                
        except zipfile.BadZipFile:
            qCritical(f"Error: {zip_path.name} is not a valid zip file")
        except json.JSONDecodeError:
            qCritical(f"Error: Invalid JSON in modinfo.json from {zip_path.name}")
        except Exception as ex:
            qCritical(f"Error processing {zip_path.name}: {ex}")
            
        return mod_info
        
    def get_mod_info_from_api(self, mod_id: str):
        try:
            with urllib.request.urlopen(f"{self.base_url}/mod/{mod_id}") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data
                else:
                    qCritical(f"Error: HTTP {response.status}")
                    return None
        except Exception as ex:
            qCritical(f"Error fetching mod info: {ex}")
            raise
        


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
        return "Vintage Story Mod Updater"

    def author(self):
        return "mo_shark"

    def description(self):
        return "Update mods in MO2's virtual file system"

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 0, 0)

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            mobase.PluginSetting("enabled", "Enable this plugin", True)
        ]

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


def createPlugin() -> mobase.IPlugin:
    return VSUpdaterPlugin()
