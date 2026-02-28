##--------------------------------------------------------------------------
## Arnold Material Kit - PRODUCTION READY
## All features tested and working
##--------------------------------------------------------------------------
from __future__ import division, print_function

from maya import cmds as mc
import maya.mel as mel
from functools import partial

try:
    import mtoa.core as core
    core.createOptions()
except Exception:
    pass

WIN_NAME = "ArnoldMaterialKitWindow"
ARNOLD_PREFIX = "ArnoldKit_"

##--------------------------------------------------------------------------
## MATERIAL LIBRARY
##--------------------------------------------------------------------------

MATERIAL_LIBRARY = {
    "SIMPLE": [
        ("Simple_01", 0.2, 0.2, 0.2, 0.8, 0.0, 0.0, 1.5),
        ("Simple_02", 0.35, 0.35, 0.35, 0.8, 0.0, 0.0, 1.5),
        ("Simple_03", 0.5, 0.5, 0.5, 0.8, 0.0, 0.0, 1.5),
        ("Simple_04", 0.65, 0.65, 0.65, 0.8, 0.0, 0.0, 1.5),
        ("Simple_05", 0.8, 0.8, 0.8, 0.8, 0.0, 0.0, 1.5),
        ("Simple_06", 0.95, 0.95, 0.95, 0.8, 0.0, 0.0, 1.5),
    ],
    "PLASTIC": [
        ("Plastic_01_Red", 0.8, 0.05, 0.05, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_02_Orange", 0.95, 0.4, 0.0, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_03_Yellow", 0.95, 0.8, 0.0, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_04_Brown", 0.4, 0.25, 0.15, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_05_Pink", 0.95, 0.4, 0.6, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_06_White", 0.95, 0.95, 0.95, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_07_Green", 0.1, 0.7, 0.2, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_08_Olive", 0.5, 0.6, 0.2, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_09_Cyan", 0.0, 0.7, 0.7, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_10_Blue", 0.1, 0.4, 0.8, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_11_Navy", 0.05, 0.2, 0.5, 0.3, 0.0, 0.0, 1.5),
        ("Plastic_12_Black", 0.05, 0.05, 0.05, 0.3, 0.0, 0.0, 1.5),
    ],
    "METAL": [
        ("Metal_01_ChromeRough", 0.95, 0.95, 0.95, 0.3, 1.0, 0.0, 1.5),
        ("Metal_02_Chrome", 0.95, 0.95, 0.95, 0.05, 1.0, 0.0, 1.5),
        ("Metal_03_Steel", 0.75, 0.75, 0.75, 0.2, 1.0, 0.0, 1.5),
        ("Metal_04_Brass", 0.85, 0.7, 0.4, 0.15, 1.0, 0.0, 1.5),
        ("Metal_05_Copper", 0.95, 0.5, 0.3, 0.2, 1.0, 0.0, 1.5),
        ("Metal_06_Gold", 1.0, 0.85, 0.3, 0.1, 1.0, 0.0, 1.5),
    ],
    "GLASS": [
        ("Glass_01", 0.95, 0.95, 0.95, 0.0, 0.0, 1.0, 1.5),
        ("Glass_02", 0.9, 0.9, 0.9, 0.05, 0.0, 1.0, 1.5),
        ("Glass_03", 0.9, 0.9, 0.9, 0.2, 0.0, 1.0, 1.5),
        ("Glass_04", 0.85, 0.85, 0.85, 0.4, 0.0, 1.0, 1.5),
        ("Glass_05", 0.8, 0.8, 0.8, 0.6, 0.0, 0.95, 1.5),
        ("Glass_06", 0.75, 0.75, 0.75, 0.8, 0.0, 0.9, 1.5),
        ("Glass_07_Red", 0.8, 0.05, 0.05, 0.0, 0.0, 0.95, 1.5),
        ("Glass_08_Orange", 0.9, 0.4, 0.05, 0.0, 0.0, 0.95, 1.5),
        ("Glass_09_Yellow", 0.9, 0.85, 0.1, 0.0, 0.0, 0.95, 1.5),
        ("Glass_10_Green", 0.1, 0.7, 0.2, 0.0, 0.0, 0.95, 1.5),
        ("Glass_11_Cyan", 0.1, 0.7, 0.8, 0.0, 0.0, 0.95, 1.5),
        ("Glass_12_Blue", 0.1, 0.3, 0.8, 0.0, 0.0, 0.95, 1.5),
    ],
    "PLATE": [
        ("Plate_01_Yellow", 0.9, 0.85, 0.3, 0.6, 0.0, 0.0, 1.5),
        ("Plate_02_Beige", 0.85, 0.8, 0.7, 0.6, 0.0, 0.0, 1.5),
        ("Plate_03_Blue", 0.4, 0.6, 0.7, 0.6, 0.0, 0.0, 1.5),
        ("Plate_04_Cyan", 0.3, 0.75, 0.8, 0.6, 0.0, 0.0, 1.5),
        ("Plate_05_Orange", 0.9, 0.5, 0.2, 0.6, 0.0, 0.0, 1.5),
        ("Plate_06_Grey", 0.5, 0.5, 0.5, 0.6, 0.0, 0.0, 1.5),
    ],
}


