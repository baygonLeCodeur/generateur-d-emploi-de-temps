import sys
from PySide6.QtCore import QLibraryInfo
print("Qt Library Paths:")
print(QLibraryInfo.path(QLibraryInfo.PluginsPath))