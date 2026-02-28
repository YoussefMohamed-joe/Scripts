"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗██╗      ██████╗ ██╗   ║
║   ████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝██║     ██╔═══██╗██║   ║
║   ██╔██╗ ██║██║   ██║██║  ██║█████╗  █████╗  ██║     ██║   ██║██║   ║
║   ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ██╔══╝  ██║     ██║   ██║╚═╝   ║
║   ██║ ╚████║╚██████╔╝██████╔╝███████╗██║     ███████╗╚██████╔╝██╗   ║
║   ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ║
║                                                                      ║
║   Transfer Any Texture. Any Shader. Any Target.                      ║
║   Author  : Youssef El Qadi                                          ║
║   Version : 4.0.0 — Full Material + Auto Assign                     ║
║   Support : Maya 2020+                                               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import webbrowser
from collections import defaultdict
import maya.cmds as cmds

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2.QtCore import Qt
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtCore import Qt
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui

MAYA_VERSION = int(cmds.about(version=True).split(".")[0])

# ══════════════════════════════════════════════════════════════════════
#  AUTO-SUGGEST LOGIC
#  Best target material for each source type
# ══════════════════════════════════════════════════════════════════════

AUTO_SUGGEST = {
    "aiStandardSurface":        ("Redshift", "RedshiftStandardMaterial"),
    "standardSurface":          ("Arnold",   "aiStandardSurface"),
    "RedshiftStandardMaterial": ("Arnold",   "aiStandardSurface"),
    "RedshiftMaterial":         ("Arnold",   "aiStandardSurface"),
    "lambert":                  ("Maya",     "standardSurface"),
    "blinn":                    ("Maya",     "standardSurface"),
    "phong":                    ("Maya",     "standardSurface"),
    "phongE":                   ("Maya",     "standardSurface"),
}

# ══════════════════════════════════════════════════════════════════════
#  SMART NODE CONVERSION TABLE
# ══════════════════════════════════════════════════════════════════════

