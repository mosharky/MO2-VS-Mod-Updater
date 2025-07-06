import mobase  # type: ignore
import PyQt6.QtGui as QtGui  # type: ignore
import PyQt6.QtWidgets as QtWidgets  # type: ignore
from PyQt6.QtCore import Qt  # type: ignore
from typing import List


class PluginWindow(QtWidgets.QDialog):
    def __init__(self, organizer, parent=None):
        self.__organizer = organizer


class VSUpdaterPlugin(mobase.IPluginTool):

    _organizer: mobase.IOrganizer

    def __init__(self):
        self.__window = None
        self.__organizer = None
        self.__parentWidget = None

        super(VSUpdaterPlugin, self).__init__()

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self._organizer = organizer
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
        self.__window = PluginWindow(self.__organizer)
        self.__window.setWindowTitle(self.name())
        self.__window.exec()

    def displayName(self) -> str:
        return self.name()

    def icon(self):
        return QtGui.QIcon("")

    def tooltip(self):
        return self.description()


def createPlugin() -> mobase.IPlugin:
    return VSUpdaterPlugin()
