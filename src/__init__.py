from .vs_mod_updater import VSModUpdaterPlugin
import mobase  # type: ignore

def createPlugin() -> mobase.IPlugin:
    return VSModUpdaterPlugin()