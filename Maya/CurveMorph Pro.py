"""
CurveMorph Pro - Advanced Path Animation System
Version: 6.0
Author: Youssef El-Qadi
Enhanced by: Animation Tools Studio

Complete path animation toolkit for Maya with:
- Create curves from animation paths
- Apply objects to follow curves
- Reflection system (save/restore curve states)
- CV control system with locators
- Vertical incline controls
- Speed and offset controls
- Animation baking and blending
- Curve utilities and measurements
- Curve Morphing (A→B transformation)
- Curve Sliding along target paths
- Master Follow with animation layers
- Smart Constraints with lock detection
- Backup System with auto-recovery
- Advanced Locator Tools
- Animation Presets Library (save/apply/manage)

Usage:
    import curvemorph_pro
    curvemorph_pro.show_ui()
"""

import maya.cmds as cmds
import maya.mel as mel
import math
import webbrowser
import json

# Optional OpenMaya API 2.0 for performance
try:
    import maya.api.OpenMaya as om2
    import maya.api.OpenMayaAnim as oma2
    HAS_OM2 = True
except ImportError:
    HAS_OM2 = False

# Tool constants
TOOL_NAME = "CurveMorph Pro"
TOOL_VERSION = "6.0"
AUTHOR = "Youssef El-Qadi"
WINDOW_NAME = "curvemorph_pro_window"
PREFIX = "CMP_"

# Contact Info
LINKEDIN_URL = "https://www.linkedin.com/in/youssef-el-qadi-6a78a4247"
PHONE_NUMBER = "01118105724"

# ============================================================================
# LANGUAGE & SETTINGS SYSTEM
# ============================================================================

# Language dictionaries
LANG_EN = {
    "tool_title": "CURVEMORPH PRO",
    "tool_subtitle": "Path Animation Without Foot Sliding",
    
    # Tab names
    "tab_create": " Create ",
    "tab_utilities": " Utilities ",
    "tab_system": " System ",
    "tab_settings": " Settings ",
    
    # Create tab
    "extract_path": "Extract Motion Path",
    "extract_desc": "Create a curve from object's animation trajectory",
    "sample_rate": "Sample Rate:",
    "frames": "frames",
    "flatten_ground": "Flatten to Ground (Y=0)",
    "straight_only": "Straight Line Only",
    "extract_btn": "Extract Path from Animation",
    
    "attach_path": "Attach to Path",
    "attach_desc": "Constrain object to follow a curve path",
    "target_curve": "Target curve name...",
    "get_btn": " Get ",
    "preserve_offset": "Preserve Position Offset",
    "align_direction": "Align to Curve Direction",
    "attach_btn": "Attach Selected to Path",
    
    "curve_snapshot": "Curve Snapshot (Save/Restore)",
    "snapshot_desc": "Save curve shape to restore after editing",
    "save_snapshot": "Save Snapshot",
    "restore_snapshot": "Restore Snapshot",
    
    "cv_control_rig": "CV Control Rig",
    "cv_desc": "Create locator controls for each curve CV",
    "generate_cv": "Generate CV Controls",
    "select_all": "Select All",
    "reparent": "Reparent",
    "remove": "Remove",
    
    "height_control": "Height Offset Control",
    "height_desc": "Add vertical position control to path-animated objects",
    "world_space": "World Space",
    "follow_path": "Follow Path",
    "remove_height": "Remove Height Controls",
    
    # Utilities tab
    "curve_editing": "Curve Editing",
    "curve_length": "Curve Length",
    "curve_info": "Curve Info",
    "lock_length": "Lock Length",
    "unlock_length": "Unlock Length",
    "rebuild_curve": "Rebuild Curve",
    "spans": "Spans:",
    "straighten": "Straighten",
    "smooth": "Smooth",
    "duplicate": "Duplicate",
    "reverse_dir": "Reverse Direction",
    "mirror_x": "Mirror X",
    "mirror_z": "Mirror Z",
    
    "animation_keys": "Animation & Keyframes",
    "bake_anim": "Bake Animation",
    "bake_world": "Bake to World",
    "delete_constraints": "Delete Constraints",
    "delete_animation": "Delete Animation",
    "tangent_presets": "Tangent Presets:",
    "linear": "Linear",
    "smooth_key": "Smooth",
    "stepped": "Stepped",
    
    "path_timing": "Path Timing & Offset",
    "position_offset": "Position Offset:",
    "apply_offset": "Apply Offset",
    "speed_mult": "Speed Multiplier:",
    "apply_speed": "Apply Speed",
    "reverse_path": "Reverse Path Direction",
    
    "locators_transforms": "Locators & Transforms",
    "loc_selection": "Locator at Selection",
    "loc_origin": "Locator at Origin",
    "match_transforms": "Match Transforms",
    "constraints_label": "Constraints:",
    "parent": "Parent",
    "point": "Point",
    "orient": "Orient",
    "measure_dist": "Measure Distance",
    
    "quick_select": "Quick Selection",
    "hierarchy": "Hierarchy",
    "curve_cvs": "Curve CVs",
    "all_constraints": "All Constraints",
    "motion_paths": "Motion Paths",
    
    # System tab
    "system_mgmt": "System Management",
    "finalize": "Finalize Animation",
    "finalize_warn": "Bake animation before removing the system!",
    "bake_selected": "Bake Selected Animation",
    
    "selective_cleanup": "Selective Cleanup",
    "remove_cv": "Remove CV Controls",
    "remove_height_ctrl": "Remove Height Controls",
    "remove_snapshot": "Remove Curve Snapshot",
    "remove_all_const": "Remove All Constraints",
    
    "danger_zone": "Danger Zone",
    "danger_warn": "These actions are destructive and cannot be undone!",
    "delete_system": "Delete Entire CurveMorph System",
    "clean_all": "Clean All CMP Nodes from Scene",
    
    "about": "About",
    "about_desc1": "Path animation toolkit for Maya",
    "about_desc2": "Bend motion paths without foot sliding",
    
    # Settings tab
    "language": "Language",
    "select_lang": "Select your preferred language:",
    "english": "English",
    "arabic": "Arabic (العربية)",
    "lang_restart": "Click to apply language instantly",
    
    "appearance": "Appearance",
    "theme_desc": "Choose your preferred color theme:",
    "dark_mode": "Dark Mode",
    "light_mode": "Light Mode",
    "theme_restart": "Click to apply theme instantly",
    
    "contact": "Contact Developer",
    "contact_desc": "Get in touch for support, feedback or collaboration:",
    "linkedin": "Open LinkedIn Profile",
    "phone_label": "Phone:",
    "copy_phone": "Copy Number",
    
    "credits": "Credits",
    "developed_by": "Developed by",
    "version": "Version",
    
    # New Advanced Features
    "tab_advanced": " Advanced ",
    
    "curve_morphing": "Curve Morphing",
    "morph_desc": "Transform one curve shape to match another",
    "morph_basic": "Morph A → B",
    "morph_preserve": "Morph (Keep Length)",
    "select_two_curves": "Select base curve, then target curve",
    
    "curve_sliding": "Curve Sliding",
    "slide_desc": "Slide curve along a target path curve",
    "slide_forward": "Slide Forward",
    "slide_backward": "Slide Backward",
    "slide_amount": "Slide Amount:",
    
    "master_follow": "Master Follow Setup",
    "master_desc": "Create master control for multiple objects",
    "set_master": "Set Master Control",
    "add_followers": "Add Follower Objects",
    "create_follow": "Create Follow System",
    "remove_follow": "Remove Follow System",
    
    "backup_system": "Backup & Recovery",
    "backup_desc": "Create automatic backup for animation recovery",
    "create_backup": "Create Backup",
    "restore_backup": "Restore from Backup",
    "clear_backup": "Clear Backups",
    
    "locator_tools": "Locator Tools",
    "loc_bigger": "Bigger",
    "loc_smaller": "Smaller",
    "loc_color": "Cycle Color",
    "loc_scale": "Scale:",
    
    "smart_constraints": "Smart Constraints",
    "smart_parent": "Smart Parent",
    "smart_point": "Smart Point",
    "smart_orient": "Smart Orient",
    "smart_desc": "Auto-skip locked attributes",
    
    "cv_advanced": "Advanced CV Controls",
    "cv_count": "CV Count:",
    "add_cvs": "Add CVs",
    "cv_to_curve": "Apply to Curve",
    
    # Animation Presets Tab
    "tab_presets": " Presets ",
    "anim_presets": "Animation Presets Library",
    "presets_desc": "Save and apply animation presets to characters",
    
    "save_preset": "Save Animation Preset",
    "preset_name": "Preset Name:",
    "preset_name_hint": "e.g. walk_cycle, run_fast...",
    "source_range": "Source Frame Range:",
    "to_label": "to",
    "save_from_sel": "Save from Selected",
    "preset_saved": "Preset saved successfully!",
    
    "apply_preset": "Apply Animation Preset",
    "select_preset": "Select Preset:",
    "no_presets": "No presets saved yet",
    "target_range": "Apply to Frame Range:",
    "blend_mode": "Blend Mode:",
    "blend_replace": "Replace",
    "blend_add": "Additive",
    "blend_multiply": "Multiply",
    "apply_to_sel": "Apply to Selected",
    "preset_applied": "Preset applied successfully!",
    
    "manage_presets": "Manage Presets",
    "refresh_list": "Refresh List",
    "delete_preset": "Delete Selected",
    "export_presets": "Export All",
    "import_presets": "Import",
    "preset_info": "Preset Info",
    "frames_label": "Frames:",
    "objects_label": "Objects:",
    "created_label": "Created:",
    
    "preset_preview": "Preview",
    # Attach to Surface
    "attach_surface": "Project to Surface",
    "surface_desc": "Snap curve CV controls onto a surface/primitive shape",
    "select_surface": "Select curve (with CV controls) first, then surface last",
    "attach_to_surface": "Project to Surface",
    "detach_surface": "Reset CVs",
    
    "validation_errors": "Validation",
    "no_selection": "Please select objects first!",
    "invalid_range": "Invalid frame range!",
    "preset_exists": "Preset name already exists. Overwrite?",
    "preset_not_found": "Preset not found!",
    "incompatible": "Preset incompatible with selection!",
}

LANG_AR = {
    "tool_title": "كيرف مورف برو",
    "tool_subtitle": "تحريك المسار بدون انزلاق القدم",
    
    # Tab names
    "tab_create": " إنشاء ",
    "tab_utilities": " أدوات ",
    "tab_system": " النظام ",
    "tab_settings": " الإعدادات ",
    
    # Create tab
    "extract_path": "استخراج مسار الحركة",
    "extract_desc": "إنشاء منحنى من مسار حركة الكائن",
    "sample_rate": "معدل العينات:",
    "frames": "إطار",
    "flatten_ground": "تسطيح على الأرض (Y=0)",
    "straight_only": "خط مستقيم فقط",
    "extract_btn": "استخراج المسار من الحركة",
    
    "attach_path": "ربط بالمسار",
    "attach_desc": "تقييد الكائن لاتباع مسار المنحنى",
    "target_curve": "اسم المنحنى المستهدف...",
    "get_btn": " جلب ",
    "preserve_offset": "الحفاظ على الإزاحة",
    "align_direction": "محاذاة مع اتجاه المنحنى",
    "attach_btn": "ربط المحدد بالمسار",
    
    "curve_snapshot": "لقطة المنحنى (حفظ/استعادة)",
    "snapshot_desc": "حفظ شكل المنحنى للاستعادة لاحقاً",
    "save_snapshot": "حفظ اللقطة",
    "restore_snapshot": "استعادة اللقطة",
    
    "cv_control_rig": "أدوات تحكم CV",
    "cv_desc": "إنشاء محددات تحكم لكل نقطة CV",
    "generate_cv": "إنشاء أدوات تحكم CV",
    "select_all": "تحديد الكل",
    "reparent": "إعادة التبعية",
    "remove": "إزالة",
    
    "height_control": "تحكم الارتفاع",
    "height_desc": "إضافة تحكم بالموضع العمودي للكائنات",
    "world_space": "المساحة العالمية",
    "follow_path": "اتباع المسار",
    "remove_height": "إزالة تحكم الارتفاع",
    
    # Utilities tab
    "curve_editing": "تحرير المنحنى",
    "curve_length": "طول المنحنى",
    "curve_info": "معلومات المنحنى",
    "lock_length": "قفل الطول",
    "unlock_length": "فتح الطول",
    "rebuild_curve": "إعادة بناء المنحنى",
    "spans": "المقاطع:",
    "straighten": "استقامة",
    "smooth": "تنعيم",
    "duplicate": "نسخ",
    "reverse_dir": "عكس الاتجاه",
    "mirror_x": "انعكاس X",
    "mirror_z": "انعكاس Z",
    
    "animation_keys": "الحركة والإطارات المفتاحية",
    "bake_anim": "خبز الحركة",
    "bake_world": "خبز للعالم",
    "delete_constraints": "حذف القيود",
    "delete_animation": "حذف الحركة",
    "tangent_presets": "إعدادات الظل:",
    "linear": "خطي",
    "smooth_key": "ناعم",
    "stepped": "متدرج",
    
    "path_timing": "توقيت وإزاحة المسار",
    "position_offset": "إزاحة الموضع:",
    "apply_offset": "تطبيق الإزاحة",
    "speed_mult": "مضاعف السرعة:",
    "apply_speed": "تطبيق السرعة",
    "reverse_path": "عكس اتجاه المسار",
    
    "locators_transforms": "المحددات والتحويلات",
    "loc_selection": "محدد عند التحديد",
    "loc_origin": "محدد عند الأصل",
    "match_transforms": "مطابقة التحويلات",
    "constraints_label": "القيود:",
    "parent": "أب",
    "point": "نقطة",
    "orient": "توجيه",
    "measure_dist": "قياس المسافة",
    
    "quick_select": "التحديد السريع",
    "hierarchy": "التسلسل",
    "curve_cvs": "نقاط CV",
    "all_constraints": "كل القيود",
    "motion_paths": "مسارات الحركة",
    
    # System tab
    "system_mgmt": "إدارة النظام",
    "finalize": "إنهاء الحركة",
    "finalize_warn": "اخبز الحركة قبل إزالة النظام!",
    "bake_selected": "خبز الحركة المحددة",
    
    "selective_cleanup": "تنظيف انتقائي",
    "remove_cv": "إزالة تحكم CV",
    "remove_height_ctrl": "إزالة تحكم الارتفاع",
    "remove_snapshot": "إزالة لقطة المنحنى",
    "remove_all_const": "إزالة كل القيود",
    
    "danger_zone": "منطقة الخطر",
    "danger_warn": "هذه الإجراءات مدمرة ولا يمكن التراجع عنها!",
    "delete_system": "حذف نظام CurveMorph بالكامل",
    "clean_all": "تنظيف كل عقد CMP من المشهد",
    
    "about": "حول",
    "about_desc1": "مجموعة أدوات تحريك المسار لمايا",
    "about_desc2": "ثني مسارات الحركة بدون انزلاق القدم",
    
    # Settings tab
    "language": "اللغة",
    "select_lang": "اختر لغتك المفضلة:",
    "english": "الإنجليزية (English)",
    "arabic": "العربية",
    "lang_restart": "انقر لتطبيق اللغة فوراً",
    
    "appearance": "المظهر",
    "theme_desc": "اختر سمة الألوان المفضلة:",
    "dark_mode": "الوضع الداكن",
    "light_mode": "الوضع الفاتح",
    "theme_restart": "انقر لتطبيق المظهر فوراً",
    
    "contact": "تواصل مع المطور",
    "contact_desc": "تواصل للدعم أو الملاحظات أو التعاون:",
    "linkedin": "فتح صفحة LinkedIn",
    "phone_label": "الهاتف:",
    "copy_phone": "نسخ الرقم",
    
    "credits": "الاعتمادات",
    "developed_by": "تطوير",
    "version": "الإصدار",
    
    # New Advanced Features
    "tab_advanced": " متقدم ",
    
    "curve_morphing": "تحويل المنحنى",
    "morph_desc": "تحويل شكل منحنى ليطابق آخر",
    "morph_basic": "تحويل A → B",
    "morph_preserve": "تحويل (حفظ الطول)",
    "select_two_curves": "اختر المنحنى الأساسي ثم المستهدف",
    
    "curve_sliding": "انزلاق المنحنى",
    "slide_desc": "تحريك المنحنى على مسار آخر",
    "slide_forward": "انزلاق للأمام",
    "slide_backward": "انزلاق للخلف",
    "slide_amount": "مقدار الانزلاق:",
    
    "master_follow": "نظام التتبع الرئيسي",
    "master_desc": "إنشاء تحكم رئيسي لعدة كائنات",
    "set_master": "تعيين التحكم الرئيسي",
    "add_followers": "إضافة كائنات تابعة",
    "create_follow": "إنشاء نظام التتبع",
    "remove_follow": "إزالة نظام التتبع",
    
    "backup_system": "النسخ الاحتياطي والاستعادة",
    "backup_desc": "إنشاء نسخة احتياطية لاستعادة الحركة",
    "create_backup": "إنشاء نسخة احتياطية",
    "restore_backup": "استعادة من النسخة",
    "clear_backup": "مسح النسخ الاحتياطية",
    
    "locator_tools": "أدوات المحددات",
    "loc_bigger": "أكبر",
    "loc_smaller": "أصغر",
    "loc_color": "تغيير اللون",
    "loc_scale": "الحجم:",
    
    "smart_constraints": "قيود ذكية",
    "smart_parent": "أب ذكي",
    "smart_point": "نقطة ذكية",
    "smart_orient": "توجيه ذكي",
    "smart_desc": "تخطي السمات المقفلة تلقائياً",
    
    "cv_advanced": "تحكم CV متقدم",
    "cv_count": "عدد CV:",
    "add_cvs": "إضافة CVs",
    "cv_to_curve": "تطبيق على المنحنى",
    
    # Animation Presets Tab
    "tab_presets": " الإعدادات المسبقة ",
    "anim_presets": "مكتبة الحركات المسبقة",
    "presets_desc": "حفظ وتطبيق الحركات على الشخصيات",
    
    "save_preset": "حفظ حركة مسبقة",
    "preset_name": "اسم الإعداد:",
    "preset_name_hint": "مثال: مشي، جري سريع...",
    "source_range": "نطاق الإطارات المصدر:",
    "to_label": "إلى",
    "save_from_sel": "حفظ من المحدد",
    "preset_saved": "تم حفظ الإعداد بنجاح!",
    
    "apply_preset": "تطبيق حركة مسبقة",
    "select_preset": "اختر الإعداد:",
    "no_presets": "لا توجد إعدادات محفوظة",
    "target_range": "تطبيق على نطاق الإطارات:",
    "blend_mode": "وضع المزج:",
    "blend_replace": "استبدال",
    "blend_add": "إضافي",
    "blend_multiply": "ضرب",
    "apply_to_sel": "تطبيق على المحدد",
    "preset_applied": "تم تطبيق الإعداد بنجاح!",
    
    "manage_presets": "إدارة الإعدادات",
    "refresh_list": "تحديث القائمة",
    "delete_preset": "حذف المحدد",
    "export_presets": "تصدير الكل",
    "import_presets": "استيراد",
    "preset_info": "معلومات الإعداد",
    "frames_label": "الإطارات:",
    "objects_label": "الكائنات:",
    "created_label": "تاريخ الإنشاء:",
    
    "preset_preview": "معاينة",
    # Attach to Surface
    "attach_surface": "إسقاط على السطح",
    "surface_desc": "لصق نقاط تحكم المنحنى على شكل السطح",
    "select_surface": "حدد المنحنى (مع نقاط التحكم) أولاً ثم السطح أخيراً",
    "attach_to_surface": "إسقاط على السطح",
    "detach_surface": "إعادة تعيين النقاط",
    
    "validation_errors": "التحقق",
    "no_selection": "الرجاء تحديد كائنات أولاً!",
    "invalid_range": "نطاق إطارات غير صالح!",
    "preset_exists": "اسم الإعداد موجود. هل تريد الاستبدال؟",
    "preset_not_found": "الإعداد غير موجود!",
    "incompatible": "الإعداد غير متوافق مع التحديد!",
}


