"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗██╗      ██████╗ ██╗   ║
║   ████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝██║     ██╔═══██╗██║   ║
║   ██║╚██╗██║██║   ██║██║  ██║█████╗  █████╗  ██║     ██║   ██║╚═╝   ║
║   ██║ ╚████║╚██████╔╝██████╔╝███████╗██║     ███████╗╚██████╔╝██╗   ║
║   ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ║
║                                                                      ║
║   Transfer Any Texture. Any Shader. Any Target.                      ║
║   Author  : Youssef El Qadi                                          ║
║   Version : 4.1.0 — Fixed Node Chain Rewiring                       ║
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
#  AUTO-SUGGEST
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
#  NODE CONVERSION TABLE
#  inputs  = { old_src_attr : new_dst_attr }   (what feeds INTO the node)
#  outputs = { old_out_attr : new_out_attr }   (what leaves the node)
# ══════════════════════════════════════════════════════════════════════

NODE_CONVERSION_TABLE = {
    # ── bump2d (height map) ───────────────────────────────────────────
    "bump2d": {
        "Redshift": {
            "type":     "RedshiftBumpMap",
            "inputs":   {"bumpValue": "input"},   # file.outAlpha → bump.input
            "outputs":  {"outNormal": "out"},     # bump.out → shader.bump_input
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
    # ── aiNormalMap (tangent normal) ──────────────────────────────────
    "aiNormalMap": {
        "Redshift": {
            "type":     "RedshiftBumpMap",
            "inputs":   {"input": "input"},       # file.outColor → bump.input
            "outputs":  {"outValue": "out"},      # bump.out → shader.bump_input
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
    # ── RedshiftBumpMap → Arnold ──────────────────────────────────────
    "RedshiftBumpMap": {
        "Arnold": {
            "type":    "aiNormalMap",
            "inputs":  {"input": "input"},
            "outputs": {"out": "outValue"},
        },
        "Maya": {
            "type":     "bump2d",
            "inputs":   {"input": "bumpValue"},
            "outputs":  {"out": "outNormal"},
            "post_set": {"bumpInterp": 1},
        },
    },
    # ── Color Correct ─────────────────────────────────────────────────
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
    # ── Range ─────────────────────────────────────────────────────────
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
    # ── Multiply ──────────────────────────────────────────────────────
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
#  MASTER MAP
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

VALUE_MAP = {k: MASTER_MAP[k] for k in [
    "baseColor", "color", "specularRoughness", "metalness",
    "specularColor", "emissionColor", "incandescence", "opacity",
    "base", "specular", "emission", "subsurface", "coat",
    "coatRoughness", "eccentricity",
]}


# ══════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════

def get_renderer_from_mat_type(mat_type):
    for renderer, mats in RENDERER_MATERIALS.items():
        if mat_type in mats:
            return renderer
    return "Maya"


def _lc_kwargs():
    kw = dict(source=True, destination=False, plugs=True)
    if MAYA_VERSION >= 2024:
        kw["fullNodeName"] = True
    return kw


def get_exact_source_plug(shader, attr):
    conns = cmds.listConnections(f"{shader}.{attr}", **_lc_kwargs()) or []
    return conns[0] if conns else None


def walk_upstream_for_file(node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return []
    visited.add(node)
    if cmds.nodeType(node) == "file":
        return [node]
    results = []
    for up in (cmds.listConnections(node, source=True, destination=False) or []):
        results += walk_upstream_for_file(up, visited)
    return results


def get_shader_from_mesh(mesh):
    sgs = cmds.listConnections(mesh, type="shadingEngine") or []
    shaders = []
    for sg in sgs:
        s = cmds.listConnections(sg + ".surfaceShader") or []
        shaders += s
    return list(set(shaders))


def get_meshes_from_shader(shader):
    sgs = cmds.listConnections(shader, type="shadingEngine") or []
    meshes = []
    for sg in sgs:
        members = cmds.sets(sg, q=True) or []
        meshes += members
    return meshes


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
    votes = defaultdict(int)
    for shader in shaders:
        stype = cmds.nodeType(shader)
        suggestion = AUTO_SUGGEST.get(stype)
        if suggestion:
            votes[suggestion] += 1
    if not votes:
        return "Arnold", "aiStandardSurface"
    return max(votes, key=votes.get)


# ══════════════════════════════════════════════════════════════════════
#  SMART NODE CHAIN CONVERTER  ← THE FIXED CORE
# ══════════════════════════════════════════════════════════════════════

def _safe_connect(src, dst, log=None):
    """Connect src → dst safely, log result."""
    try:
        if not cmds.objExists(src.split(".")[0]):
            if log is not None:
                log.append(f"  [SKIP] Source gone: {src}")
            return False
        if not cmds.objExists(dst.split(".")[0]):
            if log is not None:
                log.append(f"  [SKIP] Dest gone: {dst}")
            return False
        if cmds.isConnected(src, dst):
            return True
        cmds.connectAttr(src, dst, force=True)
        if log is not None:
            log.append(f"  [WIRE] {src}  →  {dst}")
        return True
    except Exception as e:
        if log is not None:
            log.append(f"  [WIRE-FAIL] {src} → {dst}: {e}")
        return False


def build_converted_node(src_node, target_renderer, converted_cache, log):
    """
    Create the equivalent node for target_renderer if needed.
    Recursively rebuild the FULL upstream chain.
    Returns the NEW node name (or the original if no conversion needed).
    """
    if src_node in converted_cache:
        return converted_cache[src_node]

    node_type = cmds.nodeType(src_node)

    # Passthrough — keep as-is, still recurse upstream to convert any
    # deeper nodes that feed into this one
    if node_type in PASSTHROUGH_NODES:
        converted_cache[src_node] = src_node
        # Still recurse so deeper nodes get converted
        for up in (cmds.listConnections(
                src_node, source=True, destination=False) or []):
            build_converted_node(up, target_renderer, converted_cache, log)
        return src_node

    conversion = NODE_CONVERSION_TABLE.get(node_type, {}).get(target_renderer)

    if not conversion:
        # No conversion rule — keep and recurse
        converted_cache[src_node] = src_node
        for up in (cmds.listConnections(
                src_node, source=True, destination=False) or []):
            build_converted_node(up, target_renderer, converted_cache, log)
        return src_node

    new_type = conversion["type"]

    # If same type (no change needed) keep it
    if new_type == node_type:
        converted_cache[src_node] = src_node
        for up in (cmds.listConnections(
                src_node, source=True, destination=False) or []):
            build_converted_node(up, target_renderer, converted_cache, log)
        return src_node

    if new_type not in (cmds.allNodeTypes() or []):
        log.append(f"  [WARN] Node type '{new_type}' not in Maya — keeping '{node_type}'")
        converted_cache[src_node] = src_node
        return src_node

    # Create the new node
    new_node = cmds.shadingNode(new_type, asUtility=True,
                                 name=src_node + "_RSconv")
    log.append(f"  [CREATE] {node_type} → {new_type}  ({src_node} → {new_node})")
    converted_cache[src_node] = new_node

    # Apply post-set attributes
    for attr, val in conversion.get("post_set", {}).items():
        try:
            cmds.setAttr(f"{new_node}.{attr}", val)
            log.append(f"  [SET]    {new_node}.{attr} = {val}")
        except Exception as e:
            log.append(f"  [WARN]   setAttr {new_node}.{attr}: {e}")

    # Rebuild upstream connections INTO the new node
    input_map = conversion.get("inputs", {})
    for old_src_attr, new_dst_attr in input_map.items():
        if not cmds.attributeQuery(old_src_attr, node=src_node, exists=True):
            continue
        upstream_plugs = cmds.listConnections(
            f"{src_node}.{old_src_attr}", **_lc_kwargs()
        ) or []
        for up_plug in upstream_plugs:
            up_node = up_plug.split(".")[0]
            up_attr = up_plug.split(".", 1)[1]

            # Recurse — convert the upstream node too if needed
            converted_up = build_converted_node(
                up_node, target_renderer, converted_cache, log
            )

            # Remap the output attribute if the upstream node was converted
            if converted_up != up_node:
                up_conversion = NODE_CONVERSION_TABLE.get(
                    cmds.nodeType(up_node), {}
                ).get(target_renderer, {})
                out_map = up_conversion.get("outputs", {})
                up_attr = out_map.get(up_attr, up_attr)

            src_plug = f"{converted_up}.{up_attr}"
            dst_plug = f"{new_node}.{new_dst_attr}"
            _safe_connect(src_plug, dst_plug, log)

    return new_node


def resolve_output_plug(source_plug, target_renderer, converted_cache, log):
    """
    Given the original source plug (e.g. bump2d1.outNormal),
    return the correct output plug after node conversion.

    This is what actually gets connected to the shader attribute.
    """
    src_node = source_plug.split(".")[0]
    src_attr = source_plug.split(".", 1)[1]
    node_type = cmds.nodeType(src_node)

    # Build/get the converted node
    converted = build_converted_node(src_node, target_renderer, converted_cache, log)

    if converted == src_node:
        # No conversion happened — use original plug as-is
        return source_plug

    # Remap the output attribute
    conversion = NODE_CONVERSION_TABLE.get(node_type, {}).get(target_renderer, {})
    out_map = conversion.get("outputs", {})
    new_attr = out_map.get(src_attr, src_attr)
    return f"{converted}.{new_attr}"


# ══════════════════════════════════════════════════════════════════════
#  DATA COLLECTION
# ══════════════════════════════════════════════════════════════════════

def collect_data(shader, target_mat_type):
    results = []
    for src_attr, target_map in MASTER_MAP.items():
        if target_mat_type not in target_map:
            continue
        if not cmds.attributeQuery(src_attr, node=shader, exists=True):
            continue

        tgt_attr, preferred_plug = target_map[target_mat_type]
        source_plug = get_exact_source_plug(shader, src_attr)

        if source_plug:
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
                "file_node":      file_node,
                "file_path":      file_path,
                "tgt_attr":       tgt_attr,
                "preferred_plug": preferred_plug,
                "target_type":    target_mat_type,
                "transfer_mode":  "texture",
                "raw_value":      None,
            })
        else:
            if src_attr not in VALUE_MAP:
                continue
            try:
                val = cmds.getAttr(f"{shader}.{src_attr}")
            except Exception:
                continue
            # Skip boring defaults
            if isinstance(val, list) and isinstance(val[0], tuple):
                flat = list(val[0])
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
                    f"Attribute '{tgt_attr}' not found on '{target_node}'.\n"
                    f"  ➤ Make sure renderer plugin is loaded.",
                    "entry": entry})
        if entry["source_node"]:
            nt = cmds.nodeType(entry["source_node"])
            if nt in NODE_CONVERSION_TABLE:
                conv = NODE_CONVERSION_TABLE[nt].get(target_renderer)
                if conv and conv["type"] != nt:
                    warnings.append({"level": "warn", "message":
                        f"'{entry['source_node']}' ({nt}) → "
                        f"AUTO-CONVERT to '{conv['type']}' for {target_renderer}.\n"
                        f"  ➤ NodeFlow handles this.", "entry": entry})
    return warnings


# ══════════════════════════════════════════════════════════════════════
#  DO TRANSFER  ← FIXED: uses resolve_output_plug for full chain
# ══════════════════════════════════════════════════════════════════════

def do_transfer(data, target_node, target_mat_type, mash_waiter=None):
    log = []
    color_node = None
    converted_cache = {}   # shared per-shader transfer
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
                    ex = cmds.listConnections(mash_waiter, type="MASH_Color") or []
                    color_node = ex[0] if ex else cmds.createNode(
                        "MASH_Color", name=mash_waiter + "_Color"
                    )
                    if not ex:
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

        # ── Transfer texture ───────────────────────────────────────────
        if mode == "texture":
            source_plug = entry["source_plug"]
            source_node = entry["source_node"]
            node_type   = cmds.nodeType(source_node)

            # Case A: source IS a file node — use preferred output directly
            if node_type == "file":
                final_plug = f"{source_node}.{entry['preferred_plug']}"

            # Case B: source is an intermediate node (bump2d, aiNormalMap, etc.)
            # → convert the full chain and get the correct output plug
            else:
                final_plug = resolve_output_plug(
                    source_plug, target_renderer, converted_cache, log
                )

            fp_node = final_plug.split(".")[0]
            if not cmds.objExists(fp_node):
                log.append(f"[SKIP] Source node '{fp_node}' gone.")
                continue

            try:
                if cmds.isConnected(final_plug, dst_plug):
                    log.append(f"[SKIP] Already connected: {final_plug} → {dst_plug}")
                else:
                    cmds.connectAttr(final_plug, dst_plug, force=True)
                    log.append(f"[OK-T] {final_plug:<52}  →  {dst_plug}")
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
                    f"[OK-V] {entry['shader']}.{entry['shader_attr']:<28}"
                    f"  →  {dst_plug}  =  {val}"
                )
            except Exception as e:
                log.append(f"[FAIL] value {dst_plug}: {e}")

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
    old_sgs = cmds.listConnections(old_shader, type="shadingEngine") or []
    new_sgs = cmds.listConnections(new_shader, type="shadingEngine") or []
    new_sg  = new_sgs[0] if new_sgs else None
    if not new_sg:
        log.append(f"[SKIP] No SG on new shader '{new_shader}'.")
        return 0
    total = 0
    for old_sg in old_sgs:
        members = cmds.sets(old_sg, q=True) or []
        if members:
            cmds.sets(members, e=True, forceElement=new_sg)
            total += len(members)
            log.append(
                f"[ASSIGN] {len(members)} object(s): {old_sg} → {new_sg}"
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
QTabWidget::pane { border: 1px solid #1e3a5f; background: #0d1b2a; }
QTabBar::tab {
    background: #112240; color: #7aa2c8;
    padding: 8px 20px; border: 1px solid #1e3a5f;
    border-bottom: none; border-radius: 4px 4px 0 0; min-width: 80px;
}
QTabBar::tab:selected { background: #1b3a6b; color: #fff; font-weight: bold; }
QPushButton {
    background-color: #1b3a6b; color: #cdd9e5;
    border: 1px solid #2e5fa3; border-radius: 5px;
    padding: 6px 14px; font-weight: bold; min-height: 26px;
}
QPushButton:hover   { background-color: #2e5fa3; color: #fff; }
QPushButton:pressed { background-color: #0d1b2a; }
QPushButton#autoBtn {
    background-color: #1a4a2a; color: #66dd88;
    border: 1px solid #33aa55; border-radius: 5px;
    padding: 6px 14px; font-weight: bold;
}
QPushButton#autoBtn:hover { background-color: #2a6a3a; }
QPushButton#transferBtn {
    background-color: #2e5fa3; color: #fff;
    font-size: 14px; padding: 10px 40px;
    border-radius: 8px; font-weight: bold;
}
QPushButton#transferBtn:hover    { background-color: #4080d0; }
QPushButton#transferBtn:disabled {
    background-color: #1a2a3a; color: #445566; border-color: #223344;
}
QPushButton#linkedinBtn {
    background-color: #0a66c2; color: #fff;
    padding: 9px 20px; border-radius: 6px; border: none;
}
QPushButton#linkedinBtn:hover { background-color: #1a80e0; }
QPushButton#dangerBtn {
    background-color: #2a1010; color: #e08080; border: 1px solid #883333;
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
QLineEdit:focus   { border: 1px solid #2e5fa3; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background-color: #112240; color: #cdd9e5;
    selection-background-color: #1b3a6b; border: 1px solid #1e3a5f;
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
QLabel#sectionLabel  { color: #7aa2c8; font-weight: bold; font-size: 12px; padding: 2px 0; }
QLabel#titleLabel    { color: #4080d0; font-size: 18px; font-weight: bold; }
QLabel#subtitleLabel { color: #445e78; font-size: 11px; }
QLabel#countLabel    { color: #4080d0; font-size: 11px; font-weight: bold; }
QLabel#hintLabel     { color: #556677; font-size: 11px; font-style: italic; }
QRadioButton { spacing: 6px; }
QRadioButton::indicator {
    width: 14px; height: 14px;
    border: 1px solid #2e5fa3; border-radius: 7px; background: #112240;
}
QRadioButton::indicator:checked { background: #2e5fa3; }
QScrollBar:vertical { background: #0d1b2a; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #2e5fa3; border-radius: 4px; min-height: 20px; }
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
                "border: 2px solid #4080d0; border-radius:4px; background:#1a2e4a;"
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
        txt  = f"<b>{len(warnings)} issue(s) detected.</b><br>"
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

        row = QtWidgets.QHBoxLayout()
        lc  = QtWidgets.QVBoxLayout()
        t   = QtWidgets.QLabel("⚡  NodeFlow")
        s   = QtWidgets.QLabel(
            "Transfer Any Texture · Any Shader · Any Target  |  v4.1.0"
        )
        t.setObjectName("titleLabel")
        s.setObjectName("subtitleLabel")
        lc.addWidget(t); lc.addWidget(s)
        row.addLayout(lc); row.addStretch()
        root.addLayout(row)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setObjectName("divider")
        root.addWidget(sep)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_transfer_tab(), "  🔄  Transfer  ")
        tabs.addTab(self._build_log_tab(),      "  📋  Log  ")
        tabs.addTab(self._build_help_tab(),     "  ❓  Help  ")
        root.addWidget(tabs)

    def _build_transfer_tab(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setSpacing(8)
        L.setContentsMargins(4, 4, 4, 4)

        # ① Source Mode
        self._sec(L, "①  Source Mode")
        mr = QtWidgets.QHBoxLayout()
        self.mode_single = QtWidgets.QRadioButton("Single Shader / Mesh")
        self.mode_multi  = QtWidgets.QRadioButton("Multi Select")
        self.mode_all    = QtWidgets.QRadioButton("All Scene Materials")
        self.mode_single.setChecked(True)
        for rb in (self.mode_single, self.mode_multi, self.mode_all):
            rb.toggled.connect(self._on_mode_changed)
            mr.addWidget(rb)
        mr.addStretch()
        L.addLayout(mr)

        # Single
        self.single_widget = QtWidgets.QWidget()
        sw = QtWidgets.QHBoxLayout(self.single_widget)
        sw.setContentsMargins(0, 0, 0, 0)
        self.src_field = DragDropLineEdit(
            "Drag from Outliner / Hypershade  or  type name"
        )
        b = QtWidgets.QPushButton("← Pick")
        b.setObjectName("smallBtn"); b.setFixedWidth(70)
        b.clicked.connect(lambda: self._pick(self.src_field))
        sw.addWidget(self.src_field); sw.addWidget(b)
        L.addWidget(self.single_widget)

        # Multi
        self.multi_widget = QtWidgets.QWidget()
        mw = QtWidgets.QVBoxLayout(self.multi_widget)
        mw.setContentsMargins(0, 0, 0, 0); mw.setSpacing(4)
        mb = QtWidgets.QHBoxLayout()
        for lbl, fn in [
            ("＋ From Selection", self._add_selected_to_list),
            ("＋ All Scene",      self._add_all_to_list),
            ("✕ Clear",           self._clear_list),
        ]:
            btn = QtWidgets.QPushButton(lbl)
            btn.setObjectName("dangerBtn" if "✕" in lbl else "smallBtn")
            btn.clicked.connect(fn)
            mb.addWidget(btn)
        mb.addStretch()
        mw.addLayout(mb)
        self.shader_list = QtWidgets.QListWidget()
        self.shader_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.shader_list.setFixedHeight(100)
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
        rb = QtWidgets.QPushButton("↻")
        rb.setObjectName("smallBtn"); rb.setFixedWidth(36)
        rb.clicked.connect(self._refresh_scene_count)
        aw.addWidget(self.all_label); aw.addWidget(rb); aw.addStretch()
        self.all_widget.setVisible(False)
        L.addWidget(self.all_widget)

        L.addWidget(self._div())

        # ② Target Renderer & Material
        self._sec(L, "②  Target Renderer  &  Material Type")
        tr = QtWidgets.QHBoxLayout()
        tr.setSpacing(8)

        rc = QtWidgets.QVBoxLayout()
        rl = QtWidgets.QLabel("Renderer"); rl.setObjectName("hintLabel")
        self.renderer_combo = QtWidgets.QComboBox()
        self.renderer_combo.addItems(RENDERER_OPTIONS)
        self.renderer_combo.currentTextChanged.connect(self._on_renderer_changed)
        rc.addWidget(rl); rc.addWidget(self.renderer_combo)
        tr.addLayout(rc)

        mc = QtWidgets.QVBoxLayout()
        ml = QtWidgets.QLabel("Material Type"); ml.setObjectName("hintLabel")
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.setMinimumWidth(220)
        mc.addWidget(ml); mc.addWidget(self.material_combo)
        tr.addLayout(mc)

        ac = QtWidgets.QVBoxLayout()
        ac.addWidget(QtWidgets.QLabel(""))  # spacer label to align
        self.auto_btn = QtWidgets.QPushButton("✨  Auto Suggest")
        self.auto_btn.setObjectName("autoBtn")
        self.auto_btn.setToolTip(
            "Reads source shaders and picks the best target renderer + material"
        )
        self.auto_btn.clicked.connect(self._auto_suggest)
        ac.addWidget(self.auto_btn)
        tr.addLayout(ac)
        tr.addStretch()
        L.addLayout(tr)

        self.auto_hint = QtWidgets.QLabel("")
        self.auto_hint.setObjectName("hintLabel")
        L.addWidget(self.auto_hint)

        L.addWidget(self._div())

        # ③ Target Node
        self._sec(L, "③  Target Node  —  Leave empty to auto-create per shader")
        trow = QtWidgets.QHBoxLayout()
        self.tgt_field = DragDropLineEdit(
            "Drag existing shader here  or  leave empty to auto-create"
        )
        tp = QtWidgets.QPushButton("← Pick")
        tp.setObjectName("smallBtn"); tp.setFixedWidth(70)
        tp.clicked.connect(lambda: self._pick(self.tgt_field))
        trow.addWidget(self.tgt_field); trow.addWidget(tp)
        L.addLayout(trow)

        # MASH
        self.mash_group = QtWidgets.QWidget()
        mg = QtWidgets.QVBoxLayout(self.mash_group)
        mg.setContentsMargins(0, 0, 0, 0)
        self._sec(mg, "④  MASH Waiter Node")
        mrow = QtWidgets.QHBoxLayout()
        self.mash_field = DragDropLineEdit("Drag MASH Waiter  e.g.  MASH1_Waiter")
        mp = QtWidgets.QPushButton("← Pick")
        mp.setObjectName("smallBtn"); mp.setFixedWidth(70)
        mp.clicked.connect(lambda: self._pick(self.mash_field))
        mrow.addWidget(self.mash_field); mrow.addWidget(mp)
        mg.addLayout(mrow)
        self.mash_group.setVisible(False)
        L.addWidget(self.mash_group)

        L.addWidget(self._div())

        # Scan
        sr = QtWidgets.QHBoxLayout()
        sb = QtWidgets.QPushButton("🔍  Scan Materials & Textures")
        sb.clicked.connect(self._scan)
        sr.addWidget(sb); sr.addStretch()
        L.addLayout(sr)

        # Table
        self._sec(L, "Detected Connections & Values  —  Review before Transfer")
        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Source Shader", "Attr", "Mode",
            "Source / Value", "File Node", "→ Target Attr", "Status"
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "QTableWidget { alternate-background-color: #0e1f33; }"
        )
        self.table.setMinimumHeight(180)
        L.addWidget(self.table)

        xr = QtWidgets.QHBoxLayout()
        xr.addStretch()
        self.transfer_btn = QtWidgets.QPushButton("🚀  Transfer & Auto-Assign")
        self.transfer_btn.setObjectName("transferBtn")
        self.transfer_btn.setEnabled(False)
        self.transfer_btn.clicked.connect(self._transfer)
        xr.addWidget(self.transfer_btn)
        xr.addStretch()
        L.addLayout(xr)
        L.addSpacing(8)

        scroll.setWidget(w)
        self._on_renderer_changed(self.renderer_combo.currentText())
        return scroll

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

    def _build_help_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(4, 4, 4, 4)
        help_text = QtWidgets.QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <div style='color:#cdd9e5;font-family:Segoe UI;font-size:13px;line-height:1.8'>
        <p style='color:#4080d0;font-size:16px;font-weight:bold'>
            ⚡ NodeFlow v4.1 — How to Use
        </p>
        <p style='color:#7aa2c8;font-weight:bold'>What NodeFlow Does</p>
        <p>Converts full materials between renderers — textures, values,
        intermediate nodes (bump, color correct, range) — and auto-assigns
        every mesh to the new shader. Old shaders are kept for rollback.</p>

        <p style='color:#7aa2c8;font-weight:bold'>Node Chain Fix (v4.1)</p>
        <p>When a bump2d or aiNormalMap is in the chain, NodeFlow now correctly:
        <ul>
          <li>Creates RedshiftBumpMap (or equivalent)</li>
          <li>Wires file → new bump node input</li>
          <li>Wires new bump node output → shader.bump_input</li>
        </ul>
        All intermediate node outputs are fully rewired — nothing is left dangling.</p>

        <p style='color:#7aa2c8;font-weight:bold'>Conversion Map</p>
        <ul>
            <li>bump2d → RedshiftBumpMap (inputType=0, height)</li>
            <li>aiNormalMap → RedshiftBumpMap (inputType=1, tangent normal)</li>
            <li>aiColorCorrect → rsColorCorrect</li>
            <li>aiRange → rsRange</li>
            <li>aiMultiply → rsColorLayer</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold'>Auto Suggest</p>
        <ul>
            <li>aiStandardSurface → RedshiftStandardMaterial</li>
            <li>RedshiftStandardMaterial → aiStandardSurface</li>
            <li>lambert / blinn / phong → standardSurface</li>
            <li>standardSurface → aiStandardSurface</li>
        </ul>
        <br><hr style='border-color:#1e3a5f'><br>
        <p style='color:#445e78;font-size:11px'>
            NodeFlow v4.1.0 · Youssef El Qadi · Pipeline TD
        </p>
        </div>
        """)
        L.addWidget(help_text)
        li = QtWidgets.QPushButton("  🔗  Connect on LinkedIn — Youssef El Qadi")
        li.setObjectName("linkedinBtn")
        li.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        li.clicked.connect(lambda: webbrowser.open(
            "https://www.linkedin.com/in/youssef-el-qadi-6a78a4247"
        ))
        L.addWidget(li)
        return w

    # ── Small helpers ─────────────────────────────────────────────────
    def _sec(self, layout, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setObjectName("sectionLabel")
        layout.addWidget(lbl)

    def _div(self):
        f = QtWidgets.QFrame()
        f.setFrameShape(QtWidgets.QFrame.HLine)
        f.setObjectName("divider")
        return f

    def _pick(self, field):
        sel = cmds.ls(sl=True)
        if sel:
            field.setText(sel[0])
        else:
            self._log("[WARN] Nothing selected.")

    def _log(self, msg):
        self.log_output.append(msg)

    def _on_mode_changed(self):
        self.single_widget.setVisible(self.mode_single.isChecked())
        self.multi_widget.setVisible(self.mode_multi.isChecked())
        self.all_widget.setVisible(self.mode_all.isChecked())
        if self.mode_all.isChecked():
            self._refresh_scene_count()

    def _on_renderer_changed(self, value):
        self.material_combo.clear()
        self.material_combo.addItems(get_available_materials(value))
        self.mash_group.setVisible(value == "MASH")

    def _auto_suggest(self):
        shaders, err = self._get_source_shaders()
        if err or not shaders:
            self.auto_hint.setText("⚠  Load source shaders first.")
            return
        renderer, mat_type = auto_suggest_target(shaders)
        idx = self.renderer_combo.findText(renderer)
        if idx >= 0:
            self.renderer_combo.setCurrentIndex(idx)
        idx2 = self.material_combo.findText(mat_type)
        if idx2 >= 0:
            self.material_combo.setCurrentIndex(idx2)
        self.auto_hint.setText(
            f"✨  {renderer} → {mat_type}  ({len(shaders)} shader(s) analysed)"
        )
        self._log(f"[AUTO] Suggested: {renderer} → {mat_type}")

    def _add_selected_to_list(self):
        existing = {
            self.shader_list.item(i).text()
            for i in range(self.shader_list.count())
        }
        added = 0
        for node in (cmds.ls(sl=True) or []):
            nt = cmds.nodeType(node)
            shader = node if nt in SUPPORTED_SOURCES else \
                     (get_shader_from_mesh(node) or [None])[0]
            if shader and shader not in existing:
                self.shader_list.addItem(shader)
                existing.add(shader)
                added += 1
        self._update_count()
        self._log(f"[LIST] +{added} from selection.")

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
        self._log(f"[LIST] +{added} from scene.")

    def _clear_list(self):
        self.shader_list.clear()
        self._update_count()

    def _update_count(self):
        self.count_label.setText(f"{self.shader_list.count()} shader(s)")

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
            if mode == "texture":
                src_val = entry["source_plug"] or "—"
            else:
                v = entry["raw_value"]
                src_val = str(v[0]) if (
                    isinstance(v, list) and v and isinstance(v[0], tuple)
                ) else str(v)
            status = ""
            if mode == "texture":
                if entry["file_node"] and not entry["file_path"]:
                    status = "⚠ No path"
                elif entry["source_node"] and \
                        cmds.nodeType(entry["source_node"]) in NODE_CONVERSION_TABLE:
                    status = "🔄 Will convert"
                else:
                    status = "✓"
            else:
                status = "✓"

            cols = [
                entry["shader"],
                entry["shader_attr"],
                mode_label,
                src_val,
                entry["file_node"] or ("—" if mode == "texture" else "n/a"),
                entry["tgt_attr"],
                status,
            ]
            colors = {
                0: "#4080d0",
                1: "#7aa2c8",
                2: "#88cc88" if mode == "texture" else "#ccaa44",
                5: "#88cc88",
                6: "#e08040" if "⚠" in status else
                   "#4488ff" if "convert" in status else "#448844",
            }
            for col, val in enumerate(cols):
                item = QtWidgets.QTableWidgetItem(str(val))
                if col in colors:
                    item.setForeground(QtGui.QColor(colors[col]))
                self.table.setItem(row, col, item)

    def _scan(self):
        shaders, err = self._get_source_shaders()
        if err:
            QtWidgets.QMessageBox.warning(self, "NodeFlow", err)
            return
        target_mat   = self.material_combo.currentText()
        self._all_data = []
        for shader in shaders:
            self._all_data += collect_data(shader, target_mat)
        if not self._all_data:
            self._log("[WARN] No transferable data found.")
            self.transfer_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(
                self, "NodeFlow",
                "No connected textures or attribute values found."
            )
            return
        tex = sum(1 for e in self._all_data if e["transfer_mode"] == "texture")
        val = sum(1 for e in self._all_data if e["transfer_mode"] == "value")
        self._populate_table(self._all_data)
        self.transfer_btn.setEnabled(True)
        self._log(
            f"[SCAN] {len(shaders)} shader(s) — "
            f"{tex} texture(s), {val} value(s) → {target_mat}"
        )

    def _transfer(self):
        target_mat  = self.material_combo.currentText()
        tgt_input   = self.tgt_field.text().strip()
        mash_waiter = self.mash_field.text().strip() \
                      if self.renderer_combo.currentText() == "MASH" else None

        shaders, err = self._get_source_shaders()
        if err:
            QtWidgets.QMessageBox.warning(self, "NodeFlow", err)
            return

        tgt_val  = tgt_input if tgt_input and cmds.objExists(tgt_input) else None
        warnings = validate_transfer(self._all_data, tgt_val, target_mat)
        if warnings:
            dlg = WarningDialog(warnings, parent=self)
            dlg.exec_()
            if not dlg.result_choice:
                self._log("[CANCELLED]")
                return

        data_by_shader = defaultdict(list)
        for entry in self._all_data:
            data_by_shader[entry["shader"]].append(entry)

        total_ok = total_fail = total_assigned = 0

        for shader, entries in data_by_shader.items():
            if target_mat == "MASH":
                target_node = None
            elif tgt_input and cmds.objExists(tgt_input):
                target_node = tgt_input
            else:
                target_node = create_target_shader(target_mat, shader)
                if target_node:
                    self._log(f"[CREATE] '{target_node}' for '{shader}'")
                else:
                    self._log(
                        f"[ERROR] Could not create '{target_mat}' — plugin loaded?"
                    )
                    continue

            log_lines = do_transfer(entries, target_node, target_mat, mash_waiter)
            for line in log_lines:
                self._log(line)

            total_ok   += sum(1 for l in log_lines if l.startswith("[OK"))
            total_fail += sum(1 for l in log_lines if l.startswith("[FAIL]"))

            if target_node and target_mat != "MASH":
                n = assign_shader_to_meshes(target_node, shader, log_lines)
                total_assigned += n
                for line in log_lines:
                    if "[ASSIGN]" in line:
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
            f"✅  {total_ok} attribute(s) transferred\n"
            f"❌  {total_fail} failed\n"
            f"🔗  {total_assigned} mesh(es) auto-assigned\n\n"
            f"Old shaders kept — check Log tab for details."
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