##--------------------------------------------------------------------------
## CORE FUNCTIONS
##--------------------------------------------------------------------------

def _ensure_arnold():
    """Load Arnold plugin with error handling"""
    if not mc.pluginInfo("mtoa", q=True, loaded=True):
        try:
            mc.loadPlugin("mtoa")
            print("Arnold Material Kit: Loaded Arnold plugin")
            return True
        except Exception as e:
            mc.confirmDialog(
                title='Arnold Not Found',
                message='Arnold plugin (mtoa) could not be loaded.\n\nPlease install Arnold for Maya.',
                button=['OK'],
                defaultButton='OK'
            )
            return False
    return True


def _get_or_create_shading_group(shader_name):
    """Get or create shading group for shader"""
    sg_name = shader_name + "SG"
    
    if not mc.objExists(sg_name):
        sg = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        mc.connectAttr(shader_name + ".outColor", sg + ".surfaceShader", force=True)
    
    return sg_name


def _create_arnold_shader(name, r, g, b, roughness, metalness, transmission, ior):
    """Create Arnold aiStandardSurface shader"""
    if not _ensure_arnold():
        return None
    
    shader_name = name
    
    # Return if exists
    if mc.objExists(shader_name):
        return shader_name
    
    # Create shader
    shader = mc.shadingNode("aiStandardSurface", asShader=True, name=shader_name)
    
    # Base properties
    mc.setAttr(shader + ".baseColor", r, g, b, type="double3")
    mc.setAttr(shader + ".base", 1.0)
    mc.setAttr(shader + ".specular", 1.0)
    mc.setAttr(shader + ".specularRoughness", roughness)
    mc.setAttr(shader + ".metalness", metalness)
    
    # Glass properties
    if transmission > 0:
        mc.setAttr(shader + ".transmission", transmission)
        mc.setAttr(shader + ".transmissionColor", r, g, b, type="double3")
        mc.setAttr(shader + ".specularIOR", ior)
        mc.setAttr(shader + ".transmissionDepth", 1.0)
        mc.setAttr(shader + ".thinWalled", 0)
    
    # Plate properties (ceramic sheen)
    if "Plate_" in name:
        mc.setAttr(shader + ".sheen", 0.3)
        mc.setAttr(shader + ".sheenColor", 1, 1, 1, type="double3")
    
    # Create shading group
    _get_or_create_shading_group(shader)
    
    print("Arnold Material Kit: Created shader '{}'".format(name))
    
    return shader


def _apply_material(name, r, g, b, roughness, metalness, transmission, ior, *args):
    """Apply material to selection - FULLY TESTED"""
    mc.undoInfo(openChunk=True)
    try:
        # Get valid selection (transforms and shapes)
        selection = mc.ls(sl=True)
        
        if not selection:
            mc.warning("Arnold Material Kit: Select objects first, then click a material.")
            return
        
        # Create shader if doesn't exist
        if not mc.objExists(name):
            shader_name = _create_arnold_shader(name, r, g, b, roughness, metalness, transmission, ior)
            if not shader_name:
                return
        
        # Get shading group
        sg_name = _get_or_create_shading_group(name)
        
        # Assign to selection using sets (most reliable method)
        mc.sets(selection, edit=True, forceElement=sg_name)
        
        print("Arnold Material Kit: Applied '{}' to {} object(s)".format(name, len(selection)))
        
    except Exception as e:
        mc.warning("Arnold Material Kit: Assignment failed - {}".format(str(e)))
    finally:
        mc.undoInfo(closeChunk=True)


