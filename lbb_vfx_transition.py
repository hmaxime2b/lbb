"""
╔══════════════════════════════════════════════════════════════╗
║         SCRIPT VFX — LBB RUGBY EDIT TRANSITION              ║
║         Louis Bielle-Biarrey | Blender Python Script         ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION :
  1. Ouvrir Blender (3.x ou 4.x)
  2. Onglet "Scripting" → coller ce script
  3. Adapter les chemins PLAN_1_PATH / PLAN_2_PATH
  4. Ajuster FREEZE_FRAME selon ta vidéo
  5. Cliquer "Run Script" (▶)
  6. Render > Animation (Ctrl+F12)

PLAN 1 : LBB marche (maillot blanc, nuit, casque blanc)
PLAN 2 : LBB geste klaxon après essai (maillot bleu, jour)
"""

import bpy
import math

# ─────────────────────────────────────────────
#  CONFIGURATION — ADAPTER CES VALEURS
# ─────────────────────────────────────────────

PLAN_1_PATH  = "/tmp/lbb_marche.mp4"      # Clip 1 : LBB qui marche
PLAN_2_PATH  = "/tmp/lbb_klaxon.mp4"      # Clip 2 : geste klaxon
OUTPUT_PATH  = "/tmp/lbb_render/"         # Dossier de sortie

FPS          = 30

# Frame du freeze dans le clip 1 (ajuster selon ta vidéo)
FREEZE_FRAME       = 45   # ← frame où LBB se fige
AURA_START         = FREEZE_FRAME
FLASH_FRAME        = FREEZE_FRAME + 6    # 1 frame blanche
KLAXON_CUT         = FLASH_FRAME + 1    # début plan klaxon

# Couleurs LBB (inspiré maillot Bordeaux-Bègles)
COLOR_GOLD   = (1.0,  0.85, 0.15, 1.0)   # Texte "LBB" doré
COLOR_BLUE   = (0.05, 0.4,  1.0,  1.0)   # Aura bleue électrique
COLOR_WHITE  = (1.0,  1.0,  1.0,  1.0)   # Flash blanc

# ─────────────────────────────────────────────


