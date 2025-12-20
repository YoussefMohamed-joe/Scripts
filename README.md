# Scripts Repository

A collection of professional 3D animation and rigging tools for **Autodesk Maya** and **SideFX Houdini**. This repository contains production-ready scripts designed to enhance workflow efficiency and solve common animation challenges.

---

## 📁 Repository Structure

```
Scripts/
├── Maya/
│   ├── CurveMorph Pro.py                    # Advanced path animation system
│   └── tf_smoothSkinWeight_Enhanced-Youssef Mohamed.py  # Skin weight smoothing tool
└── Houdini/
    └── pickefy.py                           # (Placeholder/In development)
```

---

## 🎬 Maya Scripts

### 1. CurveMorph Pro

**Version:** 6.0  
**Author:** Youssef El-Qadi  
**Enhanced by:** Animation Tools Studio

A comprehensive path animation toolkit for Maya that eliminates foot sliding issues in character animation. This tool provides a complete solution for creating, editing, and managing motion paths with advanced features for professional animation workflows.

#### 🚀 Key Features

##### **Create Tab**
- **Extract Motion Path**: Convert object animation trajectories into editable NURBS curves
  - Configurable sample rate (frames)
  - Option to flatten to ground plane (Y=0)
  - Straight line extraction mode
- **Attach to Path**: Constrain objects to follow curve paths
  - Preserve position offset
  - Align to curve direction
- **Curve Snapshot System**: Save and restore curve states for non-destructive editing
- **CV Control Rig**: Generate locator controls for each curve CV point
  - Select all controls
  - Reparent controls
  - Remove controls
- **Height Offset Control**: Add vertical position control to path-animated objects
  - World space mode
  - Follow path mode

##### **Utilities Tab**
- **Curve Editing Tools**:
  - Display curve length and information
  - Lock/unlock curve length
  - Rebuild curves with custom spans
  - Straighten curves
  - Smooth curves
  - Duplicate curves
  - Reverse curve direction
  - Mirror curves (X/Z axis)
- **Animation & Keyframes**:
  - Bake animation to world space
  - Delete constraints
  - Delete animation
  - Tangent presets (Linear, Smooth, Stepped)
- **Path Timing & Offset**:
  - Position offset controls
  - Speed multiplier
  - Reverse path direction
- **Locators & Transforms**:
  - Create locators at selection or origin
  - Match transforms between objects
  - Create constraints (Parent, Point, Orient)
  - Measure distances
- **Quick Selection Tools**:
  - Select hierarchy
  - Select curve CVs
  - Select all constraints
  - Select motion paths

##### **Advanced Tab**
- **Curve Morphing**: Transform one curve shape to match another
  - Basic morph (A → B)
  - Morph with length preservation
- **Curve Sliding**: Slide curves along target path curves
  - Forward/backward sliding
  - Configurable slide amount
- **Master Follow Setup**: Create master control for multiple objects
  - Set master control
  - Add follower objects
  - Create/remove follow system
- **Backup & Recovery System**:
  - Create automatic backups
  - Restore from backups
  - Clear backup data
- **Advanced Locator Tools**: Enhanced locator management
- **Animation Presets Library**: Save, apply, and manage animation presets

##### **System Tab**
- **System Management**:
  - Finalize animation (bake before cleanup)
  - Selective cleanup tools
  - Remove CV controls
  - Remove height controls
  - Remove curve snapshots
  - Remove all constraints
- **Danger Zone**: Destructive operations
  - Delete entire CurveMorph system
  - Clean all CMP nodes from scene

##### **Settings Tab**
- **Multi-language Support**: English and Arabic (العربية)
- **Appearance Themes**: Dark mode and Light mode
- **Contact Information**: Developer contact details
- **Credits**: Version and author information

#### 📖 Usage

**Basic Usage:**
```python
import curvemorph_pro
curvemorph_pro.show_ui()
```

**Extract Path from Animation:**
1. Select an animated object
2. Open CurveMorph Pro UI
3. Go to "Create" tab
4. Set sample rate and options
5. Click "Extract Path from Animation"

**Attach Object to Path:**
1. Select object and target curve
2. Click "Get" to load curve name
3. Configure offset and alignment options
4. Click "Attach Selected to Path"

**Curve Morphing:**
1. Select base curve first, then target curve
2. Go to "Advanced" tab
3. Choose morph type (Basic or Preserve Length)
4. Execute morph operation

#### 🔧 Technical Details

- **Dependencies**: Maya (Python 2.7/3.x), OpenMaya API 2.0 (optional, for performance)
- **Node Prefix**: `CMP_` (all created nodes use this prefix)
- **Window Name**: `curvemorph_pro_window`
- **API**: Uses Maya commands (`maya.cmds`) and MEL integration
- **Performance**: Optimized with OpenMaya API 2.0 when available

#### 📞 Contact