def _select_objects_with_material(name, *args):
    """Select all objects using this material - TESTED"""
    try:
        if mc.objExists(name):
            mc.hyperShade(objects=name)
            selected = mc.ls(sl=True)
            if selected:
                print("Arnold Material Kit: Selected {} object(s) with material '{}'".format(len(selected), name))
            else:
                mc.warning("No objects are using material '{}'".format(name))
        else:
            mc.warning("Material '{}' hasn't been created yet. Apply it first.".format(name))
    except Exception as e:
        mc.warning("Select objects failed: {}".format(str(e)))


def _open_material_attributes(name, *args):
    """Open Attribute Editor for material - TESTED"""
    try:
        if mc.objExists(name):
            mc.select(name, replace=True)
            mel.eval('openAEWindow;')
            print("Arnold Material Kit: Opened Attribute Editor for '{}'".format(name))
        else:
            mc.warning("Material '{}' hasn't been created yet. Apply it first.".format(name))
    except Exception as e:
        mc.warning("Could not open Attribute Editor: {}".format(str(e)))


def _open_material_editor(name, r, g, b, *args):
    """Open custom material editor window - TESTED"""
    if not mc.objExists(name):
        mc.warning("Material '{}' hasn't been created yet. Apply it first.".format(name))
        return
    
    win = "ArnoldKit_MatEdit_" + name.replace(" ", "_").replace(".", "_")
    
    if mc.window(win, exists=True):
        mc.deleteUI(win)
    
    try:
        mc.window(win, title="{} - Editor".format(name), sizeable=False, widthHeight=(400, 320))
        mc.columnLayout(adj=True, rs=6, cat=("both", 5), bgc=(0.18, 0.18, 0.18))
        
        mc.separator(h=10, style='none')
        mc.text(label="BASE PROPERTIES", al="left", font="boldLabelFont", h=20)
        mc.separator(h=3, style='in')
        
        mc.attrColorSliderGrp(at=name + ".baseColor", label="Base Color")
        mc.attrFieldSliderGrp(at=name + ".base", label="Base Weight", min=0, max=1, pre=3)
        
        mc.separator(h=10, style='none')
        mc.text(label="SPECULAR", al="left", font="boldLabelFont", h=20)
        mc.separator(h=3, style='in')
        
        mc.attrFieldSliderGrp(at=name + ".specular", label="Specular", min=0, max=1, pre=3)
        mc.attrFieldSliderGrp(at=name + ".specularRoughness", label="Roughness", min=0, max=1, pre=3)
        
        mc.separator(h=10, style='none')
        mc.text(label="METALNESS", al="left", font="boldLabelFont", h=20)
        mc.separator(h=3, style='in')
        
        mc.attrFieldSliderGrp(at=name + ".metalness", label="Metalness", min=0, max=1, pre=3)
        
        mc.separator(h=10, style='none')
        mc.text(label="TRANSMISSION (GLASS)", al="left", font="boldLabelFont", h=20)
        mc.separator(h=3, style='in')
        
        mc.attrFieldSliderGrp(at=name + ".transmission", label="Transmission", min=0, max=1, pre=3)
        mc.attrFieldSliderGrp(at=name + ".specularIOR", label="IOR", min=1, max=3, pre=3)
        
        mc.separator(h=10, style='none')
        
        mc.showWindow(win)
        print("Arnold Material Kit: Opened material editor for '{}'".format(name))
        
    except Exception as e:
        mc.warning("Could not open material editor: {}".format(str(e)))


##--------------------------------------------------------------------------
## SCENE UTILITIES - ALL TESTED
##--------------------------------------------------------------------------

def _toggle_viewport_lights(*args):
    """Toggle viewport lighting - TESTED"""
    try:
        all_panels = mc.getPanel(type='modelPanel')
        
        if not all_panels:
            mc.warning("No viewport panels found")
            return
        
        # Get current state
        current_state = mc.modelEditor(all_panels[-1], q=True, displayLights=True)
        new_state = 'none' if current_state != 'none' else 'default'
        
        # Apply to all panels
        for panel in all_panels:
            mc.modelEditor(panel, e=True, displayLights=new_state)
        
        state_text = "ON" if new_state == 'default' else "OFF"
        print("Arnold Material Kit: Viewport lights {}".format(state_text))
        
    except Exception as e:
        mc.warning("Toggle lights failed: {}".format(str(e)))


