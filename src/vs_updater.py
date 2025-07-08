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

from PyQt6.QtCore import Qt, qCritical, qWarning, qDebug, qInfo, QSize  # type: ignore
from typing import List
from pathlib import Path

# TODO: Add an update checker for the plugin itself

class PluginWindow(QtWidgets.QDialog):
    def __init__(self, organizer: mobase.IOrganizer, parent=None):
        self.organizer = organizer
        self.current_vs_version = normalize_version(
            self.organizer.managedGame().gameVersion()
        )
        # Base vintage story Mod DB API url
        self.base_url = "https://mods.vintagestory.at/api"
        # Keys are mod ids, value is an object of each mods' JSON
        self.mods_data = {}
        self.mod_updates = []
        self.model = QtGui.QStandardItemModel()
        self.tree = QtWidgets.QTreeView()

        super(PluginWindow, self).__init__(parent)

        self.setFixedSize(640, 480)

        # TODO: Set window icon

        # Left layout
        left_vertical_layout = QtWidgets.QVBoxLayout()
        check_updates_btn = QtWidgets.QPushButton("Check for Updates", self)
        check_updates_btn.clicked.connect(self.check_for_updates)
        left_vertical_layout.addWidget(check_updates_btn)

        # Right layout
        right_vertical_layout = QtWidgets.QVBoxLayout()
        update_mods_btn = QtWidgets.QPushButton("Update Mods", self)
        update_mods_btn.clicked.connect(self.update_mods)
        right_vertical_layout.addWidget(update_mods_btn)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addLayout(left_vertical_layout)
        buttons_layout.addLayout(right_vertical_layout)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        self.model.setHorizontalHeaderLabels(["Name", "Version"])
        self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        self.tree.setItemDelegateForColumn(0, RichTextDelegate(self.tree))
        self.tree.setItemDelegateForColumn(1, RichTextDelegate(self.tree))
        self.tree.setWordWrap(True)  # Enable word wrap for long text

        main_layout.addWidget(self.tree)
        self.tree.setModel(self.model)
        self.setLayout(main_layout)
        self.tree.setColumnWidth(0, 500)

    def update_mods(self):
        """Downloads all updates for mods in MO2 that are checked."""
        if not self.mod_updates:
            QtWidgets.QMessageBox.critical(
                self, "Error", "No mod updates found. Please check for updates first."
            )
            return

        # Iterate backwards to avoid skipping rows when removing
        for row in reversed(range(self.model.rowCount())):
            update_item = self.model.item(row, 0)
            if (
                update_item is not None
                and update_item.checkState() == Qt.CheckState.Checked
            ):
                mod_id = update_item.data(Qt.ItemDataRole.UserRole)
                # Find the corresponding update dict by mod_id
                update_data = next(
                    (u for u in self.mod_updates if u["mod_id"] == mod_id), None
                )
                if not update_data:
                    continue
                latest_release = update_data["latest_release"]
                filename = latest_release["filename"]
                download_url = latest_release["mainfile"]

                try:
                    old_zip_path = self.mods_data[mod_id]["path"]

                    # Download the mod zip file
                    response = urllib.request.urlopen(download_url)
                    # Output in old_zip_path.parent
                    logging.debug(f"Downloading {filename} from {download_url}")
                    zip_path = old_zip_path.parent / filename
                    with open(zip_path, "wb") as out_file:
                        out_file.write(response.read())
                    logging.info(f"Downloaded {filename} to {zip_path}")
                    # Remove update_item from model
                    self.model.removeRow(row)
                    # Delete old mod zip file if it exists
                    logging.debug(f"Deleting old mod zip: {old_zip_path}")
                    old_zip_path.unlink()
                except Exception as ex:
                    qCritical(f"Error downloading {filename}: {ex}")

    def check_for_updates(self):
        """Checks for updates for all mods in MO2."""
        # Show loading overlay until updates are checked
        loading_label = QtWidgets.QLabel("Checking for updates...", self)
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet(
            "background: rgba(255,255,255,150); font-size: 18px; padding: 40px; border: 2px solid #888;"
        )
        loading_label.setGeometry(self.rect())
        loading_label.show()
        QtWidgets.QApplication.processEvents()  # Force update

        self.populate_mods_data()
        if not self.mods_data:
            loading_label.hide()
            QtWidgets.QMessageBox.warning(
                self,
                "No Mods Found",
                "No mods found in MO2. Please add some mods first.",
            )
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

        loading_label.hide()

        if not self.mod_updates:
            QtWidgets.QMessageBox.information(
                self, "No Updates", "All mods are up to date :)"
            )
        else:
            qInfo(f"Found {len(self.mod_updates)} mod updates.")

        # Sort mod updates by name
        self.mod_updates.sort(key=lambda x: x["name"])

        # Clear the model and populate it with mod updates
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Name", "Version"])

        for update in self.mod_updates:
            update_item = QtGui.QStandardItem(update["name"])
            update_item.setEditable(False)
            update_item.setCheckable(True)
            update_item.setCheckState(Qt.CheckState.Checked)
            update_item.setData(update["mod_id"], Qt.ItemDataRole.UserRole)

            version_item = QtGui.QStandardItem(
                f"{update['current_version']} → {update['latest_version']}"
            )
            version_item.setEditable(False)

            # Add change log for each release since the current version
            for changes in update["changelog"]:
                for version, changelog_text in changes.items():
                    # Create a rich text item for the changelog
                    changelog_item = QtGui.QStandardItem()
                    if changelog_text == "":
                        changelog_item.setText("<i>No changelog found.</i>")
                    else:
                        changelog_item.setText(changelog_text)

                    changelog_item.setEditable(False)
                    changelog_version_item = QtGui.QStandardItem(
                        f"<div style='text-align:center;'><i>{version}</i></div>"
                    )
                    changelog_version_item.setEditable(False)
                    changelog_version_item.setSelectable(False)
                    update_item.appendRow([changelog_item, changelog_version_item])

            self.model.appendRow([update_item, version_item])

        self.tree.setColumnWidth(0, 500)

        logging.debug(str(self.mod_updates))

    #TODO: Improve update checking with more leniency
    def check_mod_for_update(self, mod_id: str):
        mod_db_info = self.get_mod_info_from_api(mod_id)
        current_mod_version = self.mods_data[mod_id]["version"]
        # Getting latest mod release that supports current VS version
        latest_mod_version = "0.0.0"
        latest_mod_release = {}
        for release in mod_db_info["mod"]["releases"]:
            if self.current_vs_version in release["tags"]:
                latest_mod_version = release["modversion"]
                latest_mod_release = release
                break
            elif parse_version(current_mod_version) >= parse_version(release["modversion"]):
                return

        # If current = latest, there is no need to update
        if parse_version(current_mod_version) >= parse_version(latest_mod_version):
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
                        mod_db_info, parse_version(current_mod_version)
                    ),
                }
            )

    def generate_changelog(
        self, mod_db_info: dict, current_mod_version: tuple
    ) -> list[dict]:
        """
        Generates a changelog between the current and latest release.

        The changelog is a list of dictionaries where keys are version numbers and values are the changelog text.
        """
        changelog = []
        for release in mod_db_info["mod"]["releases"]:
            release_version = parse_version(release["modversion"])
            valid_release = (
                self.current_vs_version in release["tags"]
                and release_version > current_mod_version
            )
            if valid_release:
                changelog.append({release["modversion"]: release["changelog"]})
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
                        mod_info["path"] = zip_path

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


class RichTextDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Only use rich text for child items (depth > 0)
        if index.parent().isValid():
            text = index.data()
            doc = QtGui.QTextDocument()
            doc.setHtml(text)
            painter.save()
            painter.translate(option.rect.topLeft())
            doc.setTextWidth(option.rect.width())
            ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
            doc.documentLayout().draw(painter, ctx)
            painter.restore()
        else:
            # Use default painting for top-level items (shows checkbox)
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if index.parent().isValid():
            text = index.data()
            doc = QtGui.QTextDocument()
            doc.setHtml(text)
            doc.setTextWidth(option.rect.width())
            return QSize(int(doc.idealWidth()), int(doc.size().height()))
        else:
            return super().sizeHint(option, index)


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