- **LinkedIn**: [Youssef El-Qadi](https://www.linkedin.com/in/youssef-el-qadi-6a78a4247)
- **Phone**: 01118105724

---

### 2. Smooth Skin Weight Tool (Enhanced)

**Original Author:** Tom Ferstl  
**Enhanced by:** Youssef Mohamed

A professional skin weight smoothing tool for Maya with enhanced undo/redo functionality. This tool allows artists to paint smooth skin weights directly on meshes using Maya's Artisan brush system.

#### 🎯 Features

- **Interactive Weight Painting**: Paint smooth skin weights using Maya's brush interface
- **Undo/Redo Support**: Full undo/redo functionality for each brush stroke
- **Automatic Skin Cluster Detection**: Automatically finds and uses the skin cluster on selected mesh
- **Smooth Blending**: Blends weights with surrounding vertices for natural transitions
- **Direct Script Editor Execution**: Can be run directly from Maya's script editor

#### 📖 Usage

**Method 1: Direct Execution**
1. Copy the entire script into Maya's Script Editor (Python tab)
2. Select a skinned mesh
3. Run the script
4. The smooth brush tool will activate automatically

**Method 2: Import as Module**
```python
# Save script to: C:\Users\YourName\Documents\maya\2024\scripts\tf_smoothSkinWeight.py
import tf_smoothSkinWeight
tf_smoothSkinWeight.paint()
```

**How It Works:**
1. Select a mesh with a skin cluster
2. The script automatically detects the skin cluster
3. Activates Maya's Artisan paint tool
4. Paint on the mesh to smooth skin weights
5. Each stroke is wrapped in an undo chunk for easy reversion

#### 🔧 Technical Details

- **Dependencies**: Maya (maya.cmds, maya.mel, maya.OpenMaya, maya.OpenMayaAnim)
- **Brush System**: Uses Maya's `artUserPaintCtx` for painting
- **Undo System**: Implements undo chunks using `maya.cmds.undoInfo()`
- **Weight Calculation**: Averages weights from surrounding vertices
- **Performance**: Uses OpenMaya API for efficient weight operations

#### 💡 Key Enhancements

- **Undo/Redo Functionality**: Each brush stroke is properly wrapped in an undo chunk
- **Script Editor Compatible**: Can be pasted directly into script editor without file installation
- **Improved Error Handling**: Better detection and handling of skin clusters
- **User Feedback**: In-view messages to confirm tool activation

---

## 🎨 Houdini Scripts

### pickefy.py

**Status:** In development / Placeholder

This file is currently empty or under development. Check back for updates.

---

## 📋 Requirements

### Maya Scripts
- **Autodesk Maya** 2011 or later (tested up to 2024+)
- **Python** 2.7 or 3.x (depending on Maya version)
- **OpenMaya API** (optional, for performance improvements)

### Houdini Scripts
- **SideFX Houdini** (version TBD)

---

## 🚀 Installation

### Maya Scripts

#### Option 1: Scripts Directory (Recommended)
1. Copy the script files to your Maya scripts directory:
   - **Windows**: `C:\Users\YourName\Documents\maya\2024\scripts\`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/2024/scripts/`
   - **Linux**: `~/maya/2024/scripts/`

2. Restart Maya or run:
   ```python
   import maya.cmds as cmds
   cmds.rehash()
   ```

#### Option 2: Custom Scripts Path
1. Add your custom scripts folder to Maya's script path:
   ```python
   import sys
   sys.path.append('D:/project/Scripts/Maya')
   ```

2. Import and use:
   ```python
   import curvemorph_pro
   curvemorph_pro.show_ui()
   ```

### Houdini Scripts
1. Copy scripts to your Houdini scripts directory
2. Follow Houdini's script installation guidelines

---

## 📝 Usage Examples

### CurveMorph Pro - Complete Workflow

```python
# 1. Launch the UI
import curvemorph_pro
curvemorph_pro.show_ui()

# 2. Extract path from animated character
# - Select animated character
# - Set sample rate to 5 frames
# - Click "Extract Path from Animation"

# 3. Edit the curve using CV controls
# - Generate CV controls
# - Move locators to adjust path

# 4. Morph curve to match another path
# - Select base curve, then target curve
# - Use "Morph A → B" in Advanced tab

# 5. Bake animation
# - Use "Bake Animation" in Utilities tab
# - Finalize and clean up system
```

### Smooth Skin Weight Tool

```python
# Direct execution method
# 1. Select skinned mesh
# 2. Paste entire script in Script Editor
# 3. Run script
# 4. Paint on mesh to smooth weights
# 5. Use Ctrl+Z to undo strokes
```

---

## 🛠️ Development

### Contributing

Contributions are welcome! Please follow these guidelines:

1. Maintain code style consistency
2. Add comments for complex operations
3. Test scripts in multiple Maya versions
4. Update documentation for new features

### Code Structure

- **CurveMorph Pro**: Modular design with separate functions for each feature
- **Smooth Skin Weight**: Class-based design with global painter instance
- All scripts use Maya's standard naming conventions

---

## 📄 License

Please check individual script headers for license information. Most scripts include author credits and usage terms.

---

## 🙏 Credits

- **CurveMorph Pro**: Youssef El-Qadi & Animation Tools Studio
- **Smooth Skin Weight Tool**: Tom Ferstl (original), Youssef Mohamed (enhancements)

---

## 📞 Support

For issues, questions, or feature requests:
- **CurveMorph Pro**: Contact Youssef El-Qadi via LinkedIn
- **General**: Open an issue in this repository

---

## 🔄 Version History

### CurveMorph Pro
- **v6.0**: Current version with advanced features
  - Curve morphing
  - Master follow system
  - Backup & recovery
  - Animation presets library
  - Multi-language support

### Smooth Skin Weight Tool
- **Enhanced Version**: Added undo/redo functionality
- **Original Version**: Basic smooth weight painting

---

## ⚠️ Notes

- Always save your work before using destructive operations
- Test scripts on non-critical scenes first
- Some features may require specific Maya versions
- Backup your scenes when using system cleanup tools

---

**Last Updated**: 2024
