"""Render every L1 view from the SAME scene; plan coordinates are metres.

Run: blender -b --factory-startup --python tools/render_l1_layout.py
Room envelope comes from the supplied plan. Opening/pillar sizes are estimates.
This builds a new geometric model, not an edit of an AI-generated picture.
"""
import bpy
import math
import json
import hashlib
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'concepts/L1-living-dining/fixed-layout'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
W, D, H = 4.6228, 4.9022, 2.85
objects = {}

def mat(name, color, rough=.5, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    return m

ivory = mat('Ivory walls', (.77, .74, .68), .8)
walnut = mat('Medium walnut', (.20, .10, .051), .43)
pearl = mat('Pearl grey upholstery', (.52, .54, .54), .95)
taupe = mat('Mushroom cushions', (.30, .27, .24), .98)
cream = mat('Ivory upholstery', (.76, .74, .69), .95)
brass = mat('Champagne metal', (.56, .40, .20), .3, .7)
black = mat('TV black glass', (.012, .018, .022), .23, .15)
rug = mat('Low pile grey oatmeal rug', (.46, .43, .38), 1)
marble = mat('Ivory marble subtle veins', (.83, .80, .72), .35)
n = marble.node_tree.nodes
l = marble.node_tree.links
tex = n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 3.2
tex.inputs['Detail'].default_value = 2
wave = n.new('ShaderNodeTexWave'); wave.wave_type = 'BANDS'
wave.inputs['Scale'].default_value = 3
wave.inputs['Distortion'].default_value = 8
wave.inputs['Detail Scale'].default_value = .8
coord = n.new('ShaderNodeTexCoord')
l.new(coord.outputs['Generated'], wave.inputs['Vector'])
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .78
ramp.color_ramp.elements[0].color = (.86, .83, .75, 1)
ramp.color_ramp.elements[1].position = .88
ramp.color_ramp.elements[1].color = (.57, .51, .41, 1)
ramp.color_ramp.elements[0].position = .35
ramp.color_ramp.elements[0].color = (.76, .73, .66, 1)
ramp.color_ramp.elements[1].position = .72
ramp.color_ramp.elements[1].color = (.86, .83, .76, 1)
l.new(tex.outputs['Fac'], ramp.inputs[0])
l.new(ramp.outputs['Color'], n.get('Principled BSDF').inputs['Base Color'])

def xyz(x, y, z): return (x, -y, z)

def box(name, x, y, z, sx, sy, sz, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz(x, y, z))
    o = bpy.context.object; o.name = name
    o.dimensions = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new('Soft edge', 'BEVEL'); mod.width = bevel; mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    objects[name] = o
    return o

def cyl(name, x, y, z, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=xyz(x,y,z))
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    bevel=o.modifiers.new('Edge','BEVEL'); bevel.width=.015; bevel.segments=3
    objects[name]=o
    return o

def sphere(name,x,y,z,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=xyz(x,y,z))
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    objects[name]=o
    return o

def wall_x(name, x1,x2,y): box(name,(x1+x2)/2,y,H/2,x2-x1,.12,H,ivory)
def wall_y(name, x,y1,y2): box(name,x,(y1+y2)/2,H/2,.12,y2-y1,H,ivory)
def opening_y(name,x,y1,y2):
    box(name+' lintel',x,(y1+y2)/2,2.525,.12,y2-y1,.65,ivory)
    for y in (y1,y2): box(name+' jamb '+str(y),x,y,1.1,.15,.045,2.2,walnut)
    box(name+' header',x,(y1+y2)/2,2.18,.15,y2-y1,.06,walnut)
def opening_x(name,y,x1,x2):
    box(name+' lintel',(x1+x2)/2,y,2.525,x2-x1,.12,.65,ivory)
    for x in (x1,x2): box(name+' jamb '+str(x),x,y,1.1,.045,.15,2.2,walnut)
    box(name+' header',(x1+x2)/2,y,2.18,x2-x1,.15,.06,walnut)

# Outline is stepped, following the original plan, never a generic rectangle.
verts=[xyz(x,y,-.06) for x,y in [(0,0),(W,0),(W,D),(1.16,D),(1.16,3.40),(0,3.40)]]
mesh=bpy.data.meshes.new('L1 stepped floor'); mesh.from_pydata(verts,[],[tuple(range(6))]); mesh.update()
floor=bpy.data.objects.new('L1 ivory marble floor',mesh); bpy.context.collection.objects.link(floor)
floor.data.materials.append(marble)
solid=floor.modifiers.new('Slab','SOLIDIFY'); solid.thickness=.10
roofmesh=mesh.copy()
roof=bpy.data.objects.new('Ceiling - removed only for plan cutaway',roofmesh)
bpy.context.collection.objects.link(roof)
roof.location.z=H+.06
roof.data.materials.clear(); roof.data.materials.append(ivory)
wall_x('Plan top wall',0,W,0)
wall_y('Right wall above entry',W,0,.80)
opening_y('MAIN ENTRY',W,.80,1.80)
wall_y('Right wall below entry',W,1.80,D)
wall_x('B2 short wall',1.16,1.26,D)
opening_x('B2 DOOR',D,1.26,2.10)
wall_x('B2 TV WALL',2.10,W,D)
wall_y('Lower left notch wall',1.16,3.40,D)
wall_x('Notch wall stub',.92,1.16,3.40)
wall_y('Kitchen left upper wall',0,0,.50)
opening_y('KITCHEN K1',0,.50,1.60)
wall_y('Kitchen toilet dividing side',0,1.60,2.85)
opening_y('TOILET T1',0,2.85,3.40)
# Closed B2 door in its actual wall; main and kitchen openings remain readable.
box('B2 door leaf',1.68,D+.03,1.06,.78,.04,2.12,walnut)
box('B2 door handle',1.97,D-.05,1.0,.10,.035,.025,brass,.01)
box('Main entry threshold',W,1.30,.005,.30,1.00,.02,marble)
box('Kitchen threshold',0,1.05,.005,.28,1.10,.02,marble)
# Pillar sizes are provisional; positions follow visible projections in the plan.
for name,x,y,sx,sy in [('Top left pillar',.08,.12,.18,.32),('Top right pillar',W-.10,.10,.20,.20),('Lower right pillar',W-.10,D-.17,.20,.34)]:
    box(name,x,y,H/2,sx,sy,H,ivory)

# Lengthwise dining beside kitchen, matching the owner's rough top view.
box('Dining table',1.72,1.28,.755,.76,1.20,.055,walnut,.06)
for x in (1.45,1.99):
    for y in (.80,1.76): box('Dining leg '+str((x,y)),x,y,.36,.05,.05,.72,brass,.01)
for y in (.97,1.59):
    for x,sign in ((1.08,-1),(2.36,1)):
        box('Dining chair seat '+str((x,y)),x,y,.44,.46,.46,.12,pearl,.07)
        box('Dining chair back '+str((x,y)),x+sign*.19,y,.70,.10,.46,.56,pearl,.05)
        for dx in (-.16,.16):
            for dy in (-.16,.16): box('Chair leg '+str((x,y,dx,dy)),x+dx,y+dy,.2,.025,.025,.4,walnut)

# Compact L sofa faces +plan-Y, i.e. the B2/TV wall. Its back is toward the entry.
box('Sofa base',3.32,3.45,.25,2.14,.84,.32,pearl,.085)
box('Sofa back',3.32,3.07,.64,2.14,.17,.69,pearl,.06)
box('Sofa left arm',2.30,3.44,.51,.14,.83,.43,pearl,.05)
box('Sofa right arm',4.34,3.70,.51,.14,1.35,.43,pearl,.05)
box('Sofa chaise base',4.00,3.75,.25,.71,1.42,.32,pearl,.07)
for i,x in enumerate((2.69,3.35)):
    box('Sofa seat '+str(i),x,3.48,.46,.63,.62,.16,pearl,.06)
box('Chaise cushion',4.00,3.80,.46,.61,1.14,.16,pearl,.06)
for i,x in enumerate((2.64,3.22,3.95)):
    p=box('Sofa pillow '+str(i),x,3.27,.76,.40,.14,.40,taupe if i!=1 else cream,.08)
    p.rotation_euler[0]=math.radians(12)
box('Living rug',3.29,4.05,.008,2.18,1.34,.016,rug,.015)
cyl('Side table stone top',2.08,3.45,.52,.14,.035,marble)
cyl('Side table champagne base',2.08,3.45,.25,.08,.50,brass)

# TV is fixed on B2 wall, right of its door. 50-inch approximate screen.
box('TV marble panel',3.25,D-.065,1.36,2.00,.04,2.55,marble,.015)
for x in (2.22,4.28): box('TV walnut trim '+str(x),x,D-.10,1.36,.06,.06,2.55,walnut)
box('TV console',3.22,D-.22,.40,1.94,.32,.34,walnut,.02)
for x in (2.74,3.22,3.70): box('Console brass pull '+str(x),x,D-.385,.47,.22,.012,.009,brass)
box('TV frame',3.25,D-.13,1.35,1.13,.055,.665,black,.016)
box('TV screen',3.25,D-.164,1.35,1.085,.007,.610,black,.005)
box('Soundbar',3.22,D-.29,.605,.64,.075,.055,black,.015)

# Two distinct screens bound a compact puja nook after the main entrance.
def partition(name, y, x1=3.40, x2=4.53):
    box(name+' lower panel',(x1+x2)/2,y,.20,x2-x1,.065,.40,walnut,.008)
    box(name+' top rail',(x1+x2)/2,y,1.72,x2-x1,.065,.05,walnut,.005)
    for i in range(11):
        x=x1+(x2-x1)*i/10
        box(name+' slat '+str(i),x,y,1.04,.035,.045,1.35,walnut,.004)
partition('P1 behind sofa',2.94)
partition('P2 below main entry',1.96)
# Shrine faces LEFT into open accessible side; no third partition.
box('Singhasan base',4.37,2.45,.38,.38,.70,.76,walnut,.02)
box('Singhasan altar ivory',4.34,2.45,.78,.45,.76,.04,marble,.01)
box('Singhasan back',4.55,2.45,1.28,.055,.76,1.05,marble,.014)
for y in (2.09,2.81):
    box('Shrine upright '+str(y),4.35,y,1.27,.08,.05,.98,walnut,.008)
box('Singhasan canopy',4.37,2.45,1.79,.43,.85,.08,walnut,.025)
cyl('Offering tray',4.13,2.45,.81,.10,.015,brass)
# Neutral brass forms represent deity positions without specifying the family's idols.
for y in (2.23,2.45,2.67):
    cyl('Idol plinth '+str(y),4.39,y,.83,.065,.055,brass)
    sphere('Deity placeholder body '+str(y),4.40,y,.965,(.055,.065,.11),brass)
    sphere('Deity placeholder head '+str(y),4.40,y,1.105,(.045,.045,.05),brass)
box('Prayer mat',3.88,2.45,.009,.52,.64,.018,rug,.015)

# Fixed AC location on right wall over the living zone.
box('AC unit',W-.15,3.65,2.35,.25,.80,.27,cream,.05)
box('AC outlet',W-.281,3.65,2.28,.013,.67,.04,black,.01)
# Quiet abstract art on top wall, away from openings.
box('Art frame',1.55,.075,1.62,1.0,.035,.65,walnut,.008)
box('Art canvas',1.55,.052,1.62,.93,.008,.58,cream)
for x,z,s in ((1.28,1.67,.12),(1.58,1.53,.17),(1.82,1.68,.10)):
    o=cyl('Abstract motif '+str(x),x,.04,z,s,.005,taupe)
    o.rotation_euler[0]=math.pi/2

# Fan, pendant, ceiling perimeter and fixed artificial lighting; no windows.
cyl('Fan hub',3.30,3.68,2.48,.12,.14,brass)
cyl('Fan rod',3.30,3.68,2.68,.025,.29,brass)
for i in range(3):
    a=2*math.pi*i/3
    o=box('Fan blade '+str(i),3.30+.30*math.cos(a),3.68-.30*math.sin(a),2.47,.64,.13,.025,walnut,.045)
    o.rotation_euler[2]=a
ceiling_parts=[]
for name,x,y,sx,sy in [('Top border',W/2,.10,W,.20),('Right border',W-.10,D/2,.20,D),('B2 border',(1.16+W)/2,D-.10,W-1.16,.20)]:
    ceiling_parts.append(box(name,x,y,2.77,sx,sy,.13,ivory))
cyl('Dining pendant wire',1.72,1.28,2.40,.01,.85,brass)
sphere('Dining pendant shade',1.72,1.28,1.98,(.23,.23,.15),cream)

def area(name,x,y,z,power,size,color=(1,.91,.78),target=None):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.location=xyz(x,y,z)
    if target: o.rotation_euler=(Vector(xyz(*target))-o.location).to_track_quat('-Z','Y').to_euler()
    return o
area('Dining light',1.72,1.28,2.73,125,1.1)
area('Living ambient',3.1,3.6,2.72,190,1.5)
area('Entry ambient',3.2,.70,2.72,130,1.2)
area('Middle ambient',1.6,2.60,2.72,100,1)
area('Shrine light',4.25,2.45,1.70,12,.25,(1,.80,.51),(4.5,2.45,1.05))
area('TV wall wash',3.25,4.42,2.60,35,.7,(1,.87,.69),(3.25,4.85,1.4))

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=40
scene.cycles.use_denoising=False
scene.render.resolution_x=1000; scene.render.resolution_y=750; scene.render.resolution_percentage=100
scene.world.color=(.13,.13,.13)
scene.view_settings.view_transform='AgX'
scene.view_settings.exposure=-.65
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.threads_mode='FIXED'; scene.render.threads=8

def camera(name,location,target,lens=24,ortho=None):
    data=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    o.location=xyz(*location); o.rotation_euler=(Vector(xyz(*target))-o.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens; data.clip_start=.05
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    return o

cameras={
    '01-top':camera('TOP same room', (W/2,D/2,10),(W/2,D/2,0),ortho=7.35),
    '02-entry-to-tv':camera('A from entry zone toward B2 TV', (2.76,.35,2.10),(3.05,3.82,1.05),lens=18),
    '03-tv-to-entry':camera('B from B2 side toward entry', (1.96,4.55,1.75),(3.55,1.56,1.18),lens=18),
    '04-dining-to-puja':camera('C from dining side to puja',(0.40,1.94,1.65),(4.25,2.50,1.12),lens=22),
}
# Identity matrix overhead means screen-right = plan-right and screen-up = plan-top.
cameras['01-top'].rotation_euler=(0,0,0)
scene.camera=cameras['02-entry-to-tv']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'l1-fixed-layout.blend'))
manifest={
    'units':'metres', 'plan_axes':'x left-to-right, y top-to-bottom; Blender world Y=-plan y',
    'room_envelope':[W,D], 'height_assumed':H,
    'source':'Original supplied floor-plan orientation; envelope printed dimensions; openings and pillars approximate',
    'main_entry':{'wall':'right','y_range':[.8,1.8]},
    'kitchen':{'wall':'left','y_range':[.5,1.6]},
    'B2_door':{'wall':'bottom','x_range':[1.26,2.10]},
    'TV':{'wall':'bottom / B2','center_x':3.25},
    'P1_behind_sofa':{'y':2.94,'x_range':[3.4,4.53]},
    'P2_below_main_entry':{'y':1.96,'x_range':[3.4,4.53]},
    'shrine':{'right_wall_center_y':2.45,'open_access':'left'},
    'sofa':{'width':2.14,'body_depth':.84,'chaise_depth':1.42,'faces':'bottom / B2 TV'},
    'cameras':{k:{'world_location':list(v.location),'rotation':list(v.rotation_euler)} for k,v in cameras.items()},
    'objects':{o.name:{'center':[o.location.x,-o.location.y,o.location.z],'size':list(o.dimensions)} for o in bpy.data.objects if o.type=='MESH'},
    'limitations':['All views are a geometric concept, not site-verified construction drawings.','Puja nook is compact; validate ritual space and entry clearance before finalising.','Approximate seat-eye to screen distance is about 1.6 m; select screen size and seating after measurement.'],
}
(OUT/'layout.json').write_text(json.dumps(manifest,indent=2))

selected=os.environ.get('L1_RENDER_VIEWS','').split(',')
def geometry_fingerprint():
    state={o.name:[list(row) for row in o.matrix_world] for o in bpy.data.objects if o.type=='MESH'}
    return hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
fingerprint=geometry_fingerprint()
render_evidence={}
for name,cam in cameras.items():
    if selected != [''] and name not in selected: continue
    # No furniture, door, wall or partition moves between these renders.
    scene.camera=cam
    roof.hide_render=(name=='01-top')
    assert geometry_fingerprint()==fingerprint, 'Geometry moved between cameras'
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    render_evidence[name]={'geometry_sha256':fingerprint,'ceiling_cutaway':roof.hide_render,'camera':cam.name}
(OUT/'render-evidence.json').write_text(json.dumps(render_evidence,indent=2))