def get_setting(key, default=None):
    """Get a setting from Maya's optionVar"""
    var_name = PREFIX + key
    if cmds.optionVar(exists=var_name):
        return cmds.optionVar(query=var_name)
    return default


def set_setting(key, value):
    """Set a setting in Maya's optionVar"""
    var_name = PREFIX + key
    if isinstance(value, int):
        cmds.optionVar(intValue=(var_name, value))
    elif isinstance(value, float):
        cmds.optionVar(floatValue=(var_name, value))
    else:
        cmds.optionVar(stringValue=(var_name, str(value)))


def get_language():
    """Get current language setting"""
    return get_setting("language", "en")


def set_language(lang):
    """Set language and refresh UI"""
    set_setting("language", lang)
    cmds.inViewMessage(msg="Language: {}".format(
        "English" if lang == "en" else "العربية"), pos="midCenter", fade=True)


def get_theme():
    """Get current theme (dark/light)"""
    return get_setting("theme", "dark")


def set_theme(theme):
    """Set theme and refresh UI"""
    set_setting("theme", theme)
    cmds.inViewMessage(msg="Theme: {}".format(
        "Dark Mode" if theme == "dark" else "Light Mode"), pos="midCenter", fade=True)


def get_text(key):
    """Get localized text"""
    lang = get_language()
    lang_dict = LANG_AR if lang == "ar" else LANG_EN
    return lang_dict.get(key, LANG_EN.get(key, key))


def open_linkedin():
    """Open LinkedIn profile in browser"""
    try:
        webbrowser.open(LINKEDIN_URL)
        cmds.inViewMessage(msg="Opening LinkedIn...", pos="midCenter", fade=True)
    except:
        cmds.warning("Could not open browser. Visit: " + LINKEDIN_URL)


def copy_phone():
    """Copy phone number to clipboard"""
    try:
        # Use Maya's internal clipboard
        cmds.textField("cmp_phone_field", edit=True, text=PHONE_NUMBER)
        cmds.textField("cmp_phone_field", edit=True, selectCommand=lambda: None)
        mel.eval('copyTextToClipboard("{}")'.format(PHONE_NUMBER))
        cmds.inViewMessage(msg="Phone number copied!", pos="midCenter", fade=True)
    except:
        cmds.inViewMessage(msg="Phone: " + PHONE_NUMBER, pos="midCenter", fade=True)


# ============================================================================
# UI FUNCTIONS
# ============================================================================

