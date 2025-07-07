from .vs_updater import VSUpdaterPlugin
import mobase  # type: ignore

def createPlugin() -> mobase.IPlugin:
    return VSUpdaterPlugin()