def clear_scene():
    """Repart d'une scène propre."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    print("✓ Scène nettoyée")


def setup_render():
    """1920×1080 @ 30fps, sortie MP4."""
    scene = bpy.context.scene
    render = scene.render

    render.engine            = 'BLENDER_EEVEE'
    render.resolution_x      = 1920
    render.resolution_y      = 1080
    render.resolution_percentage = 100
    render.fps               = FPS

    scene.frame_start        = 1
    scene.frame_end          = KLAXON_CUT + 90   # marge plan 2

    # Sortie PNG séquence (compatible tous builds Blender)
    # Importer ensuite dans Premiere : Fichier > Importer > sélectionner 0001.png
    # → cocher "Séquence d'images" → Premiere assemble automatiquement
    render.image_settings.file_format  = 'PNG'
    render.image_settings.color_mode   = 'RGBA'   # alpha pour compositing
    render.image_settings.compression  = 15        # 0=max qualité, 100=max compression
    render.filepath                    = OUTPUT_PATH

    print("✓ Render : 1920×1080 @ 30fps — EEVEE — PNG séquence (RGBA)")


# ══════════════════════════════════════════════
#  2. COMPOSITOR — Effets visuels freeze frame
# ══════════════════════════════════════════════

def build_compositor():
    """
    Pipeline nodes :
    Render → N&B → Contraste → Glow → Color Balance
          → Vignette → Flash animé → Zoom → Output

    Analyse des plans :
    - Plan 1 (nuit, blanc) : bon contraste → glow sur les hautes lumières
    - Plan 2 (jour, bleu) : couleurs vives → garder couleurs naturelles
    """
    scene = bpy.context.scene
    scene.use_nodes = True
    tree  = scene.node_tree
    tree.nodes.clear()

    N = tree.nodes
    L = tree.links

    # ── INPUT ──────────────────────────────────
    rl = N.new('CompositorNodeRLayers')
    rl.location = (-900, 300)

    # ── N&B (saturation → 0) ───────────────────
    hs = N.new('CompositorNodeHueSat')
    hs.location = (-620, 300)
    hs.inputs['Saturation'].default_value = 0.0
    hs.inputs['Value'].default_value      = 1.05
    hs.label = "N&B"
    L.new(rl.outputs['Image'], hs.inputs['Image'])

    # ── CONTRASTE ÉLEVÉ ────────────────────────
    bc = N.new('CompositorNodeBrightContrast')
    bc.location = (-340, 300)
    bc.inputs['Bright'].default_value    = 8.0
    bc.inputs['Contrast'].default_value  = 65.0
    bc.label = "Contraste +"
    L.new(hs.outputs['Image'], bc.inputs['Image'])

    # ── GLOW (Fog Glow sur les hautes lumières) ─
    # → colle parfaitement aux lumières stade Plan 1
    glare = N.new('CompositorNodeGlare')
    glare.location = (-60, 300)
    glare.glare_type  = 'FOG_GLOW'
    glare.threshold   = 0.65
    glare.size        = 7
    glare.label = "Glow stade"
    L.new(bc.outputs['Image'], glare.inputs['Image'])

    # ── COLOR BALANCE (tons froids dans ombres) ─
    cb = N.new('CompositorNodeColorBalance')
    cb.location = (220, 300)
    cb.correction_method = 'LIFT_GAMMA_GAIN'
    cb.lift  = (0.82, 0.82, 1.00)   # ombres bleues
    cb.gamma = (1.00, 1.00, 1.00)   # tons moyens neutres
    cb.gain  = (1.05, 1.00, 0.92)   # hautes lumières légèrement chaudes
    cb.label = "Color Grade Freeze"
    L.new(glare.outputs['Image'], cb.inputs['Image'])

    # ── VIGNETTE ───────────────────────────────
    ell = N.new('CompositorNodeEllipseMask')
    ell.location = (220, 0)
    ell.width  = 0.75
    ell.height = 0.75

    vig_blur = N.new('CompositorNodeBlur')
    vig_blur.location = (450, 0)
    vig_blur.filter_type = 'GAUSS'
    vig_blur.size_x = 90
    vig_blur.size_y = 90
    L.new(ell.outputs['Mask'], vig_blur.inputs['Image'])

    inv = N.new('CompositorNodeInvert')
    inv.location = (680, 0)
    L.new(vig_blur.outputs['Image'], inv.inputs['Color'])

    vig_mix = N.new('CompositorNodeMixRGB')
    vig_mix.location = (680, 300)
    vig_mix.blend_type = 'MULTIPLY'
    vig_mix.inputs['Fac'].default_value = 0.65
    L.new(cb.outputs['Image'],    vig_mix.inputs[1])
    L.new(inv.outputs['Color'],   vig_mix.inputs[2])

    # ── FLASH BLANC ANIMÉ (1 frame) ────────────
    flash_rgb = N.new('CompositorNodeRGB')
    flash_rgb.location = (680, -150)
    flash_rgb.outputs[0].default_value = COLOR_WHITE

    flash_mix = N.new('CompositorNodeMixRGB')
    flash_mix.location = (950, 300)
    flash_mix.blend_type = 'MIX'
    flash_mix.label = "Flash animé"
    L.new(vig_mix.outputs['Image'],      flash_mix.inputs[1])
    L.new(flash_rgb.outputs['RGBA'],     flash_mix.inputs[2])

    fac = flash_mix.inputs['Fac']
    fac.default_value = 0.0

    def key_flash(frame, value):
        scene.frame_set(frame)
        fac.default_value = value
        fac.keyframe_insert("default_value")

    key_flash(FLASH_FRAME - 2, 0.0)
    key_flash(FLASH_FRAME,     1.0)   # ← impact beat
    key_flash(FLASH_FRAME + 1, 0.0)

    # ── ZOOM ANIMÉ (Transform) ─────────────────
    tf = N.new('CompositorNodeTransform')
    tf.location = (1200, 300)
    tf.label = "Zoom 100→115%"
    L.new(flash_mix.outputs['Image'], tf.inputs['Image'])

    sc = tf.inputs['Scale']
    sc.default_value = 1.0

    def key_zoom(frame, value):
        scene.frame_set(frame)
        sc.default_value = value
        sc.keyframe_insert("default_value")

    key_zoom(AURA_START,    1.00)
    key_zoom(FLASH_FRAME,   1.15)
    key_zoom(KLAXON_CUT,    1.00)   # reset pour plan 2

    # ── OUTPUT ─────────────────────────────────
    out = N.new('CompositorNodeComposite')
    out.location = (1480, 300)
    L.new(tf.outputs['Image'], out.inputs['Image'])

    viewer = N.new('CompositorNodeViewer')
    viewer.location = (1480, 100)
    L.new(tf.outputs['Image'], viewer.inputs['Image'])

    print("✓ Compositor : N&B → Contraste → Glow → Grade → Vignette → Flash → Zoom")


# ══════════════════════════════════════════════
#  3. TEXTE "LBB" ANIMÉ
# ══════════════════════════════════════════════

def create_lbb_text():
    """
    Texte 3D "LBB" doré, centré en bas d'écran.
    Animation : scale punch (0 → 1.4 → 1.0 → explosion avec flash)

    Choix gold (#FFD93D) : contraste maximal sur fond N&B
    Position bas : laisse le visage de LBB visible en haut
    """
    bpy.ops.object.text_add(location=(0, -3.2, 0))
    obj = bpy.context.active_object
    obj.name = "LBB_Text"

    td = obj.data
    td.body         = "LBB"
    td.align_x      = 'CENTER'
    td.align_y      = 'CENTER'
    td.size         = 2.8
    td.extrude      = 0.08
    td.bevel_depth  = 0.025
    td.bevel_resolution = 2

    # Matériau émissif doré
    mat = bpy.data.materials.new("Mat_LBB_Gold")
    mat.use_nodes = True
    mn = mat.node_tree.nodes
    ml = mat.node_tree.links
    mn.clear()

    em = mn.new('ShaderNodeEmission')
    em.inputs['Color'].default_value    = COLOR_GOLD
    em.inputs['Strength'].default_value = 6.0

    op = mn.new('ShaderNodeOutputMaterial')
    ml.new(em.outputs['Emission'], op.inputs['Surface'])
    obj.data.materials.append(mat)

    # ── ANIMATION ──────────────────────────────
    scene = bpy.context.scene

    def key_text(frame, sx, sy, sz):
        scene.frame_set(frame)
        obj.scale = (sx, sy, sz)
        obj.keyframe_insert("scale")

    key_text(FREEZE_FRAME - 1, 0.0,  0.0,  0.0)   # invisible avant
    key_text(FREEZE_FRAME,     1.4,  1.4,  1.4)   # frappe initiale
    key_text(FREEZE_FRAME + 2, 1.0,  1.0,  1.0)   # stabilisation
    key_text(FLASH_FRAME - 1,  1.0,  1.0,  1.0)   # maintien
    key_text(FLASH_FRAME,      2.2,  2.2,  2.2)   # explose avec flash
    key_text(FLASH_FRAME + 1,  0.0,  0.0,  0.0)   # disparaît

    # Interpolation BACK pour effet rebond
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BACK'

    print("✓ Texte 'LBB' — doré (#FFD93D) — animation punch créée")
    return obj


# ══════════════════════════════════════════════
#  4. AURA D'ÉNERGIE AUTOUR DU JOUEUR
# ══════════════════════════════════════════════

def create_energy_aura():
    """
    Aura bleue électrique : plan émissif derrière le joueur.
    Texture Noise animée pour mouvement organique.
    Apparaît au freeze, explose au flash.

    Bleu choisi pour contraste maximal avec :
    - Maillot blanc Plan 1 (nuit)
    - Gold du texte LBB
    """
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.05))
    aura = bpy.context.active_object
    aura.name = "LBB_Aura"
    aura.scale = (2.0, 4.5, 1.0)   # proportions silhouette joueur

    mat = bpy.data.materials.new("Mat_Aura_Blue")
    mat.use_nodes   = True
    mat.blend_method = 'ADD'
    mn = mat.node_tree.nodes
    ml = mat.node_tree.links
    mn.clear()

    # Texture bruit animée (donne le mouvement électrique)
    coords = mn.new('ShaderNodeTexCoord')
    noise  = mn.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value     = 6.0
    noise.inputs['Detail'].default_value    = 12.0
    noise.inputs['Roughness'].default_value = 0.75
    ml.new(coords.outputs['Object'], noise.inputs['Vector'])

    # Rampe de couleur : transparent → bleu électrique
    ramp = mn.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color    = (0, 0, 0, 0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color    = COLOR_BLUE
    ml.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    em = mn.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 9.0
    ml.new(ramp.outputs['Color'], em.inputs['Color'])

    transp = mn.new('ShaderNodeBsdfTransparent')
    mix_sh = mn.new('ShaderNodeMixShader')
    ml.new(ramp.outputs['Fac'],     mix_sh.inputs['Fac'])
    ml.new(transp.outputs['BSDF'],  mix_sh.inputs[1])
    ml.new(em.outputs['Emission'],  mix_sh.inputs[2])

    op = mn.new('ShaderNodeOutputMaterial')
    ml.new(mix_sh.outputs['Shader'], op.inputs['Surface'])
    aura.data.materials.append(mat)

    # ── ANIMATION ──────────────────────────────
    scene = bpy.context.scene

    def key_aura(frame, sx, sy):
        scene.frame_set(frame)
        aura.scale = (sx, sy, 1.0)
        aura.keyframe_insert("scale")

    key_aura(AURA_START - 1,  0.0,  0.0)
    key_aura(AURA_START,      1.6,  4.8)   # pop
    key_aura(AURA_START + 2,  1.2,  3.8)   # settle
    key_aura(FLASH_FRAME - 1, 1.3,  4.0)   # maintien
    key_aura(FLASH_FRAME,     2.5,  6.5)   # explosion
    key_aura(FLASH_FRAME + 1, 0.0,  0.0)   # disparaît

    # Animer le bruit (W = time offset) pour électricité vivante
    noise.inputs['W'].default_value = 0.0
    scene.frame_set(AURA_START)
    noise.inputs['W'].keyframe_insert("default_value")
    scene.frame_set(FLASH_FRAME)
    noise.inputs['W'].default_value = 3.5
    noise.inputs['W'].keyframe_insert("default_value")

    print("✓ Aura bleue électrique — Noise animé — explosion au flash")
    return aura


# ══════════════════════════════════════════════
#  5. CAMERA + SHAKE POST-FLASH
# ══════════════════════════════════════════════

def setup_camera_and_shake():
    """
    Positionne la caméra face au joueur.
    Shake agressif 7 frames après le flash (plan klaxon).
    """
    bpy.ops.object.camera_add(location=(0, -8, 0))
    cam = bpy.context.active_object
    cam.name = "Camera_LBB"
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cam.data.lens = 35

    bpy.context.scene.camera = cam

    # Pattern shake : amplitude décroissante
    shake = [
        #  Δframe   x       y
        (0,         0.00,   0.00),
        (1,         0.18,  -0.12),
        (2,        -0.14,   0.09),
        (3,         0.11,  -0.07),
        (4,        -0.08,   0.05),
        (5,         0.05,  -0.03),
        (6,        -0.02,   0.02),
        (7,         0.00,   0.00),
    ]

    base_x = cam.location.x
    base_y = cam.location.y
    scene  = bpy.context.scene

    for df, dx, dy in shake:
        scene.frame_set(FLASH_FRAME + df)
        cam.location.x = base_x + dx
        cam.location.y = base_y + dy
        cam.keyframe_insert("location")

    print("✓ Caméra créée + shake 7 frames post-flash (amplitude décroissante)")
    return cam


# ══════════════════════════════════════════════
#  6. LUMIÈRE DE SCÈNE
# ══════════════════════════════════════════════

def setup_lighting():
    """
    Éclairage inspiré Plan 1 (stade nuit, lumières dures).
    Lumière principale forte + contre-jour bleu pour l'aura.
    """
    # Key light (blanc chaud, simuler projecteurs stade)
    bpy.ops.object.light_add(type='AREA', location=(3, -5, 5))
    key = bpy.context.active_object
    key.name = "Key_Stade"
    key.data.energy = 800
    key.data.color  = (1.0, 0.95, 0.85)
    key.data.size   = 3.0
    key.rotation_euler = (math.radians(45), 0, math.radians(30))

    # Contre-jour bleu (simule l'aura électrique)
    bpy.ops.object.light_add(type='SPOT', location=(-2, 5, 2))
    back = bpy.context.active_object
    back.name = "Back_Aura"
    back.data.energy     = 300
    back.data.color      = (0.1, 0.4, 1.0)
    back.data.spot_size  = math.radians(60)
    back.rotation_euler  = (math.radians(-30), 0, math.radians(-150))

    print("✓ Éclairage : Key stade (blanc chaud) + Back aura (bleu)")


# ══════════════════════════════════════════════
#  RÉSUMÉ TIMELINE
# ══════════════════════════════════════════════

def print_timeline():
    bar = "─" * 56
    print(f"""
╔{bar}╗
║          TIMELINE VFX LBB — RÉSUMÉ COMPLET              ║
╠{bar}╣
║  Frame {FREEZE_FRAME:3d}  │ FREEZE — N&B + Contraste + Glow activés   ║
║  Frame {FREEZE_FRAME:3d}  │ Texte "LBB" or apparaît (punch scale)     ║
║  Frame {AURA_START:3d}  │ Aura bleue électrique — apparition         ║
║  Frame {AURA_START:3d}→{FLASH_FRAME}  │ Zoom progressif 100% → 115%              ║
║  Frame {FLASH_FRAME:3d}  │ ★ FLASH BLANC (1 frame) — impact beat     ║
║  Frame {FLASH_FRAME:3d}  │ "LBB" explose × 2.2 avec le flash         ║
║  Frame {KLAXON_CUT:3d}  │ CUT → Plan klaxon (bras levé)             ║
║  Frame {KLAXON_CUT:3d}→{KLAXON_CUT+7}  │ Camera shake 7 frames                    ║
╠{bar}╣
║  DURÉE TRANSITION : {(FLASH_FRAME - FREEZE_FRAME)/FPS:.2f}s  (calé sur beat)          ║
╚{bar}╝

PROCHAINES ÉTAPES :
  1. Changer FREEZE_FRAME selon ta vidéo
  2. Render > Image (F12) pour prévisualiser
  3. Ctrl+F12 pour le rendu complet
  4. Importer la séquence rendue dans Premiere Pro
  5. Caler le FLASH_FRAME sur le beat musical
""")


# ══════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("\n▶ Démarrage script LBB VFX Transition...\n")

    clear_scene()
    setup_render()
    build_compositor()
    create_lbb_text()
    create_energy_aura()
    setup_camera_and_shake()
    setup_lighting()
    print_timeline()

    print("✅ Script terminé — Lance F12 pour prévisualiser !")