NODE_CONVERSION_TABLE = {
    "bump2d": {
        "Redshift": {
            "type":     "RedshiftBumpMap",
            "inputs":   {"bumpValue": "input"},
            "outputs":  {"outNormal": "out"},
            "post_set": {"inputType": 0},
        },
        "Arnold": {
            "type":    "bump2d",
            "inputs":  {"bumpValue": "bumpValue"},
            "outputs": {"outNormal": "outNormal"},
        },
        "Maya": {
            "type":    "bump2d",
            "inputs":  {"bumpValue": "bumpValue"},
            "outputs": {"outNormal": "outNormal"},
        },
    },
    "aiNormalMap": {
        "Redshift": {
            "type":     "RedshiftBumpMap",
            "inputs":   {"input": "input"},
            "outputs":  {"outValue": "out"},
            "post_set": {"inputType": 1},
        },
        "Arnold": {
            "type":    "aiNormalMap",
            "inputs":  {"input": "input"},
            "outputs": {"outValue": "outValue"},
        },
        "Maya": {
            "type":     "bump2d",
            "inputs":   {"input": "bumpValue"},
            "outputs":  {"outValue": "outNormal"},
            "post_set": {"bumpInterp": 1},
        },
    },
    "aiColorCorrect": {
        "Redshift": {
            "type":    "rsColorCorrect",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
        "Arnold": {
            "type":    "aiColorCorrect",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
        "Maya": {
            "type":    "colorCorrect",
            "inputs":  {"input": "inColor"},
            "outputs": {"outColor": "outColor"},
        },
    },
    "rsColorCorrect": {
        "Arnold": {
            "type":    "aiColorCorrect",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
        "Maya": {
            "type":    "colorCorrect",
            "inputs":  {"input": "inColor"},
            "outputs": {"outColor": "outColor"},
        },
        "Redshift": {
            "type":    "rsColorCorrect",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
    },
    "aiRange": {
        "Redshift": {
            "type":    "rsRange",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
        "Maya": {
            "type":    "remapValue",
            "inputs":  {"input": "inputValue"},
            "outputs": {"outColor": "outValue"},
        },
        "Arnold": {
            "type":    "aiRange",
            "inputs":  {"input": "input"},
            "outputs": {"outColor": "outColor"},
        },
    },
    "aiMultiply": {
        "Redshift": {
            "type":    "rsColorLayer",
            "inputs":  {"input1": "input1"},
            "outputs": {"outColor": "outColor"},
        },
        "Maya": {
            "type":    "multiplyDivide",
            "inputs":  {"input1": "input1"},
            "outputs": {"outColor": "output"},
        },
        "Arnold": {
            "type":    "aiMultiply",
            "inputs":  {"input1": "input1"},
            "outputs": {"outColor": "outColor"},
        },
    },
}

PASSTHROUGH_NODES = {
    "file", "place2dTexture", "colorCorrect",
    "remapValue", "remapColor", "remapHsv",
    "multiplyDivide", "clamp", "reverse",
    "blendColors", "condition", "ramp",
    "noise", "fractal", "stencil",
    "layeredTexture", "gammaCorrect",
    "hsvToRgb", "rgbToHsv",
    "unitConversion", "luminance",
}

# ══════════════════════════════════════════════════════════════════════
#  RENDERER / MATERIAL LISTS
# ══════════════════════════════════════════════════════════════════════

RENDERER_MATERIALS = {
    "Redshift": [
        "RedshiftStandardMaterial", "RedshiftArchitectural",
        "RedshiftCarPaint", "RedshiftHair", "RedshiftIncandescent",
        "RedshiftMaterial", "RedshiftMaterialBlender",
        "RedshiftMatteShadowCatcher", "RedshiftOSLSurfaceShader",
        "RedshiftOpenPBRMaterial", "RedshiftPrincipledHair",
        "RedshiftShaderSwitch", "RedshiftSkin", "RedshiftSprite",
        "RedshiftSubSurfaceScatter", "RedshiftToonMaterial",
    ],
    "Arnold": [
        "aiStandardSurface", "aiFlat", "aiAmbientOcclusion",
        "aiCarPaint", "aiHair", "aiLayerShader", "aiMatte",
        "aiMixShader", "aiShadowMatte", "aiSkin", "aiToon", "aiWireframe",
    ],
    "Maya": [
        "standardSurface", "lambert", "blinn",
        "phong", "phongE", "surfaceShader",
    ],
    "MASH": ["MASH"],
}

RENDERER_OPTIONS = list(RENDERER_MATERIALS.keys())

SUPPORTED_SOURCES = [
    "aiStandardSurface", "standardSurface",
    "lambert", "blinn", "phong", "phongE",
    "RedshiftStandardMaterial", "RedshiftMaterial",
]

# ══════════════════════════════════════════════════════════════════════
#  MASTER MAPPING TABLE  (textures + raw values)
#  Format: src_attr: { target_mat: (tgt_attr, preferred_plug) }
# ══════════════════════════════════════════════════════════════════════

MASTER_MAP = {
    "baseColor": {
        "RedshiftStandardMaterial": ("base_color",         "outColor"),
        "RedshiftMaterial":         ("diffuse_color",      "outColor"),
        "RedshiftArchitectural":    ("diffuse",            "outColor"),
        "RedshiftCarPaint":         ("base_color",         "outColor"),
        "RedshiftSkin":             ("overall_color",      "outColor"),
        "RedshiftToonMaterial":     ("base_color",         "outColor"),
        "RedshiftOpenPBRMaterial":  ("base_color",         "outColor"),
        "aiStandardSurface":        ("baseColor",          "outColor"),
        "aiFlat":                   ("color",              "outColor"),
        "aiToon":                   ("base_color",         "outColor"),
        "standardSurface":          ("baseColor",          "outColor"),
        "lambert":                  ("color",              "outColor"),
        "blinn":                    ("color",              "outColor"),
        "phong":                    ("color",              "outColor"),
        "phongE":                   ("color",              "outColor"),
        "surfaceShader":            ("outColor",           "outColor"),
        "MASH":                     ("MASH_Color.texture", "outColor"),
    },
    "color": {
        "RedshiftStandardMaterial": ("base_color",         "outColor"),
        "RedshiftMaterial":         ("diffuse_color",      "outColor"),
        "aiStandardSurface":        ("baseColor",          "outColor"),
        "standardSurface":          ("baseColor",          "outColor"),
        "lambert":                  ("color",              "outColor"),
        "blinn":                    ("color",              "outColor"),
        "phong":                    ("color",              "outColor"),
        "phongE":                   ("color",              "outColor"),
        "MASH":                     ("MASH_Color.texture", "outColor"),
    },
    "specularRoughness": {
        "RedshiftStandardMaterial": ("refl_roughness",     "outAlpha"),
        "RedshiftMaterial":         ("refl_roughness",     "outAlpha"),
        "RedshiftOpenPBRMaterial":  ("specular_roughness", "outAlpha"),
        "RedshiftToonMaterial":     ("refl_roughness",     "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",  "outAlpha"),
        "standardSurface":          ("specularRoughness",  "outAlpha"),
        "blinn":                    ("eccentricity",       "outAlpha"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "eccentricity": {
        "RedshiftStandardMaterial": ("refl_roughness",     "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",  "outAlpha"),
        "standardSurface":          ("specularRoughness",  "outAlpha"),
    },
    "roughness": {
        "RedshiftStandardMaterial": ("refl_roughness",     "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",  "outAlpha"),
        "standardSurface":          ("specularRoughness",  "outAlpha"),
    },
    "metalness": {
        "RedshiftStandardMaterial": ("metalness",          "outAlpha"),
        "RedshiftOpenPBRMaterial":  ("metalness",          "outAlpha"),
        "aiStandardSurface":        ("metalness",          "outAlpha"),
        "standardSurface":          ("metalness",          "outAlpha"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "specularColor": {
        "RedshiftStandardMaterial": ("refl_color",         "outColor"),
        "RedshiftMaterial":         ("refl_color",         "outColor"),
        "aiStandardSurface":        ("specularColor",      "outColor"),
        "standardSurface":          ("specularColor",      "outColor"),
        "blinn":                    ("specularColor",      "outColor"),
        "phong":                    ("specularColor",      "outColor"),
        "phongE":                   ("specularColor",      "outColor"),
    },
    "emissionColor": {
        "RedshiftStandardMaterial": ("emission_color",     "outColor"),
        "RedshiftIncandescent":     ("color",              "outColor"),
        "RedshiftOpenPBRMaterial":  ("emission_color",     "outColor"),
        "aiStandardSurface":        ("emissionColor",      "outColor"),
        "standardSurface":          ("emissionColor",      "outColor"),
        "MASH":                     ("MASH_Color.texture", "outColor"),
    },
    "incandescence": {
        "RedshiftStandardMaterial": ("emission_color",     "outColor"),
        "RedshiftIncandescent":     ("color",              "outColor"),
        "aiStandardSurface":        ("emissionColor",      "outColor"),
        "standardSurface":          ("emissionColor",      "outColor"),
    },
    "opacity": {
        "RedshiftStandardMaterial": ("opacity_color",      "outColor"),
        "RedshiftMaterial":         ("opacity_color",      "outColor"),
        "RedshiftSprite":           ("opacity_color",      "outColor"),
        "aiStandardSurface":        ("opacity",            "outColor"),
        "standardSurface":          ("opacity",            "outColor"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "transparency": {
        "RedshiftStandardMaterial": ("opacity_color",      "outColor"),
        "aiStandardSurface":        ("opacity",            "outColor"),
        "standardSurface":          ("opacity",            "outColor"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "normalCamera": {
        "RedshiftStandardMaterial": ("bump_input",         "out"),
        "RedshiftMaterial":         ("bump_input",         "out"),
        "RedshiftOpenPBRMaterial":  ("bump_input",         "out"),
        "RedshiftToonMaterial":     ("bump_input",         "out"),
        "aiStandardSurface":        ("normalCamera",       "outNormal"),
        "standardSurface":          ("normalCamera",       "outNormal"),
        "blinn":                    ("normalCamera",       "outNormal"),
        "phong":                    ("normalCamera",       "outNormal"),
        "lambert":                  ("normalCamera",       "outNormal"),
    },
    "displacementShader": {
        "RedshiftStandardMaterial": ("_displacement_",     "outColor"),
        "RedshiftMaterial":         ("_displacement_",     "outColor"),
        "aiStandardSurface":        ("_displacement_",     "outColor"),
        "standardSurface":          ("_displacement_",     "outColor"),
    },
    "subsurfaceColor": {
        "RedshiftStandardMaterial": ("subsurface_color",   "outColor"),
        "RedshiftSkin":             ("shallow_color",      "outColor"),
        "aiStandardSurface":        ("subsurfaceColor",    "outColor"),
        "standardSurface":          ("subsurfaceColor",    "outColor"),
    },
    "coatColor": {
        "RedshiftStandardMaterial": ("coat_color",         "outColor"),
        "aiStandardSurface":        ("coatColor",          "outColor"),
        "standardSurface":          ("coatColor",          "outColor"),
    },
    "coatRoughness": {
        "RedshiftStandardMaterial": ("coat_roughness",     "outAlpha"),
        "aiStandardSurface":        ("coatRoughness",      "outAlpha"),
        "standardSurface":          ("coatRoughness",      "outAlpha"),
    },
    # scalar weights
    "base": {
        "RedshiftStandardMaterial": ("diffuse_weight",     "outAlpha"),
        "aiStandardSurface":        ("base",               "outAlpha"),
        "standardSurface":          ("base",               "outAlpha"),
    },
    "specular": {
        "RedshiftStandardMaterial": ("refl_weight",        "outAlpha"),
        "aiStandardSurface":        ("specular",           "outAlpha"),
        "standardSurface":          ("specular",           "outAlpha"),
    },
    "emission": {
        "RedshiftStandardMaterial": ("emission_weight",    "outAlpha"),
        "aiStandardSurface":        ("emission",           "outAlpha"),
        "standardSurface":          ("emission",           "outAlpha"),
    },
    "subsurface": {
        "RedshiftStandardMaterial": ("subsurface_weight",  "outAlpha"),
        "aiStandardSurface":        ("subsurface",         "outAlpha"),
        "standardSurface":          ("subsurface",         "outAlpha"),
    },
    "coat": {
        "RedshiftStandardMaterial": ("coat_weight",        "outAlpha"),
        "aiStandardSurface":        ("coat",               "outAlpha"),
        "standardSurface":          ("coat",               "outAlpha"),
    },
}

# ══════════════════════════════════════════════════════════════════════
#  RAW VALUE TRANSFER MAP
#  Attributes with no texture — transfer the raw float/color value
# ══════════════════════════════════════════════════════════════════════

VALUE_MAP = {
    "baseColor":         MASTER_MAP["baseColor"],
    "color":             MASTER_MAP["color"],
    "specularRoughness": MASTER_MAP["specularRoughness"],
    "metalness":         MASTER_MAP["metalness"],
    "specularColor":     MASTER_MAP["specularColor"],
    "emissionColor":     MASTER_MAP["emissionColor"],
    "incandescence":     MASTER_MAP["incandescence"],
    "opacity":           MASTER_MAP["opacity"],
    "base":              MASTER_MAP["base"],
    "specular":          MASTER_MAP["specular"],
    "emission":          MASTER_MAP["emission"],
    "subsurface":        MASTER_MAP["subsurface"],
    "coat":              MASTER_MAP["coat"],
    "coatRoughness":     MASTER_MAP["coatRoughness"],
    "metalness":         MASTER_MAP["metalness"],
    "eccentricity":      MASTER_MAP["eccentricity"],
}


# ══════════════════════════════════════════════════════════════════════
#  SMART NODE CHAIN CONVERTER
# ══════════════════════════════════════════════════════════════════════

def get_renderer_from_mat_type(mat_type):
    for renderer, mats in RENDERER_MATERIALS.items():
        if mat_type in mats:
            return renderer
    return "Maya"


def convert_node_for_renderer(src_node, target_renderer, converted_cache):
    if src_node in converted_cache:
        return converted_cache[src_node]
    node_type = cmds.nodeType(src_node)
    if node_type in PASSTHROUGH_NODES:
        converted_cache[src_node] = src_node
        return src_node
    conversion = NODE_CONVERSION_TABLE.get(node_type, {}).get(target_renderer)
    if not conversion:
        converted_cache[src_node] = src_node
        return src_node
    new_type = conversion["type"]
    if new_type not in (cmds.allNodeTypes() or []):
        converted_cache[src_node] = src_node
        return src_node
    new_node = cmds.shadingNode(new_type, asUtility=True,
                                 name=src_node + "_NF_conv")
    converted_cache[src_node] = new_node
    for attr, val in conversion.get("post_set", {}).items():
        try:
            cmds.setAttr(f"{new_node}.{attr}", val)
        except Exception:
            pass
    kwargs = dict(source=True, destination=False, plugs=True)
    if MAYA_VERSION >= 2024:
        kwargs["fullNodeName"] = True
    for old_in, new_in in conversion.get("inputs", {}).items():
        if not cmds.attributeQuery(old_in, node=src_node, exists=True):
            continue
        ups = cmds.listConnections(f"{src_node}.{old_in}", **kwargs) or []
        for up_plug in ups:
            up_node = up_plug.split(".")[0]
            conv_up = convert_node_for_renderer(up_node, target_renderer, converted_cache)
            up_attr = up_plug.split(".", 1)[1]
            try:
                dst = f"{new_node}.{new_in}"
                new_up_plug = f"{conv_up}.{up_attr}"
                if not cmds.isConnected(new_up_plug, dst):
                    cmds.connectAttr(new_up_plug, dst, force=True)
            except Exception:
                pass
    return new_node


def get_final_plug(source_plug, target_renderer, converted_cache):
    src_node  = source_plug.split(".")[0]
    src_attr  = source_plug.split(".", 1)[1]
    node_type = cmds.nodeType(src_node)
    conversion = NODE_CONVERSION_TABLE.get(node_type, {}).get(target_renderer)
    if not conversion:
        return source_plug
    new_node     = convert_node_for_renderer(src_node, target_renderer, converted_cache)
    new_out_attr = conversion.get("outputs", {}).get(src_attr, src_attr)
    return f"{new_node}.{new_out_attr}"


# ══════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════════

def get_shader_from_mesh(mesh):
    sgs = cmds.listConnections(mesh, type="shadingEngine") or []
    shaders = []
    for sg in sgs:
        s = cmds.listConnections(sg + ".surfaceShader") or []
        shaders += s
    return list(set(shaders))


def get_meshes_from_shader(shader):
    """Return all mesh shapes assigned to a shader."""
    sgs = cmds.listConnections(shader, type="shadingEngine") or []
    meshes = []
    for sg in sgs:
        members = cmds.sets(sg, q=True) or []
        meshes += members
    return meshes


def walk_upstream_for_file(node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return []
    visited.add(node)
    if cmds.nodeType(node) == "file":
        return [node]
    results = []
    for up in (cmds.listConnections(node, source=True, destination=False, plugs=False) or []):
        results += walk_upstream_for_file(up, visited)
    return results


def get_exact_source_plug(shader, attr):
    kwargs = dict(source=True, destination=False, plugs=True)
    if MAYA_VERSION >= 2024:
        kwargs["fullNodeName"] = True
    conns = cmds.listConnections(f"{shader}.{attr}", **kwargs) or []
    return conns[0] if conns else None


def get_all_scene_shaders():
    found = []
    for t in SUPPORTED_SOURCES:
        found += cmds.ls(type=t) or []
    return list(set(found))


def get_available_materials(renderer):
    all_types = set(cmds.allNodeTypes() or [])
    mats = RENDERER_MATERIALS.get(renderer, [])
    available = [m for m in mats if m in all_types or m == "MASH"]
    return available if available else mats


def auto_suggest_target(shaders):
    """
    Given a list of source shaders, suggest the best renderer + material.
    Uses majority vote if multiple shaders of different types.
    """
    votes = defaultdict(int)
    for shader in shaders:
        stype = cmds.nodeType(shader)
        suggestion = AUTO_SUGGEST.get(stype)
        if suggestion:
            votes[suggestion] += 1
    if not votes:
        return "Arnold", "aiStandardSurface"
    return max(votes, key=votes.get)


def collect_data(shader, target_mat_type):
    """
    Collect BOTH texture connections AND raw attribute values.
    Returns list of transfer entries.
    """
    results = []
    for src_attr, target_map in MASTER_MAP.items():
        if target_mat_type not in target_map:
            continue
        if not cmds.attributeQuery(src_attr, node=shader, exists=True):
            continue

        tgt_attr, preferred_plug = target_map[target_mat_type]
        source_plug = get_exact_source_plug(shader, src_attr)

        if source_plug:
            # Has texture connection
            source_node = source_plug.split(".")[0]
            file_nodes  = walk_upstream_for_file(source_node)
            file_node   = file_nodes[0] if file_nodes else None
            file_path   = (cmds.getAttr(file_node + ".fileTextureName") or "") \
                          if file_node else ""
            results.append({
                "shader":         shader,
                "shader_attr":    src_attr,
                "source_plug":    source_plug,
                "source_node":    source_node,
                "source_attr":    source_plug.split(".", 1)[1],
                "file_node":      file_node,
                "file_path":      file_path,
                "tgt_attr":       tgt_attr,
                "preferred_plug": preferred_plug,
                "target_type":    target_mat_type,
                "transfer_mode":  "texture",
                "raw_value":      None,
            })
        else:
            # No texture — transfer raw value
            if src_attr not in VALUE_MAP:
                continue
            try:
                val = cmds.getAttr(f"{shader}.{src_attr}")
            except Exception:
                continue

            # Skip default/unimportant values to keep table clean
            if isinstance(val, list) and isinstance(val[0], tuple):
                flat = list(val[0])
                # Skip pure black (0,0,0) for color attrs that aren't color
                if flat == [0.0, 0.0, 0.0] and src_attr not in (
                    "baseColor", "color", "specularColor"
                ):
                    continue
            elif isinstance(val, float) and val == 0.0 and src_attr in (
                "emission", "subsurface", "coat"
            ):
                continue

            results.append({
                "shader":         shader,
                "shader_attr":    src_attr,
                "source_plug":    None,
                "source_node":    None,
                "source_attr":    None,
                "file_node":      None,
                "file_path":      "",
                "tgt_attr":       tgt_attr,
                "preferred_plug": preferred_plug,
                "target_type":    target_mat_type,
                "transfer_mode":  "value",
                "raw_value":      val,
            })

    return results


def validate_transfer(data, target_node, target_mat_type):
    warnings = []
    slot_seen = {}
    target_renderer = get_renderer_from_mat_type(target_mat_type)
    for entry in data:
        tgt_attr = entry["tgt_attr"]
        if entry["file_node"] and not entry["file_path"]:
            warnings.append({"level": "warn", "message":
                f"File node '{entry['file_node']}' on '{entry['shader_attr']}' "
                f"has NO texture path.\n  ➤ Assign an image in Hypershade first.",
                "entry": entry})
        if tgt_attr in slot_seen:
            warnings.append({"level": "warn", "message":
                f"Conflict: '{slot_seen[tgt_attr]['shader_attr']}' and "
                f"'{entry['shader_attr']}' both target '{tgt_attr}'.\n"
                f"  ➤ Last connection wins.", "entry": entry})
        slot_seen[tgt_attr] = entry
        if target_mat_type not in ("MASH",) and target_node and \
                not tgt_attr.startswith("_displacement_") and \
                not tgt_attr.startswith("MASH_"):
            base = tgt_attr.split(".")[0]
            if not cmds.attributeQuery(base, node=target_node, exists=True):
                warnings.append({"level": "error", "message":
                    f"Attribute '{tgt_attr}' NOT found on '{target_node}'.\n"
                    f"  ➤ Make sure the renderer plugin is loaded.",
                    "entry": entry})
        node_type = cmds.nodeType(entry["source_node"]) \
                    if entry["source_node"] else None
        if node_type and node_type in NODE_CONVERSION_TABLE:
            conv = NODE_CONVERSION_TABLE[node_type].get(target_renderer)
            if conv and conv["type"] != node_type:
                warnings.append({"level": "warn", "message":
                    f"'{entry['source_node']}' ({node_type}) will be "
                    f"AUTO-CONVERTED to '{conv['type']}' for {target_renderer}.\n"
                    f"  ➤ NodeFlow handles this automatically.",
                    "entry": entry})
    return warnings


def do_transfer(data, target_node, target_mat_type, mash_waiter=None):
    log = []
    color_node = None
    converted_cache = {}
    target_renderer = get_renderer_from_mat_type(target_mat_type)

    for entry in data:
        tgt_attr = entry["tgt_attr"]
        mode     = entry["transfer_mode"]

        # ── Resolve destination plug ───────────────────────────────────
        if target_mat_type == "MASH":
            if not mash_waiter or not cmds.objExists(mash_waiter):
                log.append("[ERROR] MASH Waiter not found.")
                continue
            if tgt_attr.startswith("MASH_Color."):
                mash_attr = tgt_attr.split(".", 1)[1]
                if color_node is None:
                    existing = cmds.listConnections(mash_waiter, type="MASH_Color") or []
                    if existing:
                        color_node = existing[0]
                    else:
                        color_node = cmds.createNode(
                            "MASH_Color", name=mash_waiter + "_Color"
                        )
                        cmds.setAttr(color_node + ".mapType", 1)
                        log.append(f"[INFO] Created MASH_Color: {color_node}")
                dst_plug = f"{color_node}.{mash_attr}"
            elif tgt_attr.startswith("MASH_Distribute."):
                mash_attr = tgt_attr.split(".", 1)[1]
                dist = cmds.listConnections(mash_waiter, type="MASH_Distribute") or []
                if not dist:
                    log.append(f"[SKIP] No MASH_Distribute for '{entry['shader_attr']}'.")
                    continue
                cmds.setAttr(dist[0] + ".useStrengthMap", 1)
                dst_plug = f"{dist[0]}.{mash_attr}"
            else:
                continue
        elif tgt_attr == "_displacement_":
            sgs = cmds.listConnections(target_node, type="shadingEngine") or []
            if not sgs:
                log.append("[SKIP] No shadingGroup for displacement.")
                continue
            dst_plug = f"{sgs[0]}.displacementShader"
        else:
            if not target_node or not cmds.objExists(target_node):
                log.append(f"[ERROR] Target '{target_node}' not found.")
                continue
            dst_plug = f"{target_node}.{tgt_attr}"

        # ── Transfer texture connection ────────────────────────────────
        if mode == "texture":
            source_node = entry["source_node"]
            source_plug = entry["source_plug"]

            if cmds.nodeType(source_node) == "file":
                final_plug = f"{source_node}.{entry['preferred_plug']}"
            else:
                final_plug = get_final_plug(source_plug, target_renderer, converted_cache)

            fp_node = final_plug.split(".")[0]
            if not cmds.objExists(fp_node):
                log.append(f"[SKIP] Source node '{fp_node}' gone.")
                continue
            try:
                if cmds.isConnected(final_plug, dst_plug):
                    log.append(f"[SKIP] Already connected: {final_plug} → {dst_plug}")
                else:
                    cmds.connectAttr(final_plug, dst_plug, force=True)
                    log.append(f"[OK-T] {final_plug:<50}  →  {dst_plug}")
            except Exception as e:
                log.append(f"[FAIL] {final_plug}  →  {dst_plug}\n       {e}")

        # ── Transfer raw value ─────────────────────────────────────────
        elif mode == "value":
            val = entry["raw_value"]
            try:
                if isinstance(val, list) and isinstance(val[0], tuple):
                    cmds.setAttr(dst_plug, *val[0], type="double3")
                elif isinstance(val, list):
                    cmds.setAttr(dst_plug, *val, type="double3")
                else:
                    cmds.setAttr(dst_plug, val)
                log.append(
                    f"[OK-V] {entry['shader']}.{entry['shader_attr']:<30}"
                    f"  →  {dst_plug}  =  {val}"
                )
            except Exception as e:
                log.append(f"[FAIL] value set {dst_plug}: {e}")

    return log


def create_target_shader(mat_type, base_name):
    if mat_type == "MASH":
        return None
    if mat_type not in (cmds.allNodeTypes() or []):
        return None
    shader = cmds.shadingNode(mat_type, asShader=True, name=base_name + "_NF")
    sg = cmds.sets(renderable=True, noSurfaceShader=True,
                   empty=True, name=shader + "SG")
    try:
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader")
    except Exception:
        pass
    return shader


def assign_shader_to_meshes(new_shader, old_shader, log):
    """Assign new shader to all meshes that had old shader, keep old shader."""
    old_sgs = cmds.listConnections(old_shader, type="shadingEngine") or []
    new_sgs = cmds.listConnections(new_shader, type="shadingEngine") or []
    new_sg  = new_sgs[0] if new_sgs else None

    if not new_sg:
        log.append(f"[SKIP] No shading group on new shader '{new_shader}'.")
        return 0

    total = 0
    for old_sg in old_sgs:
        members = cmds.sets(old_sg, q=True) or []
        if members:
            cmds.sets(members, e=True, forceElement=new_sg)
            total += len(members)
            log.append(
                f"[ASSIGN] {len(members)} object(s) reassigned: "
                f"{old_sg} → {new_sg}"
            )
    return total


# ══════════════════════════════════════════════════════════════════════
#  STYLE
# ══════════════════════════════════════════════════════════════════════

STYLE = """
QWidget {
    background-color: #0d1b2a;
    color: #cdd9e5;
    font-family: 'Segoe UI', Arial;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #1e3a5f;
    background: #0d1b2a;
}
QTabBar::tab {
    background: #112240; color: #7aa2c8;
    padding: 8px 20px; border: 1px solid #1e3a5f;
    border-bottom: none; border-radius: 4px 4px 0 0;
    min-width: 80px;
}
QTabBar::tab:selected {
    background: #1b3a6b; color: #ffffff; font-weight: bold;
}
QPushButton {
    background-color: #1b3a6b; color: #cdd9e5;
    border: 1px solid #2e5fa3; border-radius: 5px;
    padding: 6px 14px; font-weight: bold; min-height: 26px;
}
QPushButton:hover   { background-color: #2e5fa3; color: #ffffff; }
QPushButton:pressed { background-color: #0d1b2a; }
QPushButton#autoBtn {
    background-color: #1a4a2a; color: #66dd88;
    border: 1px solid #33aa55; border-radius: 5px;
    padding: 6px 12px; font-weight: bold;
}
QPushButton#autoBtn:hover { background-color: #2a6a3a; }
QPushButton#transferBtn {
    background-color: #2e5fa3; color: #ffffff;
    font-size: 14px; padding: 10px 40px;
    border-radius: 8px; font-weight: bold;
}
QPushButton#transferBtn:hover    { background-color: #4080d0; }
QPushButton#transferBtn:disabled {
    background-color: #1a2a3a; color: #445566; border-color: #223344;
}
QPushButton#linkedinBtn {
    background-color: #0a66c2; color: #ffffff;
    padding: 9px 20px; border-radius: 6px; border: none;
}
QPushButton#linkedinBtn:hover { background-color: #1a80e0; }
QPushButton#dangerBtn {
    background-color: #2a1010; color: #e08080;
    border: 1px solid #883333;
}
QPushButton#dangerBtn:hover { background-color: #3a1818; }
QPushButton#smallBtn {
    padding: 4px 10px; font-size: 12px; min-height: 22px;
}
QLineEdit, QComboBox {
    background-color: #112240; border: 1px solid #1e3a5f;
    border-radius: 4px; padding: 4px 8px;
    color: #cdd9e5; min-height: 26px;
}
QLineEdit:focus     { border: 1px solid #2e5fa3; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background-color: #112240; color: #cdd9e5;
    selection-background-color: #1b3a6b;
    border: 1px solid #1e3a5f;
}
QListWidget {
    background-color: #0a1628; border: 1px solid #1e3a5f;
    border-radius: 4px; color: #cdd9e5;
}
QListWidget::item           { padding: 4px 8px; }
QListWidget::item:selected  { background-color: #1b3a6b; color: #fff; }
QListWidget::item:hover     { background-color: #162d50; }
QTableWidget {
    background-color: #0a1628; gridline-color: #1e3a5f;
    border: 1px solid #1e3a5f; border-radius: 4px;
}
QTableWidget::item          { padding: 3px 6px; }
QTableWidget::item:selected { background-color: #1b3a6b; color: #fff; }
QHeaderView::section {
    background-color: #112240; color: #7aa2c8;
    border: 1px solid #1e3a5f; padding: 5px 6px; font-weight: bold;
}
QTextEdit {
    background-color: #0a1628; border: 1px solid #1e3a5f;
    border-radius: 4px; color: #cdd9e5;
    font-family: 'Consolas', monospace; font-size: 12px;
}
QLabel#sectionLabel {
    color: #7aa2c8; font-weight: bold;
    font-size: 12px; padding: 2px 0;
}
QLabel#titleLabel {
    color: #4080d0; font-size: 18px; font-weight: bold;
}
QLabel#subtitleLabel { color: #445e78; font-size: 11px; }
QLabel#countLabel    { color: #4080d0; font-size: 11px; font-weight: bold; }
QLabel#hintLabel     { color: #556677; font-size: 11px; font-style: italic; }
QRadioButton { spacing: 6px; }
QRadioButton::indicator {
    width: 14px; height: 14px;
    border: 1px solid #2e5fa3; border-radius: 7px; background: #112240;
}
QRadioButton::indicator:checked { background: #2e5fa3; }
QScrollBar:vertical {
    background: #0d1b2a; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2e5fa3; border-radius: 4px; min-height: 20px;
}
QFrame#divider { color: #1e3a5f; }
"""


# ══════════════════════════════════════════════════════════════════════
#  DRAG DROP LINE EDIT
# ══════════════════════════════════════════════════════════════════════

class DragDropLineEdit(QtWidgets.QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() or \
                event.mimeData().hasFormat("application/x-maya-data"):
            event.acceptProposedAction()
            self.setStyleSheet(
                "border: 2px solid #4080d0; border-radius: 4px; "
                "background-color: #1a2e4a;"
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event):
        self.setStyleSheet("")
        if event.mimeData().hasFormat("application/x-maya-data"):
            raw  = bytes(event.mimeData().data(
                "application/x-maya-data")).decode("utf-8", errors="ignore")
            node = self._parse_maya_mime(raw)
            if node:
                self.setText(node.strip())
                event.acceptProposedAction()
                return
        if event.mimeData().hasText():
            text = event.mimeData().text().strip()
            text = text.split("|")[-1].split("\n")[0].strip()
            self.setText(text)
            event.acceptProposedAction()

    def _parse_maya_mime(self, raw):
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        for line in lines:
            if "|" in line:
                line = line.split("|")[-1]
            if cmds.objExists(line):
                return line
        return lines[0] if lines else None


# ══════════════════════════════════════════════════════════════════════
#  WARNING DIALOG
# ══════════════════════════════════════════════════════════════════════

class WarningDialog(QtWidgets.QDialog):
    def __init__(self, warnings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️  NodeFlow — Warnings")
        self.setMinimumSize(680, 400)
        self.setStyleSheet(STYLE)
        self.result_choice = False
        L = QtWidgets.QVBoxLayout(self)
        L.setSpacing(10)

        has_err = any(w["level"] == "error" for w in warnings)
        txt = f"<b>{len(warnings)} issue(s) detected.</b><br>"
        txt += ("🔴 <b>Errors found</b> — fix recommended."
                if has_err else
                "Warnings only — you may continue or fix first.")
        hdr = QtWidgets.QLabel(txt)
        hdr.setWordWrap(True)
        L.addWidget(hdr)

        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)
        for i, w in enumerate(warnings, 1):
            icon = "🔴" if w["level"] == "error" else "🟡"
            self.text.append(f"{icon}  Issue {i}:\n{w['message']}\n{'─'*55}\n")
        L.addWidget(self.text)

        row = QtWidgets.QHBoxLayout()
        yes = QtWidgets.QPushButton("✅  Yes, Continue")
        no  = QtWidgets.QPushButton("❌  No, Fix First")
        yes.clicked.connect(self._yes)
        no.clicked.connect(self._no)
        row.addWidget(yes)
        row.addWidget(no)
        L.addLayout(row)

    def _yes(self): self.result_choice = True;  self.accept()
    def _no(self):  self.result_choice = False; self.reject()


# ══════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════

class NodeFlowTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            "NodeFlow  ⚡  Transfer Any Texture · Any Shader · Any Target"
        )
        self.setMinimumSize(960, 760)
        self.setStyleSheet(STYLE)
        self._all_data = []
        self._build_ui()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(6)

        # ── Header ────────────────────────────────────────────────────
        hdr_row = QtWidgets.QHBoxLayout()
        left_col = QtWidgets.QVBoxLayout()
        title    = QtWidgets.QLabel("⚡  NodeFlow")
        subtitle = QtWidgets.QLabel(
            "Transfer Any Texture · Any Shader · Any Target  |  v4.0.0"
        )
        title.setObjectName("titleLabel")
        subtitle.setObjectName("subtitleLabel")
        left_col.addWidget(title)
        left_col.addWidget(subtitle)
        hdr_row.addLayout(left_col)
        hdr_row.addStretch()
        root.addLayout(hdr_row)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setObjectName("divider")
        root.addWidget(sep)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_transfer_tab(), "  🔄  Transfer  ")
        tabs.addTab(self._build_log_tab(),      "  📋  Log  ")
        tabs.addTab(self._build_help_tab(),     "  ❓  Help  ")
        root.addWidget(tabs)

    # ── Transfer Tab ──────────────────────────────────────────────────
    def _build_transfer_tab(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setSpacing(8)
        L.setContentsMargins(4, 4, 4, 4)

        # ── ① Source Mode ─────────────────────────────────────────────
        self._add_section_label(L, "①  Source Mode")
        mode_row = QtWidgets.QHBoxLayout()
        self.mode_single = QtWidgets.QRadioButton("Single Shader / Mesh")
        self.mode_multi  = QtWidgets.QRadioButton("Multi Select")
        self.mode_all    = QtWidgets.QRadioButton("All Scene Materials")
        self.mode_single.setChecked(True)
        for rb in (self.mode_single, self.mode_multi, self.mode_all):
            rb.toggled.connect(self._on_mode_changed)
            mode_row.addWidget(rb)
        mode_row.addStretch()
        L.addLayout(mode_row)

        # Single field
        self.single_widget = QtWidgets.QWidget()
        sw = QtWidgets.QHBoxLayout(self.single_widget)
        sw.setContentsMargins(0, 0, 0, 0)
        self.src_field = DragDropLineEdit(
            "Drag from Outliner / Hypershade  or  type name"
        )
        b = QtWidgets.QPushButton("← Pick")
        b.setObjectName("smallBtn")
        b.setFixedWidth(70)
        b.clicked.connect(lambda: self._pick(self.src_field))
        sw.addWidget(self.src_field)
        sw.addWidget(b)
        L.addWidget(self.single_widget)

        # Multi list
        self.multi_widget = QtWidgets.QWidget()
        mw = QtWidgets.QVBoxLayout(self.multi_widget)
        mw.setContentsMargins(0, 0, 0, 0)
        mw.setSpacing(4)
        mb_row = QtWidgets.QHBoxLayout()
        for label, slot in [
            ("＋ From Selection", self._add_selected_to_list),
            ("＋ All Scene",      self._add_all_to_list),
            ("✕ Clear",           self._clear_list),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setObjectName("smallBtn")
            if "✕" in label:
                btn.setObjectName("dangerBtn")
            btn.clicked.connect(slot)
            mb_row.addWidget(btn)
        mb_row.addStretch()
        mw.addLayout(mb_row)
        self.shader_list = QtWidgets.QListWidget()
        self.shader_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.shader_list.setFixedHeight(110)
        self.count_label = QtWidgets.QLabel("0 shader(s)")
        self.count_label.setObjectName("countLabel")
        mw.addWidget(self.shader_list)
        mw.addWidget(self.count_label)
        self.multi_widget.setVisible(False)
        L.addWidget(self.multi_widget)

        # All scene
        self.all_widget = QtWidgets.QWidget()
        aw = QtWidgets.QHBoxLayout(self.all_widget)
        aw.setContentsMargins(0, 0, 0, 0)
        self.all_label = QtWidgets.QLabel("0 shader(s) in scene")
        self.all_label.setObjectName("countLabel")
        ref_btn = QtWidgets.QPushButton("↻")
        ref_btn.setObjectName("smallBtn")
        ref_btn.setFixedWidth(36)
        ref_btn.clicked.connect(self._refresh_scene_count)
        aw.addWidget(self.all_label)
        aw.addWidget(ref_btn)
        aw.addStretch()
        self.all_widget.setVisible(False)
        L.addWidget(self.all_widget)

        L.addWidget(self._make_divider())

        # ── ② Target Renderer + Auto Suggest ─────────────────────────
        self._add_section_label(L, "②  Target Renderer  &  Material Type")

        target_row = QtWidgets.QHBoxLayout()
        target_row.setSpacing(6)

        # Renderer combo
        ren_col = QtWidgets.QVBoxLayout()
        ren_lbl = QtWidgets.QLabel("Renderer")
        ren_lbl.setObjectName("hintLabel")
        self.renderer_combo = QtWidgets.QComboBox()
        self.renderer_combo.addItems(RENDERER_OPTIONS)
        self.renderer_combo.currentTextChanged.connect(self._on_renderer_changed)
        ren_col.addWidget(ren_lbl)
        ren_col.addWidget(self.renderer_combo)
        target_row.addLayout(ren_col)

        # Material combo
        mat_col = QtWidgets.QVBoxLayout()
        mat_lbl = QtWidgets.QLabel("Material Type")
        mat_lbl.setObjectName("hintLabel")
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.setMinimumWidth(220)
        mat_col.addWidget(mat_lbl)
        mat_col.addWidget(self.material_combo)
        target_row.addLayout(mat_col)

        # Auto button
        auto_col = QtWidgets.QVBoxLayout()
        auto_spacer = QtWidgets.QLabel("")
        self.auto_btn = QtWidgets.QPushButton("✨ Auto Suggest")
        self.auto_btn.setObjectName("autoBtn")
        self.auto_btn.setToolTip(
            "Analyzes your source shaders and picks the best target automatically"
        )
        self.auto_btn.clicked.connect(self._auto_suggest)
        auto_col.addWidget(auto_spacer)
        auto_col.addWidget(self.auto_btn)
        target_row.addLayout(auto_col)
        target_row.addStretch()

        L.addLayout(target_row)

        # Auto hint label
        self.auto_hint = QtWidgets.QLabel("")
        self.auto_hint.setObjectName("hintLabel")
        L.addWidget(self.auto_hint)

        L.addWidget(self._make_divider())

        # ── ③ Target Node ─────────────────────────────────────────────
        self._add_section_label(
            L, "③  Target Node  —  Leave empty to auto-create per shader"
        )
        tgt_row = QtWidgets.QHBoxLayout()
        self.tgt_field = DragDropLineEdit(
            "Drag existing target shader here  or  leave empty to auto-create"
        )
        tp = QtWidgets.QPushButton("← Pick")
        tp.setObjectName("smallBtn")
        tp.setFixedWidth(70)
        tp.clicked.connect(lambda: self._pick(self.tgt_field))
        tgt_row.addWidget(self.tgt_field)
        tgt_row.addWidget(tp)
        L.addLayout(tgt_row)

        # MASH waiter
        self.mash_group = QtWidgets.QWidget()
        mg = QtWidgets.QVBoxLayout(self.mash_group)
        mg.setContentsMargins(0, 0, 0, 0)
        self._add_section_label(mg, "④  MASH Waiter Node")
        mr = QtWidgets.QHBoxLayout()
        self.mash_field = DragDropLineEdit("Drag MASH Waiter  e.g.  MASH1_Waiter")
        mp = QtWidgets.QPushButton("← Pick")
        mp.setObjectName("smallBtn")
        mp.setFixedWidth(70)
        mp.clicked.connect(lambda: self._pick(self.mash_field))
        mr.addWidget(self.mash_field)
        mr.addWidget(mp)
        mg.addLayout(mr)
        self.mash_group.setVisible(False)
        L.addWidget(self.mash_group)

        L.addWidget(self._make_divider())

        # ── Scan ──────────────────────────────────────────────────────
        scan_row = QtWidgets.QHBoxLayout()
        scan_btn = QtWidgets.QPushButton("🔍  Scan Materials & Textures")
        scan_btn.clicked.connect(self._scan)
        scan_row.addWidget(scan_btn)
        scan_row.addStretch()
        L.addLayout(scan_row)

        # ── Table ─────────────────────────────────────────────────────
        self._add_section_label(L, "Detected Connections & Values  —  Review before Transfer")

        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Source Shader", "Attr", "Mode",
            "Source Plug / Value", "File", "→ Target Attr", "Status"
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch
        )
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "QTableWidget { alternate-background-color: #0e1f33; }"
        )
        self.table.setMinimumHeight(180)
        L.addWidget(self.table)

        # ── Transfer ──────────────────────────────────────────────────
        xfer_row = QtWidgets.QHBoxLayout()
        xfer_row.addStretch()
        self.transfer_btn = QtWidgets.QPushButton("🚀  Transfer & Auto-Assign")
        self.transfer_btn.setObjectName("transferBtn")
        self.transfer_btn.setEnabled(False)
        self.transfer_btn.clicked.connect(self._transfer)
        xfer_row.addWidget(self.transfer_btn)
        xfer_row.addStretch()
        L.addLayout(xfer_row)
        L.addSpacing(8)

        scroll.setWidget(w)
        self._on_renderer_changed(self.renderer_combo.currentText())
        return scroll

    # ── Log Tab ───────────────────────────────────────────────────────
    def _build_log_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(4, 4, 4, 4)
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        clr = QtWidgets.QPushButton("🗑  Clear Log")
        clr.clicked.connect(self.log_output.clear)
        L.addWidget(self.log_output)
        L.addWidget(clr, alignment=Qt.AlignRight)
        return w

    # ── Help Tab ──────────────────────────────────────────────────────
    def _build_help_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(4, 4, 4, 4)
        L.setSpacing(10)

        help_text = QtWidgets.QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <div style='color:#cdd9e5;font-family:Segoe UI;font-size:13px;line-height:1.8'>
        <p style='color:#4080d0;font-size:16px;font-weight:bold'>
            ⚡ NodeFlow v4.0 — How to Use
        </p>

        <p style='color:#7aa2c8;font-weight:bold'>What NodeFlow Does</p>
        <p>NodeFlow converts full materials between renderers — transferring both
        <b>texture connections</b> (file nodes, full upstream chains) and
        <b>raw attribute values</b> (roughness, metalness, base color, etc.)
        Then it <b>auto-assigns</b> every mesh to the new shader automatically.
        Old shaders are kept untouched for rollback.</p>

        <p style='color:#7aa2c8;font-weight:bold'>Source Modes</p>
        <ul>
            <li><b>Single:</b> One mesh or shader.</li>
            <li><b>Multi Select:</b> Add shaders to list from selection or scene.</li>
            <li><b>All Scene Materials:</b> Converts every supported shader in the scene.</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold'>✨ Auto Suggest Button</p>
        <p>Analyzes your source shaders and picks the most logical target:</p>
        <ul>
            <li>aiStandardSurface → RedshiftStandardMaterial</li>
            <li>RedshiftStandardMaterial → aiStandardSurface</li>
            <li>lambert / blinn / phong → standardSurface</li>
            <li>standardSurface → aiStandardSurface</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold'>Transfer Modes</p>
        <ul>
            <li><b>[T] Texture:</b> File node connected → rewires full chain to new shader.</li>
            <li><b>[V] Value:</b> No texture → copies the raw float/color value directly.</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold'>Smart Node Conversion</p>
        <ul>
            <li>bump2d → RedshiftBumpMap (height mode)</li>
            <li>aiNormalMap → RedshiftBumpMap (tangent normal mode)</li>
            <li>aiColorCorrect → rsColorCorrect</li>
            <li>aiRange → rsRange / remapValue</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold'>Auto Assign</p>
        <p>After transfer, all meshes using the old shader are automatically
        reassigned to the new shader. The old shader stays in the scene.</p>

        <p style='color:#7aa2c8;font-weight:bold'>Maya Version</p>
        <p>Maya 2020 and above. Auto-detects Maya 2024+ fullNodeName support.</p>

        <br><hr style='border-color:#1e3a5f'><br>
        <p style='color:#445e78;font-size:11px'>
            NodeFlow v4.0.0 · Youssef El Qadi · Pipeline TD
        </p>
        </div>
        """)
        L.addWidget(help_text)

        li_btn = QtWidgets.QPushButton(
            "  🔗  Connect on LinkedIn — Youssef El Qadi"
        )
        li_btn.setObjectName("linkedinBtn")
        li_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        li_btn.clicked.connect(lambda: webbrowser.open(
            "https://www.linkedin.com/in/youssef-el-qadi-6a78a4247"
        ))
        L.addWidget(li_btn)
        return w

    # ══════════════════════════════════════════════════════════════════
    #  UI HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _make_divider(self):
        f = QtWidgets.QFrame()
        f.setFrameShape(QtWidgets.QFrame.HLine)
        f.setObjectName("divider")
        return f

    def _add_section_label(self, layout, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setObjectName("sectionLabel")
        layout.addWidget(lbl)

    def _pick(self, field):
        sel = cmds.ls(sl=True)
        if sel:
            field.setText(sel[0])
        else:
            self._log("[WARN] Nothing selected in Maya.")

    def _log(self, msg):
        self.log_output.append(msg)

    def _on_mode_changed(self):
        is_s = self.mode_single.isChecked()
        is_m = self.mode_multi.isChecked()
        is_a = self.mode_all.isChecked()
        self.single_widget.setVisible(is_s)
        self.multi_widget.setVisible(is_m)
        self.all_widget.setVisible(is_a)
        if is_a:
            self._refresh_scene_count()

    def _on_renderer_changed(self, value):
        self.material_combo.clear()
        self.material_combo.addItems(get_available_materials(value))
        self.mash_group.setVisible(value == "MASH")

    def _auto_suggest(self):
        shaders, err = self._get_source_shaders()
        if err or not shaders:
            self.auto_hint.setText("⚠  Scan source shaders first.")
            return
        renderer, mat_type = auto_suggest_target(shaders)
        # Set renderer combo
        idx = self.renderer_combo.findText(renderer)
        if idx >= 0:
            self.renderer_combo.setCurrentIndex(idx)
        # Set material combo (after renderer changed)
        idx2 = self.material_combo.findText(mat_type)
        if idx2 >= 0:
            self.material_combo.setCurrentIndex(idx2)
        self.auto_hint.setText(
            f"✨  Suggested: {renderer} → {mat_type}  "
            f"(based on {len(shaders)} source shader(s))"
        )
        self._log(f"[AUTO] Suggested target: {renderer} → {mat_type}")

    def _add_selected_to_list(self):
        added = 0
        existing = {
            self.shader_list.item(i).text()
            for i in range(self.shader_list.count())
        }
        for node in (cmds.ls(sl=True) or []):
            nt = cmds.nodeType(node)
            shader = node if nt in SUPPORTED_SOURCES else \
                     (get_shader_from_mesh(node) or [None])[0]
            if shader and shader not in existing:
                self.shader_list.addItem(shader)
                existing.add(shader)
                added += 1
        self._update_count()
        self._log(f"[LIST] Added {added} shader(s) from selection.")

    def _add_all_to_list(self):
        existing = {
            self.shader_list.item(i).text()
            for i in range(self.shader_list.count())
        }
        added = 0
        for s in get_all_scene_shaders():
            if s not in existing:
                self.shader_list.addItem(s)
                existing.add(s)
                added += 1
        self._update_count()
        self._log(f"[LIST] Added {added} shader(s) from scene.")

    def _clear_list(self):
        self.shader_list.clear()
        self._update_count()

    def _update_count(self):
        self.count_label.setText(
            f"{self.shader_list.count()} shader(s)"
        )

    def _refresh_scene_count(self):
        n = len(get_all_scene_shaders())
        self.all_label.setText(f"{n} supported shader(s) in scene")

    def _get_source_shaders(self):
        if self.mode_single.isChecked():
            src = self.src_field.text().strip()
            if not src or not cmds.objExists(src):
                return None, f"Node '{src}' not found."
            nt = cmds.nodeType(src)
            if nt in SUPPORTED_SOURCES:
                return [src], None
            s = get_shader_from_mesh(src)
            return (s, None) if s else (None, f"No supported shader on '{src}'.")
        elif self.mode_multi.isChecked():
            s = [self.shader_list.item(i).text()
                 for i in range(self.shader_list.count())]
            return (s, None) if s else (None, "Shader list is empty.")
        else:
            s = get_all_scene_shaders()
            return (s, None) if s else (None, "No supported shaders in scene.")

    def _populate_table(self, data):
        self.table.setRowCount(0)
        for entry in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            mode = entry["transfer_mode"]
            mode_label = "🔗 Texture" if mode == "texture" else "🔢 Value"
            src_val = (entry["source_plug"] or
                       str(entry["raw_value"]) if entry["raw_value"] is not None
                       else "—")
            if isinstance(entry["raw_value"], list) and entry["raw_value"]:
                v = entry["raw_value"]
                src_val = str(v[0]) if isinstance(v[0], tuple) else str(v)
            cols = [
                entry["shader"],
                entry["shader_attr"],
                mode_label,
                src_val,
                entry["file_node"] or ("—" if mode == "texture" else "n/a"),
                entry["tgt_attr"],
                "⚠ No path" if (mode == "texture" and
                                entry["file_node"] and
                                not entry["file_path"]) else "✓",
            ]
            colors = {
                0: "#4080d0",
                1: "#7aa2c8",
                2: "#88cc88" if mode == "texture" else "#ccaa44",
                5: "#88cc88",
                6: "#e08040" if "⚠" in cols[6] else "#448844",
            }
            for col, val in enumerate(cols):
                item = QtWidgets.QTableWidgetItem(str(val))
                if col in colors:
                    item.setForeground(QtGui.QColor(colors[col]))
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch
        )

    # ── Scan ──────────────────────────────────────────────────────────
    def _scan(self):
        shaders, err = self._get_source_shaders()
        if err:
            QtWidgets.QMessageBox.warning(self, "NodeFlow", err)
            return

        target_mat = self.material_combo.currentText()
        self._all_data = []
        for shader in shaders:
            self._all_data += collect_data(shader, target_mat)

        if not self._all_data:
            self._log("[WARN] No transferable data found.")
            self.transfer_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(
                self, "NodeFlow",
                "No connected textures or attribute values found.\n"
                "Make sure the shader has textures or non-default values."
            )
            return

        tex_count = sum(1 for e in self._all_data if e["transfer_mode"] == "texture")
        val_count = sum(1 for e in self._all_data if e["transfer_mode"] == "value")
        self._populate_table(self._all_data)
        self.transfer_btn.setEnabled(True)
        self._log(
            f"[SCAN] {len(shaders)} shader(s) — "
            f"{tex_count} texture(s), {val_count} value(s) → {target_mat}"
        )

    # ── Transfer ──────────────────────────────────────────────────────
    def _transfer(self):
        target_mat  = self.material_combo.currentText()
        tgt_input   = self.tgt_field.text().strip()
        mash_waiter = self.mash_field.text().strip() \
                      if self.renderer_combo.currentText() == "MASH" else None

        shaders, err = self._get_source_shaders()
        if err:
            QtWidgets.QMessageBox.warning(self, "NodeFlow", err)
            return

        # Validate
        tgt_for_val = tgt_input if tgt_input and cmds.objExists(tgt_input) else None
        warnings = validate_transfer(self._all_data, tgt_for_val, target_mat)
        if warnings:
            dlg = WarningDialog(warnings, parent=self)
            dlg.exec_()
            if not dlg.result_choice:
                self._log("[CANCELLED] Transfer cancelled.")
                return

        # Group by shader
        data_by_shader = defaultdict(list)
        for entry in self._all_data:
            data_by_shader[entry["shader"]].append(entry)

        total_ok = total_fail = total_assigned = 0

        for shader, entries in data_by_shader.items():
            # Resolve or create target
            if target_mat == "MASH":
                target_node = None
            elif tgt_input and cmds.objExists(tgt_input):
                target_node = tgt_input
            else:
                target_node = create_target_shader(target_mat, shader)
                if target_node:
                    self._log(f"[CREATE] '{target_node}' for '{shader}'")
                else:
                    self._log(f"[ERROR] Could not create '{target_mat}' — plugin loaded?")
                    continue

            # Transfer
            log_lines = do_transfer(entries, target_node, target_mat, mash_waiter)
            for line in log_lines:
                self._log(line)

            total_ok   += sum(1 for l in log_lines if l.startswith("[OK"))
            total_fail += sum(1 for l in log_lines if l.startswith("[FAIL]"))

            # Auto-assign meshes
            if target_node and target_mat != "MASH":
                n = assign_shader_to_meshes(target_node, shader, log_lines)
                total_assigned += n
                for line in log_lines:
                    if line.startswith("[ASSIGN]"):
                        self._log(line)

        self._log(
            f"\n{'─'*60}\n"
            f"[DONE] ✅ {total_ok} transferred  "
            f"❌ {total_fail} failed  "
            f"🔗 {total_assigned} object(s) reassigned\n"
            f"{'─'*60}\n"
        )
        QtWidgets.QMessageBox.information(
            self, "NodeFlow — Done",
            f"Transfer complete!\n\n"
            f"✅  {total_ok} attribute(s) transferred\n"
            f"❌  {total_fail} failed\n"
            f"🔗  {total_assigned} mesh(es) auto-assigned\n\n"
            f"Old shaders kept — check Log for details."
        )


# ══════════════════════════════════════════════════════════════════════
#  LAUNCH
# ══════════════════════════════════════════════════════════════════════

def launch():
    try:
        ptr      = omui.MQtUtil.mainWindow()
        maya_win = wrapInstance(int(ptr), QtWidgets.QWidget)
    except Exception:
        maya_win = None

    global _nodeflow_tool
    try:
        _nodeflow_tool.close()
        _nodeflow_tool.deleteLater()
    except Exception:
        pass

    _nodeflow_tool = NodeFlowTool(parent=maya_win)
    _nodeflow_tool.show()


launch()