def show_ui():
    """Main function to show the UI"""
    # Clean up any existing callbacks
    remove_preset_selection_callback()
    
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)
    
    # Get current theme
    theme = get_theme()
    is_dark = theme == "dark"
    
    def on_window_close():
        """Cleanup when window is closed"""
        remove_preset_selection_callback()
    
    window = cmds.window(
        WINDOW_NAME,
        title="{} v{}".format(TOOL_NAME, TOOL_VERSION),
        width=420,
        height=820,
        sizeable=True,
        closeCommand=on_window_close
    )
    
    # ===== THEME-AWARE COLOR PALETTE =====
    if is_dark:
        # Dark theme colors - Rich dark aesthetic
        primary = [0.18, 0.56, 0.82]      # Ocean blue
        secondary = [0.93, 0.46, 0.14]    # Warm orange  
        success = [0.22, 0.72, 0.52]      # Emerald green
        warning = [0.96, 0.76, 0.18]      # Golden yellow
        danger = [0.89, 0.28, 0.35]       # Coral red
        accent = [0.62, 0.42, 0.84]       # Violet purple
        teal = [0.18, 0.68, 0.68]         # Teal
        slate = [0.32, 0.34, 0.38]        # Slate gray
        
        # Background colors
        bg_main = [0.20, 0.21, 0.24]      # Main background
        bg_frame = [0.24, 0.25, 0.28]     # Frame background
        bg_header = [0.14, 0.15, 0.17]    # Header background
        bg_section = [0.18, 0.19, 0.22]   # Section background
        header_bg = [0.12, 0.13, 0.15]    # Title header
        dark = [0.16, 0.17, 0.20]         # Dark accent
    else:
        # Light theme colors - Professional light aesthetic
        # Rich, saturated button colors that pop on light backgrounds
        primary = [0.15, 0.45, 0.72]      # Deep blue
        secondary = [0.85, 0.45, 0.12]    # Deep orange  
        success = [0.15, 0.55, 0.38]      # Forest green
        warning = [0.88, 0.68, 0.08]      # Deep gold
        danger = [0.82, 0.25, 0.30]       # Deep red
        accent = [0.52, 0.32, 0.72]       # Deep purple
        teal = [0.12, 0.52, 0.52]         # Deep teal
        slate = [0.32, 0.36, 0.42]        # Dark slate for contrast
        
        # Background colors - Medium-light grays for Maya text compatibility
        # These provide good contrast with Maya's default light text
        bg_main = [0.52, 0.53, 0.55]      # Medium gray - readable text
        bg_frame = [0.56, 0.57, 0.59]     # Slightly lighter frames
        bg_header = [0.42, 0.44, 0.48]    # Darker headers
        bg_section = [0.54, 0.55, 0.57]   # Section background
        header_bg = [0.38, 0.40, 0.45]    # Title header - darker
        dark = [0.48, 0.50, 0.52]         # Dark accent areas
    
    # Main form layout with background
    form = cmds.formLayout(backgroundColor=bg_main)
    
    # Create tabs with modern styling
    main_layout = cmds.tabLayout(parent=form, innerMarginWidth=5, innerMarginHeight=5, 
                                  backgroundColor=bg_main)
    
    # ==================== TAB 1: CREATE & SETUP ====================
    tab1 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col1 = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    # Modern Header
    cmds.separator(height=8, style="none")
    cmds.text(label="   " + get_text("tool_title"), font="boldLabelFont", height=36, 
              backgroundColor=header_bg, align="left")
    cmds.text(label="   " + get_text("tool_subtitle"), height=22,
              backgroundColor=bg_header, align="left", font="smallPlainLabelFont")
    cmds.separator(height=12, style="none")
    
    # ===== EXTRACT PATH =====
    cmds.frameLayout(label="  " + get_text("extract_path"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("extract_desc"), align="left", 
              font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=2, columnWidth4=[85, 50, 50, 100])
    cmds.text(label=get_text("sample_rate"), align="right")
    cmds.intField("sample_frames", value=5, minValue=1, width=45)
    cmds.text(label=get_text("frames"))
    cmds.text(label="")
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.checkBox("zero_vertical", label=get_text("flatten_ground"), value=True)
    cmds.checkBox("start_end_only", label=get_text("straight_only"), value=False)
    
    cmds.separator(height=8, style="none")
    cmds.button(label=get_text("extract_btn"), height=38, backgroundColor=primary, 
                command=lambda x: create_curve_from_animation_cmd())
    cmds.setParent(col1)
    
    # ===== ATTACH TO PATH =====
    cmds.frameLayout(label="  " + get_text("attach_path"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("attach_desc"), align="left",
              font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "right"])
    cmds.textField("curve_name_field", text="", placeholderText=get_text("target_curve"))
    cmds.button(label=get_text("get_btn"), width=50, backgroundColor=slate, command=lambda x: get_selected_curve())
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.checkBox("maintain_offset", label=get_text("preserve_offset"), value=True)
    cmds.checkBox("follow_rotation", label=get_text("align_direction"), value=True)
    
    cmds.separator(height=8, style="none")
    cmds.button(label=get_text("attach_btn"), height=38, backgroundColor=success,
                command=lambda x: apply_object_to_curve_cmd())
    cmds.setParent(col1)
    
    # ===== CURVE SNAPSHOT =====
    cmds.frameLayout(label="  " + get_text("curve_snapshot"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("snapshot_desc"), align="left",
              font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("save_snapshot"), height=32, backgroundColor=secondary,
                command=lambda x: create_reflection_cmd())
    cmds.button(label=get_text("restore_snapshot"), height=32, backgroundColor=warning,
                command=lambda x: reset_to_reflection_cmd())
    cmds.setParent("..")
    cmds.setParent(col1)
    
    # ===== CV CONTROL RIG =====
    cmds.frameLayout(label="  " + get_text("cv_control_rig"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("cv_desc"), align="left",
              font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.button(label=get_text("generate_cv"), height=34, backgroundColor=accent,
                command=lambda x: create_cv_controls_cmd())
    
    cmds.separator(height=6, style="none")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=[120, 100, 100])
    cmds.button(label=get_text("select_all"), height=28, command=lambda x: select_all_cv_controls())
    cmds.button(label=get_text("reparent"), height=28, command=lambda x: reparent_controls_cmd())
    cmds.button(label=get_text("remove"), height=28, backgroundColor=danger,
                command=lambda x: delete_cv_controls_cmd())
    cmds.setParent("..")
    
    cmds.separator(height=8, style="none")
    cmds.text(label=get_text("surface_desc"), align="left", font="smallObliqueLabelFont", height=18)
    cmds.button(label=get_text("attach_to_surface"), height=32, backgroundColor=teal,
                command=lambda x: attach_objects_to_surface())
    cmds.setParent(col1)
    
    # ===== HEIGHT CONTROL =====
    cmds.frameLayout(label="  " + get_text("height_control"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("height_desc"), align="left",
              font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("world_space"), height=30, backgroundColor=teal,
                command=lambda x: create_incline_control(independent=True))
    cmds.button(label=get_text("follow_path"), height=30, backgroundColor=secondary,
                command=lambda x: create_incline_control(independent=False))
    cmds.setParent("..")
    
    cmds.button(label=get_text("remove_height"), height=26, backgroundColor=danger,
                command=lambda x: delete_incline_control())
    cmds.setParent(col1)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # ==================== TAB 2: UTILITIES ====================
    tab2 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col2 = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    cmds.separator(height=8, style="none")
    
    # ===== CURVE EDITING =====
    cmds.frameLayout(label="  " + get_text("curve_editing"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("curve_length"), height=28, command=lambda x: show_curve_length_cmd())
    cmds.button(label=get_text("curve_info"), height=28, command=lambda x: show_curve_info())
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("lock_length"), height=28, backgroundColor=warning, command=lambda x: lock_curve_length())
    cmds.button(label=get_text("unlock_length"), height=28, backgroundColor=success, command=lambda x: unlock_curve_length())
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=[200, 55, 50])
    cmds.button(label=get_text("rebuild_curve"), height=28, command=lambda x: rebuild_curve_cmd())
    cmds.text(label=get_text("spans"))
    cmds.intField("rebuild_spans", value=10, minValue=1, width=45)
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("straighten"), height=28, command=lambda x: make_curve_straight_cmd())
    cmds.button(label=get_text("smooth"), height=28, command=lambda x: smooth_curve_cmd())
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("duplicate"), height=28, command=lambda x: duplicate_curve_cmd())
    cmds.button(label=get_text("reverse_dir"), height=28, command=lambda x: reverse_curve_cmd())
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("mirror_x"), height=28, command=lambda x: mirror_curve("x"))
    cmds.button(label=get_text("mirror_z"), height=28, command=lambda x: mirror_curve("z"))
    cmds.setParent("..")
    cmds.setParent(col2)
    
    # ===== KEYFRAME TOOLS =====
    cmds.frameLayout(label="  " + get_text("animation_keys"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("bake_anim"), height=32, backgroundColor=warning,
                command=lambda x: bake_animation_cmd())
    cmds.button(label=get_text("bake_world"), height=32,
                command=lambda x: bake_to_world_space())
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("delete_constraints"), height=28, command=lambda x: delete_constraints_cmd())
    cmds.button(label=get_text("delete_animation"), height=28, command=lambda x: delete_animation_cmd())
    cmds.setParent("..")
    
    cmds.separator(height=8, style="none")
    cmds.text(label=get_text("tangent_presets"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnAttach3=["both", "both", "both"])
    cmds.button(label=get_text("linear"), height=26, command=lambda x: set_key_tangent("linear"))
    cmds.button(label=get_text("smooth_key"), height=26, command=lambda x: set_key_tangent("auto"))
    cmds.button(label=get_text("stepped"), height=26, command=lambda x: set_key_tangent("step"))
    cmds.setParent("..")
    cmds.setParent(col2)
    
    # ===== PATH TIMING =====
    cmds.frameLayout(label="  " + get_text("path_timing"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("position_offset"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=5, adjustableColumn=1, columnWidth5=[70, 40, 45, 45, 40])
    cmds.floatField("offset_value", value=0.0, precision=3, width=65)
    cmds.button(label="-1", height=26, command=lambda x: offset_path_animation(-1.0))
    cmds.button(label="-0.1", height=26, command=lambda x: offset_path_animation(-0.1))
    cmds.button(label="+0.1", height=26, command=lambda x: offset_path_animation(0.1))
    cmds.button(label="+1", height=26, command=lambda x: offset_path_animation(1.0))
    cmds.setParent("..")
    cmds.button(label=get_text("apply_offset"), height=28, backgroundColor=primary, command=lambda x: apply_offset_cmd())
    
    cmds.separator(height=8, style="none")
    cmds.text(label=get_text("speed_mult"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=1, columnWidth4=[90, 50, 50, 50])
    cmds.floatField("speed_value", value=1.0, precision=2, width=85)
    cmds.button(label="0.5x", height=26, command=lambda x: set_speed_multiplier(0.5))
    cmds.button(label="1x", height=26, command=lambda x: set_speed_multiplier(1.0))
    cmds.button(label="2x", height=26, command=lambda x: set_speed_multiplier(2.0))
    cmds.setParent("..")
    cmds.button(label=get_text("apply_speed"), height=28, backgroundColor=primary, command=lambda x: apply_speed_cmd())
    
    cmds.separator(height=8, style="none")
    cmds.button(label=get_text("reverse_path"), height=28, command=lambda x: reverse_path_animation())
    cmds.setParent(col2)
    
    # ===== LOCATORS & TRANSFORMS =====
    cmds.frameLayout(label="  " + get_text("locators_transforms"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("loc_selection"), height=28, command=lambda x: create_locator_at_selection_cmd())
    cmds.button(label=get_text("loc_origin"), height=28, command=lambda x: create_locator_at_origin())
    cmds.setParent("..")
    
    cmds.button(label=get_text("match_transforms"), height=28, command=lambda x: match_transforms_cmd())
    
    cmds.separator(height=6, style="none")
    cmds.text(label=get_text("constraints_label"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnAttach3=["both", "both", "both"])
    cmds.button(label=get_text("parent"), height=26, command=lambda x: create_parent_constraint())
    cmds.button(label=get_text("point"), height=26, command=lambda x: create_point_constraint())
    cmds.button(label=get_text("orient"), height=26, command=lambda x: create_orient_constraint())
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.button(label=get_text("measure_dist"), height=28, command=lambda x: measure_distance())
    cmds.setParent(col2)
    
    # ===== QUICK SELECT =====
    cmds.frameLayout(label="  " + get_text("quick_select"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("hierarchy"), height=28, command=lambda x: cmds.select(hi=True))
    cmds.button(label=get_text("curve_cvs"), height=28, command=lambda x: select_curve_cvs())
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("all_constraints"), height=28, command=lambda x: select_constraints())
    cmds.button(label=get_text("motion_paths"), height=28, command=lambda x: select_motion_paths())
    cmds.setParent("..")
    cmds.setParent(col2)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # ==================== TAB 3: SYSTEM ====================
    tab3 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col3 = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    cmds.separator(height=8, style="none")
    cmds.text(label="   " + get_text("system_mgmt"), font="boldLabelFont", height=32, 
              backgroundColor=header_bg, align="left")
    cmds.separator(height=12, style="none")
    
    # ===== FINALIZE =====
    cmds.frameLayout(label="  " + get_text("finalize"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("finalize_warn"), align="left",
              font="smallPlainLabelFont", height=22)
    cmds.button(label=get_text("bake_selected"), height=38, backgroundColor=warning,
                command=lambda x: bake_animation_cmd())
    cmds.setParent(col3)
    
    # ===== SELECTIVE CLEANUP =====
    cmds.frameLayout(label="  " + get_text("selective_cleanup"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.button(label=get_text("remove_cv"), height=28, command=lambda x: delete_cv_controls_cmd())
    cmds.button(label=get_text("remove_height_ctrl"), height=28, command=lambda x: delete_incline_control())
    cmds.button(label=get_text("remove_snapshot"), height=28, command=lambda x: delete_reflection())
    cmds.button(label=get_text("remove_all_const"), height=28, command=lambda x: delete_all_constraints())
    cmds.setParent(col3)
    
    # ===== DANGER ZONE =====
    cmds.separator(height=15, style="none")
    cmds.frameLayout(label="  " + get_text("danger_zone"), collapsable=True, collapse=True,
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("danger_warn"), 
              align="center", font="smallPlainLabelFont", height=25)
    cmds.separator(height=4, style="none")
    
    cmds.button(label=get_text("delete_system"), height=42, backgroundColor=[0.82, 0.22, 0.28],
                command=lambda x: delete_system_cmd())
    cmds.separator(height=4, style="none")
    cmds.button(label=get_text("clean_all"), height=36, backgroundColor=[0.72, 0.28, 0.32],
                command=lambda x: clean_scene())
    cmds.setParent(col3)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # ==================== TAB 4: ADVANCED ====================
    tab4 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col4_adv = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    cmds.separator(height=8, style="none")
    cmds.text(label="   " + get_text("tab_advanced").strip(), font="boldLabelFont", height=32, 
              backgroundColor=header_bg, align="left")
    cmds.separator(height=12, style="none")
    
    # ===== CURVE MORPHING =====
    cmds.frameLayout(label="  " + get_text("curve_morphing"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("morph_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.text(label=get_text("select_two_curves"), align="left", font="smallObliqueLabelFont", height=18)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("morph_basic"), height=32, backgroundColor=accent,
                command=lambda x: morph_curve_basic())
    cmds.button(label=get_text("morph_preserve"), height=32, backgroundColor=teal,
                command=lambda x: morph_curve_preserve_length())
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    # ===== CURVE SLIDING =====
    cmds.frameLayout(label="  " + get_text("curve_sliding"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("slide_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=[120, 60, 100])
    cmds.text(label=get_text("slide_amount"), align="right")
    cmds.floatField("slide_amount_field", value=0.05, precision=3, minValue=0.001, maxValue=0.5, width=55)
    cmds.text(label="(0-1)")
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("slide_forward"), height=30, backgroundColor=success,
                command=lambda x: slide_curve_forward())
    cmds.button(label=get_text("slide_backward"), height=30, backgroundColor=warning,
                command=lambda x: slide_curve_backward())
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    # ===== MASTER FOLLOW =====
    cmds.frameLayout(label="  " + get_text("master_follow"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("master_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.button(label=get_text("create_follow"), height=32, backgroundColor=primary,
                command=lambda x: create_master_follow_system())
    cmds.button(label=get_text("remove_follow"), height=26, backgroundColor=danger,
                command=lambda x: remove_master_follow_system())
    cmds.setParent(col4_adv)
    
    # ===== SMART CONSTRAINTS =====
    cmds.frameLayout(label="  " + get_text("smart_constraints"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("smart_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnAttach3=["both", "both", "both"])
    cmds.button(label=get_text("smart_parent"), height=28, 
                command=lambda x: apply_smart_constraint("parent"))
    cmds.button(label=get_text("smart_point"), height=28,
                command=lambda x: apply_smart_constraint("point"))
    cmds.button(label=get_text("smart_orient"), height=28,
                command=lambda x: apply_smart_constraint("orient"))
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    # ===== BACKUP & RECOVERY =====
    cmds.frameLayout(label="  " + get_text("backup_system"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("backup_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("create_backup"), height=30, backgroundColor=secondary,
                command=lambda x: create_backup_for_selection())
    cmds.button(label=get_text("restore_backup"), height=30, backgroundColor=success,
                command=lambda x: restore_from_backup())
    cmds.setParent("..")
    
    cmds.button(label=get_text("clear_backup"), height=26, backgroundColor=danger,
                command=lambda x: clear_all_backups())
    cmds.setParent(col4_adv)
    
    # ===== LOCATOR TOOLS =====
    cmds.frameLayout(label="  " + get_text("locator_tools"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnAttach3=["both", "both", "both"])
    cmds.button(label=get_text("loc_bigger"), height=28,
                command=lambda x: make_locators_bigger())
    cmds.button(label=get_text("loc_smaller"), height=28,
                command=lambda x: make_locators_smaller())
    cmds.button(label=get_text("loc_color"), height=28,
                command=lambda x: cycle_locator_color())
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    # ===== ATTACH TO SURFACE =====
    cmds.frameLayout(label="  " + get_text("attach_surface"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("surface_desc"), align="left", font="smallPlainLabelFont", height=20)
    cmds.text(label=get_text("select_surface"), align="left", font="smallObliqueLabelFont", height=18)
    cmds.separator(height=4, style="none")
    
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.button(label=get_text("attach_to_surface"), height=32, backgroundColor=primary,
                command=lambda x: attach_objects_to_surface())
    cmds.button(label=get_text("detach_surface"), height=32, backgroundColor=danger,
                command=lambda x: detach_objects_from_surface())
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    # ===== ADVANCED CV CONTROLS =====
    cmds.frameLayout(label="  " + get_text("cv_advanced"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnWidth3=[100, 60, 100])
    cmds.text(label=get_text("cv_count"), align="right")
    cmds.intField("cv_count_field", value=10, minValue=4, maxValue=100, width=55)
    cmds.button(label=get_text("add_cvs"), height=26,
                command=lambda x: add_cv_controls_with_count(cmds.intField("cv_count_field", query=True, value=True)))
    cmds.setParent("..")
    cmds.setParent(col4_adv)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # ==================== TAB 5: ANIMATION PRESETS ====================
    tab5 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col5_presets = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    cmds.separator(height=8, style="none")
    cmds.text(label="   " + get_text("anim_presets"), font="boldLabelFont", height=32, 
              backgroundColor=header_bg, align="left")
    cmds.text(label="   " + get_text("presets_desc"), height=22,
              backgroundColor=bg_header, align="left", font="smallPlainLabelFont")
    cmds.separator(height=8, style="none")
    
    # ===== CONTROLLER STATUS =====
    cmds.frameLayout(label="  Current Selection", collapsable=False, 
                     marginWidth=12, marginHeight=8, font="boldLabelFont",
                     backgroundColor=bg_section)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_section)
    cmds.text("controller_info_text", label="Select controllers to see presets", 
              align="center", font="boldLabelFont", height=24, backgroundColor=dark)
    cmds.text(label="Presets are saved per controller combination", 
              align="center", font="smallObliqueLabelFont", height=18)
    cmds.setParent(col5_presets)
    
    cmds.separator(height=8, style="none")
    
    # ===== PRESET LIBRARY =====
    cmds.frameLayout(label="  " + get_text("select_preset"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label="Select controllers, then choose a preset to apply:", 
              align="left", font="smallPlainLabelFont", height=18)
    cmds.separator(height=4, style="none")
    
    # Preset list
    global _preset_list_ui
    _preset_list_ui = cmds.textScrollList(
        "preset_scroll_list",
        numberOfRows=8,
        allowMultiSelection=False,
        height=150,
        selectCommand=update_preset_info_ui,
        backgroundColor=bg_section
    )
    
    # Refresh list on creation and setup selection callback
    cmds.evalDeferred(refresh_preset_list_ui)
    cmds.evalDeferred(setup_preset_selection_callback)
    
    cmds.separator(height=6, style="none")
    
    # Preset info display
    cmds.frameLayout(label=get_text("preset_info"), collapsable=False, 
                     marginWidth=8, marginHeight=6, font="smallPlainLabelFont",
                     backgroundColor=bg_section)
    cmds.text("preset_info_text", label="Select a preset to see info", align="left", 
              font="smallPlainLabelFont", height=55, wordWrap=True)
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    
    # Management buttons
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=1, columnWidth4=[80, 80, 80, 80])
    cmds.button(label=get_text("refresh_list"), height=26, 
                command=refresh_preset_list_ui)
    cmds.button(label=get_text("delete_preset"), height=26, backgroundColor=danger,
                command=cmd_delete_preset)
    cmds.button(label=get_text("export_presets"), height=26,
                command=lambda x: export_presets_for_controllers())
    cmds.button(label=get_text("import_presets"), height=26,
                command=lambda x: import_presets_for_controllers())
    cmds.setParent("..")
    cmds.setParent(col5_presets)
    
    # ===== SAVE PRESET =====
    cmds.frameLayout(label="  " + get_text("save_preset"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.text(label="Save animation from selected controllers:", 
              align="left", font="smallPlainLabelFont", height=18)
    cmds.separator(height=4, style="none")
    
    # Preset name
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=[100, 200])
    cmds.text(label=get_text("preset_name"), align="right")
    cmds.textField("preset_name_field", placeholderText=get_text("preset_name_hint"), width=200)
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    
    # Source frame range
    cmds.text(label=get_text("source_range"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=5, adjustableColumn=1, columnWidth5=[80, 80, 30, 80, 60])
    cmds.text(label="")
    cmds.floatField("preset_start_frame", value=cmds.playbackOptions(query=True, minTime=True), precision=0, width=75)
    cmds.text(label=get_text("to_label"), align="center")
    cmds.floatField("preset_end_frame", value=cmds.playbackOptions(query=True, maxTime=True), precision=0, width=75)
    cmds.text(label=get_text("frames"))
    cmds.setParent("..")
    
    cmds.separator(height=8, style="none")
    cmds.button(label=get_text("save_from_sel"), height=38, backgroundColor=success,
                command=cmd_save_preset)
    cmds.setParent(col5_presets)
    
    # ===== APPLY PRESET =====
    cmds.frameLayout(label="  " + get_text("apply_preset"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    # Target frame range - start and end
    cmds.text(label=get_text("target_range"), align="left", font="smallPlainLabelFont")
    cmds.rowLayout(numberOfColumns=5, adjustableColumn=1, columnWidth5=[60, 75, 30, 75, 60])
    cmds.text(label="Start:")
    cmds.floatField("apply_start_frame", value=cmds.playbackOptions(query=True, minTime=True), precision=0, width=70)
    cmds.text(label=get_text("to_label"), align="center")
    cmds.floatField("apply_end_frame", value=cmds.playbackOptions(query=True, maxTime=True), precision=0, width=70)
    cmds.text(label="End")
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    
    # Blend mode
    cmds.text(label=get_text("blend_mode"), align="left", font="smallPlainLabelFont")
    cmds.radioCollection("blend_mode_collection")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, columnAttach3=["both", "both", "both"])
    cmds.radioButton("blend_replace_rb", label=get_text("blend_replace"), select=True)
    cmds.radioButton("blend_add_rb", label=get_text("blend_add"))
    cmds.radioButton("blend_mult_rb", label=get_text("blend_multiply"))
    cmds.setParent("..")
    
    cmds.separator(height=8, style="none")
    
    # Apply button
    cmds.button(label=get_text("apply_to_sel"), height=40, backgroundColor=primary,
                command=cmd_apply_preset)
    cmds.setParent(col5_presets)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # ==================== TAB 6: SETTINGS ====================
    tab6 = cmds.scrollLayout(childResizable=True, backgroundColor=bg_main)
    col6 = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, backgroundColor=bg_main)
    
    cmds.separator(height=8, style="none")
    cmds.text(label="   " + get_text("tab_settings").strip(), font="boldLabelFont", height=32, 
              backgroundColor=header_bg, align="left")
    cmds.separator(height=12, style="none")
    
    # ===== LANGUAGE =====
    cmds.frameLayout(label="  " + get_text("language"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("select_lang"), align="left", font="smallPlainLabelFont", height=22)
    cmds.separator(height=4, style="none")
    
    # Language radio buttons
    current_lang = get_language()
    cmds.radioCollection("lang_collection")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.radioButton("lang_en", label=get_text("english"), select=(current_lang == "en"),
                     onCommand=lambda x: set_language_and_refresh("en"))
    cmds.radioButton("lang_ar", label=get_text("arabic"), select=(current_lang == "ar"),
                     onCommand=lambda x: set_language_and_refresh("ar"))
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.text(label=get_text("lang_restart"), align="center", font="smallObliqueLabelFont", height=20)
    cmds.setParent(col6)
    
    # ===== APPEARANCE =====
    cmds.frameLayout(label="  " + get_text("appearance"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("theme_desc"), align="left", font="smallPlainLabelFont", height=22)
    cmds.separator(height=4, style="none")
    
    # Theme radio buttons
    current_theme = get_theme()
    cmds.radioCollection("theme_collection")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "both"])
    cmds.radioButton("theme_dark", label=get_text("dark_mode"), select=(current_theme == "dark"),
                     onCommand=lambda x: set_theme_and_refresh("dark"))
    cmds.radioButton("theme_light", label=get_text("light_mode"), select=(current_theme == "light"),
                     onCommand=lambda x: set_theme_and_refresh("light"))
    cmds.setParent("..")
    
    cmds.separator(height=6, style="none")
    cmds.text(label=get_text("theme_restart"), align="center", font="smallObliqueLabelFont", height=20)
    cmds.setParent(col6)
    
    # ===== CONTACT =====
    cmds.frameLayout(label="  " + get_text("contact"), collapsable=True, 
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, backgroundColor=bg_frame)
    
    cmds.text(label=get_text("contact_desc"), align="left", font="smallPlainLabelFont", height=22)
    cmds.separator(height=8, style="none")
    
    # LinkedIn button
    cmds.button(label=get_text("linkedin"), height=36, backgroundColor=primary,
                command=lambda x: open_linkedin())
    
    cmds.separator(height=10, style="none")
    
    # Phone section
    cmds.text(label=get_text("phone_label"), align="left", font="boldLabelFont", height=20)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=["both", "right"])
    cmds.textField("cmp_phone_field", text=PHONE_NUMBER, editable=False, font="boldLabelFont")
    cmds.button(label=get_text("copy_phone"), width=100, backgroundColor=slate, command=lambda x: copy_phone())
    cmds.setParent("..")
    cmds.setParent(col6)
    
    # ===== CREDITS =====
    cmds.separator(height=15, style="none")
    cmds.frameLayout(label="  " + get_text("credits"), collapsable=True, collapse=False,
                     marginWidth=12, marginHeight=10, font="boldLabelFont",
                     backgroundColor=bg_frame)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4, backgroundColor=bg_frame)
    
    cmds.separator(height=8, style="none")
    cmds.text(label=TOOL_NAME, font="boldLabelFont", height=28, align="center")
    cmds.text(label="{} {}".format(get_text("version"), TOOL_VERSION), height=22, align="center")
    cmds.separator(height=8, style="none")
    cmds.text(label="{}: {}".format(get_text("developed_by"), AUTHOR), font="boldLabelFont", height=24, align="center")
    cmds.separator(height=8, style="none")
    cmds.text(label=get_text("about_desc1"), font="smallPlainLabelFont", height=18, align="center")
    cmds.text(label=get_text("about_desc2"), font="smallPlainLabelFont", height=18, align="center")
    cmds.separator(height=10, style="none")
    cmds.setParent(col6)
    
    cmds.separator(height=15, style="none")
    cmds.setParent(main_layout)
    
    # Set modern tab labels - shorter names
    cmds.tabLayout(main_layout, edit=True, tabLabel=[
        (tab1, "Create"),
        (tab2, "Edit"),
        (tab3, "Bake"),
        (tab4, "Tools"),
        (tab5, "Presets"),
        (tab6, "Settings")
    ])
    
    # Attach tab layout to form
    cmds.formLayout(form, edit=True,
        attachForm=[
            (main_layout, 'top', 0),
            (main_layout, 'left', 0),
            (main_layout, 'right', 0),
            (main_layout, 'bottom', 0)
        ]
    )
    
    cmds.showWindow(window)


def set_language_and_refresh(lang):
    """Set language and refresh UI"""
    set_language(lang)
    # Refresh UI to apply changes
    cmds.evalDeferred(show_ui)


def set_theme_and_refresh(theme):
    """Set theme and refresh UI"""  
    set_theme(theme)
    # Refresh UI to apply changes immediately
    cmds.evalDeferred(show_ui)


# ============================================================================
# COMMAND FUNCTIONS (UI Callbacks)
# ============================================================================

def get_selected_curve():
    """Get selected curve name"""
    sel = cmds.ls(selection=True)
    if sel:
        cmds.textField("curve_name_field", edit=True, text=sel[0])


def create_curve_from_animation_cmd():
    """Create curve from animated object"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select an animated object!")
        return
    
    sample_rate = cmds.intField("sample_frames", query=True, value=True)
    zero_vert = cmds.checkBox("zero_vertical", query=True, value=True)
    start_end = cmds.checkBox("start_end_only", query=True, value=True)
    
    curve = create_curve_from_animation(sel[0], sample_rate, zero_vert, start_end)
    if curve:
        cmds.textField("curve_name_field", edit=True, text=curve)
        cmds.select(curve)
        cmds.inViewMessage(msg="Curve created: {}".format(curve), pos="midCenter", fade=True)


def apply_object_to_curve_cmd():
    """Apply selected object to curve"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select an object!")
        return
    
    curve_name = cmds.textField("curve_name_field", query=True, text=True)
    if not curve_name or not cmds.objExists(curve_name):
        cmds.warning("Please select a valid curve!")
        return
    
    maintain_offset = cmds.checkBox("maintain_offset", query=True, value=True)
    follow_rotation = cmds.checkBox("follow_rotation", query=True, value=True)
    
    apply_object_to_curve(sel[0], curve_name, maintain_offset, follow_rotation)


def create_reflection_cmd():
    """Create reflection (backup) of curve"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    create_reflection(sel[0])


def reset_to_reflection_cmd():
    """Reset curve to reflection state"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    reset_to_reflection(sel[0])


def create_cv_controls_cmd():
    """Create CV controls"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    create_cv_controls(sel[0])


def delete_cv_controls_cmd():
    """Delete CV controls"""
    delete_cv_controls()


def reparent_controls_cmd():
    """Reparent CV controls"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select the control to be the new root!")
        return
    reparent_controls(sel[0])


def show_curve_length_cmd():
    """Show curve length"""
    sel = cmds.ls(selection=True)
    if sel:
        try:
            length = cmds.arclen(sel[0])
            cmds.inViewMessage(msg="Curve length: {:.3f}".format(length), pos="midCenter", fade=True)
        except:
            cmds.warning("Please select a curve!")


def make_curve_straight_cmd():
    """Make curve straight"""
    sel = cmds.ls(selection=True)
    if sel:
        make_curve_straight(sel[0])


def smooth_curve_cmd():
    """Smooth curve"""
    sel = cmds.ls(selection=True)
    if sel:
        try:
            cmds.smoothCurve(sel[0] + ".cv[*]", smoothness=5)
            cmds.inViewMessage(msg="Curve smoothed!", pos="midCenter", fade=True)
        except:
            cmds.warning("Failed to smooth curve!")


def rebuild_curve_cmd():
    """Rebuild curve"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    spans = cmds.intField("rebuild_spans", query=True, value=True)
    rebuild_curve(sel[0], spans)


def duplicate_curve_cmd():
    """Duplicate curve"""
    sel = cmds.ls(selection=True)
    if sel:
        dup = cmds.duplicate(sel[0])[0]
        cmds.select(dup)
        cmds.inViewMessage(msg="Duplicated: {}".format(dup), pos="midCenter", fade=True)


def reverse_curve_cmd():
    """Reverse curve"""
    sel = cmds.ls(selection=True)
    if sel:
        try:
            cmds.reverseCurve(sel[0], constructionHistory=False, replaceOriginal=True)
            cmds.inViewMessage(msg="Curve reversed!", pos="midCenter", fade=True)
        except:
            cmds.warning("Failed to reverse curve!")


def bake_animation_cmd():
    """Bake animation"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select objects to bake!")
        return
    bake_animation(sel)


def delete_constraints_cmd():
    """Delete constraints on selected"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select objects!")
        return
    delete_constraints(sel)


def delete_animation_cmd():
    """Delete animation on selected"""
    sel = cmds.ls(selection=True)
    if sel:
        for obj in sel:
            try:
                cmds.cutKey(obj, clear=True)
            except:
                pass
        cmds.inViewMessage(msg="Animation deleted!", pos="midCenter", fade=True)


def create_locator_at_selection_cmd():
    """Create locator at selection"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select an object!")
        return
    create_locators_at_objects(sel)


def create_locator_at_origin():
    """Create locator at origin"""
    loc = cmds.spaceLocator(name=PREFIX + "locator")[0]
    cmds.select(loc)


def match_transforms_cmd():
    """Match transforms"""
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning("Select source then target!")
        return
    match_transforms(sel[0], sel[1])


def apply_offset_cmd():
    """Apply path offset"""
    offset = cmds.floatField("offset_value", query=True, value=True)
    apply_path_offset(offset)


def apply_speed_cmd():
    """Apply speed multiplier"""
    speed = cmds.floatField("speed_value", query=True, value=True)
    apply_speed_multiplier(speed)


def delete_system_cmd():
    """Delete CurveMorph system"""
    delete_curvemorph_system()


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def create_curve_from_animation(obj, sample_rate=5, zero_vertical=True, start_end_only=False):
    """Create a curve from an animated object's path"""
    if not cmds.objExists(obj):
        cmds.warning("Object '{}' does not exist!".format(obj))
        return None
    
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    current_time = cmds.currentTime(query=True)
    positions = []
    
    try:
        if start_end_only:
            cmds.currentTime(start)
            try:
                pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                if zero_vertical:
                    pos[1] = 0
                positions.append(pos)
            except:
                cmds.warning("Could not get position at frame {}".format(start))
                return None
            
            cmds.currentTime(end)
            try:
                pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                if zero_vertical:
                    pos[1] = 0
                positions.append(pos)
            except:
                cmds.warning("Could not get position at frame {}".format(end))
                return None
        else:
            for frame in range(start, end + 1, sample_rate):
                try:
                    cmds.currentTime(frame)
                    pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                    if zero_vertical:
                        pos[1] = 0
                    positions.append(pos)
                except:
                    continue
            
            try:
                cmds.currentTime(end)
                pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                if zero_vertical:
                    pos[1] = 0
                if not positions or positions[-1] != pos:
                    positions.append(pos)
            except:
                pass
        
        if len(positions) < 2:
            cmds.warning("Not enough positions to create curve!")
            return None
        
        clean_positions = [positions[0]]
        for pos in positions[1:]:
            last = clean_positions[-1]
            dist = math.sqrt(sum((a-b)**2 for a, b in zip(pos, last)))
            if dist > 0.001:
                clean_positions.append(pos)
        
        if len(clean_positions) < 2:
            cmds.warning("Object not moving enough!")
            return None
        
        curve = cmds.curve(point=clean_positions, degree=min(3, len(clean_positions)-1), name=PREFIX + "curve")
        
        if len(clean_positions) > 3:
            spans = max(4, len(clean_positions) // 2)
            try:
                cmds.rebuildCurve(curve, spans=spans, keepRange=1, keepEndPoints=True, constructionHistory=False)
            except:
                pass
        
        try:
            cmds.setAttr(curve + ".dispCV", 1)
        except:
            pass
        
        return curve
    finally:
        try:
            cmds.currentTime(current_time)
        except:
            pass


def apply_object_to_curve(obj, curve_name, maintain_offset=True, follow_rotation=True):
    """Apply an animated object to follow a curve"""
    if not cmds.objExists(obj):
        cmds.warning("Object '{}' does not exist!".format(obj))
        return
    
    if not cmds.objExists(curve_name):
        cmds.warning("Curve '{}' does not exist!".format(curve_name))
        return
    
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    current_time = cmds.currentTime(query=True)
    
    shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shapes:
        cmds.warning("Not a valid curve!")
        return
    
    npoc = None
    path_loc = None
    
    cycle_check_state = True
    try:
        cycle_check_state = cmds.cycleCheck(query=True, evaluation=True)
        cmds.cycleCheck(evaluation=False)
    except:
        pass
    
    try:
        npoc = cmds.createNode("nearestPointOnCurve")
        cmds.connectAttr(shapes[0] + ".worldSpace[0]", npoc + ".inputCurve")
        
        u_values = []
        for frame in range(start, end + 1):
            try:
                cmds.currentTime(frame)
                pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                cmds.setAttr(npoc + ".inPositionX", pos[0])
                cmds.setAttr(npoc + ".inPositionY", pos[1])
                cmds.setAttr(npoc + ".inPositionZ", pos[2])
                u_val = cmds.getAttr(npoc + ".parameter")
                u_values.append((frame, u_val))
            except:
                continue
        
        if not u_values:
            cmds.warning("Could not sample animation!")
            return
        
        if npoc:
            cmds.delete(npoc)
            npoc = None
        
        path_loc = cmds.spaceLocator(name=PREFIX + "path_loc")[0]
        
        try:
            motion_path = cmds.pathAnimation(path_loc, curve=curve_name, follow=follow_rotation,
                followAxis="x", upAxis="y", worldUpType="scene", fractionMode=False,
                startTimeU=start, endTimeU=end)
        except Exception as e:
            cmds.warning("Failed to create motion path: {}".format(str(e)))
            if path_loc:
                cmds.delete(path_loc)
            return
        
        try:
            cmds.cutKey(motion_path, attribute="uValue", clear=True)
        except:
            pass
        
        for frame, u_val in u_values:
            try:
                cmds.setKeyframe(motion_path + ".uValue", value=u_val, time=frame)
            except:
                pass
        
        try:
            cmds.keyTangent(motion_path, attribute="uValue", inTangentType="linear", outTangentType="linear")
        except:
            pass
        
        try:
            cmds.parentConstraint(path_loc, obj, maintainOffset=maintain_offset)
        except Exception as e:
            cmds.warning("Failed to create constraint: {}".format(str(e)))
            return
        
        grp = cmds.group([path_loc], name=PREFIX + "system_grp")
        cmds.inViewMessage(msg="Object applied to curve!", pos="midCenter", fade=True)
        
    except Exception as e:
        cmds.warning("Error applying object to curve: {}".format(str(e)))
        if npoc:
            try:
                cmds.delete(npoc)
            except:
                pass
        if path_loc:
            try:
                cmds.delete(path_loc)
            except:
                pass
    finally:
        try:
            cmds.cycleCheck(evaluation=cycle_check_state)
        except:
            pass
        try:
            cmds.currentTime(current_time)
            cmds.select(obj)
        except:
            pass


def create_reflection(curve_name):
    """Save snapshot of current curve CV positions (does NOT create new curve)"""
    
    if not cmds.objExists(curve_name):
        cmds.warning("Curve '{}' does not exist!".format(curve_name))
        return
    
    # Get curve shape
    shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shapes:
        cmds.warning("Not a valid curve!")
        return
    
    try:
        # Get all CV positions
        num_cvs = cmds.getAttr(shapes[0] + ".controlPoints", size=True)
        if isinstance(num_cvs, list):
            num_cvs = len(num_cvs) if num_cvs else 0
        num_cvs = int(num_cvs)
        
        if num_cvs < 2:
            cmds.warning("Curve needs at least 2 CVs!")
            return
        
        # Store CV positions as JSON string in curve attribute
        # Get CV positions in object space (CVs are relative to curve transform)
        cv_positions = []
        for i in range(num_cvs):
            try:
                cv = "{}.cv[{}]".format(curve_name, i)
                # Get CV position in object space
                # pointPosition with local=True gets object space position
                pos = cmds.pointPosition(cv, local=True)
                cv_positions.append([float(pos[0]), float(pos[1]), float(pos[2])])
            except:
                # Fallback: try world space and we'll handle it on restore
                try:
                    pos = cmds.pointPosition(cv, world=True)
                    cv_positions.append([float(pos[0]), float(pos[1]), float(pos[2])])
                except Exception as e:
                    cmds.warning("Could not get position for CV {}: {}".format(i, str(e)))
                    return
        
        # Store as JSON in curve attribute
        import json
        snapshot_data = json.dumps(cv_positions)
        
        # Create attribute if it doesn't exist
        if not cmds.attributeQuery("snapshotData", node=curve_name, exists=True):
            cmds.addAttr(curve_name, longName="snapshotData", dataType="string")
        
        # Save snapshot
        cmds.setAttr(curve_name + ".snapshotData", snapshot_data, type="string")
        
        # Also store CV count for validation
        if not cmds.attributeQuery("snapshotCVCount", node=curve_name, exists=True):
            cmds.addAttr(curve_name, longName="snapshotCVCount", attributeType="long")
        cmds.setAttr(curve_name + ".snapshotCVCount", num_cvs)
        
        cmds.inViewMessage(msg="Snapshot saved! ({} CVs)".format(num_cvs), pos="midCenter", fade=True)
        
    except Exception as e:
        cmds.warning("Failed to save snapshot: {}".format(str(e)))


def reset_to_reflection(curve_name):
    """Restore curve to saved snapshot (restores CV positions in place)"""
    if not cmds.objExists(curve_name):
        cmds.warning("Curve '{}' does not exist!".format(curve_name))
        return
    
    if not cmds.attributeQuery("snapshotData", node=curve_name, exists=True):
        cmds.warning("No snapshot found! Save a snapshot first.")
        return
    
    try:
        snapshot_data = cmds.getAttr(curve_name + ".snapshotData")
        if not snapshot_data or snapshot_data.strip() == "":
            cmds.warning("Snapshot data is empty!")
            return
        
        shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
        if not shapes:
            cmds.warning("Not a valid curve!")
            return
        
        num_cvs = cmds.getAttr(shapes[0] + ".controlPoints", size=True)
        if isinstance(num_cvs, list):
            num_cvs = len(num_cvs) if num_cvs else 0
        num_cvs = int(num_cvs)
        
        # Get saved CV count
        if cmds.attributeQuery("snapshotCVCount", node=curve_name, exists=True):
            saved_cv_count = cmds.getAttr(curve_name + ".snapshotCVCount")
            if saved_cv_count != num_cvs:
                cmds.warning("CV count mismatch! Saved: {}, Current: {}".format(saved_cv_count, num_cvs))
                if not cmds.confirmDialog(
                    title="CV Count Mismatch",
                    message="Snapshot has {} CVs, but curve has {} CVs.\nRestore anyway?".format(saved_cv_count, num_cvs),
                    button=["Yes", "Cancel"],
                    defaultButton="Yes",
                    cancelButton="Cancel"
                ) == "Yes":
                    return
                num_cvs = min(saved_cv_count, num_cvs)
        
        # Parse JSON data
        import json
        try:
            cv_positions = json.loads(snapshot_data)
        except:
            cmds.warning("Invalid snapshot data! Cannot restore.")
            return
        
        if len(cv_positions) != num_cvs:
            cmds.warning("CV count mismatch in snapshot data!")
            num_cvs = min(len(cv_positions), num_cvs)
        
        # Restore CV positions in object space
        restored_count = 0
        for i in range(num_cvs):
            try:
                cv = "{}.cv[{}]".format(curve_name, i)
                pos = cv_positions[i]
                
                # CV positions are stored as [x, y, z] lists
                if not isinstance(pos, list) or len(pos) < 3:
                    continue
                
                # Restore CV position in object space
                try:
                    cmds.move(pos[0], pos[1], pos[2], cv, relative=False, objectSpace=True)
                except:
                    try:
                        cmds.move(pos[0], pos[1], pos[2], cv, relative=False)
                    except:
                        try:
                            cmds.xform(cv, translation=pos, objectSpace=True)
                        except:
                            continue
                
                restored_count += 1
            except Exception as e:
                cmds.warning("Could not restore CV {}: {}".format(i, str(e)))
                continue
        
        if restored_count > 0:
            cmds.inViewMessage(msg="Snapshot restored! ({} CVs)".format(restored_count), pos="midCenter", fade=True)
        else:
            cmds.warning("Failed to restore any CVs!")
            
    except Exception as e:
        cmds.warning("Failed to restore snapshot: {}".format(str(e)))


def delete_reflection():
    """Delete snapshot data from curve"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    
    curve_name = sel[0]
    if not cmds.objExists(curve_name):
        cmds.warning("Curve '{}' does not exist!".format(curve_name))
        return
    
    # Check if snapshot exists
    if not cmds.attributeQuery("snapshotData", node=curve_name, exists=True):
        cmds.warning("No snapshot found on this curve!")
        return
    
    try:
        # Clear snapshot data
        cmds.setAttr(curve_name + ".snapshotData", "", type="string")
        if cmds.attributeQuery("snapshotCVCount", node=curve_name, exists=True):
            cmds.setAttr(curve_name + ".snapshotCVCount", 0)
        
        cmds.inViewMessage(msg="Snapshot deleted!", pos="midCenter", fade=True)
    except Exception as e:
        cmds.warning("Failed to delete snapshot: {}".format(str(e)))


def create_cv_controls(curve_name):
    """Create locator controls for curve CVs"""
    if not cmds.objExists(curve_name):
        cmds.warning("Curve '{}' does not exist!".format(curve_name))
        return
    
    shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shapes:
        cmds.warning("Not a valid curve!")
        return
    
    try:
        num_cvs = cmds.getAttr(shapes[0] + ".controlPoints", size=True)
        if isinstance(num_cvs, list):
            num_cvs = len(num_cvs) if num_cvs else 0
        num_cvs = int(num_cvs)
    except:
        cmds.warning("Could not get CV count!")
        return
    
    if num_cvs < 2:
        cmds.warning("Curve needs at least 2 CVs!")
        return
    
    controls = []
    created_clusters = []
    
    try:
        for i in range(num_cvs):
            try:
                cv = "{}.cv[{}]".format(curve_name, i)
                pos = cmds.pointPosition(cv, world=True)
                
                cluster_result = cmds.cluster(cv, name=PREFIX + "cluster_{}".format(i))
                if not cluster_result or len(cluster_result) < 2:
                    continue
                cluster, handle = cluster_result[0], cluster_result[1]
                created_clusters.append((cluster, handle))
                
                loc = cmds.spaceLocator(name=PREFIX + "cv_ctrl_{}".format(i))[0]
                cmds.xform(loc, worldSpace=True, translation=pos)
                
                try:
                    cmds.setAttr(loc + ".overrideEnabled", 1)
                    cmds.setAttr(loc + ".overrideColor", 17)
                except:
                    pass
                
                try:
                    cmds.parent(handle, loc)
                    cmds.setAttr(handle + ".visibility", 0)
                except:
                    pass
                
                controls.append(loc)
            except Exception as e:
                cmds.warning("Failed to create control for CV {}: {}".format(i, str(e)))
                continue
        
        if not controls:
            cmds.warning("Failed to create any CV controls!")
            for cluster, handle in created_clusters:
                try:
                    cmds.delete(cluster, handle)
                except:
                    pass
            return
        
        grp = cmds.group(controls, name=PREFIX + "cv_controls_grp")
        
        try:
            if not cmds.attributeQuery("cvControlGroup", node=curve_name, exists=True):
                cmds.addAttr(curve_name, longName="cvControlGroup", dataType="string")
            cmds.setAttr(curve_name + ".cvControlGroup", grp, type="string")
        except:
            pass
        
        cmds.select(grp)
        cmds.inViewMessage(msg="CV controls created! ({})".format(len(controls)), pos="midCenter", fade=True)
    except Exception as e:
        cmds.warning("Error creating CV controls: {}".format(str(e)))
        for cluster, handle in created_clusters:
            try:
                cmds.delete(cluster, handle)
            except:
                pass
        for loc in controls:
            try:
                cmds.delete(loc)
            except:
                pass


def delete_cv_controls():
    """Delete all CV controls"""
    
    # Find and delete control groups
    groups = cmds.ls(PREFIX + "cv_controls_grp*", PREFIX + "cluster*")
    clusters = cmds.ls(type="cluster")
    
    for c in clusters:
        if PREFIX in c:
            try:
                cmds.delete(c)
            except:
                pass
    
    for g in groups:
        if cmds.objExists(g):
            try:
                cmds.delete(g)
            except:
                pass
    
    cmds.inViewMessage(msg="CV controls deleted!", pos="midCenter", fade=True)


def select_all_cv_controls():
    """Select all CV controls"""
    controls = cmds.ls(PREFIX + "cv_ctrl_*")
    if controls:
        cmds.select(controls)
    else:
        cmds.warning("No CV controls found!")


def reparent_controls(new_root):
    """Reparent CV controls with new root"""
    controls = cmds.ls(PREFIX + "cv_ctrl_*")
    if not controls:
        cmds.warning("No CV controls found!")
        return
    
    # Unparent all
    for ctrl in controls:
        try:
            cmds.parent(ctrl, world=True)
        except:
            pass
    
    # Find index of new root
    idx = controls.index(new_root) if new_root in controls else 0
    
    # Reparent in chain from new root
    for i in range(idx + 1, len(controls)):
        try:
            cmds.parent(controls[i], controls[i-1])
        except:
            pass
    
    for i in range(idx - 1, -1, -1):
        try:
            cmds.parent(controls[i], controls[i+1])
        except:
            pass
    
    cmds.inViewMessage(msg="Controls reparented!", pos="midCenter", fade=True)


def create_incline_control(independent=True):
    """Create vertical incline control for object on curve
    
    This creates a control that allows adjusting the vertical position/incline
    of an object while it follows a curve path.
    
    Independent mode: Control moves separately, affects object's Y position via expression
    Linked mode: Control follows object but allows Y offset adjustment
    """
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select an object to create incline control for!")
        return
    
    obj = sel[0]
    
    # Create control locator
    ctrl_name = PREFIX + "incline_ctrl"
    # Make unique name
    counter = 0
    while cmds.objExists(ctrl_name + str(counter) if counter > 0 else ctrl_name):
        counter += 1
    ctrl_name = ctrl_name + str(counter) if counter > 0 else ctrl_name
    
    ctrl = cmds.spaceLocator(name=ctrl_name)[0]
    cmds.setAttr(ctrl + ".overrideEnabled", 1)
    cmds.setAttr(ctrl + ".overrideColor", 14 if independent else 17)  # Green or Yellow
    
    # Scale locator for visibility
    cmds.setAttr(ctrl + ".localScaleX", 20)
    cmds.setAttr(ctrl + ".localScaleY", 20)
    cmds.setAttr(ctrl + ".localScaleZ", 20)
    
    # Position at object location
    pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
    cmds.xform(ctrl, worldSpace=True, translation=[pos[0], pos[1], pos[2]])
    
    # Add control attributes
    cmds.addAttr(ctrl, longName="verticalOffset", attributeType="double", defaultValue=0, keyable=True)
    cmds.addAttr(ctrl, longName="inclineMultiplier", attributeType="double", defaultValue=1, min=0, max=10, keyable=True)
    
    # Create a group for the object to allow offset without breaking constraints
    offset_grp = cmds.group(empty=True, name=PREFIX + "incline_offset_grp")
    cmds.xform(offset_grp, worldSpace=True, translation=pos)
    
    # Check if object has parent constraint
    parent_constraints = cmds.listConnections(obj, type="parentConstraint")
    point_constraints = cmds.listConnections(obj, type="pointConstraint")
    
    if independent:
        # Independent mode: Control is separate, use expression to add vertical offset
        # Create expression to add Y offset to object
        expr_name = PREFIX + "incline_expr"
        counter = 0
        while cmds.objExists(expr_name + str(counter) if counter > 0 else expr_name):
            counter += 1
        expr_name = expr_name + str(counter) if counter > 0 else expr_name
        
        # Create a plus minus average node for clean offset addition
        pma = cmds.createNode("plusMinusAverage", name=PREFIX + "incline_pma")
        
        # Get current Y translation connection if any
        y_connections = cmds.listConnections(obj + ".translateY", source=True, plugs=True)
        
        if y_connections:
            # Disconnect existing and reconnect through PMA
            cmds.disconnectAttr(y_connections[0], obj + ".translateY")
            cmds.connectAttr(y_connections[0], pma + ".input1D[0]")
        
        # Connect vertical offset
        cmds.connectAttr(ctrl + ".verticalOffset", pma + ".input1D[1]")
        cmds.connectAttr(pma + ".output1D", obj + ".translateY", force=True)
        
        cmds.inViewMessage(msg="Independent incline control created! Move the verticalOffset attribute.", pos="midCenter", fade=True)
    else:
        # Linked mode: Control follows object XZ but controls Y
        # Parent constraint XZ only, Y is controlled by locator
        
        # Create a decompose matrix to get object position
        decomp = cmds.createNode("decomposeMatrix", name=PREFIX + "incline_decomp")
        cmds.connectAttr(obj + ".worldMatrix[0]", decomp + ".inputMatrix")
        
        # Connect X and Z from object to control
        cmds.connectAttr(decomp + ".outputTranslateX", ctrl + ".translateX")
        cmds.connectAttr(decomp + ".outputTranslateZ", ctrl + ".translateZ")
        
        # Set initial Y
        cmds.setAttr(ctrl + ".translateY", pos[1])
        
        # Now control's Y (plus offset) drives object Y
        pma = cmds.createNode("plusMinusAverage", name=PREFIX + "incline_pma")
        cmds.connectAttr(ctrl + ".translateY", pma + ".input1D[0]")
        cmds.connectAttr(ctrl + ".verticalOffset", pma + ".input1D[1]")
        
        # Disconnect any existing Y connection
        y_connections = cmds.listConnections(obj + ".translateY", source=True, plugs=True)
        if y_connections:
            try:
                cmds.disconnectAttr(y_connections[0], obj + ".translateY")
            except:
                pass
        
        cmds.connectAttr(pma + ".output1D", obj + ".translateY", force=True)
        
        cmds.inViewMessage(msg="Linked incline control created! Move control Y or adjust verticalOffset.", pos="midCenter", fade=True)
    
    # Store reference on object
    if not cmds.attributeQuery("inclineControl", node=obj, exists=True):
        cmds.addAttr(obj, longName="inclineControl", dataType="string")
    cmds.setAttr(obj + ".inclineControl", ctrl, type="string")
    
    # Clean up unused group
    cmds.delete(offset_grp)
    
    cmds.select(ctrl)


def delete_incline_control():
    """Delete incline controls and related nodes"""
    deleted = False
    
    # Delete incline control locators
    ctrls = cmds.ls(PREFIX + "incline_ctrl*")
    if ctrls:
        for ctrl in ctrls:
            if cmds.objExists(ctrl):
                try:
                    cmds.delete(ctrl)
                    deleted = True
                except:
                    pass
    
    # Delete incline expressions
    exprs = cmds.ls(PREFIX + "incline_expr*")
    if exprs:
        for expr in exprs:
            if cmds.objExists(expr):
                try:
                    cmds.delete(expr)
                    deleted = True
                except:
                    pass
    
    # Delete incline plus minus average nodes
    pmas = cmds.ls(PREFIX + "incline_pma*")
    if pmas:
        for pma in pmas:
            if cmds.objExists(pma):
                try:
                    cmds.delete(pma)
                    deleted = True
                except:
                    pass
    
    # Delete incline decompose matrix nodes
    decomps = cmds.ls(PREFIX + "incline_decomp*")
    if decomps:
        for decomp in decomps:
            if cmds.objExists(decomp):
                try:
                    cmds.delete(decomp)
                    deleted = True
                except:
                    pass
    
    if deleted:
        cmds.inViewMessage(msg="Incline controls deleted!", pos="midCenter", fade=True)
    else:
        cmds.inViewMessage(msg="No incline controls found.", pos="midCenter", fade=True)


def make_curve_straight(curve_name):
    """Make curve straight"""
    shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shapes:
        return
    
    num_cvs = cmds.getAttr(shapes[0] + ".controlPoints", size=True)
    if isinstance(num_cvs, list):
        num_cvs = len(num_cvs) if num_cvs else 0
    num_cvs = int(num_cvs)
    start_pos = cmds.pointPosition("{}.cv[0]".format(curve_name), world=True)
    end_pos = cmds.pointPosition("{}.cv[{}]".format(curve_name, num_cvs-1), world=True)
    
    for i in range(num_cvs):
        t = float(i) / (num_cvs - 1)
        new_pos = [start_pos[j] + (end_pos[j] - start_pos[j]) * t for j in range(3)]
        cmds.xform("{}.cv[{}]".format(curve_name, i), worldSpace=True, translation=new_pos)
    
    cmds.inViewMessage(msg="Curve straightened!", pos="midCenter", fade=True)


def rebuild_curve(curve_name, spans):
    """Rebuild curve"""
    try:
        cmds.rebuildCurve(curve_name, spans=spans, keepRange=1, keepEndPoints=True,
                          constructionHistory=False)
        cmds.inViewMessage(msg="Curve rebuilt!", pos="midCenter", fade=True)
    except:
        cmds.warning("Failed to rebuild!")


def mirror_curve(axis):
    """Mirror curve on axis"""
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    dup = cmds.duplicate(sel[0])[0]
    scale_vals = [1, 1, 1]
    if axis == "x":
        scale_vals[0] = -1
    elif axis == "z":
        scale_vals[2] = -1
    
    cmds.scale(scale_vals[0], scale_vals[1], scale_vals[2], dup, relative=True)
    cmds.makeIdentity(dup, apply=True, scale=True)
    cmds.select(dup)
    cmds.inViewMessage(msg="Curve mirrored!", pos="midCenter", fade=True)


def lock_curve_length():
    """Lock curve length"""
    try:
        mel.eval("LockCurveLength")
        cmds.inViewMessage(msg="Curve length locked!", pos="midCenter", fade=True)
    except:
        pass


def unlock_curve_length():
    """Unlock curve length"""
    try:
        mel.eval("UnlockCurveLength")
        cmds.inViewMessage(msg="Curve length unlocked!", pos="midCenter", fade=True)
    except:
        pass


def show_curve_info():
    """Show curve info"""
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    shapes = cmds.listRelatives(sel[0], shapes=True, type="nurbsCurve")
    if not shapes:
        cmds.warning("Not a curve!")
        return
    
    num_cvs = cmds.getAttr(shapes[0] + ".controlPoints", size=True)
    if isinstance(num_cvs, list):
        num_cvs = len(num_cvs) if num_cvs else 0
    num_cvs = int(num_cvs)
    spans = cmds.getAttr(shapes[0] + ".spans")
    degree = cmds.getAttr(shapes[0] + ".degree")
    length = cmds.arclen(sel[0])
    
    info = "CVs: {} | Spans: {} | Degree: {} | Length: {:.2f}".format(num_cvs, spans, degree, length)
    cmds.inViewMessage(msg=info, pos="midCenter", fade=True)


def bake_animation(objects):
    """Bake animation"""
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    
    try:
        cmds.bakeResults(objects, time=(start, end), simulation=True, sampleBy=1)
        cmds.inViewMessage(msg="Animation baked!", pos="midCenter", fade=True)
    except Exception as e:
        cmds.warning("Bake failed: {}".format(str(e)))


def bake_to_world_space():
    """Bake to world space"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select objects to bake!")
        return
    
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    
    baked_count = 0
    temp_locators = []
    
    for obj in sel:
        if not cmds.objExists(obj):
            continue
        
        loc = None
        try:
            loc = cmds.spaceLocator()[0]
            temp_locators.append(loc)
            
            try:
                cmds.parentConstraint(obj, loc, maintainOffset=False)
            except:
                cmds.warning("Could not constrain locator to {}".format(obj))
                if loc:
                    cmds.delete(loc)
                    temp_locators.remove(loc)
                continue
            
            try:
                cmds.bakeResults(loc, time=(start, end), simulation=True, sampleBy=1)
            except Exception as e:
                cmds.warning("Bake failed for {}: {}".format(obj, str(e)))
                if loc:
                    cmds.delete(loc)
                    temp_locators.remove(loc)
                continue
            
            delete_constraints([obj])
            
            try:
                cmds.parentConstraint(loc, obj, maintainOffset=False)
            except:
                cmds.warning("Could not constrain {} to locator".format(obj))
                continue
            
            try:
                cmds.bakeResults(obj, time=(start, end), simulation=True, sampleBy=1)
            except Exception as e:
                cmds.warning("Bake failed for {}: {}".format(obj, str(e)))
                continue
            
            baked_count += 1
        except Exception as e:
            cmds.warning("Error processing {}: {}".format(obj, str(e)))
        finally:
            if loc and loc in temp_locators:
                try:
                    cmds.delete(loc)
                    temp_locators.remove(loc)
                except:
                    pass
    
    for loc in temp_locators:
        try:
            cmds.delete(loc)
        except:
            pass
    
    if baked_count > 0:
        cmds.inViewMessage(msg="Baked {} objects to world space!".format(baked_count), pos="midCenter", fade=True)
    else:
        cmds.warning("No objects were baked!")


def delete_constraints(objects):
    """Delete constraints"""
    for obj in objects:
        constraints = cmds.listRelatives(obj, type="constraint") or []
        if constraints:
            cmds.delete(constraints)


def delete_all_constraints():
    """Delete all constraints in scene"""
    constraints = cmds.ls(type="constraint")
    if constraints:
        cmds.delete(constraints)
        cmds.inViewMessage(msg="All constraints deleted!", pos="midCenter", fade=True)


def create_locators_at_objects(objects):
    """Create locators at objects"""
    locs = []
    for obj in objects:
        pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
        rot = cmds.xform(obj, query=True, worldSpace=True, rotation=True)
        loc = cmds.spaceLocator(name=obj + "_loc")[0]
        cmds.xform(loc, worldSpace=True, translation=pos)
        cmds.xform(loc, worldSpace=True, rotation=rot)
        locs.append(loc)
    cmds.select(locs)
    cmds.inViewMessage(msg="Locators created!", pos="midCenter", fade=True)


def match_transforms(source, target):
    """Match transforms"""
    pos = cmds.xform(target, query=True, worldSpace=True, translation=True)
    rot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
    cmds.xform(source, worldSpace=True, translation=pos)
    cmds.xform(source, worldSpace=True, rotation=rot)
    cmds.inViewMessage(msg="Transforms matched!", pos="midCenter", fade=True)


def create_parent_constraint():
    """Create parent constraint"""
    sel = cmds.ls(selection=True)
    if len(sel) >= 2:
        cmds.parentConstraint(sel[1], sel[0], maintainOffset=True)
        cmds.inViewMessage(msg="Parent constraint created!", pos="midCenter", fade=True)


def create_point_constraint():
    """Create point constraint"""
    sel = cmds.ls(selection=True)
    if len(sel) >= 2:
        cmds.pointConstraint(sel[1], sel[0], maintainOffset=True)
        cmds.inViewMessage(msg="Point constraint created!", pos="midCenter", fade=True)


def create_orient_constraint():
    """Create orient constraint"""
    sel = cmds.ls(selection=True)
    if len(sel) >= 2:
        cmds.orientConstraint(sel[1], sel[0], maintainOffset=True)
        cmds.inViewMessage(msg="Orient constraint created!", pos="midCenter", fade=True)


def measure_distance():
    """Measure distance between two objects"""
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning("Select two objects!")
        return
    
    pos1 = cmds.xform(sel[0], query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(sel[1], query=True, worldSpace=True, translation=True)
    
    dist = math.sqrt(sum((a-b)**2 for a, b in zip(pos1, pos2)))
    cmds.inViewMessage(msg="Distance: {:.3f}".format(dist), pos="midCenter", fade=True)


def select_curve_cvs():
    """Select curve CVs"""
    sel = cmds.ls(selection=True)
    if sel:
        cmds.select(sel[0] + ".cv[*]")


def select_constraints():
    """Select all constraints"""
    sel = cmds.ls(selection=True)
    if sel:
        for obj in sel:
            constraints = cmds.listRelatives(obj, type="constraint") or []
            if constraints:
                cmds.select(constraints, add=True)


def select_motion_paths():
    """Select motion paths"""
    mps = cmds.ls(type="motionPath")
    if mps:
        cmds.select(mps)


def set_key_tangent(tangent_type):
    """Set key tangent type"""
    sel = cmds.ls(selection=True)
    if sel:
        try:
            cmds.keyTangent(sel, inTangentType=tangent_type, outTangentType=tangent_type)
            cmds.inViewMessage(msg="Tangents set to {}!".format(tangent_type), pos="midCenter", fade=True)
        except:
            pass


def offset_path_animation(delta):
    """Add to offset field"""
    current = cmds.floatField("offset_value", query=True, value=True)
    cmds.floatField("offset_value", edit=True, value=current + delta)


def set_speed_multiplier(speed):
    """Set speed field"""
    cmds.floatField("speed_value", edit=True, value=speed)


def apply_path_offset(offset):
    """Apply offset to path animation"""
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    # Find motion paths
    for obj in sel:
        connections = cmds.listConnections(obj, type="motionPath") or []
        constraints = cmds.listRelatives(obj, type="parentConstraint") or []
        
        for con in constraints:
            targets = cmds.parentConstraint(con, query=True, targetList=True) or []
            for target in targets:
                mps = cmds.listConnections(target, type="motionPath") or []
                connections.extend(mps)
        
        for mp in connections:
            try:
                cmds.keyframe(mp + ".uValue", edit=True, relative=True, valueChange=offset)
            except:
                pass
    
    cmds.inViewMessage(msg="Offset applied: {}".format(offset), pos="midCenter", fade=True)


def apply_speed_multiplier(speed):
    """Apply speed multiplier to path animation"""
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    for obj in sel:
        connections = cmds.listConnections(obj, type="motionPath") or []
        constraints = cmds.listRelatives(obj, type="parentConstraint") or []
        
        for con in constraints:
            targets = cmds.parentConstraint(con, query=True, targetList=True) or []
            for target in targets:
                mps = cmds.listConnections(target, type="motionPath") or []
                connections.extend(mps)
        
        for mp in connections:
            try:
                cmds.scaleKey(mp + ".uValue", valueScale=speed, valuePivot=0)
            except:
                pass
    
    cmds.inViewMessage(msg="Speed multiplier applied: {}x".format(speed), pos="midCenter", fade=True)


def reverse_path_animation():
    """Reverse path animation"""
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    for obj in sel:
        connections = cmds.listConnections(obj, type="motionPath") or []
        
        for mp in connections:
            try:
                # Get keyframes
                keys = cmds.keyframe(mp + ".uValue", query=True, valueChange=True) or []
                times = cmds.keyframe(mp + ".uValue", query=True, timeChange=True) or []
                
                if keys and times:
                    max_val = max(keys)
                    # Reverse values
                    cmds.cutKey(mp + ".uValue", clear=True)
                    for t, v in zip(times, keys):
                        cmds.setKeyframe(mp + ".uValue", time=t, value=max_val - v)
            except:
                pass
    
    cmds.inViewMessage(msg="Path animation reversed!", pos="midCenter", fade=True)


def delete_curvemorph_system():
    """Delete entire CurveMorph system"""
    
    # Find all CMP objects
    to_delete = []
    all_transforms = cmds.ls(type="transform")
    
    for t in all_transforms:
        if PREFIX in t or "path_master" in t.lower():
            to_delete.append(t)
    
    # Delete clusters
    clusters = cmds.ls(type="cluster")
    for c in clusters:
        if PREFIX in c:
            try:
                cmds.delete(c)
            except:
                pass
    
    # Delete transforms
    for item in to_delete:
        if cmds.objExists(item):
            try:
                cmds.delete(item)
            except:
                pass
    
    cmds.inViewMessage(msg="CurveMorph system deleted!", pos="midCenter", fade=True)


def clean_scene():
    """Clean all CMP nodes from scene"""
    
    deleted_count = 0
    
    # Delete all CMP prefixed nodes
    all_nodes = cmds.ls("CMP_*", "*_CMP*")
    
    for node in all_nodes:
        if cmds.objExists(node):
            try:
                cmds.delete(node)
                deleted_count += 1
            except:
                pass
    
    # Delete clusters that were created by this tool
    clusters = cmds.ls(type="cluster")
    for c in clusters:
        if not cmds.objExists(c):
            continue
        try:
            connections = cmds.listConnections(c, type="transform")
            if connections:
                for conn in connections:
                    if conn and PREFIX in conn:
                        cmds.delete(c)
                        deleted_count += 1
                        break
        except:
            pass
    
    # Also clean up any plusMinusAverage, decomposeMatrix nodes from incline controls
    for node_type in ["plusMinusAverage", "decomposeMatrix"]:
        nodes = cmds.ls(PREFIX + "*", type=node_type)
        for node in nodes:
            if cmds.objExists(node):
                try:
                    cmds.delete(node)
                    deleted_count += 1
                except:
                    pass
    
    cmds.inViewMessage(msg="Scene cleaned! {} nodes deleted.".format(deleted_count), pos="midCenter", fade=True)


def load_plugin(plugin_name):
    """Load Maya plugin"""
    try:
        if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
            cmds.loadPlugin(plugin_name, quiet=True)
    except:
        pass


# ============================================================================
# DATA PERSISTENCE SYSTEM - Scene-stored data using network nodes
# ============================================================================

def get_data_node():
    """Get or create the CurveMorph data network node"""
    node_name = PREFIX + "data_node"
    if not cmds.objExists(node_name):
        current_sel = cmds.ls(selection=True)
        node_name = cmds.createNode("network", name=node_name)
        # Add storage attributes
        cmds.addAttr(node_name, longName="connectedObjects", dataType="string")
        cmds.addAttr(node_name, longName="pathCurve", dataType="string")
        cmds.addAttr(node_name, longName="masterControl", dataType="string")
        cmds.addAttr(node_name, longName="followerObjects", dataType="string")
        cmds.addAttr(node_name, longName="backupLocators", dataType="string")
        if current_sel:
            cmds.select(current_sel, replace=True)
        else:
            cmds.select(clear=True)
    return node_name


def save_scene_data(key, data):
    """Save data to the scene network node"""
    node = get_data_node()
    attr_name = "{}.{}".format(node, key)
    
    if not cmds.attributeQuery(key, node=node, exists=True):
        cmds.addAttr(node, longName=key, dataType="string")
    
    data_json = json.dumps(data) if data else ""
    cmds.setAttr(attr_name, data_json, type="string")


def load_scene_data(key, default=None):
    """Load data from the scene network node"""
    node = get_data_node()
    attr_name = "{}.{}".format(node, key)
    
    if cmds.attributeQuery(key, node=node, exists=True):
        try:
            raw_data = cmds.getAttr(attr_name)
            if raw_data and raw_data.strip():
                return json.loads(raw_data)
        except:
            pass
    return default if default is not None else []


def clear_scene_data():
    """Clear all scene data"""
    node_name = PREFIX + "data_node"
    if cmds.objExists(node_name):
        cmds.delete(node_name)


# ============================================================================
# SMART CONSTRAINTS - Auto-detect and skip locked attributes
# ============================================================================

def get_unlocked_channels(obj, channel_type="translate"):
    """Get list of unlocked channels for an object"""
    channels = []
    axis_map = {"translate": ["tx", "ty", "tz"], "rotate": ["rx", "ry", "rz"]}
    
    for attr in axis_map.get(channel_type, []):
        full_attr = "{}.{}".format(obj, attr)
        if cmds.objExists(full_attr):
            if not cmds.getAttr(full_attr, lock=True):
                # Check if keyable or at least settable
                try:
                    keyable_attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
                    if attr in keyable_attrs or attr.replace("t", "translate").replace("r", "rotate") in keyable_attrs:
                        channels.append(attr[-1])  # x, y, or z
                except:
                    channels.append(attr[-1])
    return channels


def smart_parent_constraint(driver, driven, maintain_offset=True):
    """Create parent constraint, auto-skipping locked channels"""
    trans_channels = get_unlocked_channels(driven, "translate")
    rot_channels = get_unlocked_channels(driven, "rotate")
    
    skip_trans = [a for a in ["x", "y", "z"] if a not in trans_channels]
    skip_rot = [a for a in ["x", "y", "z"] if a not in rot_channels]
    
    if not trans_channels and not rot_channels:
        cmds.warning("All channels locked on {}".format(driven))
        return None
    
    try:
        if skip_trans and skip_rot:
            return cmds.parentConstraint(driver, driven, maintainOffset=maintain_offset,
                                         skipTranslate=skip_trans, skipRotate=skip_rot)[0]
        elif skip_trans:
            return cmds.parentConstraint(driver, driven, maintainOffset=maintain_offset,
                                         skipTranslate=skip_trans)[0]
        elif skip_rot:
            return cmds.parentConstraint(driver, driven, maintainOffset=maintain_offset,
                                         skipRotate=skip_rot)[0]
        else:
            return cmds.parentConstraint(driver, driven, maintainOffset=maintain_offset)[0]
    except Exception as e:
        cmds.warning("Constraint failed: {}".format(str(e)))
        return None


def smart_point_constraint(driver, driven, maintain_offset=True):
    """Create point constraint, auto-skipping locked channels"""
    channels = get_unlocked_channels(driven, "translate")
    skip = [a for a in ["x", "y", "z"] if a not in channels]
    
    if not channels:
        cmds.warning("All translate channels locked on {}".format(driven))
        return None
    
    try:
        if skip:
            return cmds.pointConstraint(driver, driven, maintainOffset=maintain_offset, skip=skip)[0]
        return cmds.pointConstraint(driver, driven, maintainOffset=maintain_offset)[0]
    except Exception as e:
        cmds.warning("Point constraint failed: {}".format(str(e)))
        return None


def smart_orient_constraint(driver, driven, maintain_offset=True):
    """Create orient constraint, auto-skipping locked channels"""
    channels = get_unlocked_channels(driven, "rotate")
    skip = [a for a in ["x", "y", "z"] if a not in channels]
    
    if not channels:
        cmds.warning("All rotate channels locked on {}".format(driven))
        return None
    
    try:
        if skip:
            return cmds.orientConstraint(driver, driven, maintainOffset=maintain_offset, skip=skip)[0]
        return cmds.orientConstraint(driver, driven, maintainOffset=maintain_offset)[0]
    except Exception as e:
        cmds.warning("Orient constraint failed: {}".format(str(e)))
        return None


def apply_smart_constraint(constraint_type):
    """Apply smart constraint from UI - source then target selection"""
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning("Select driver first, then driven object!")
        return
    
    driver = sel[0]
    driven_objects = sel[1:]
    
    for driven in driven_objects:
        if constraint_type == "parent":
            result = smart_parent_constraint(driver, driven, maintain_offset=True)
        elif constraint_type == "point":
            result = smart_point_constraint(driver, driven, maintain_offset=True)
        elif constraint_type == "orient":
            result = smart_orient_constraint(driver, driven, maintain_offset=True)
        else:
            result = None
        
        if result:
            cmds.inViewMessage(msg="Smart {} constraint created!".format(constraint_type), 
                             pos="midCenter", fade=True)


# ============================================================================
# BACKUP & RECOVERY SYSTEM
# ============================================================================

def get_backup_group():
    """Get or create backup locators group"""
    grp_name = PREFIX + "backup_grp"
    if not cmds.objExists(grp_name):
        grp_name = cmds.group(empty=True, name=grp_name)
        cmds.setAttr("{}.visibility".format(grp_name), 0)
        # Lock all transforms
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            try:
                cmds.setAttr("{}.{}".format(grp_name, attr), lock=True)
            except:
                pass
    return grp_name


def create_backup_locator(obj):
    """Create a backup locator with baked animation from object"""
    if not cmds.objExists(obj):
        cmds.warning("Object {} does not exist".format(obj))
        return None
    
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    
    # Create locator
    short_name = obj.split("|")[-1].split(":")[-1]
    loc_name = PREFIX + short_name + "_backup"
    
    if cmds.objExists(loc_name):
        cmds.delete(loc_name)
    
    loc = cmds.spaceLocator(name=loc_name)[0]
    
    # Constrain and bake
    constraint = cmds.parentConstraint(obj, loc, maintainOffset=False)[0]
    
    cmds.bakeResults(loc, time=(start, end), simulation=True, sampleBy=1,
                     disableImplicitControl=True, preserveOutsideKeys=True)
    
    cmds.delete(constraint)
    
    # Parent to backup group and lock
    backup_grp = get_backup_group()
    cmds.parent(loc, backup_grp)
    
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
        try:
            cmds.setAttr("{}.{}".format(loc, attr), lock=True)
        except:
            pass
    
    # Store in scene data
    backups = load_scene_data("backupLocators", [])
    loc_full = cmds.ls(loc, long=True)[0]
    if loc_full not in backups:
        backups.append(loc_full)
        save_scene_data("backupLocators", backups)
    
    return loc


def create_backup_for_selection():
    """Create backup locators for selected objects"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select objects to backup!")
        return
    
    cmds.waitCursor(state=True)
    cmds.refresh(suspend=True)
    
    try:
        created = []
        for obj in sel:
            loc = create_backup_locator(obj)
            if loc:
                created.append(loc)
        
        if created:
            cmds.inViewMessage(msg="Created {} backup locators".format(len(created)), 
                             pos="midCenter", fade=True)
    finally:
        cmds.refresh(suspend=False)
        cmds.waitCursor(state=False)


def restore_from_backup():
    """Restore animation from backup locators"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select objects to restore!")
        return
    
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    
    restored = 0
    for obj in sel:
        short_name = obj.split("|")[-1].split(":")[-1]
        backup_name = PREFIX + short_name + "_backup"
        
        if cmds.objExists(backup_name):
            # Unlock backup for constraining
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.setAttr("{}.{}".format(backup_name, attr), lock=False)
                except:
                    pass
            
            # Constrain object to backup
            constraint = cmds.parentConstraint(backup_name, obj, maintainOffset=False)[0]
            cmds.bakeResults(obj, time=(start, end), simulation=True, sampleBy=1)
            cmds.delete(constraint)
            
            # Re-lock backup
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.setAttr("{}.{}".format(backup_name, attr), lock=True)
                except:
                    pass
            
            restored += 1
    
    cmds.inViewMessage(msg="Restored {} objects from backup".format(restored), 
                      pos="midCenter", fade=True)


def clear_all_backups():
    """Clear all backup locators"""
    backup_grp = PREFIX + "backup_grp"
    if cmds.objExists(backup_grp):
        cmds.delete(backup_grp)
    save_scene_data("backupLocators", [])
    cmds.inViewMessage(msg="All backups cleared!", pos="midCenter", fade=True)


# ============================================================================
# CURVE MORPHING SYSTEM
# ============================================================================

def get_curve_cv_count(curve):
    """Get CV count for a curve"""
    shapes = cmds.listRelatives(curve, shapes=True, type="nurbsCurve")
    if not shapes:
        return None
    spans = cmds.getAttr("{}.spans".format(curve))
    degree = cmds.getAttr("{}.degree".format(curve))
    return spans + degree


def get_curve_length(curve):
    """Get arc length of curve"""
    shapes = cmds.listRelatives(curve, shapes=True, type="nurbsCurve")
    if not shapes:
        return None
    
    # Use arclen command
    try:
        return cmds.arclen(curve)
    except:
        return None


def sample_curve_position(curve, parameter):
    """Sample position on curve at normalized parameter (0-1)"""
    shapes = cmds.listRelatives(curve, shapes=True, type="nurbsCurve")
    if not shapes:
        return None
    
    min_param = cmds.getAttr("{}.minValue".format(curve))
    max_param = cmds.getAttr("{}.maxValue".format(curve))
    actual_param = min_param + (max_param - min_param) * parameter
    
    # Create temp pointOnCurveInfo
    poc = cmds.createNode("pointOnCurveInfo")
    cmds.connectAttr("{}.worldSpace[0]".format(shapes[0]), "{}.inputCurve".format(poc))
    cmds.setAttr("{}.parameter".format(poc), actual_param)
    
    pos = cmds.getAttr("{}.position".format(poc))[0]
    cmds.delete(poc)
    
    return pos


def morph_curve_basic():
    """Morph base curve (first selected) to match target curve (second selected)"""
    sel = cmds.ls(selection=True)
    if len(sel) != 2:
        cmds.warning("Select base curve first, then target curve!")
        return
    
    base, target = sel[0], sel[1]
    
    # Validate curves
    base_shapes = cmds.listRelatives(base, shapes=True, type="nurbsCurve")
    target_shapes = cmds.listRelatives(target, shapes=True, type="nurbsCurve")
    
    if not base_shapes or not target_shapes:
        cmds.warning("Both selections must be NURBS curves!")
        return
    
    # Match CV count
    target_cvs = get_curve_cv_count(target)
    base_cvs = get_curve_cv_count(base)
    
    if target_cvs and base_cvs and target_cvs != base_cvs:
        # Rebuild base to match target CV count
        cmds.rebuildCurve(base, constructionHistory=False, replaceOriginal=True,
                         spans=target_cvs - 3, degree=3, keepRange=1, keepEndPoints=True)
    
    # Create blendShape
    blend = cmds.blendShape(target, base, origin="world")[0]
    
    # Set weight to 1
    cmds.setAttr("{}.w[0]".format(blend), 1.0)
    
    cmds.inViewMessage(msg="Curve morphing created! Adjust blendShape weight.", 
                      pos="midCenter", fade=True)
    cmds.select(base)
    
    return blend


def morph_curve_preserve_length():
    """Morph curve while preserving original length using joint chain"""
    sel = cmds.ls(selection=True)
    if len(sel) != 2:
        cmds.warning("Select base curve first, then target curve!")
        return
    
    base, target = sel[0], sel[1]
    
    # Validate curves
    base_shapes = cmds.listRelatives(base, shapes=True, type="nurbsCurve")
    target_shapes = cmds.listRelatives(target, shapes=True, type="nurbsCurve")
    
    if not base_shapes or not target_shapes:
        cmds.warning("Both selections must be NURBS curves!")
        return
    
    base_length = get_curve_length(base)
    base_cvs = get_curve_cv_count(base)
    
    if not base_length or not base_cvs:
        cmds.warning("Could not get curve properties!")
        return
    
    # Store original distances between CV points
    distances = []
    for i in range(base_cvs - 1):
        pos1 = cmds.pointPosition("{}.cv[{}]".format(base, i), world=True)
        pos2 = cmds.pointPosition("{}.cv[{}]".format(base, i+1), world=True)
        dist = math.sqrt(sum((a-b)**2 for a, b in zip(pos1, pos2)))
        distances.append(dist)
    
    # Store distances on base curve
    for i, dist in enumerate(distances):
        attr_name = "storedDist_{}".format(i)
        if not cmds.attributeQuery(attr_name, node=base, exists=True):
            cmds.addAttr(base, longName=attr_name, attributeType="double", defaultValue=dist)
        else:
            cmds.setAttr("{}.{}".format(base, attr_name), dist)
    
    # Create joint chain for length preservation
    joints = []
    grp = cmds.group(empty=True, name=PREFIX + "morph_joints_grp")
    
    cmds.select(clear=True)
    for i in range(base_cvs):
        param = float(i) / (base_cvs - 1) if base_cvs > 1 else 0
        pos = sample_curve_position(base, param)
        if pos:
            jnt = cmds.joint(name=PREFIX + "cv_{}_joint".format(i), position=pos)
            joints.append(jnt)
    
    if joints:
        cmds.parent(joints[0], grp)
    
    # Create clusters on base curve CVs and parent to joints
    for i, jnt in enumerate(joints):
        cv = "{}.cv[{}]".format(base, i)
        cluster = cmds.cluster(cv, name=PREFIX + "morph_cluster_{}".format(i))
        cmds.parent(cluster[1], jnt)
        cmds.setAttr("{}.visibility".format(cluster[1]), 0)
    
    # Position joints on target curve maintaining distances
    target_length = get_curve_length(target)
    if target_length:
        current_param = 0.0
        target_pos = sample_curve_position(target, 0)
        if target_pos and joints:
            cmds.xform(joints[0], worldSpace=True, translation=target_pos)
        
        for i in range(1, len(joints)):
            if i-1 < len(distances):
                # Find parameter at stored distance
                target_dist = distances[i-1]
                # Simple linear approximation
                param_increment = target_dist / target_length
                current_param = min(1.0, current_param + param_increment)
                
                next_pos = sample_curve_position(target, current_param)
                if next_pos:
                    cmds.xform(joints[i], worldSpace=True, translation=next_pos)
    
    cmds.select(joints)
    cmds.inViewMessage(msg="Length-preserving morph created! Select joints to adjust.", 
                      pos="midCenter", fade=True)
    
    return grp


# ============================================================================
# CURVE SLIDING SYSTEM
# ============================================================================

def get_slide_offset(curve):
    """Get stored slide offset for curve"""
    if not cmds.attributeQuery("slideOffset", node=curve, exists=True):
        cmds.addAttr(curve, longName="slideOffset", attributeType="double", defaultValue=0.0)
        return 0.0
    return cmds.getAttr("{}.slideOffset".format(curve))


def set_slide_offset(curve, offset):
    """Set slide offset for curve"""
    if not cmds.attributeQuery("slideOffset", node=curve, exists=True):
        cmds.addAttr(curve, longName="slideOffset", attributeType="double", defaultValue=offset)
    else:
        cmds.setAttr("{}.slideOffset".format(curve), offset)


def slide_curve(direction=1, amount=0.05):
    """Slide curve along target curve
    
    Args:
        direction: 1 for forward, -1 for backward
        amount: slide increment (0-1 normalized)
    """
    sel = cmds.ls(selection=True)
    if len(sel) != 2:
        cmds.warning("Select base curve, then target curve!")
        return False
    
    base, target = sel[0], sel[1]
    
    # Validate curves
    base_shapes = cmds.listRelatives(base, shapes=True, type="nurbsCurve")
    target_shapes = cmds.listRelatives(target, shapes=True, type="nurbsCurve")
    
    if not base_shapes or not target_shapes:
        cmds.warning("Both selections must be NURBS curves!")
        return False
    
    # Find joints for this curve
    base_cvs = get_curve_cv_count(base)
    joints = []
    for i in range(base_cvs if base_cvs else 20):
        jnt_name = PREFIX + "cv_{}_joint".format(i)
        if cmds.objExists(jnt_name):
            joints.append(jnt_name)
        else:
            break
    
    if not joints:
        cmds.warning("No morph joints found. Run 'Morph (Keep Length)' first!")
        return False
    
    # Get stored distances
    distances = []
    for i in range(20):
        attr_name = "storedDist_{}".format(i)
        if cmds.attributeQuery(attr_name, node=base, exists=True):
            distances.append(cmds.getAttr("{}.{}".format(base, attr_name)))
        else:
            break
    
    if not distances:
        cmds.warning("No stored distances found!")
        return False
    
    # Calculate new offset
    current_offset = get_slide_offset(base)
    new_offset = current_offset + (direction * amount)
    
    # Clamp offset
    new_offset = max(0.0, min(1.0, new_offset))
    
    # Check if slide is possible
    target_length = get_curve_length(target)
    total_length = sum(distances)
    required_ratio = total_length / target_length if target_length else 1.0
    
    if new_offset + required_ratio > 1.0 and direction > 0:
        cmds.warning("Cannot slide further - end of curve reached!")
        return False
    
    if new_offset < 0 and direction < 0:
        cmds.warning("Cannot slide further - start of curve reached!")
        return False
    
    # Move joints
    current_param = new_offset
    first_pos = sample_curve_position(target, current_param)
    if first_pos and joints:
        cmds.xform(joints[0], worldSpace=True, translation=first_pos)
    
    for i in range(1, len(joints)):
        if i-1 < len(distances):
            target_dist = distances[i-1]
            param_increment = target_dist / target_length if target_length else 0.05
            current_param = min(1.0, current_param + param_increment)
            
            next_pos = sample_curve_position(target, current_param)
            if next_pos:
                cmds.xform(joints[i], worldSpace=True, translation=next_pos)
    
    set_slide_offset(base, new_offset)
    cmds.inViewMessage(msg="Slid {} to offset {:.2f}".format(
        "forward" if direction > 0 else "backward", new_offset), 
        pos="midCenter", fade=True)
    
    cmds.select(sel)
    return True


def slide_curve_forward():
    """Slide curve forward along target"""
    amount = 0.05
    try:
        amount = cmds.floatField("slide_amount_field", query=True, value=True)
    except:
        pass
    return slide_curve(direction=1, amount=amount)


def slide_curve_backward():
    """Slide curve backward along target"""
    amount = 0.05
    try:
        amount = cmds.floatField("slide_amount_field", query=True, value=True)
    except:
        pass
    return slide_curve(direction=-1, amount=amount)


# ============================================================================
# LOCATOR TOOLS
# ============================================================================

def scale_locators(factor):
    """Scale selected locators by factor"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select locators!")
        return
    
    for obj in sel:
        shapes = cmds.listRelatives(obj, shapes=True, type="locator")
        if shapes:
            for shape in shapes:
                for axis in ["X", "Y", "Z"]:
                    attr = "{}.localScale{}".format(shape, axis)
                    current = cmds.getAttr(attr)
                    cmds.setAttr(attr, current * factor)
    
    cmds.inViewMessage(msg="Locators scaled!", pos="midCenter", fade=True)


def make_locators_bigger():
    """Make selected locators bigger"""
    scale_locators(1.5)


def make_locators_smaller():
    """Make selected locators smaller"""
    scale_locators(0.67)


# Color cycle for locators
LOCATOR_COLORS = [17, 18, 13, 14, 6, 9, 12, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
_color_index = [0]  # Mutable to track state


def cycle_locator_color():
    """Cycle through colors for selected locators"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select locators!")
        return
    
    color = LOCATOR_COLORS[_color_index[0] % len(LOCATOR_COLORS)]
    _color_index[0] += 1
    
    for obj in sel:
        shapes = cmds.listRelatives(obj, shapes=True)
        if shapes:
            for shape in shapes:
                cmds.setAttr("{}.overrideEnabled".format(shape), 1)
                cmds.setAttr("{}.overrideColor".format(shape), color)
        else:
            cmds.setAttr("{}.overrideEnabled".format(obj), 1)
            cmds.setAttr("{}.overrideColor".format(obj), color)
    
    cmds.inViewMessage(msg="Color changed!", pos="midCenter", fade=True)


# ============================================================================
# MASTER FOLLOW SYSTEM
# ============================================================================

def create_master_follow_system():
    """Create a master follow system for selected objects"""
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning("Select master control first, then follower objects!")
        return
    
    master = sel[0]
    followers = sel[1:]
    
    # Store in scene data
    save_scene_data("masterControl", master)
    save_scene_data("followerObjects", followers)
    
    # Create animation layer for master follow
    layer_name = PREFIX + "master_follow_layer"
    if cmds.objExists(layer_name):
        cmds.delete(layer_name)
    
    # Create the layer
    layer = cmds.animLayer(layer_name)
    
    # Add followers to the layer
    for follower in followers:
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            full_attr = "{}.{}".format(follower, attr)
            if cmds.objExists(full_attr) and not cmds.getAttr(full_attr, lock=True):
                try:
                    cmds.animLayer(layer, edit=True, attribute=full_attr)
                except:
                    pass
    
    # Create locator at master position
    master_loc = cmds.spaceLocator(name=PREFIX + "master_follow_loc")[0]
    pos = cmds.xform(master, query=True, worldSpace=True, translation=True)
    rot = cmds.xform(master, query=True, worldSpace=True, rotation=True)
    cmds.xform(master_loc, worldSpace=True, translation=pos, rotation=rot)
    
    # Constrain locator to master
    cmds.parentConstraint(master, master_loc, maintainOffset=True)
    
    # Create offset controls for each follower
    offsets = []
    for follower in followers:
        offset_grp = cmds.group(empty=True, name=follower.split("|")[-1] + "_follow_offset")
        fpos = cmds.xform(follower, query=True, worldSpace=True, translation=True)
        frot = cmds.xform(follower, query=True, worldSpace=True, rotation=True)
        cmds.xform(offset_grp, worldSpace=True, translation=fpos, rotation=frot)
        
        # Constrain to master locator
        cmds.parentConstraint(master_loc, offset_grp, maintainOffset=True)
        
        # Add influence attribute
        cmds.addAttr(offset_grp, longName="followInfluence", attributeType="double", 
                    defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
        
        offsets.append(offset_grp)
    
    # Group everything
    grp = cmds.group([master_loc] + offsets, name=PREFIX + "master_follow_grp")
    
    cmds.select(grp)
    cmds.inViewMessage(msg="Master follow system created! Adjust follow_offset groups.", 
                      pos="midCenter", fade=True)
    
    return grp


def remove_master_follow_system():
    """Remove the master follow system"""
    grp = PREFIX + "master_follow_grp"
    layer = PREFIX + "master_follow_layer"
    
    if cmds.objExists(grp):
        cmds.delete(grp)
    if cmds.objExists(layer):
        cmds.delete(layer)
    
    save_scene_data("masterControl", "")
    save_scene_data("followerObjects", [])
    
    cmds.inViewMessage(msg="Master follow system removed!", pos="midCenter", fade=True)


# ============================================================================
# ADVANCED CV CONTROLS
# ============================================================================

def add_cv_controls_with_count(cv_count=10):
    """Add CV controls with specified count, rebuilding curve if needed"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select a curve!")
        return
    
    curve = sel[0]
    shapes = cmds.listRelatives(curve, shapes=True, type="nurbsCurve")
    if not shapes:
        cmds.warning("Selection is not a NURBS curve!")
        return
    
    # Rebuild curve to desired CV count
    cmds.rebuildCurve(curve, constructionHistory=False, replaceOriginal=True,
                     spans=cv_count - 3, degree=3, keepRange=1, keepEndPoints=True)
    
    # Now create CV controls using existing function
    create_cv_controls(curve)
    
    cmds.inViewMessage(msg="Created {} CV controls".format(cv_count), pos="midCenter", fade=True)


# ============================================================================
# ATTACH TO SURFACE SYSTEM
# ============================================================================

def attach_objects_to_surface():
    """Project curve CV controls onto a surface - snaps them to the surface perfectly.
    
    Selection order:
    1. Select the curve (or CV control locators) FIRST
    2. Select the surface/mesh/primitive LAST
    
    The CV locators will snap to the closest point on the surface.
    Works even when curve length changes.
    """
    sel = cmds.ls(orderedSelection=True, long=True)
    if len(sel) < 2:
        cmds.warning("Select curve/objects first, then surface last (at least 2 items)")
        return
    
    surface = sel[-1]
    sources = sel[:-1]
    
    surface_shapes = cmds.listRelatives(surface, shapes=True, noIntermediate=True)
    if not surface_shapes:
        cmds.warning("Last selection must be a mesh or NURBS surface!")
        return
    
    surface_shape = surface_shapes[0]
    surface_type = cmds.nodeType(surface_shape)
    if surface_type not in ["mesh", "nurbsSurface"]:
        cmds.warning("Last selection must be a mesh or NURBS surface!")
        return
    
    # Collect all objects to project
    objects_to_project = []
    
    for src in sources:
        shapes = cmds.listRelatives(src, shapes=True, noIntermediate=True, fullPath=True) or []
        
        if shapes:
            shape_type = cmds.nodeType(shapes[0])
            
            if shape_type == "locator":
                objects_to_project.append(src)
            
            elif shape_type == "nurbsCurve":
                if cmds.attributeQuery("cvControlGroup", node=src, exists=True):
                    grp_name = cmds.getAttr(src + ".cvControlGroup")
                    if grp_name and cmds.objExists(grp_name):
                        children = cmds.listRelatives(grp_name, children=True, type="transform") or []
                        for child in children:
                            child_shapes = cmds.listRelatives(child, shapes=True)
                            if child_shapes and cmds.nodeType(child_shapes[0]) == "locator":
                                objects_to_project.append(child)
                
                if not objects_to_project:
                    cmds.warning("Curve has no CV controls! Use 'Create CV Controls' first.")
                    return
            else:
                objects_to_project.append(src)
        else:
            objects_to_project.append(src)
    
    if not objects_to_project:
        cmds.warning("No valid objects found to project!")
        return
    
    cmds.undoInfo(openChunk=True)
    
    try:
        projected_count = 0
        
        # Create a clean duplicate of the surface for constraining
        temp_surface = cmds.duplicate(surface, returnRootsOnly=True)[0]
        temp_surface = cmds.rename(temp_surface, PREFIX + "projection_surface")
        cmds.makeIdentity(temp_surface, apply=True, translate=True, rotate=True, scale=True)
        cmds.delete(temp_surface, constructionHistory=True)
        
        for obj in objects_to_project:
            if not cmds.objExists(obj):
                continue
            
            try:
                # Use geometry constraint - Maya's native way to snap to surface
                # This is the most reliable method
                constraint = cmds.geometryConstraint(temp_surface, obj, weight=1.0)
                
                if constraint:
                    # Force evaluation
                    cmds.dgeval(obj)
                    cmds.refresh(force=True)
                    
                    # Get the new position after constraint
                    new_pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                    
                    # Delete constraint
                    cmds.delete(constraint)
                    
                    # Set the position explicitly (constraint might not have applied)
                    cmds.xform(obj, worldSpace=True, translation=new_pos)
                    
                    projected_count += 1
            except Exception as e:
                cmds.warning("Could not project {}: {}".format(obj, str(e)))
                continue
        
        # Delete temp surface
        if cmds.objExists(temp_surface):
            cmds.delete(temp_surface)
        
        if projected_count > 0:
            cmds.inViewMessage(msg="Projected {} controls onto surface!".format(projected_count), 
                             pos="midCenter", fade=True)
        else:
            cmds.warning("Failed to project any objects!")
            
    except Exception as e:
        cmds.warning("Project to surface failed: {}".format(str(e)))
        # Cleanup
        if cmds.objExists(PREFIX + "projection_surface"):
            try:
                cmds.delete(PREFIX + "projection_surface")
            except:
                pass
    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.select(sources)


def detach_objects_from_surface():
    """Reset - restore curve from snapshot if available, or clean up any leftover constraints"""
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Select a curve to reset!")
        return
    
    cmds.undoInfo(openChunk=True)
    
    try:
        reset_count = 0
        
        for obj in sel:
            if not cmds.objExists(obj):
                continue
            
            shapes = cmds.listRelatives(obj, shapes=True, noIntermediate=True) or []
            
            # If it's a curve with a snapshot, restore it
            if shapes and cmds.nodeType(shapes[0]) == "nurbsCurve":
                if cmds.attributeQuery("snapshotData", node=obj, exists=True):
                    snapshot_data = cmds.getAttr(obj + ".snapshotData")
                    if snapshot_data and snapshot_data.strip():
                        # Restore from snapshot
                        reset_to_reflection(obj)
                        reset_count += 1
                        continue
            
            # Clean up any leftover geometry constraints
            objects_to_check = [obj]
            
            if shapes and cmds.nodeType(shapes[0]) == "nurbsCurve":
                if cmds.attributeQuery("cvControlGroup", node=obj, exists=True):
                    grp_name = cmds.getAttr(obj + ".cvControlGroup")
                    if grp_name and cmds.objExists(grp_name):
                        children = cmds.listRelatives(grp_name, children=True, type="transform") or []
                        objects_to_check.extend(children)
            
            for check_obj in objects_to_check:
                if not cmds.objExists(check_obj):
                    continue
                
                try:
                    constraints = cmds.listRelatives(check_obj, type="geometryConstraint") or []
                    connections = cmds.listConnections(check_obj, type="geometryConstraint") or []
                    constraints.extend(connections)
                    constraints = list(set(constraints))
                    
                    if constraints:
                        for c in constraints:
                            try:
                                cmds.delete(c)
                            except:
                                pass
                        reset_count += 1
                except:
                    pass
        
        # Clean up temp surfaces
        temp_surfaces = cmds.ls(PREFIX + "temp_surface*", type="transform") or []
        for temp in temp_surfaces:
            try:
                cmds.delete(temp)
            except:
                pass
        
        if reset_count > 0:
            cmds.inViewMessage(msg="Reset {} items!".format(reset_count), pos="midCenter", fade=True)
        else:
            cmds.inViewMessage(msg="Nothing to reset (save a snapshot first)", pos="midCenter", fade=True)
            
    except Exception as e:
        cmds.warning("Reset failed: {}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)


# ============================================================================
# ANIMATION PRESETS SYSTEM - Controller-Based Presets
# ============================================================================

# Global preset storage
_animation_presets = {}  # {controller_key: {preset_name: preset_data}}
_preset_list_ui = None
_current_controller_key = None
_selection_callback_id = None


def get_presets_node():
    """Get or create the animation presets network node"""
    node_name = PREFIX + "presets_node"
    if not cmds.objExists(node_name):
        current_sel = cmds.ls(selection=True)
        node_name = cmds.createNode("network", name=node_name)
        cmds.addAttr(node_name, longName="presetsData", dataType="string")
        cmds.setAttr("{}.presetsData".format(node_name), "{}", type="string")
        if current_sel:
            cmds.select(current_sel, replace=True)
        else:
            cmds.select(clear=True)
    return node_name


def load_presets_from_scene():
    """Load all presets from scene into memory"""
    global _animation_presets
    node = get_presets_node()
    try:
        data = cmds.getAttr("{}.presetsData".format(node))
        if data and data.strip():
            try:
                loaded = json.loads(data)
                # Validate structure
                if isinstance(loaded, dict):
                    _animation_presets = loaded
                else:
                    _animation_presets = {}
            except (json.JSONDecodeError, ValueError) as e:
                cmds.warning("Preset data corrupted, resetting: {}".format(str(e)))
                _animation_presets = {}
        else:
            _animation_presets = {}
    except Exception as e:
        cmds.warning("Failed to load presets: {}".format(str(e)))
        _animation_presets = {}
    return _animation_presets


def save_presets_to_scene():
    """Save all presets from memory to scene"""
    global _animation_presets
    try:
        node = get_presets_node()
        data = json.dumps(_animation_presets)
        cmds.setAttr("{}.presetsData".format(node), data, type="string")
    except Exception as e:
        cmds.warning("Failed to save presets: {}".format(str(e)))


def generate_controller_key(objects):
    """Generate a unique key for a set of controllers
    
    The key is based on the sorted short names of all controllers,
    ensuring the same controllers always produce the same key.
    """
    if not objects:
        return None
    
    # Get short names (without namespace and path)
    short_names = []
    for obj in objects:
        short = obj.split("|")[-1]  # Remove path
        if ":" in short:
            short = short.split(":")[-1]  # Remove namespace
        short_names.append(short)
    
    # Sort and join to create consistent key
    short_names.sort()
    return "|".join(short_names)


def get_current_controller_key():
    """Get the controller key for current selection"""
    sel = cmds.ls(selection=True)
    if not sel:
        return None
    return generate_controller_key(sel)


def get_presets_for_controllers(controller_key):
    """Get all presets saved for a specific controller set"""
    load_presets_from_scene()
    
    if controller_key and controller_key in _animation_presets:
        return _animation_presets[controller_key]
    return {}


def get_preset_names_for_current_selection():
    """Get preset names for currently selected controllers"""
    controller_key = get_current_controller_key()
    if not controller_key:
        return []
    
    presets = get_presets_for_controllers(controller_key)
    return list(presets.keys())


def validate_selection_for_preset():
    """Validate current selection for saving preset"""
    sel = cmds.ls(selection=True)
    if not sel:
        return False, get_text("no_selection")
    
    # Filter out invalid objects
    valid_objects = []
    for obj in sel:
        if cmds.objExists(obj):
            valid_objects.append(obj)
    
    if not valid_objects:
        return False, "No valid objects in selection!"
    
    # Check if objects have animation
    has_anim = False
    for obj in valid_objects:
        try:
            # Check for keyframes on any transform attributes
            for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:
                full_attr = "{}.{}".format(obj, attr)
                if cmds.objExists(full_attr):
                    keys = cmds.keyframe(full_attr, query=True) or []
                    if keys:
                        has_anim = True
                        break
            if has_anim:
                break
        except:
            continue
    
    if not has_anim:
        return False, "Selected objects have no animation!"
    
    return True, valid_objects


def validate_frame_range(start, end):
    """Validate frame range"""
    try:
        start = float(start)
        end = float(end)
    except (TypeError, ValueError):
        return False, get_text("invalid_range") + " (invalid numbers)"
    
    if start is None or end is None:
        return False, get_text("invalid_range")
    if start >= end:
        return False, get_text("invalid_range") + " (start must be < end)"
    if end - start < 1:
        return False, get_text("invalid_range") + " (minimum 1 frame)"
    if start < 0 or end < 0:
        return False, get_text("invalid_range") + " (frames must be positive)"
    return True, None


def extract_animation_data(objects, start_frame, end_frame):
    """Extract animation data from objects within frame range"""
    anim_data = {
        "keyframes": {},
        "object_names": [],
        "full_names": [],  # Store full names for exact matching
        "frame_range": [start_frame, end_frame],
        "frame_count": int(end_frame - start_frame + 1),
        "created": cmds.date(format="DD/MM/YYYY HH:mm"),
        "attributes": ["tx", "ty", "tz", "rx", "ry", "rz"]
    }
    
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
    current_time = cmds.currentTime(query=True)
    
    try:
        for obj in objects:
            if not cmds.objExists(obj):
                continue
            
            short_name = obj.split("|")[-1]
            if ":" in short_name:
                short_name = short_name.split(":")[-1]
            
            anim_data["object_names"].append(short_name)
            anim_data["full_names"].append(obj)
            anim_data["keyframes"][short_name] = {}
            
            for attr in attrs:
                full_attr = "{}.{}".format(obj, attr)
                if not cmds.objExists(full_attr):
                    continue
                
                # Skip locked attributes
                try:
                    if cmds.getAttr(full_attr, lock=True):
                        continue
                except:
                    pass
                
                # Get keyframe data within range
                try:
                    keys = cmds.keyframe(full_attr, query=True, time=(start_frame, end_frame), 
                                        timeChange=True) or []
                    values = cmds.keyframe(full_attr, query=True, time=(start_frame, end_frame),
                                          valueChange=True) or []
                    
                    if keys and values and len(keys) == len(values):
                        # Normalize times relative to start
                        normalized = [(float(k - start_frame), float(v)) for k, v in zip(keys, values)]
                        anim_data["keyframes"][short_name][attr] = normalized
                    else:
                        # Sample the animation if no keyframes in range
                        sampled = []
                        for frame in range(int(start_frame), int(end_frame) + 1):
                            try:
                                cmds.currentTime(frame)
                                val = cmds.getAttr(full_attr)
                                sampled.append((float(frame - start_frame), float(val)))
                            except:
                                pass
                        if sampled:
                            anim_data["keyframes"][short_name][attr] = sampled
                except Exception as e:
                    # Skip this attribute if we can't read it
                    pass
    finally:
        # Always restore current time
        try:
            cmds.currentTime(current_time)
        except:
            pass
    
    return anim_data


def save_animation_preset(preset_name, start_frame, end_frame):
    """Save animation from selected objects as a controller-specific preset"""
    global _animation_presets
    
    # Validate
    valid, result = validate_selection_for_preset()
    if not valid:
        cmds.warning(result)
        return False
    
    objects = result
    
    valid, error = validate_frame_range(start_frame, end_frame)
    if not valid:
        cmds.warning(error)
        return False
    
    # Generate controller key
    controller_key = generate_controller_key(objects)
    if not controller_key:
        cmds.warning("Could not identify controllers!")
        return False
    
    # Load existing presets
    load_presets_from_scene()
    
    # Initialize controller group if needed
    if controller_key not in _animation_presets:
        _animation_presets[controller_key] = {}
    
    # Check if preset exists for this controller set
    if preset_name in _animation_presets[controller_key]:
        confirm = cmds.confirmDialog(
            title="Overwrite Preset",
            message=get_text("preset_exists"),
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if confirm != "Yes":
            return False
    
    cmds.waitCursor(state=True)
    try:
        # Extract animation data
        anim_data = extract_animation_data(objects, start_frame, end_frame)
        anim_data["controller_key"] = controller_key
        
        # Save to memory and scene
        _animation_presets[controller_key][preset_name] = anim_data
        save_presets_to_scene()
        
        cmds.inViewMessage(msg=get_text("preset_saved") + " '{}'".format(preset_name), 
                          pos="midCenter", fade=True)
        
        # Refresh UI list
        refresh_preset_list_ui()
        
        return True
    except Exception as e:
        cmds.warning("Failed to save preset: {}".format(str(e)))
        return False
    finally:
        cmds.waitCursor(state=False)


def apply_animation_preset(preset_name, target_start_frame, target_end_frame=None, blend_mode="replace"):
    """Apply a saved preset to the SAME controllers it was saved from
    
    Args:
        preset_name: Name of the preset to apply
        target_start_frame: Start frame to apply the animation
        target_end_frame: End frame (optional) - if provided, animation will be time-scaled to fit
        blend_mode: "replace", "additive", or "multiply"
    """
    
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning(get_text("no_selection"))
        return False
    
    controller_key = generate_controller_key(sel)
    if not controller_key:
        cmds.warning("Could not identify controllers!")
        return False
    
    load_presets_from_scene()
    
    # Check if preset exists for this controller set
    if controller_key not in _animation_presets:
        cmds.warning(get_text("preset_not_found") + " for these controllers")
        return False
    
    if preset_name not in _animation_presets[controller_key]:
        cmds.warning(get_text("preset_not_found"))
        return False
    
    preset = _animation_presets[controller_key][preset_name]
    
    # Validate target frame range
    if target_start_frame is None or target_start_frame < 0:
        cmds.warning("Invalid target start frame!")
        return False
    
    # Calculate time scaling factor
    preset_frame_count = preset.get("frame_count", 1)
    if preset_frame_count < 1:
        preset_frame_count = 1
    
    # If end frame provided, scale the animation
    time_scale = 1.0
    if target_end_frame is not None and target_end_frame > target_start_frame:
        target_duration = target_end_frame - target_start_frame
        time_scale = float(target_duration) / float(preset_frame_count - 1) if preset_frame_count > 1 else 1.0
    
    current_time = cmds.currentTime(query=True)
    cmds.waitCursor(state=True)
    cmds.undoInfo(openChunk=True)
    
    try:
        applied_count = 0
        failed_attrs = []
        
        for obj in sel:
            if not cmds.objExists(obj):
                continue
            
            short_name = obj.split("|")[-1]
            if ":" in short_name:
                short_name = short_name.split(":")[-1]
            
            # Find matching data - exact match required for same controllers
            if short_name not in preset["keyframes"]:
                continue
            
            obj_data = preset["keyframes"][short_name]
            
            # Apply keyframes
            for attr, keyframes in obj_data.items():
                if not keyframes:
                    continue
                
                full_attr = "{}.{}".format(obj, attr)
                if not cmds.objExists(full_attr):
                    continue
                
                # Check if locked
                try:
                    if cmds.getAttr(full_attr, lock=True):
                        continue
                except:
                    pass
                
                try:
                    for rel_frame, value in keyframes:
                        # Apply time scaling
                        scaled_frame = rel_frame * time_scale
                        actual_frame = target_start_frame + scaled_frame
                        
                        if blend_mode == "replace":
                            cmds.setKeyframe(obj, attribute=attr, time=actual_frame, value=float(value))
                        elif blend_mode == "additive":
                            cmds.currentTime(actual_frame)
                            try:
                                current = cmds.getAttr(full_attr)
                                cmds.setKeyframe(obj, attribute=attr, time=actual_frame, value=float(current + value))
                            except:
                                pass
                        elif blend_mode == "multiply":
                            cmds.currentTime(actual_frame)
                            try:
                                current = cmds.getAttr(full_attr)
                                cmds.setKeyframe(obj, attribute=attr, time=actual_frame, value=float(current * value))
                            except:
                                pass
                except Exception as e:
                    failed_attrs.append("{}.{}".format(short_name, attr))
                    continue
            
            applied_count += 1
        
        # Restore time
        try:
            cmds.currentTime(current_time)
        except:
            pass
        
        if applied_count > 0:
            if target_end_frame is not None and target_end_frame > target_start_frame:
                actual_end = int(target_end_frame)
            else:
                actual_end = int(target_start_frame + preset_frame_count - 1)
            
            msg = get_text("preset_applied") + " '{}' (frames {}-{})".format(
                preset_name, int(target_start_frame), actual_end)
            if failed_attrs:
                msg += " ({} attrs skipped)".format(len(failed_attrs))
            cmds.inViewMessage(msg=msg, pos="midCenter", fade=True)
        else:
            cmds.warning("No matching controllers found in preset!")
        
        return applied_count > 0
        
    except Exception as e:
        cmds.warning("Failed to apply preset: {}".format(str(e)))
        return False
    finally:
        try:
            cmds.currentTime(current_time)
        except:
            pass
        cmds.undoInfo(closeChunk=True)
        cmds.waitCursor(state=False)


def delete_animation_preset(preset_name):
    """Delete a saved preset for the current controller set"""
    global _animation_presets
    
    controller_key = get_current_controller_key()
    if not controller_key:
        cmds.warning("Select controllers first!")
        return False
    
    load_presets_from_scene()
    
    if controller_key in _animation_presets and preset_name in _animation_presets[controller_key]:
        del _animation_presets[controller_key][preset_name]
        
        # Clean up empty controller groups
        if not _animation_presets[controller_key]:
            del _animation_presets[controller_key]
        
        save_presets_to_scene()
        cmds.inViewMessage(msg="Preset '{}' deleted".format(preset_name), pos="midCenter", fade=True)
        refresh_preset_list_ui()
        return True
    
    cmds.warning(get_text("preset_not_found"))
    return False


def get_preset_info(preset_name):
    """Get info about a preset for current controllers"""
    controller_key = get_current_controller_key()
    if not controller_key:
        return None
    
    load_presets_from_scene()
    
    if controller_key not in _animation_presets:
        return None
    
    if preset_name not in _animation_presets[controller_key]:
        return None
    
    preset = _animation_presets[controller_key][preset_name]
    return {
        "name": preset_name,
        "frames": preset.get("frame_count", 0),
        "objects": len(preset.get("object_names", [])),
        "object_names": preset.get("object_names", []),
        "created": preset.get("created", "Unknown"),
        "frame_range": preset.get("frame_range", [0, 0])
    }


def export_presets_for_controllers():
    """Export presets for current controller set to a JSON file"""
    controller_key = get_current_controller_key()
    if not controller_key:
        cmds.warning("Select controllers first!")
        return
    
    load_presets_from_scene()
    
    if controller_key not in _animation_presets or not _animation_presets[controller_key]:
        cmds.warning("No presets for these controllers!")
        return
    
    file_path = cmds.fileDialog2(
        fileFilter="JSON Files (*.json);;All Files (*.*)",
        dialogStyle=2,
        caption="Export Animation Presets",
        fileMode=0
    )
    
    if not file_path:
        return
    
    file_path = file_path[0]
    if not file_path.endswith(".json"):
        file_path += ".json"
    
    try:
        export_data = {
            "controller_key": controller_key,
            "presets": _animation_presets[controller_key],
            "export_date": cmds.date(format="DD/MM/YYYY HH:mm"),
            "version": TOOL_VERSION
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        cmds.inViewMessage(msg="Presets exported to {}".format(file_path.split("\\")[-1]), pos="midCenter", fade=True)
    except IOError as e:
        cmds.warning("Export failed - file access error: {}".format(str(e)))
    except Exception as e:
        cmds.warning("Export failed: {}".format(str(e)))


def import_presets_for_controllers():
    """Import presets for current controller set from a JSON file"""
    global _animation_presets
    
    controller_key = get_current_controller_key()
    if not controller_key:
        cmds.warning("Select controllers first!")
        return
    
    file_path = cmds.fileDialog2(
        fileFilter="JSON Files (*.json);;All Files (*.*)",
        dialogStyle=2,
        caption="Import Animation Presets",
        fileMode=1
    )
    
    if not file_path:
        return
    
    file_path = file_path[0]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Validate import data structure
        if not isinstance(import_data, dict):
            cmds.warning("Invalid preset file format!")
            return
        
        load_presets_from_scene()
        
        # Initialize controller group if needed
        if controller_key not in _animation_presets:
            _animation_presets[controller_key] = {}
        
        # Import presets - support both new format (with "presets" key) and old format
        imported_presets = import_data.get("presets", import_data)
        
        if not isinstance(imported_presets, dict):
            cmds.warning("Invalid preset data structure!")
            return
        
        count = 0
        skipped = 0
        
        for name, data in imported_presets.items():
            # Validate preset data structure
            if not isinstance(data, dict) or "keyframes" not in data:
                skipped += 1
                continue
            
            # Validate name
            if not name or not isinstance(name, str):
                skipped += 1
                continue
            
            if name not in _animation_presets[controller_key]:
                _animation_presets[controller_key][name] = data
                count += 1
            else:
                # Add suffix for duplicates
                counter = 1
                new_name = name + "_imported"
                while new_name in _animation_presets[controller_key]:
                    new_name = name + "_imported_{}".format(counter)
                    counter += 1
                _animation_presets[controller_key][new_name] = data
                count += 1
        
        save_presets_to_scene()
        refresh_preset_list_ui()
        
        msg = "Imported {} presets".format(count)
        if skipped > 0:
            msg += " ({} skipped - invalid format)".format(skipped)
        cmds.inViewMessage(msg=msg, pos="midCenter", fade=True)
    except IOError as e:
        cmds.warning("Import failed - file access error: {}".format(str(e)))
    except json.JSONDecodeError as e:
        cmds.warning("Import failed - invalid JSON: {}".format(str(e)))
    except Exception as e:
        cmds.warning("Import failed: {}".format(str(e)))


def refresh_preset_list_ui(*args):
    """Refresh the preset list based on current selection"""
    global _preset_list_ui, _current_controller_key
    
    try:
        if not _preset_list_ui or not cmds.textScrollList(_preset_list_ui, exists=True):
            return
        
        # Clear the list
        cmds.textScrollList(_preset_list_ui, edit=True, removeAll=True)
        
        # Get current controller key
        controller_key = get_current_controller_key()
        _current_controller_key = controller_key
        
        # Update controller info display
        if cmds.text("controller_info_text", exists=True):
            if controller_key:
                sel = cmds.ls(selection=True)
                count = len(sel) if sel else 0
                cmds.text("controller_info_text", edit=True, 
                         label="Selected: {} controllers".format(count))
            else:
                cmds.text("controller_info_text", edit=True, 
                         label="Select controllers to see presets")
        
        if not controller_key:
            cmds.textScrollList(_preset_list_ui, edit=True, 
                               append="[ Select controllers to see presets ]")
            return
        
        # Get presets for this controller set
        presets = get_presets_for_controllers(controller_key)
        
        if not presets:
            cmds.textScrollList(_preset_list_ui, edit=True, 
                               append="[ No presets for these controllers ]")
            cmds.textScrollList(_preset_list_ui, edit=True, 
                               append="[ Save a new preset below ]")
            return
        
        # Add presets to list
        for name in sorted(presets.keys()):
            try:
                preset = presets[name]
                if not isinstance(preset, dict):
                    continue
                frame_count = preset.get("frame_count", "?")
                label = "{} ({} frames)".format(name, frame_count)
                cmds.textScrollList(_preset_list_ui, edit=True, append=label)
            except:
                continue
    except Exception as e:
        # Silently fail to avoid breaking UI
        pass


def get_selected_preset_name():
    """Get the currently selected preset name from UI"""
    global _preset_list_ui
    if _preset_list_ui and cmds.textScrollList(_preset_list_ui, exists=True):
        selected = cmds.textScrollList(_preset_list_ui, query=True, selectItem=True)
        if selected and not selected[0].startswith("["):
            # Extract name from label "name (X frames)"
            return selected[0].split(" (")[0]
    return None


def update_preset_info_ui(*args):
    """Update the info display when preset is selected"""
    try:
        preset_name = get_selected_preset_name()
        if not preset_name or preset_name.startswith("["):
            if cmds.text("preset_info_text", exists=True):
                cmds.text("preset_info_text", edit=True, label="Select a preset to see info")
            return
        
        info = get_preset_info(preset_name)
        if info and cmds.text("preset_info_text", exists=True):
            frame_range = info.get("frame_range", [0, 0])
            obj_names = info.get("object_names", [])
            obj_display = ", ".join(obj_names[:3])
            if len(obj_names) > 3:
                obj_display += "..."
            
            info_str = "Frames: {} ({}-{})\nObjects: {}\nCreated: {}".format(
                info.get("frames", "?"),
                int(frame_range[0]) if len(frame_range) > 0 else 0, 
                int(frame_range[1]) if len(frame_range) > 1 else 0,
                obj_display if obj_display else "?",
                info.get("created", "Unknown")
            )
            cmds.text("preset_info_text", edit=True, label=info_str)
    except Exception as e:
        # Silently fail to avoid breaking UI
        pass


def setup_preset_selection_callback():
    """Setup callback to refresh preset list when selection changes"""
    global _selection_callback_id
    
    # Remove existing callback
    remove_preset_selection_callback()
    
    try:
        import maya.api.OpenMaya as om
        _selection_callback_id = om.MEventMessage.addEventCallback(
            "SelectionChanged", 
            lambda *args: cmds.evalDeferred(refresh_preset_list_ui)
        )
    except Exception as e:
        cmds.warning("Could not setup selection callback: {}".format(str(e)))


def remove_preset_selection_callback():
    """Remove the selection callback"""
    global _selection_callback_id
    
    if _selection_callback_id is not None:
        try:
            import maya.api.OpenMaya as om
            om.MMessage.removeCallback(_selection_callback_id)
        except:
            pass
        _selection_callback_id = None


# UI Command wrappers for presets
def cmd_save_preset(*args):
    """UI command to save preset"""
    try:
        if not cmds.textField("preset_name_field", exists=True):
            cmds.warning("UI not initialized!")
            return
        
        name = cmds.textField("preset_name_field", query=True, text=True)
        if not name or name.strip() == "":
            cmds.warning("Please enter a preset name!")
            return
        
        # Validate name (no special characters that could break JSON)
        if any(c in name for c in ['|', ':', '[', ']', '{', '}']):
            cmds.warning("Preset name contains invalid characters!")
            return
        
        if not cmds.floatField("preset_start_frame", exists=True) or not cmds.floatField("preset_end_frame", exists=True):
            cmds.warning("UI fields not found!")
            return
        
        start = cmds.floatField("preset_start_frame", query=True, value=True)
        end = cmds.floatField("preset_end_frame", query=True, value=True)
        
        save_animation_preset(name.strip(), int(start), int(end))
    except Exception as e:
        cmds.warning("Error saving preset: {}".format(str(e)))


def cmd_apply_preset(*args):
    """UI command to apply preset"""
    try:
        preset_name = get_selected_preset_name()
        if not preset_name or preset_name.startswith("["):
            cmds.warning("Please select a preset from the list!")
            return
        
        if not cmds.floatField("apply_start_frame", exists=True) or not cmds.floatField("apply_end_frame", exists=True):
            cmds.warning("UI not initialized!")
            return
        
        target_start = cmds.floatField("apply_start_frame", query=True, value=True)
        target_end = cmds.floatField("apply_end_frame", query=True, value=True)
        
        # Validate frame range
        if target_end <= target_start:
            cmds.warning("End frame must be greater than start frame!")
            return
        
        # Get blend mode
        blend_mode = "replace"
        try:
            if cmds.radioButton("blend_replace_rb", exists=True) and cmds.radioButton("blend_replace_rb", query=True, select=True):
                blend_mode = "replace"
            elif cmds.radioButton("blend_add_rb", exists=True) and cmds.radioButton("blend_add_rb", query=True, select=True):
                blend_mode = "additive"
            elif cmds.radioButton("blend_mult_rb", exists=True) and cmds.radioButton("blend_mult_rb", query=True, select=True):
                blend_mode = "multiply"
        except:
            pass  # Default to replace
        
        apply_animation_preset(preset_name, int(target_start), int(target_end), blend_mode)
    except Exception as e:
        cmds.warning("Error applying preset: {}".format(str(e)))


def cmd_delete_preset(*args):
    """UI command to delete preset"""
    preset_name = get_selected_preset_name()
    if preset_name:
        confirm = cmds.confirmDialog(
            title="Delete Preset",
            message="Delete preset '{}'?".format(preset_name),
            button=["Yes", "No"],
            defaultButton="No"
        )
        if confirm == "Yes":
            delete_animation_preset(preset_name)


# Entry point
if __name__ == "__main__":
    show_ui()
