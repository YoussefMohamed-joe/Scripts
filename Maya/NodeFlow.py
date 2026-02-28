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
║   Version : 1.0.0                                                    ║
║   Support : Maya 2020+                                               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import webbrowser
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

# ─── Maya Version ─────────────────────────────────────────────────────
MAYA_VERSION = int(cmds.about(version=True).split(".")[0])

# ══════════════════════════════════════════════════════════════════════
#  MASTER MAPPING TABLE
#  Format: source_attr → { target_shader_type: (target_attr, src_plug) }
#  src_plug: which output plug to use from the file node
# ══════════════════════════════════════════════════════════════════════

MASTER_MAP = {
    # ── Base Color / Diffuse ──────────────────────────────────────
    "baseColor": {
        "RedshiftStandardMaterial": ("diffuse_color",       "outColor"),
        "aiStandardSurface":        ("baseColor",           "outColor"),
        "standardSurface":          ("baseColor",           "outColor"),
        "lambert":                  ("color",               "outColor"),
        "blinn":                    ("color",               "outColor"),
        "MASH":                     ("MASH_Color.texture",  "outColor"),
    },
    "color": {
        "RedshiftStandardMaterial": ("diffuse_color",       "outColor"),
        "aiStandardSurface":        ("baseColor",           "outColor"),
        "standardSurface":          ("baseColor",           "outColor"),
        "MASH":                     ("MASH_Color.texture",  "outColor"),
    },

    # ── Roughness ─────────────────────────────────────────────────
    "specularRoughness": {
        "RedshiftStandardMaterial": ("refl_roughness",      "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",   "outAlpha"),
        "standardSurface":          ("specularRoughness",   "outAlpha"),
        "blinn":                    ("eccentricity",        "outAlpha"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "eccentricity": {
        "RedshiftStandardMaterial": ("refl_roughness",      "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",   "outAlpha"),
        "standardSurface":          ("specularRoughness",   "outAlpha"),
    },
    "roughness": {
        "RedshiftStandardMaterial": ("refl_roughness",      "outAlpha"),
        "aiStandardSurface":        ("specularRoughness",   "outAlpha"),
        "standardSurface":          ("specularRoughness",   "outAlpha"),
    },

    # ── Metalness ─────────────────────────────────────────────────
    "metalness": {
        "RedshiftStandardMaterial": ("metalness",           "outAlpha"),
        "aiStandardSurface":        ("metalness",           "outAlpha"),
        "standardSurface":          ("metalness",           "outAlpha"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },

    # ── Specular Color ────────────────────────────────────────────
    "specularColor": {
        "RedshiftStandardMaterial": ("refl_color",          "outColor"),
        "aiStandardSurface":        ("specularColor",       "outColor"),
        "standardSurface":          ("specularColor",       "outColor"),
        "blinn":                    ("specularColor",       "outColor"),
    },

    # ── Emission ──────────────────────────────────────────────────
    "emissionColor": {
        "RedshiftStandardMaterial": ("emission_color",      "outColor"),
        "aiStandardSurface":        ("emissionColor",       "outColor"),
        "standardSurface":          ("emissionColor",       "outColor"),
        "MASH":                     ("MASH_Color.texture",  "outColor"),
    },
    "incandescence": {
        "RedshiftStandardMaterial": ("emission_color",      "outColor"),
        "aiStandardSurface":        ("emissionColor",       "outColor"),
        "standardSurface":          ("emissionColor",       "outColor"),
    },

    # ── Opacity / Transparency ────────────────────────────────────
    "opacity": {
        "RedshiftStandardMaterial": ("opacity_color",       "outColor"),
        "aiStandardSurface":        ("opacity",             "outColor"),
        "standardSurface":          ("opacity",             "outColor"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },
    "transparency": {
        "RedshiftStandardMaterial": ("opacity_color",       "outColor"),
        "aiStandardSurface":        ("opacity",             "outColor"),
        "standardSurface":          ("opacity",             "outColor"),
        "MASH":                     ("MASH_Distribute.strengthMap", "outAlpha"),
    },

    # ── Normal Map ────────────────────────────────────────────────
    "normalCamera": {
        "RedshiftStandardMaterial": ("bump_input",          "outColor"),
        "aiStandardSurface":        ("normalCamera",        "outColor"),
        "standardSurface":          ("normalCamera",        "outColor"),
    },

    # ── Displacement ──────────────────────────────────────────────
    "displacementShader": {
        "RedshiftStandardMaterial": ("displacement",        "outColor"),
        "aiStandardSurface":        ("displacementShader",  "outColor"),
        "standardSurface":          ("displacementShader",  "outColor"),
    },

    # ── Subsurface ────────────────────────────────────────────────
    "subsurfaceColor": {
        "RedshiftStandardMaterial": ("ms_color0",           "outColor"),
        "aiStandardSurface":        ("subsurfaceColor",     "outColor"),
        "standardSurface":          ("subsurfaceColor",     "outColor"),
    },

    # ── Coat ──────────────────────────────────────────────────────
    "coatColor": {
        "RedshiftStandardMaterial": ("coat_color",          "outColor"),
        "aiStandardSurface":        ("coatColor",           "outColor"),
        "standardSurface":          ("coatColor",           "outColor"),
    },
    "coatRoughness": {
        "RedshiftStandardMaterial": ("coat_roughness",      "outAlpha"),
        "aiStandardSurface":        ("coatRoughness",       "outAlpha"),
        "standardSurface":          ("coatRoughness",       "outAlpha"),
    },
}

SUPPORTED_SOURCES = [
    "aiStandardSurface", "standardSurface",
    "lambert", "blinn", "phong", "phongE",
    "RedshiftStandardMaterial"
]

TARGET_OPTIONS = [
    "RedshiftStandardMaterial",
    "aiStandardSurface",
    "standardSurface",
    "lambert",
    "blinn",
    "MASH",
]

TARGET_NODE_TYPE = {
    "RedshiftStandardMaterial": "RedshiftStandardMaterial",
    "aiStandardSurface":        "aiStandardSurface",
    "standardSurface":          "standardSurface",
    "lambert":                  "lambert",
    "blinn":                    "blinn",
}


# ══════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════════

def get_shader_from_mesh(mesh):
    sgs = cmds.listConnections(mesh, type="shadingEngine") or []
    shaders = []
    for sg in sgs:
        s = cmds.listConnections(sg + ".surfaceShader") or []
        shaders += s
    return shaders


def walk_upstream_for_file(node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return []
    visited.add(node)
    if cmds.nodeType(node) == "file":
        return [node]
    results = []
    upstream = cmds.listConnections(
        node, source=True, destination=False, plugs=False
    ) or []
    for up in upstream:
        results += walk_upstream_for_file(up, visited)
    return results


def get_exact_source_plug(shader, attr):
    kwargs = dict(source=True, destination=False, plugs=True)
    if MAYA_VERSION >= 2024:
        kwargs["fullNodeName"] = True
    conns = cmds.listConnections(f"{shader}.{attr}", **kwargs) or []
    return conns[0] if conns else None


def collect_texture_data(shader, target_type):
    results = []
    for src_attr, target_map in MASTER_MAP.items():
        if target_type not in target_map:
            continue
        if not cmds.attributeQuery(src_attr, node=shader, exists=True):
            continue

        source_plug = get_exact_source_plug(shader, src_attr)
        if not source_plug:
            continue

        source_node = source_plug.split(".")[0]
        source_attr = source_plug.split(".", 1)[1]
        tgt_attr, preferred_plug = target_map[target_type]

        file_nodes = walk_upstream_for_file(source_node)
        file_node  = file_nodes[0] if file_nodes else None
        file_path  = ""
        if file_node:
            file_path = cmds.getAttr(file_node + ".fileTextureName") or ""

        # Use the actual connected plug, but override with preferred if mismatch
        final_plug = source_plug
        if file_node:
            final_plug = f"{file_node}.{preferred_plug}"

        results.append({
            "shader":       shader,
            "shader_attr":  src_attr,
            "source_plug":  source_plug,
            "final_plug":   final_plug,
            "source_node":  source_node,
            "source_attr":  source_attr,
            "file_node":    file_node,
            "file_path":    file_path,
            "tgt_attr":     tgt_attr,
            "target_type":  target_type,
        })
    return results


def validate_transfer(data):
    warnings = []
    slot_seen = {}
    for entry in data:
        if entry["file_node"] and not entry["file_path"]:
            warnings.append({
                "level": "warn",
                "message": (
                    f"File node '{entry['file_node']}' on attribute '{entry['shader_attr']}' "
                    f"has NO texture path assigned.\n"
                    f"➤ Fix: Open Hypershade and assign an image to this file node first."
                ),
                "entry": entry
            })
        key = entry["tgt_attr"]
        if key in slot_seen:
            warnings.append({
                "level": "warn",
                "message": (
                    f"Conflict: Both '{slot_seen[key]['shader_attr']}' and "
                    f"'{entry['shader_attr']}' want to connect to target slot '{key}'.\n"
                    f"➤ Fix: Only the last one will be applied. Remove the unwanted connection."
                ),
                "entry": entry
            })
        slot_seen[key] = entry

        src_a = entry["source_attr"]
        _, preferred = MASTER_MAP[entry["shader_attr"]][entry["target_type"]]
        if ("outColor" in preferred and "outAlpha" in src_a) or \
           ("outAlpha" in preferred and "outColor" in src_a):
            warnings.append({
                "level": "warn",
                "message": (
                    f"Plug type mismatch on '{entry['shader_attr']}':\n"
                    f"  Original connection used '{src_a}' but target expects '{preferred}'.\n"
                    f"➤ Fix: Check the output type of node '{entry['source_node']}'."
                ),
                "entry": entry
            })
    return warnings


def get_or_create_mash_color_node(mash_waiter):
    existing = cmds.listConnections(mash_waiter, type="MASH_Color") or []
    if existing:
        return existing[0], False
    node = cmds.createNode("MASH_Color", name=mash_waiter + "_Color")
    cmds.setAttr(node + ".mapType", 1)
    return node, True


def do_transfer(data, target_node, target_type, mash_waiter=None):
    log = []
    color_node = None

    for entry in data:
        tgt_attr = entry["tgt_attr"]
        src_plug = entry["final_plug"]

        # ── MASH special handling ──────────────────────────────────
        if target_type == "MASH":
            if not mash_waiter or not cmds.objExists(mash_waiter):
                log.append("[ERROR] MASH Waiter node not found. Skipping MASH transfers.")
                continue

            if tgt_attr.startswith("MASH_Color."):
                mash_attr = tgt_attr.split(".", 1)[1]
                if color_node is None:
                    color_node, created = get_or_create_mash_color_node(mash_waiter)
                    if created:
                        log.append(f"[INFO] Created MASH_Color node: {color_node}")
                dst_plug = f"{color_node}.{mash_attr}"

            elif tgt_attr.startswith("MASH_Distribute."):
                mash_attr = tgt_attr.split(".", 1)[1]
                dist_nodes = cmds.listConnections(mash_waiter, type="MASH_Distribute") or []
                if not dist_nodes:
                    log.append(f"[SKIP] No MASH_Distribute found for '{entry['shader_attr']}'.")
                    continue
                cmds.setAttr(dist_nodes[0] + ".useStrengthMap", 1)
                dst_plug = f"{dist_nodes[0]}.{mash_attr}"
            else:
                log.append(f"[SKIP] Unknown MASH target: {tgt_attr}")
                continue

        # ── Standard shader handling ───────────────────────────────
        else:
            if not target_node or not cmds.objExists(target_node):
                log.append(f"[ERROR] Target node '{target_node}' not found.")
                continue

            # Handle displacement — connects to shading group, not shader
            if tgt_attr == "displacement":
                sgs = cmds.listConnections(target_node, type="shadingEngine") or []
                if sgs:
                    dst_plug = f"{sgs[0]}.displacementShader"
                else:
                    log.append(f"[SKIP] No shading group found for displacement.")
                    continue
            else:
                dst_plug = f"{target_node}.{tgt_attr}"

        try:
            if not cmds.isConnected(src_plug, dst_plug):
                cmds.connectAttr(src_plug, dst_plug, force=True)
            log.append(f"[OK]   {src_plug:<45}  →  {dst_plug}")
        except Exception as e:
            log.append(f"[FAIL] {src_plug}  →  {dst_plug}\n       {e}")

    return log


def create_target_shader(target_type, base_name):
    node_type = TARGET_NODE_TYPE.get(target_type)
    if not node_type:
        return None
    shader = cmds.shadingNode(node_type, asShader=True, name=base_name + "_NF")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader + "SG")
    cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader")
    return shader


# ══════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
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
    background: #112240;
    color: #7aa2c8;
    padding: 8px 22px;
    border: 1px solid #1e3a5f;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
}
QTabBar::tab:selected {
    background: #1b3a6b;
    color: #ffffff;
    font-weight: bold;
}
QPushButton {
    background-color: #1b3a6b;
    color: #cdd9e5;
    border: 1px solid #2e5fa3;
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: bold;
}
QPushButton:hover  { background-color: #2e5fa3; color: #ffffff; }
QPushButton:pressed { background-color: #0d1b2a; }
QPushButton#transferBtn {
    background-color: #2e5fa3;
    font-size: 14px;
    padding: 10px 40px;
    border-radius: 8px;
}
QPushButton#transferBtn:hover    { background-color: #4080d0; }
QPushButton#transferBtn:disabled {
    background-color: #1a2a3a;
    color: #445566;
    border-color: #223344;
}
QPushButton#linkedinBtn {
    background-color: #0a66c2;
    color: #ffffff;
    font-size: 13px;
    padding: 9px 20px;
    border-radius: 6px;
    border: none;
}
QPushButton#linkedinBtn:hover { background-color: #1a80e0; }
QLineEdit, QComboBox {
    background-color: #112240;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cdd9e5;
    min-height: 28px;
}
QLineEdit:focus { border: 1px solid #2e5fa3; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #112240;
    selection-background-color: #1b3a6b;
    border: 1px solid #1e3a5f;
}
QTableWidget {
    background-color: #0a1628;
    gridline-color: #1e3a5f;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
}
QTableWidget::item          { padding: 4px 8px; }
QTableWidget::item:selected { background-color: #1b3a6b; color: #ffffff; }
QHeaderView::section {
    background-color: #112240;
    color: #7aa2c8;
    border: 1px solid #1e3a5f;
    padding: 6px;
    font-weight: bold;
}
QTextEdit {
    background-color: #0a1628;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    color: #cdd9e5;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}
QLabel#sectionLabel {
    color: #7aa2c8;
    font-weight: bold;
    font-size: 12px;
    padding: 4px 0px;
}
QLabel#titleLabel {
    color: #4080d0;
    font-size: 17px;
    font-weight: bold;
    padding: 4px 0px;
}
QLabel#subtitleLabel {
    color: #445e78;
    font-size: 11px;
    padding: 0px;
}
QScrollBar:vertical {
    background: #0d1b2a; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2e5fa3; border-radius: 4px; min-height: 20px;
}
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #2e5fa3;
    border-radius: 3px;
    background: #112240;
}
QCheckBox::indicator:checked { background: #2e5fa3; }
"""


class DragDropLineEdit(QtWidgets.QLineEdit):
    """QLineEdit that accepts Maya node drag-and-drop from Outliner/Hypershade."""
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
                "background-color: #112240;"
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event):
        self.setStyleSheet("")
        if event.mimeData().hasFormat("application/x-maya-data"):
            raw = bytes(
                event.mimeData().data("application/x-maya-data")
            ).decode("utf-8", errors="ignore")
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


class WarningDialog(QtWidgets.QDialog):
    def __init__(self, warnings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️  NodeFlow — Transfer Warnings")
        self.setMinimumSize(640, 380)
        self.setStyleSheet(STYLE)
        self.result_choice = False
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        header = QtWidgets.QLabel(
            f"<b>{len(warnings)} issue(s) detected</b> before transfer.<br>"
            "Review carefully. Choose <b>Yes</b> to continue anyway, "
            "or <b>No</b> to cancel and fix first."
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)
        for i, w in enumerate(warnings, 1):
            icon = "🔴" if w["level"] == "error" else "🟡"
            self.text.append(f"{icon}  Issue {i}:\n{w['message']}\n{'─'*60}\n")
        layout.addWidget(self.text)

        row = QtWidgets.QHBoxLayout()
        yes = QtWidgets.QPushButton("✅  Yes, Continue Transfer")
        no  = QtWidgets.QPushButton("❌  No, I'll Fix First")
        yes.clicked.connect(self._yes)
        no.clicked.connect(self._no)
        row.addWidget(yes)
        row.addWidget(no)
        layout.addLayout(row)

    def _yes(self): self.result_choice = True;  self.accept()
    def _no(self):  self.result_choice = False; self.reject()


# ══════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════

class NodeFlowTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NodeFlow  —  Transfer Any Texture. Any Shader. Any Target.")
        self.setMinimumSize(900, 660)
        self.setStyleSheet(STYLE)
        self._texture_data  = []
        self._target_shader = None
        self._build_ui()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(8)

        # Header
        title    = QtWidgets.QLabel("⚡  NodeFlow")
        subtitle = QtWidgets.QLabel("Transfer Any Texture · Any Shader · Any Target  |  v1.0.0")
        title.setObjectName("titleLabel")
        subtitle.setObjectName("subtitleLabel")
        root.addWidget(title)
        root.addWidget(subtitle)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color: #1e3a5f;")
        root.addWidget(sep)

        # Tabs
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_transfer_tab(), "  🔄  Transfer  ")
        tabs.addTab(self._build_log_tab(),      "  📋  Log  ")
        tabs.addTab(self._build_help_tab(),     "  ❓  Help  ")
        root.addWidget(tabs)

    # ── Transfer Tab ──────────────────────────────────────────────────
    def _build_transfer_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setSpacing(10)

        # Source
        lbl = QtWidgets.QLabel("① Source  —  Mesh or Shader")
        lbl.setObjectName("sectionLabel")
        L.addWidget(lbl)

        src_row = QtWidgets.QHBoxLayout()
        self.src_field = DragDropLineEdit(
            "Drag from Outliner / Hypershade  or  type name  e.g.  aiStandardSurface1"
        )
        src_pick = QtWidgets.QPushButton("← Pick Selected")
        src_pick.setFixedWidth(130)
        src_pick.clicked.connect(lambda: self._pick(self.src_field))
        src_row.addWidget(self.src_field)
        src_row.addWidget(src_pick)
        L.addLayout(src_row)

        # Target Type
        lbl2 = QtWidgets.QLabel("② Target Shader Type")
        lbl2.setObjectName("sectionLabel")
        L.addWidget(lbl2)

        type_row = QtWidgets.QHBoxLayout()
        self.target_combo = QtWidgets.QComboBox()
        self.target_combo.addItems(TARGET_OPTIONS)
        self.target_combo.currentTextChanged.connect(self._on_target_changed)
        type_row.addWidget(self.target_combo)
        type_row.addStretch()
        L.addLayout(type_row)

        # Target Node (existing or new)
        lbl3 = QtWidgets.QLabel("③ Target Node  —  Existing node  or  leave empty to create new")
        lbl3.setObjectName("sectionLabel")
        L.addWidget(lbl3)

        tgt_row = QtWidgets.QHBoxLayout()
        self.tgt_field = DragDropLineEdit(
            "Drag target shader here  or  leave empty to auto-create"
        )
        tgt_pick = QtWidgets.QPushButton("← Pick Selected")
        tgt_pick.setFixedWidth(130)
        tgt_pick.clicked.connect(lambda: self._pick(self.tgt_field))
        tgt_row.addWidget(self.tgt_field)
        tgt_row.addWidget(tgt_pick)
        L.addLayout(tgt_row)

        # MASH Waiter (shown only when MASH selected)
        self.mash_group = QtWidgets.QWidget()
        mash_L = QtWidgets.QVBoxLayout(self.mash_group)
        mash_L.setContentsMargins(0, 0, 0, 0)
        mash_lbl = QtWidgets.QLabel("④ MASH Waiter Node")
        mash_lbl.setObjectName("sectionLabel")
        mash_row = QtWidgets.QHBoxLayout()
        self.mash_field = DragDropLineEdit(
            "Drag MASH Waiter here  e.g.  MASH1_Waiter"
        )
        mash_pick = QtWidgets.QPushButton("← Pick Selected")
        mash_pick.setFixedWidth(130)
        mash_pick.clicked.connect(lambda: self._pick(self.mash_field))
        mash_row.addWidget(self.mash_field)
        mash_row.addWidget(mash_pick)
        mash_L.addWidget(mash_lbl)
        mash_L.addLayout(mash_row)
        self.mash_group.setVisible(False)
        L.addWidget(self.mash_group)

        # Scan button
        scan_btn = QtWidgets.QPushButton("🔍  Scan Textures")
        scan_btn.clicked.connect(self._scan)
        L.addWidget(scan_btn)

        # Table
        tbl_lbl = QtWidgets.QLabel("Detected Connections  —  Review before Transfer")
        tbl_lbl.setObjectName("sectionLabel")
        L.addWidget(tbl_lbl)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Shader Attr", "Source Plug", "File Node", "→ Target Attr", "File Path"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "QTableWidget { alternate-background-color: #0e1f33; }"
        )
        L.addWidget(self.table)

        # Transfer button
        self.transfer_btn = QtWidgets.QPushButton("🚀  Transfer Textures")
        self.transfer_btn.setObjectName("transferBtn")
        self.transfer_btn.setEnabled(False)
        self.transfer_btn.clicked.connect(self._transfer)
        L.addWidget(self.transfer_btn, alignment=Qt.AlignCenter)

        return w

    # ── Log Tab ───────────────────────────────────────────────────────
    def _build_log_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        clear_btn = QtWidgets.QPushButton("🗑  Clear Log")
        clear_btn.clicked.connect(self.log_output.clear)
        L.addWidget(self.log_output)
        L.addWidget(clear_btn, alignment=Qt.AlignRight)
        return w

    # ── Help Tab ──────────────────────────────────────────────────────
    def _build_help_tab(self):
        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setSpacing(12)

        help_text = QtWidgets.QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <div style='color:#cdd9e5;font-family:Segoe UI;font-size:13px;line-height:1.8'>

        <p style='color:#4080d0;font-size:16px;font-weight:bold'>
            ⚡ NodeFlow — How to Use
        </p>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>What is NodeFlow?</p>
        <p>NodeFlow transfers texture connections from any Maya shader to any target shader
        or MASH network — preserving the full upstream node chain (file nodes,
        place2dTexture, colorCorrect, bump2d, etc.) with 100% plug accuracy.</p>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Step by Step</p>
        <ol>
            <li>Assign your textures to your source shader in Hypershade as normal.</li>
            <li>Open NodeFlow.</li>
            <li><b>Source:</b> Drag your mesh or shader from Outliner / Hypershade into field ①,
                or click <i>Pick Selected</i>.</li>
            <li><b>Target Type:</b> Choose your target renderer or MASH from the dropdown ②.</li>
            <li><b>Target Node:</b> Drag an existing target shader into field ③,
                or leave it empty to auto-create a new one.</li>
            <li><b>MASH only:</b> Drag your MASH Waiter node into field ④ (appears automatically).</li>
            <li>Click <b>Scan Textures</b> — review the table to confirm all mappings.</li>
            <li>Click <b>Transfer Textures</b>.</li>
            <li>If warnings appear, read them and choose Yes to continue or No to fix first.</li>
        </ol>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Supported Sources</p>
        <p>aiStandardSurface · standardSurface · lambert · blinn · phong · phongE ·
        RedshiftStandardMaterial</p>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Supported Targets</p>
        <p>RedshiftStandardMaterial · aiStandardSurface · standardSurface ·
        lambert · blinn · MASH Network</p>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Channels Transferred</p>
        <p>Base Color · Roughness · Metalness · Specular · Emission · Opacity ·
        Normal · Displacement · Subsurface · Coat</p>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Warning System</p>
        <ul>
            <li>🟡 Empty file node — no texture path assigned.</li>
            <li>🟡 Plug type mismatch — outColor vs outAlpha conflict.</li>
            <li>🟡 Slot conflict — two sources competing for same target attribute.</li>
            <li>🔴 Missing MASH nodes — Distribute or Waiter not found.</li>
        </ul>

        <p style='color:#7aa2c8;font-weight:bold;font-size:14px'>Maya Version Support</p>
        <p>Maya 2020 and above. Plug name resolution uses fullNodeName on Maya 2024+
        automatically.</p>

        <br>
        <hr style='border-color:#1e3a5f'>
        <br>

        <p style='color:#445e78;font-size:11px'>
            NodeFlow v1.0.0 · Developed by Youssef El Qadi · Pipeline TD
        </p>
        </div>
        """)
        L.addWidget(help_text)

        linkedin_btn = QtWidgets.QPushButton(
            "  🔗  Connect with me on LinkedIn — Youssef El Qadi"
        )
        linkedin_btn.setObjectName("linkedinBtn")
        linkedin_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        linkedin_btn.clicked.connect(
            lambda: webbrowser.open(
                "https://www.linkedin.com/in/youssef-el-qadi-6a78a4247"
            )
        )
        L.addWidget(linkedin_btn)
        return w

    # ── Helpers ───────────────────────────────────────────────────────
    def _pick(self, field):
        sel = cmds.ls(sl=True)
        if sel:
            field.setText(sel[0])
        else:
            self._log("[WARN] Nothing selected in Maya.")

    def _log(self, msg):
        self.log_output.append(msg)

    def _on_target_changed(self, value):
        self.mash_group.setVisible(value == "MASH")

    def _populate_table(self, data):
        self.table.setRowCount(0)
        for entry in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            cols = [
                entry["shader_attr"],
                entry["final_plug"],
                entry["file_node"] or "—",
                entry["tgt_attr"],
                entry["file_path"] or "—",
            ]
            for col, val in enumerate(cols):
                item = QtWidgets.QTableWidgetItem(val)
                # Color code: green for OK, orange for empty path
                if col == 4 and val == "—":
                    item.setForeground(QtGui.QColor("#e08040"))
                elif col == 0:
                    item.setForeground(QtGui.QColor("#7aa2c8"))
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    # ── Scan ──────────────────────────────────────────────────────────
    def _scan(self):
        src = self.src_field.text().strip()
        if not src or not cmds.objExists(src):
            QtWidgets.QMessageBox.warning(
                self, "NodeFlow", f"Node '{src}' not found in scene."
            )
            return

        target_type = self.target_combo.currentText()
        node_type   = cmds.nodeType(src)

        if node_type in SUPPORTED_SOURCES:
            shaders = [src]
        else:
            shaders = get_shader_from_mesh(src)
            if not shaders:
                QtWidgets.QMessageBox.warning(
                    self, "NodeFlow",
                    f"No supported shader found on '{src}'.\n"
                    f"Supported: {', '.join(SUPPORTED_SOURCES)}"
                )
                return

        self._texture_data = []
        for shader in shaders:
            self._texture_data += collect_texture_data(shader, target_type)

        if not self._texture_data:
            self._log(f"[WARN] No transferable textures found on '{src}' for target '{target_type}'.")
            self.transfer_btn.setEnabled(False)
            QtWidgets.QMessageBox.information(
                self, "NodeFlow",
                "No connected textures were found.\n"
                "Make sure file nodes are connected to the shader in Hypershade."
            )
            return

        self._populate_table(self._texture_data)
        self.transfer_btn.setEnabled(True)
        self._log(
            f"[SCAN] {len(self._texture_data)} connection(s) found on '{src}' "
            f"→ target: {target_type}"
        )

    # ── Transfer ──────────────────────────────────────────────────────
    def _transfer(self):
        target_type = self.target_combo.currentText()
        tgt_input   = self.tgt_field.text().strip()
        mash_waiter = self.mash_field.text().strip() if target_type == "MASH" else None

        # Resolve or create target node
        if target_type == "MASH":
            target_node = None  # MASH handles its own nodes internally
        elif tgt_input:
            if not cmds.objExists(tgt_input):
                QtWidgets.QMessageBox.warning(
                    self, "NodeFlow", f"Target node '{tgt_input}' not found in scene."
                )
                return
            target_node = tgt_input
        else:
            # Auto-create
            src_name    = self.src_field.text().strip()
            target_node = create_target_shader(target_type, src_name)
            self._log(f"[INFO] Auto-created target shader: {target_node}")

        # Validate
        warnings = validate_transfer(self._texture_data)
        if warnings:
            dlg = WarningDialog(warnings, parent=self)
            dlg.exec_()
            if not dlg.result_choice:
                self._log("[CANCELLED] Transfer cancelled by user.")
                return

        # Execute
        log_lines = do_transfer(
            self._texture_data, target_node, target_type, mash_waiter
        )
        for line in log_lines:
            self._log(line)

        ok    = sum(1 for l in log_lines if l.startswith("[OK]"))
        fails = sum(1 for l in log_lines if l.startswith("[FAIL]"))

        self._log(
            f"\n{'─'*60}\n"
            f"[DONE] ✅ {ok} transferred   ❌ {fails} failed\n"
            f"{'─'*60}\n"
        )
        QtWidgets.QMessageBox.information(
            self, "NodeFlow — Transfer Complete",
            f"Transfer complete!\n\n"
            f"✅  {ok} connection(s) transferred\n"
            f"❌  {fails} failed\n\n"
            f"Check the Log tab for full details."
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
