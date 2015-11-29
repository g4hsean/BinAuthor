import sys
import imp
#sys.path.append(r'C:\\Users\\titan\\Desktop\\BinAuthor\\BinAuthor.py')
sys.path.append(r'C:\\Users\\titan\\Desktop\\BinAuthor\\')
plugin = imp.load_source(__name__, 'C:\\Users\\titan\\Desktop\\BinAuthor\\BinAuthor.py')

# Export the plugin entry
PLUGIN_ENTRY = plugin.PLUGIN_ENTRY