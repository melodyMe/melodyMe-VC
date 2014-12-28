#!/bin/sh

productbuild \
    --component "dist/melodyMe Video Converter.app" /Applications \
    --sign '3rd Party Mac Developer Installer: PlexiLabs' \
    --product setup-files/osx/mvc3_definition.plist mvc3.pkg
