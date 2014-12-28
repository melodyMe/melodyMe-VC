import os
import sys

version = '1.0.0'

# platform-independent arguments for setup()
setup_args = {
    'name': 'melodyMe Video Converter',
    'description': 'melodyMe Video Converter is super simple way to convert almost any video to MP4, WebM (vp8), Ogg Theora, or for Android, iPhone, and more.',
    'author': 'PlexiLabs',
    'author_email': 'info@plexilabs.me',
    'url': 'http://video-converter.melodyme.net',
    'license': 'MIT',
    'version': version,
    'packages': [
        'mvc',
        'mvc.osx',
        'mvc.qtfaststart',
        'mvc.resources',
        'mvc.ui',
        'mvc.widgets',
        'mvc.widgets.gtk',
        'mvc.widgets.osx',
        'mvc.windows',
    ],
    'package_data': {
        'mvc.resources': [
            'converters/*.py',
            'images/*.*',
        ],
    },
}

if sys.platform.startswith("linux"):
    platform = 'linux'
elif sys.platform.startswith("win32"):
    platform = 'windows'
elif sys.platform.startswith("darwin"):
    platform = 'osx'
else:
    sys.stderr.write("Unknown platform: %s" % sys.platform)

root_dir = os.path.abspath(os.path.dirname(__file__))
setup_dir = os.path.join(root_dir, 'setup-files', platform)

script_vars = {
    'VERSION': version,
    'ROOT_DIR': root_dir,
    'SETUP_DIR': setup_dir,
    'SETUP_ARGS': setup_args,
}

execfile(os.path.join(setup_dir, 'setup.py'), script_vars)
