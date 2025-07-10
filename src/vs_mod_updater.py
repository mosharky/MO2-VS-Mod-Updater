from .utils import *

import zipfile
import json
import urllib.request
import logging
import concurrent.futures
import mobase  # type: ignore
import PyQt6.QtGui as QtGui  # type: ignore
import PyQt6.QtWidgets as QtWidgets  # type: ignore

from PyQt6.QtCore import Qt, QSize  # type: ignore
from typing import List
from pathlib import Path


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

        # Set window icon
        icon_path = Path(__file__).parent / "icons" / "logo.ico"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        # Left layout
        left_vertical_layout = QtWidgets.QVBoxLayout()
        check_updates_btn = QtWidgets.QPushButton("🔄 Check for Updates", self)
        check_updates_btn.clicked.connect(self.check_for_updates)
        left_vertical_layout.addWidget(check_updates_btn)

        # Right layout
        right_vertical_layout = QtWidgets.QVBoxLayout()
        update_mods_btn = QtWidgets.QPushButton("Update Mods ⬇️", self)
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

        # Enable rich text rendering in the tree view (only applies to child items)
        self.tree.setItemDelegateForColumn(0, RichTextDelegate(self.tree))
        self.tree.setItemDelegateForColumn(1, RichTextDelegate(self.tree))
        self.tree.setWordWrap(True)

        main_layout.addWidget(self.tree)
        self.tree.setModel(self.model)
        self.setLayout(main_layout)
        self.tree.setColumnWidth(0, 500)

    def update_mods(self):
        """Downloads all updates for mods in MO2 that are checked."""
        # Check if there are any available updates
        if not self.mod_updates:
            QtWidgets.QMessageBox.critical(
                self, "Error", "No mod updates found. Please check for updates first."
            )
            return

        # Count how many mods are selected for update
        selected_count = 0
        for row in range(self.model.rowCount()):
            update_item = self.model.item(row, 0)
            if (
                update_item is not None
                and update_item.checkState() == Qt.CheckState.Checked
            ):
                selected_count += 1

        if selected_count == 0:
            QtWidgets.QMessageBox.information(
                self, "No Selection", "No mods are selected for update."
            )
            return

        # Show confirmation dialog
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Updates",
            f"Are you sure you want to update {selected_count} mod(s)?\n\n"
            "This will download new versions and replace the existing mod files.",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.Yes,
        )

        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        # Track successful updates
        successful_updates = 0
        failed_updates = []

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
                mod_name = update_data["name"]

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
                    successful_updates += 1
                except Exception as ex:
                    logging.critical(f"Error downloading {filename}: {ex}")
                    failed_updates.append(mod_name)

        # Show completion dialog
        if successful_updates > 0 or failed_updates:
            if failed_updates:
                # Some updates failed
                failed_list = "\n".join(f"• {mod}" for mod in failed_updates)
                QtWidgets.QMessageBox.warning(
                    self,
                    "Updated Mods with Errors",
                    f"Successfully updated {successful_updates} mod(s).\n\n"
                    f"Failed to update {len(failed_updates)} mod(s):\n{failed_list}\n\n"
                    "Check the logs for more details about the failed updates.",
                )
            else:
                # All updates successful
                QtWidgets.QMessageBox.information(
                    self,
                    "Updated Mods Successfully",
                    f"Successfully updated {successful_updates} mod(s)!\n\n",
                )

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
                logging.critical(f"Error checking mod {mod_id}: {ex}")

        # Run checks in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(safe_check, self.mods_data.keys()))

        loading_label.hide()

        if not self.mod_updates:
            QtWidgets.QMessageBox.information(
                self, "No Updates", "All mods are up to date :)"
            )
        else:
            logging.info(f"Found {len(self.mod_updates)} mod updates.")

        # Sort mod updates by name
        self.mod_updates.sort(key=lambda x: x["name"])

        # Clear the model and populate it with mod updates
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Name", "Version"])

        for update in self.mod_updates:
            # Create item to display the update
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

    def check_mod_for_update(self, mod_id: str):
        mod_db_info = self.get_mod_info_from_api(mod_id)
        current_mod_version = self.mods_data[mod_id]["version"]
        current_mod_version_parsed = parse_version(current_mod_version)

        latest_mod_version = None
        latest_mod_release = None
        # Getting latest mod release that supports current VS version
        for release in mod_db_info["mod"]["releases"]:
            release_version = release["modversion"]
            release_version_parsed = parse_version(release_version)
            latest_supported_vs_version = parse_version(release["tags"][-1])
            current_vs_version_parsed = parse_version(self.current_vs_version)
            # An update is found if the release version is greater than the current mod version
            # and the current VS version is supported by the release
            # or if the current VS version's minor version matches the latest supported VS version's minor version
            if release_version_parsed > current_mod_version_parsed and (
                self.current_vs_version in release["tags"]
                or (
                    len(current_vs_version_parsed) >= 2
                    and len(latest_supported_vs_version) >= 2
                    and current_vs_version_parsed[1] == latest_supported_vs_version[1]
                )
            ):
                latest_mod_version = release["modversion"]
                latest_mod_release = release
                break
            # No update found
            elif current_mod_version_parsed >= release_version_parsed:
                return

        # If no update was found
        # and if 'current_mod_version_parsed >= release_version_parsed' was never reached
        if latest_mod_version is None or latest_mod_release is None:
            return

        self.mod_updates.append(
            {
                "mod_id": mod_id,
                "name": mod_db_info["mod"]["name"],
                "current_version": current_mod_version,
                "latest_version": latest_mod_version,
                "latest_release": latest_mod_release,
                "changelog": self.generate_changelog(
                    mod_db_info, current_mod_version_parsed
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
                    # ASSUMPTION: The last entry in the list is always the latest version
                    return data["gameversions"][-1]["name"]
                else:
                    logging.critical(f"Error: HTTP {response.status}")
                    return None
        except Exception as ex:
            logging.critical(f"Error fetching latest game versions: {ex}")
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
                    logging.critical(
                        f"Warning: modinfo.json not found in {zip_path.name}"
                    )

                zip_ref.close()

        except zipfile.BadZipFile:
            logging.critical(f"Error: {zip_path.name} is not a valid zip file")
        except json.JSONDecodeError:
            logging.critical(
                f"Error: Invalid JSON in modinfo.json from {zip_path.name}; could not update the mod. Report this to the mod author."
            )
        except Exception as ex:
            logging.critical(f"Error processing {zip_path.name}: {ex}")

        return mod_info

    def get_mod_info_from_api(self, mod_id: str) -> dict:
        """Returns all data from ModDB page"""
        data = {}
        try:
            with urllib.request.urlopen(f"{self.base_url}/mod/{mod_id}") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                else:
                    logging.critical(f"Error: HTTP {response.status}")
        except Exception as ex:
            logging.critical(f"Error fetching mod info: {ex}")
            raise
        return data


class RichTextDelegate(QtWidgets.QStyledItemDelegate):
    def is_dark_theme(self, option):
        """Detect if the current theme is dark by checking background color brightness."""
        bg_color = option.palette.color(QtGui.QPalette.ColorRole.Base)
        # Calculate luminance using the standard formula
        luminance = (
            0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
        ) / 255
        return luminance < 0.5

    def adjust_text_for_theme(self, text, is_dark):
        """Adjust text colors based on theme."""
        if is_dark:
            # Dark theme: use light colors
            text = text.replace("color: black", "color: #ffffff")
            text = text.replace("color: #000000", "color: #ffffff")
            text = text.replace("color: #000", "color: #fff")
            # If no color is specified, add default light color
            if "color:" not in text.lower() and not text.startswith("<div"):
                text = f'<span style="color: #ffffff;">{text}</span>'
            elif text.startswith("<div") and "color:" not in text.lower():
                text = text.replace("<div", '<div style="color: #ffffff;"')
            elif text.startswith("<i>") and "color:" not in text.lower():
                text = f'<span style="color: #cccccc;">{text}</span>'
        else:
            # Light theme: use dark colors (default)
            text = text.replace("color: white", "color: #000000")
            text = text.replace("color: #ffffff", "color: #000000")
            text = text.replace("color: #fff", "color: #000")
            # If no color is specified, add default dark color
            if "color:" not in text.lower() and not text.startswith("<div"):
                text = f'<span style="color: #000000;">{text}</span>'
            elif text.startswith("<div") and "color:" not in text.lower():
                text = text.replace("<div", '<div style="color: #000000;"')
            elif text.startswith("<i>") and "color:" not in text.lower():
                text = f'<span style="color: #666666;">{text}</span>'

        return text

    def paint(self, painter, option, index):
        # Only use rich text for child items (depth > 0)
        if index.parent().isValid():
            text = index.data()
            is_dark = self.is_dark_theme(option)
            text = self.adjust_text_for_theme(text, is_dark)

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
            is_dark = self.is_dark_theme(option)
            text = self.adjust_text_for_theme(text, is_dark)

            doc = QtGui.QTextDocument()
            doc.setHtml(text)
            doc.setTextWidth(option.rect.width())
            return QSize(int(doc.idealWidth()), int(doc.size().height()))
        else:
            return super().sizeHint(option, index)


class VSModUpdaterPlugin(mobase.IPluginTool):

    def __init__(self):
        self.__window = None
        # self.organizer = None
        self.__parentWidget = None

        super(VSModUpdaterPlugin, self).__init__()

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.organizer = organizer
        return True

    def name(self) -> str:
        return "VS Mod Updater"

    def author(self):
        return "mosharky"

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
        # Get the path to the icon file relative to this plugin file
        icon_path = Path(__file__).parent / "icons" / "logo.ico"
        return QtGui.QIcon(str(icon_path))

    def tooltip(self):
        return self.description()
