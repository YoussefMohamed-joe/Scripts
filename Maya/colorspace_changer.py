#--------------------------------------------------------------------------#
# Arnold Colorspace Batch Changer - PERFECTLY FIXED (Feb 2026)
# Handles fileTextureName errors, validates Arnold file nodes only
# No deprecated flags, robust node detection
#--------------------------------------------------------------------------#
from __future__ import division, print_function
from maya import cmds as mc
from functools import partial

WIN_NAME = "ArnoldColorspaceChangerWindow"

#--------------------------------------------------------------------------#
# COLORSPACE OPTIONS
#--------------------------------------------------------------------------#
COLORSPACE_OPTIONS = [
    "Utility - Raw",
    "Utility - sRGB - Texture", 
    "Utility - Linear - sRGB",
    "Raw",
    "sRGB",
    "ACEScg",
    "scene-linear Rec.709-sRGB",
    "scene-linear DCI-P3 D65",
    "lin_rec709",
    "lin_srgb",
    "ACES - ACEScg",
    "ACES - ACES2065-1",
    "Input - Generic - sRGB - Texture",
]

SELECTED_COLORSPACE = "Utility - Raw"

#--------------------------------------------------------------------------#
# CORE FUNCTIONS - FULLY ROBUST
#--------------------------------------------------------------------------#
def _get_selected_file_nodes():
    """Get ONLY valid Arnold file nodes (with colorSpace attr) from selection/connections."""
    selection = mc.ls(sl=True)
    if not selection:
        return []
    
    file_nodes = []
    # Priority 1: Direct file nodes in selection
    for node in selection:
        if (mc.nodeType(node) == "file" and 
            mc.attributeQuery("colorSpace", node=node, exists=True)):
            file_nodes.append(node)
    
    # Priority 2: Connected file nodes from selection (skip compounds like fileTextureName)
    if not file_nodes:
        for node in selection:
            connections = mc.listConnections(node, type="file") or []
            for conn in connections:
                # Skip if compound path (contains .)
                if '.' in conn:
                    continue
                if (mc.nodeType(conn) == "file" and 
                    mc.attributeQuery("colorSpace", node=conn, exists=True)):
                    file_nodes.append(conn)
    
    return list(set(file_nodes))  # Deduplicate

def _set_colorspace(colorspace, *args):
    """Store selected colorspace."""
    global SELECTED_COLORSPACE
    SELECTED_COLORSPACE = colorspace
    print("Arnold Colorspace Changer: Selected colorspace = '{}'".format(colorspace))

def _apply_colorspace(*args):
    """Apply to VALID selected file nodes only."""
    global SELECTED_COLORSPACE
    mc.undoInfo(openChunk=True)
    try:
        file_nodes = _get_selected_file_nodes()
        if not file_nodes:
            mc.confirmDialog(
                title='No Valid Textures',
                message='No Arnold file nodes found.\n\nSelect:\n- File nodes directly\n- Materials/images (script finds connected files)\n\nUse "Select All File Nodes" button.',
                button=['OK'], defaultButton='OK'
            )
            return
        
        success_count = 0
        failed_nodes = []
        for file_node in file_nodes:
            try:
                mc.setAttr(file_node + ".colorSpace", SELECTED_COLORSPACE, type="string")
                success_count += 1
                print("✓ Applied '{}' to: {}".format(SELECTED_COLORSPACE, file_node))
            except Exception as e:
                failed_nodes.append(file_node)
                print("✗ Failed on {}: {}".format(file_node, str(e)))
        
        if success_count > 0:
            mc.confirmDialog(
                title='Success!',
                message='Changed {} file node(s) to "{}"'.format(success_count, SELECTED_COLORSPACE),
                button=['OK'], defaultButton='OK'
            )
            print("Arnold Colorspace Changer: Updated {} nodes to '{}'".format(success_count, SELECTED_COLORSPACE))
        
        if failed_nodes:
            mc.warning("Failed {} nodes: {}".format(len(failed_nodes), ", ".join(failed_nodes)))
            
    finally:
        mc.undoInfo(closeChunk=True)

def _apply_to_all_raw(*args):
    """Batch change all Raw textures."""
    global SELECTED_COLORSPACE
    mc.undoInfo(openChunk=True)
    try:
        all_files = mc.ls(type="file") or []
        raw_nodes = [n for n in all_files 
                    if mc.attributeQuery("colorSpace", node=n, exists=True) 
                    and ("raw" in mc.getAttr(n + ".colorSpace").lower())]
        
        if not raw_nodes:
            mc.warning("No Raw textures found")
            return
        
        result = mc.confirmDialog(
            title='Batch Raw → "{}"'.format(SELECTED_COLORSPACE),
            message='{} Raw textures → "{}"?'.format(len(raw_nodes), SELECTED_COLORSPACE),
            button=['Yes', 'No'], defaultButton='Yes', cancelButton='No'
        )
        if result == 'Yes':
            for node in raw_nodes:
                mc.setAttr(node + ".colorSpace", SELECTED_COLORSPACE, type="string")
            print("✓ Changed {} Raw → '{}'".format(len(raw_nodes), SELECTED_COLORSPACE))
    finally:
        mc.undoInfo(closeChunk=True)

