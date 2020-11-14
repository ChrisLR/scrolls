r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/pi/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *
######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "scrolls"

TELNET_PORTS = [4040]

GLOBAL_SCRIPTS = {
    'mobdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for mob data'
    },
    'objdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for obj data'
    },
    'roomdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for room data'
    },
    'booksdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage room for all books'
    }
}

CMDSET_UNLOGGEDIN = "evennia.contrib.menu_login.UnloggedinCmdSet"
BASE_BATCHPROCESS_PATHS += ["resources"]

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