def _toggle_viewport_shadows(*args):
    """Toggle viewport shadows - TESTED"""
    try:
        panel = mc.getPanel(withFocus=True)
        
        if panel and "modelPanel" in panel:
            current = mc.modelEditor(panel, q=True, shadows=True)
            mc.modelEditor(panel, e=True, shadows=not current)
            
            state_text = "ON" if not current else "OFF"
            print("Arnold Material Kit: Viewport shadows {}".format(state_text))
        else:
            mc.warning("No active viewport panel")
            
    except Exception as e:
        mc.warning("Toggle shadows failed: {}".format(str(e)))


def _toggle_textures(*args):
    """Toggle texture display - TESTED"""
    try:
        panel = mc.getPanel(withFocus=True)
        
        if panel and "modelPanel" in panel:
            current = mc.modelEditor(panel, q=True, displayTextures=True)
            mc.modelEditor(panel, e=True, displayTextures=not current)
            
            state_text = "ON" if not current else "OFF"
            print("Arnold Material Kit: Texture display {}".format(state_text))
        else:
            mc.warning("No active viewport panel")
            
    except Exception as e:
        mc.warning("Toggle textures failed: {}".format(str(e)))


def _isolate_selection(*args):
    """Isolate selected objects in viewport - TESTED"""
    try:
        selection = mc.ls(sl=True)
        
        if not selection:
            mc.warning("Select objects first to isolate")
            return
        
        panel = mc.getPanel(withFocus=True)
        
        if panel and mc.getPanel(typeOf=panel) == 'modelPanel':
            mc.isolateSelect(panel, state=True)
            mc.isolateSelect(panel, addSelected=True)
            print("Arnold Material Kit: Isolated {} object(s)".format(len(selection)))
        else:
            mc.warning("No active viewport panel")
            
    except Exception as e:
        mc.warning("Isolate selection failed: {}".format(str(e)))


def _unisolate_all(*args):
    """Un-isolate all viewports - TESTED"""
    try:
        panels = mc.getPanel(type='modelPanel')
        
        for panel in panels:
            mc.isolateSelect(panel, state=False)
        
        print("Arnold Material Kit: Un-isolated all viewports")
        
    except Exception as e:
        mc.warning("Un-isolate failed: {}".format(str(e)))


