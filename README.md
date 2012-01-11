===================================
Smart Highlighting Plugin for Gedit
===================================

Description
===========

Fork of http://code.google.com/p/smart-highlighting-gedit/ to enable GSettings
and refactor a bit.

Features
========

* Built with GObject Introspection, so works only on Gnome3
* Highlight occurrences of current selected text
* Match occurrences using regular expression
* Highlighting colors and matching options are selectable
* Match occurrences using plain text
* Multi-language support
    * English
    * Chinese

Installation
============

1. Run install.sh to install plugin files, locale files, and GSettings
  schema file. Without the GSettings schema installed, you cannot configure
  the colors or other settings.
2. Restart Gedit, then go to Edit->Preferences->Plugins and check the box next
  to `Smart Highlighting`.