def _apply_to_all_srgb(*args):
    """Batch change all sRGB textures."""
    global SELECTED_COLORSPACE
    mc.undoInfo(openChunk=True)
    try:
        all_files = mc.ls(type="file") or []
        srgb_nodes = [n for n in all_files 
                     if mc.attributeQuery("colorSpace", node=n, exists=True) 
                     and "srgb" in mc.getAttr(n + ".colorSpace").lower()]
        
        if not srgb_nodes:
            mc.warning("No sRGB textures found")
            return
        
        result = mc.confirmDialog(
            title='Batch sRGB → "{}"'.format(SELECTED_COLORSPACE),
            message='{} sRGB textures → "{}"?'.format(len(srgb_nodes), SELECTED_COLORSPACE),
            button=['Yes', 'No'], defaultButton='Yes', cancelButton='No'
        )
        if result == 'Yes':
            for node in srgb_nodes:
                mc.setAttr(node + ".colorSpace", SELECTED_COLORSPACE, type="string")
            print("✓ Changed {} sRGB → '{}'".format(len(srgb_nodes), SELECTED_COLORSPACE))
    finally:
        mc.undoInfo(closeChunk=True)

def _select_all_file_nodes(*args):
    """Select ALL valid Arnold file nodes."""
    all_files = [n for n in mc.ls(type="file") or [] 
                if mc.attributeQuery("colorSpace", node=n, exists=True)]
    if all_files:
        mc.select(all_files, replace=True)
        print("Arnold Colorspace Changer: Selected {} valid file nodes".format(len(all_files)))
    else:
        mc.warning("No Arnold file nodes in scene")

def _refresh_selection_count(*args):
    """Update count display."""
    count = len(_get_selected_file_nodes())
    if mc.text("selectionCountText", exists=True):
        mc.text("selectionCountText", edit=True, label="Valid Arnold Files: {}".format(count))
    return count

#--------------------------------------------------------------------------#
# UI BUILDER - PERFECT
#--------------------------------------------------------------------------#
def _build_ui():
    """Build production-ready UI."""
    global SELECTED_COLORSPACE
    if mc.window(WIN_NAME, exists=True):
        mc.deleteUI(WIN_NAME)
    
    mc.window(WIN_NAME, title="Arnold Colorspace Changer v2.0", sizeable=False, widthHeight=(420, 320))
    main_col = mc.columnLayout(adj=True, rs=8, cat=("both", 10), bgc=(0.18, 0.18, 0.22))
    
    # Header
    mc.separator(h=10, style="none")
    mc.text(label="🎨 ARNOLD COLORSPACE BATCH CHANGER", font="boldLabelFont", h=25)
    mc.separator(h=8, style="in")
    
    # Count
    mc.separator(h=5, style="none")
    mc.text("selectionCountText", label="Valid Files: 0", font="boldLabelFont", h=22, bgc=(0.3, 0.5, 0.3))
    mc.separator(h=5, style="none")
    
    # Colorspace
    mc.frameLayout(label="🎯 COLORSPACE", collapsable=False, mw=5, mh=8)
    mc.columnLayout(adj=True, rs=5, cat=("both", 5))
    mc.text(label="Select target colorspace:", al="left")
    mc.optionMenu("colorspaceMenu", label="Colorspace:", changeCommand=_set_colorspace, h=28)
    for cs in COLORSPACE_OPTIONS:
        mc.menuItem(label=cs)
    mc.setParent(".."); mc.setParent("..")
    
    # Main Apply
    mc.separator(h=12, style="none")
    mc.button(label="✅ APPLY TO SELECTED FILES", c=_apply_colorspace, h=45, bgc=(0.2, 0.7, 0.2))
    mc.button(label="🔄 Refresh Count", c=_refresh_selection_count, h=28, bgc=(0.3, 0.4, 0.6))
    
    # Quick Actions
    mc.separator(h=12, style="none")
    mc.frameLayout(label="⚡ QUICK ACTIONS", collapsable=False, mw=5, mh=8)
    mc.columnLayout(adj=True, rs=4, cat=("both", 5))
    mc.button(label="📋 Select ALL Arnold Files", c=_select_all_file_nodes, h=32, bgc=(0.4, 0.5, 0.7))
    mc.rowLayout(nc=2, cw2=(205, 205))
    mc.button(label="🔄 All Raw → Selected", c=_apply_to_all_raw, h=32, bgc=(0.8, 0.4, 0.2))
    mc.button(label="🔄 All sRGB → Selected", c=_apply_to_all_srgb, h=32, bgc=(0.2, 0.6, 0.8))
    mc.setParent(".."); mc.setParent(".."); mc.setParent("..")
    
    # Instructions
    mc.separator(h=12, style="none")
    mc.text(label="📖 HOW TO USE:", al="left", font="boldLabelFont")
    mc.text(label="1. Select materials/images → Refresh Count", al="left", font="smallPlainLabelFont")
    mc.text(label="2. Pick colorspace → Apply", al="left", font="smallPlainLabelFont")
    mc.text(label="3. Or use Quick Actions for scene-wide", al="left", font="smallPlainLabelFont")
    mc.separator(h=10, style="none")
    
    mc.showWindow(WIN_NAME)
    _refresh_selection_count()
    SELECTED_COLORSPACE = COLORSPACE_OPTIONS[0]

def show():
    """Launch tool."""
    _build_ui()

if __name__ == "__main__":
    show()
