#!/bin/sh


PLUGIN_NAME="smart_highlight"
SCHEMA_NAME="org.gnome.gedit.plugins.smart-highlight.gschema.xml"

# gedit plugin directory
PLUGIN_DEST=~/.local/share/gedit/plugins/

# create it
mkdir -p ${PLUGIN_DEST}

# remove previous version and currect version of plugin
rm -r ${PLUGIN_DEST}/${PLUGIN_NAME}
rm ${PLUGIN_DEST}/${PLUGIN_NAME}.plugin

# install current verion of plugin
cp -rv ${PLUGIN_NAME} ${PLUGIN_DEST}
cp -v ${PLUGIN_NAME}.plugin ${PLUGIN_DEST}


LOCALE_DEST=/usr/share/locale

echo "Requesting root to install locale files."
sudo cp -rv ${PLUGIN_NAME}/locale/* ${LOCALE_DEST}

echo "Requesting root to install GSettings schema."
sudo cp smart_highlight/$SCHEMA_NAME /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