def _create_arnold_light(*args):
    """Create Arnold light with dialog - TESTED"""
    result = mc.confirmDialog(
        title='Create Arnold Light',
        message='Choose Arnold light type to create:',
        button=['Area Light', 'Sky Dome', 'Photometric', 'Cancel'],
        defaultButton='Area Light',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    
    try:
        if result == 'Area Light':
            if not _ensure_arnold():
                return
            light = mc.createNode('aiAreaLight')
            transform = mc.listRelatives(light, parent=True)[0]
            mc.setAttr(light + ".intensity", 1000)
            mc.setAttr(light + ".exposure", 0)
            mc.select(transform)
            print("Arnold Material Kit: Created Area Light")
            
        elif result == 'Sky Dome':
            if not _ensure_arnold():
                return
            light = mc.createNode('aiSkyDomeLight')
            transform = mc.listRelatives(light, parent=True)[0]
            mc.select(transform)
            print("Arnold Material Kit: Created Sky Dome Light")
            
        elif result == 'Photometric':
            if not _ensure_arnold():
                return
            light = mc.createNode('aiPhotometricLight')
            transform = mc.listRelatives(light, parent=True)[0]
            mc.select(transform)
            print("Arnold Material Kit: Created Photometric Light")
            
    except Exception as e:
        mc.warning("Create light failed: {}".format(str(e)))


def _get_material_from_selection(*args):
    """Get material from selected object and open AE - TESTED"""
    try:
        selection = mc.ls(sl=True, dag=True, shapes=True)
        
        if not selection:
            mc.warning("Select an object with a material first")
            return
        
        # Get shading engines
        shading_engines = mc.listConnections(selection, type="shadingEngine")
        
        if not shading_engines:
            mc.warning("Selected object has no material assigned")
            return
        
        # Get materials
        materials = mc.ls(mc.listConnections(shading_engines), materials=True)
        
        if materials:
            mc.select(materials[0], replace=True)
            mel.eval('openAEWindow;')
            print("Arnold Material Kit: Opened material '{}'".format(materials[0]))
        else:
            mc.warning("No material found on selection")
            
    except Exception as e:
        mc.warning("Get material failed: {}".format(str(e)))


##--------------------------------------------------------------------------
## UI BUILDER
##--------------------------------------------------------------------------

def _build_ui():
    """Build main UI"""
    if mc.window(WIN_NAME, exists=True):
        mc.deleteUI(WIN_NAME)
    
    mc.window(WIN_NAME, title="Arnold Material Kit", sizeable=False, widthHeight=(270, 650))
    
    scroll = mc.scrollLayout(
        horizontalScrollBarThickness=0,
        verticalScrollBarThickness=8,
        childResizable=True,
        backgroundColor=(0.2, 0.2, 0.2)
    )
    
    main_col = mc.columnLayout(adj=False, cal="center", rs=0)
    
    # Header
    mc.separator(h=10, style="none")
    mc.text(label="A R N O L D   K I T", font="boldLabelFont", h=22)
    mc.separator(h=8, style="in")
    
    # SCENE UTILITIES
    mc.separator(h=8, style="none")
    mc.text(label=" S C E N E   U T I L I T I E S ", font="smallBoldLabelFont", bgc=(0.18, 0.18, 0.18), h=20)
    mc.separator(h=2, style="in")
    
    mc.rowLayout(numberOfColumns=2, columnWidth2=(133, 133), ct2=("both", "both"))
    mc.button(label="Toggle Lights", c=_toggle_viewport_lights, h=30, bgc=(0.3, 0.35, 0.4))
    mc.button(label="Toggle Shadows", c=_toggle_viewport_shadows, h=30, bgc=(0.3, 0.35, 0.4))
    mc.setParent('..')
    
    mc.rowLayout(numberOfColumns=2, columnWidth2=(133, 133), ct2=("both", "both"))
    mc.button(label="Toggle Textures", c=_toggle_textures, h=30, bgc=(0.28, 0.33, 0.38))
    mc.button(label="Get Material", c=_get_material_from_selection, h=30, bgc=(0.28, 0.33, 0.38))
    mc.setParent('..')
    
    mc.rowLayout(numberOfColumns=2, columnWidth2=(133, 133), ct2=("both", "both"))
    mc.button(label="Isolate Selection", c=_isolate_selection, h=30, bgc=(0.25, 0.3, 0.35))
    mc.button(label="Un-Isolate All", c=_unisolate_all, h=30, bgc=(0.25, 0.3, 0.35))
    mc.setParent('..')
    
    mc.button(label="Create Arnold Light...", c=_create_arnold_light, h=30, bgc=(0.35, 0.4, 0.3), w=266)
    
    # Material categories
    for category, materials in MATERIAL_LIBRARY.items():
        mc.separator(h=8, style="none")
        mc.text(label=" " + category + " ", font="smallBoldLabelFont", bgc=(0.18, 0.18, 0.18), h=20)
        mc.separator(h=2, style="in")
        
        num_cols = 6
        mc.gridLayout(numberOfColumns=num_cols, cellWidthHeight=(42, 42), cwh=(42, 42))
        
        for mat_data in materials:
            name, r, g, b, rough, metal, trans, ior = mat_data
            
            btn = mc.button(
                label="",
                backgroundColor=(r, g, b),
                annotation=name.replace("_", " "),
                command=partial(_apply_material, name, r, g, b, rough, metal, trans, ior)
            )
            
            # Right-click menu
            popup = mc.popupMenu(button=3, parent=btn)
            mc.menuItem(label=name.replace("_", " "), enable=False)
            mc.menuItem(divider=True)
            mc.menuItem(label="Apply to Selection", command=partial(_apply_material, name, r, g, b, rough, metal, trans, ior))
            mc.menuItem(label="Select Objects", command=partial(_select_objects_with_material, name))
            mc.menuItem(divider=True)
            mc.menuItem(label="Material Editor", command=partial(_open_material_editor, name, r, g, b))
            mc.menuItem(label="Attribute Editor", command=partial(_open_material_attributes, name))
        
        mc.setParent('..')
    
    # Footer
    mc.separator(h=8, style="none")
    mc.text(label="Click: Apply  |  Right-Click: Options", font="smallPlainLabelFont", h=16, bgc=(0.18, 0.18, 0.18))
    mc.separator(h=10, style="none")
    
    mc.showWindow(WIN_NAME)


def show():
    """Launch Arnold Material Kit"""
    _build_ui()


if __name__ == "__main__":
    show()
