'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from . import ui_properties, ui_panels, pref_operators, pref_panels, ui_operators


classes = (
    pref_operators.PREFERENCES_OT_CGT_install_dependencies_button,
    pref_operators.PREFERENCES_OT_CGT_uninstall_dependencies_button,
    pref_panels.BLENDARMOCAP_CGT_preferences,

    ui_properties.CGTProperties,

    ui_operators.UI_CGT_transfer_anim_button,
    ui_operators.UI_CGT_toggle_drivers_button,
    ui_operators.UI_CGT_smooth_empties_in_col,
    ui_operators.WM_CGT_modal_detection_operator,
    ui_operators.WM_CGT_modal_connection_listener_operator,
    ui_panels.UI_PT_CGT_main_panel,
    # ui_panels.UI_PT_RemappingPanel
)


def register():
    print('Registing BlendArMocap\n')
    for _class in classes:
        register_class(_class)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CGTProperties)


def unregister():
    print("Unregister BlendArMocap")
    for cls in classes:
        try:
            unregister_class(cls)
        except RuntimeError:
            # Class may not be registered
            pass
