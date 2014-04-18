# -*- encoding:utf-8 -*-
# __init__.py
#
#
# Copyright 2012 Nemec
# Copyright 2010 swatch
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import re
import logging
import os.path
from gi.repository import GObject, Gtk, Gio, Gdk, Gedit, PeasGtk

import gettext
APP_NAME = 'smart-highlight'
#LOCALE_DIR = '/usr/share/locale'
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = '/usr/share/locale'
try:
    t = gettext.translation(APP_NAME, LOCALE_DIR)
    _ = t.gettext
except:
    pass

logging.basicConfig()
LOG_LEVEL = logging.WARN


class Settings(object):
    def __init__(self, schema):
        pass


class SmartHighlightingPlugin(
        GObject.Object, Gedit.ViewActivatable, PeasGtk.Configurable):
    __gtype_name__ = "SmartHighlightingPlugin"
    SCHEMA_KEY = "org.gnome.gedit.plugins." + APP_NAME
    default_settings = {
        'match-whole-word': True,
        'match-case': False,
        'foreground-color': '#ffffff',
        'background-color': '#000000'
    }
    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.logger = logging.getLogger(APP_NAME)
        self.logger.setLevel(LOG_LEVEL)
        self.update_colors = True
        self.settings = None
        if self.has_settings_schema:
            self.settings = Gio.Settings.new(self.SCHEMA_KEY)
        
            self.settings.connect('changed::foreground-color', self.on_color_change)
            self.settings.connect('changed::background-color', self.on_color_change)
        else:
            self.logger.warn("Settings schema not installed. "
                                                "Plugin will not be configurable.")

    def do_activate(self):
        self.view.get_buffer().connect('mark-set', self.on_textbuffer_markset_event)

    def do_update_state(self):
        self._plugin.update_ui()

    @property
    def has_settings_schema(self):
        return self.SCHEMA_KEY in Gio.Settings.list_schemas()

    def create_regex(self, pattern):
        pattern = re.escape(r'%s' % pattern)
        if ((self.has_settings_schema and
                    self.settings.get_boolean('match-whole-word')) or
                (not self.has_settings_schema and
                    self.default_settings['match-whole-word'])):
            pattern = r'\b%s\b' % pattern
            
        if ((self.has_settings_schema and
                    self.settings.get_boolean('match-case')) or
                (not self.has_settings_schema and
                    self.default_settings['match-case'])):
            regex = re.compile(pattern, re.MULTILINE)
        else:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        
        return regex

    def smart_highlighting_action(self, buf, search_pattern):
        self.smart_highlight_off(buf)
        if re.search('\W', search_pattern):
            return    # Only match up to one word
        regex = self.create_regex(search_pattern)
        start, end = buf.get_bounds()
        text = buf.get_text(start, end, True)
        
        for match in regex.finditer(text):
            self.smart_highlight_on(buf, match.start(), match.end() - match.start())
    
    def on_textbuffer_markset_event(self, textbuffer, iter, textmark):
        if textmark.get_name() == None:
            return
        if textbuffer.get_selection_bounds():
            start, end = textbuffer.get_selection_bounds()
            self.smart_highlighting_action(textbuffer, textbuffer.get_text(start, end, True))
        else:
            self.smart_highlight_off(textbuffer)


    def fill_tag_table(self, buf):
        """Set the foreground and background tag colors for the current buffer."""
        self.update_colors = False
        tag = buf.get_tag_table().lookup('smart_highlight')
        if tag != None:
            buf.get_tag_table().remove(tag)
        # Get valid foreground color
        fg = self.default_settings['foreground-color']
        if self.has_settings_schema:
            tmp_fg = self.settings.get_string('foreground-color')
            if Gdk.color_parse(tmp_fg):
                fg = tmp_fg
        # Get valid background color
        bg = self.default_settings['background-color']
        if self.has_settings_schema:
            tmp_bg = self.settings.get_string('background-color')
            if Gdk.color_parse(tmp_bg):
                bg = tmp_bg
        buf.create_tag("smart_highlight", foreground=fg, background=bg)

    def smart_highlight_on(self, buf, highlight_start, highlight_len):
        """Apply color tag to textbuffer at matched location."""
        if (self.update_colors or
                buf.get_tag_table().lookup('smart_highlight') == None):
            self.fill_tag_table(buf)
        buf.apply_tag_by_name('smart_highlight',
            buf.get_iter_at_offset(highlight_start),
            buf.get_iter_at_offset(highlight_start + highlight_len))
        
    def smart_highlight_off(self, buf):
        """Remove color tag from textbuffer."""
        start, end = buf.get_bounds()
        if (self.update_colors or
                buf.get_tag_table().lookup('smart_highlight') == None):
            self.fill_tag_table(buf)
        buf.remove_tag_by_name('smart_highlight', start, end)

    def do_create_configure_widget(self):
        return Config(self.has_settings_schema, self.settings).get_widget()

    def on_color_change(self, settings, key):
        self.update_colors = True


class Config(object):
    def __init__(self, has_settings_schema, settings):
        self.has_settings_schema = has_settings_schema
        self.settings = settings
        self.logger = logging.getLogger(APP_NAME)
        
    def get_widget(self):
        gladefile = os.path.join(os.path.dirname(__file__),"config.ui")
        UI = Gtk.Builder()
        UI.set_translation_domain('smart-highlight')
        UI.add_from_file(gladefile)
        widget = UI.get_object('smart_highlight_config')
        
        matchWholeWordCheckbutton = UI.get_object("matchWholeWordCheckbutton")
        matchCaseCheckbutton = UI.get_object("matchCaseCheckbutton")
        fgColorbutton = UI.get_object("fgColorbutton")
        bgColorbutton = UI.get_object("bgColorbutton")
        
        if self.has_settings_schema:
            matchWholeWordCheckbutton.set_active(self.settings.get_boolean('match-whole-word'))
            matchCaseCheckbutton.set_active(self.settings.get_boolean('match-case'))
            fgColorbutton.set_color(
                Gdk.color_parse(self.settings.get_string('foreground-color')) or
                    Gdk.color_parse(self.default_settings['foreground-color']))
            bgColorbutton.set_color(
                Gdk.color_parse(self.settings.get_string('background-color')) or
                    Gdk.color_parse(self.default_settings['background-color']))
            
            signals = {
                "on_matchWholeWordCheckbutton_toggled": self.on_matchWholeWordCheckbutton_toggled,
                "on_matchCaseCheckbutton_toggled": self.on_matchCaseCheckbutton_toggled,
                "on_fgColorbutton_color_set": self.on_fgColorbutton_color_set,
                "on_bgColorbutton_color_set": self.on_bgColorbutton_color_set
            }
            UI.connect_signals(signals)
        else:
            self.logger.warn("Configuration disabled because settings schema "
                                                "is not installed.")
            widget.set_sensitive(False)
        
        return widget

    def on_matchWholeWordCheckbutton_toggled(self, widget):
        self.settings.set_boolean('match-whole-word', widget.get_active())
        
    def on_matchCaseCheckbutton_toggled(self, widget):
        self.settings.set_boolean('match-case', widget.get_active())
        
    def on_fgColorbutton_color_set(self, widget):
        self.settings.set_string('foreground-color', widget.get_color().to_string())
        
    def on_bgColorbutton_color_set(self, widget):
        self.settings.set_string('background-color', widget.get_color().to_string())
