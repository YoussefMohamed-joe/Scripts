# -----------------------------------------------------------------------------------
# AUTHOR:     Tom Ferstl
#             t.ferstl@gmx.net
#
# INSTALL:    copy script to your maya scripts directory (i.e. C:\Users\xx\Documents\maya\2011\scripts )
#
# USAGE:      select a skinned mesh and execute the following python commands (without # and whitespace):
#             import tf_smoothSkinWeight
#             tf_smoothSkinWeight.paint()
# Edited By: Youssef Mohamed Added Undo/Redo functionality Plus you can take the code directly and run from the script Editor
# -----------------------------------------------------------------------------------

# Paste into Script Editor (Python) and run

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

# ---------------- Undo chunk guards ----------------
_undo_open = [False]

def _begin_stroke_undo():
    if not _undo_open[0]:
        mc.undoInfo(openChunk=True, chunkName='tf_smoothSkinWeight_stroke')
        _undo_open[0] = True

def _end_stroke_undo():
    if _undo_open[0]:
        mc.undoInfo(closeChunk=True)
        _undo_open[0] = False

# ---------------- Core painter ----------------
class SmoothPainter(object):
    def __init__(self):
        self.skinCluster = None
        self.skinClusterName = ""
        self.obj = None
        self.meshName = ""

        sel = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(sel)
        if sel.length() == 0:
            return

        dagPath = om.MDagPath()
        comp = om.MObject()
        sel.getDagPath(0, dagPath, comp)
        self.obj = dagPath
        self.meshName = dagPath.partialPathName()
        dagPath.extendToShape()
        node = dagPath.node()

        # Find skinCluster
        try:
            itDG = om.MItDependencyGraph(node, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
            while not itDG.isDone():
                self.skinCluster = oma.MFnSkinCluster(itDG.currentItem())
                fnDep = om.MFnDependencyNode(itDG.currentItem())
                self.skinClusterName = fnDep.name()
                break
        except:
            pass

    def setWeight(self, vtx, value):
        if not self.skinCluster:
            return
        dagPath = self.obj
        fnSkin = self.skinCluster

        # Build single-vertex component
        compFn = om.MFnSingleIndexedComponent()
        vComp = compFn.create(om.MFn.kMeshVertComponent)
        compFn.addElement(int(vtx))

        oldWeights = om.MDoubleArray()
        surrWeights = om.MDoubleArray()
        infUtil = om.MScriptUtil()
        infPtr = infUtil.asUintPtr()

        # Get connected vertices
        mit = om.MItMeshVertex(dagPath, vComp)
        surrIds = om.MIntArray()
        mit.getConnectedVertices(surrIds)
        surrCount = len(surrIds)

        surrFn = om.MFnSingleIndexedComponent()
        sComp = surrFn.create(om.MFn.kMeshVertComponent)
        surrFn.addElements(surrIds)

        # Read weights
        fnSkin.getWeights(dagPath, vComp, oldWeights, infPtr)
        fnSkin.getWeights(dagPath, sComp, surrWeights, infPtr)
        infCount = om.MScriptUtil.getUint(infPtr)

        # Get influence objects to get their names
        infDags = om.MDagPathArray()
        fnSkin.influenceObjects(infDags)

        # Compute new weights
        newWeights = []
        if surrCount > 0:
            for i in range(infCount):
                acc = 0.0
                for j in range(i, len(surrWeights), infCount):
                    acc += surrWeights[j]
                avg = acc / float(surrCount)
                nw = (avg * float(value)) + (oldWeights[i] * (1.0 - float(value)))
                newWeights.append(nw)
        else:
            for i in range(infCount):
                newWeights.append(oldWeights[i])

        # CRITICAL: Use MEL skinPercent command to apply (this DOES register undo)
        vtxName = '%s.vtx[%d]' % (self.meshName, int(vtx))
        
        # Build skinPercent command with -tv flags
        cmd = 'skinPercent'
        for i in range(infCount):
            infName = infDags[i].partialPathName()
            cmd += ' -tv "%s" %f' % (infName, newWeights[i])
        cmd += ' "%s" "%s"' % (self.skinClusterName, vtxName)
        
        # Execute via MEL (registers undo inside the open chunk)
        mm.eval(cmd)

# Global painter
_painter = [None]

def _apply_smooth_weight(index, val):
    if _painter[0] is None:
        _painter[0] = SmoothPainter()
    if _painter[0]:
        _painter[0].setWeight(int(index), float(val))

# ---------------- MEL integration ----------------
def _install_ctx_callbacks():
    mel = r'''
global proc tf_smoothBrush(string $context)
{
    artUserPaintCtx -e
        -ic  "tf_smooth_init"
        -fc  "tf_smooth_finish"
        -svc "tf_smooth_setValue"
        $context;
}

global proc tf_smooth_init(string $name)
{
    python("import __main__; __main__._begin_stroke_undo()");
    python("import __main__; __main__._painter[0] = __main__.SmoothPainter()");
}

global proc tf_smooth_finish(string $name)
{
    python("import __main__; __main__._end_stroke_undo()");
}

global proc tf_smooth_setValue(int $slot, int $index, float $val)
{
    python("import __main__; __main__._apply_smooth_weight(" + $index + ", " + $val + ")");
}
'''
    mm.eval(mel)

def activate():
    _install_ctx_callbacks()
    mm.eval('ScriptPaintTool;')
    mm.eval('artUserPaintCtx -e -tsc "tf_smoothBrush" `currentCtx`;')
    mc.inViewMessage(amg='Smooth Skin Weights: Undo/Redo enabled', pos='topCenter', fade=True)

# Run
activate()
