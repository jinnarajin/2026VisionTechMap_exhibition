"""Blender 4.x Scripting 작업 공간에서 실행하는 독립형 양개 창문 에셋.
외부 파일이나 패키지가 필요 없다. 기존 장면의 Window_Asset 컬렉션만 교체한다.
"""
import bpy
import math
from mathutils import Matrix

# -----------------------------------------------------------------------------
# 조정 가능한 치수 (m)와 비율. 정면은 -Y, 창문 바닥은 Z=0이다.
# 지나치게 작은 개구부나 음수 치수는 허용하지 않는다.
# -----------------------------------------------------------------------------
WINDOW_WIDTH = 1.20
WINDOW_HEIGHT = 1.50
FRAME_DEPTH = 0.16
FRAME_BORDER = 0.10              # 고정 프레임의 좌우/상하 폭
SASH_WIDTH = 0.495               # 두 창짝 사이에 10 mm 틈
SASH_HEIGHT = 1.30
SASH_DEPTH = 0.042
SASH_STILE = 0.052               # 창짝 세로 및 상하 가로 프레임 폭
MUNTIN_HEIGHT = 0.026            # 유리 사이 가로살 높이
GLASS_THICKNESS = 0.004
OPEN_ANGLE_DEG = 175             # 닫힌 상태에서 각 창짝이 실제 회전하는 각도
HINGE_LENGTH = 0.085
HINGE_RADIUS = 0.006
BEVEL_SIZE = 0.0015              # 작은 베벨로 몰딩 단차 보존
COLLECTION_NAME = "Window_Asset"

# 설정값이 서로 맞지 않으면 모델 생성 전에 원인을 알려준다.
if min(WINDOW_WIDTH, WINDOW_HEIGHT, FRAME_DEPTH, FRAME_BORDER, SASH_WIDTH,
       SASH_HEIGHT, SASH_DEPTH, SASH_STILE, MUNTIN_HEIGHT, GLASS_THICKNESS,
       HINGE_LENGTH, HINGE_RADIUS, BEVEL_SIZE) <= 0:
    raise ValueError("모든 크기와 베벨 값은 0보다 커야 합니다.")
if 2 * SASH_WIDTH > WINDOW_WIDTH - 2 * FRAME_BORDER:
    raise ValueError("두 창짝이 고정 프레임의 개구부보다 넓습니다.")
if SASH_HEIGHT > WINDOW_HEIGHT - 2 * FRAME_BORDER:
    raise ValueError("창짝 높이가 고정 프레임의 개구부보다 큽니다.")
if SASH_WIDTH <= 2 * SASH_STILE or SASH_HEIGHT <= 2 * SASH_STILE + 2 * MUNTIN_HEIGHT:
    raise ValueError("창짝의 유리 개구부가 너무 작습니다.")
if SASH_DEPTH >= FRAME_DEPTH:
    raise ValueError("창짝 깊이는 고정 프레임 깊이보다 작아야 합니다.")

# 컬렉션을 교체할 때 다른 컬렉션에도 연결된 오브젝트는 보존한다.
# 자식 컬렉션도 삭제하지 않고 연결만 해제한다. 삭제 전 사용자 데이터를 확인할 것.
old = bpy.data.collections.get(COLLECTION_NAME)
if old is not None:
    for child in list(old.children):
        old.children.unlink(child)
    for obj in list(old.objects):
        if len(obj.users_collection) > 1:
            old.objects.unlink(obj)
        else:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)

collection = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(collection)

# 기존 장면의 단위 설정은 바꾸지 않는다. Blender 기본 길이 단위 1을 1m로 사용한다.
def material(name, color, metallic=0.0, roughness=0.35, transmission=0.0):
    """새 재질을 만들어 기존 재질을 덮어쓰지 않는다."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        def set_input(names, value):
            for key in names:
                socket = bsdf.inputs.get(key)
                if socket is not None:
                    socket.default_value = value
                    break
        set_input(("Base Color",), color)
        set_input(("Metallic",), metallic)
        set_input(("Roughness",), roughness)
        # Blender 버전에 따라 소켓 이름이 바뀔 수 있다.
        set_input(("Transmission Weight", "Transmission"), transmission)
        set_input(("IOR",), 1.45)
    return mat

paint = material("Window_Ivory_Paint", (0.82, 0.80, 0.72, 1.0), roughness=0.3)
glass = material("Window_Pale_Glass", (0.78, 0.91, 0.94, 1.0), roughness=0.08, transmission=1.0)
metal = material("Window_Hinge_Metal", (0.48, 0.50, 0.49, 1.0), metallic=0.8, roughness=0.28)

def mesh_object(name, vertices, faces, mat, parent=None, bevel=BEVEL_SIZE):
    """선택 상태에 의존하지 않고 독립 메쉬와 작은 비파괴 베벨을 만든다."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent  # 정점은 부모 원점 기준의 로컬 좌표다.
    if bevel > 0:
        mod = obj.modifiers.new("Small_Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj

def box(name, center, size, mat, parent=None, bevel=BEVEL_SIZE):
    x, y, z = center
    a, b, c = (v / 2 for v in size)
    verts = [(x-a,y-b,z-c), (x+a,y-b,z-c), (x+a,y+b,z-c), (x-a,y+b,z-c),
             (x-a,y-b,z+c), (x+a,y-b,z+c), (x+a,y+b,z+c), (x-a,y+b,z+c)]
    faces = [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5),
             (2,3,7,6), (3,0,4,7)]
    return mesh_object(name, verts, faces, mat, parent, min(bevel, min(size) * 0.2))

def cylinder(name, center, radius, height, mat, parent=None, sides=24):
    """수직 Z축 경첩 통. 메쉬 좌표는 부모의 로컬 좌표를 사용한다."""
    x, y, z = center
    vertices = []
    for dz in (-height / 2, height / 2):
        vertices.extend((x + radius * math.cos(2*math.pi*i/sides),
                         y + radius * math.sin(2*math.pi*i/sides), z + dz)
                        for i in range(sides))
    faces = [tuple(reversed(range(sides))), tuple(range(sides, 2*sides))]
    faces.extend((i, (i+1)%sides, (i+1)%sides+sides, i+sides) for i in range(sides))
    return mesh_object(name, vertices, faces, mat, parent, min(BEVEL_SIZE * 0.5, radius * 0.15))

def ring(prefix, outer_w, outer_h, border, y, depth):
    """네 개의 선형 부재로 단차가 있는 사각 몰딩을 구성한다."""
    zmid = WINDOW_HEIGHT / 2
    for side, sign in (("Left", -1), ("Right", 1)):
        box(prefix + "_" + side, (sign * (outer_w-border)/2, y, zmid),
            (border, depth, outer_h), paint)
    for side, sign in (("Bottom", -1), ("Top", 1)):
        box(prefix + "_" + side, (0, y, zmid + sign*(outer_h-border)/2),
            (outer_w-2*border, depth, border), paint)

# 바깥 고정 프레임과 전면의 서로 다른 폭·깊이를 가진 몰딩 층.
ring("Fixed_Frame", WINDOW_WIDTH, WINDOW_HEIGHT, FRAME_BORDER, 0, FRAME_DEPTH)
front = -FRAME_DEPTH / 2
ring("Molding_Outer", WINDOW_WIDTH, WINDOW_HEIGHT, FRAME_BORDER * 0.20, front-0.004, 0.008)
ring("Molding_Middle", WINDOW_WIDTH-FRAME_BORDER*0.42, WINDOW_HEIGHT-FRAME_BORDER*0.42,
     FRAME_BORDER*0.16, front-0.007, 0.014)
ring("Molding_Inner", WINDOW_WIDTH-FRAME_BORDER*1.20, WINDOW_HEIGHT-FRAME_BORDER*1.20,
     FRAME_BORDER*0.17, front-0.004, 0.008)

# 회전축은 프레임의 정면보다 앞에 둔다. 이 간격은 175도 개방 시 창짝과
# 프레임의 간섭을 줄이며, 경첩 형상도 해당 축을 중심으로 배치한다.
opening_half = WINDOW_WIDTH/2 - FRAME_BORDER
hinge_y = front - 0.014
sash_center_y = 0.006 + SASH_DEPTH/2  # 축 뒤쪽에 창짝의 닫힌 위치
sash_bottom = (WINDOW_HEIGHT - SASH_HEIGHT)/2
clear_h = SASH_HEIGHT - 2*SASH_STILE - 2*MUNTIN_HEIGHT
pane_h = clear_h / 3
inner_w = SASH_WIDTH - 2*SASH_STILE

def make_sash(label, side):
    """side=-1은 왼쪽, +1은 오른쪽. 빈 오브젝트가 수직 경첩 축이다."""
    pivot = bpy.data.objects.new(label + "_Hinge_Pivot", None)
    collection.objects.link(pivot)
    pivot.empty_display_type = 'PLAIN_AXES'
    pivot.empty_display_size = 0.045
    pivot.location = (side * opening_half, hinge_y, sash_bottom)
    # 닫힌 창짝은 안쪽으로 뻗고, 두 창짝은 정면 쪽으로 반대 방향 회전한다.
    pivot.rotation_euler.z = side * math.radians(OPEN_ANGLE_DEG)
    direction = -side
    mid_x = direction * SASH_WIDTH/2
    for n, x in (("Hinge_Stile", direction*SASH_STILE/2),
                 ("Meeting_Stile", direction*(SASH_WIDTH-SASH_STILE/2))):
        box(label + "_" + n, (x, sash_center_y, SASH_HEIGHT/2),
            (SASH_STILE, SASH_DEPTH, SASH_HEIGHT), paint, pivot)
    for n, z in (("Bottom_Rail", SASH_STILE/2), ("Top_Rail", SASH_HEIGHT-SASH_STILE/2)):
        box(label + "_" + n, (mid_x, sash_center_y, z),
            (inner_w, SASH_DEPTH, SASH_STILE), paint, pivot)
    for i in range(3):
        z0 = SASH_STILE + i*(pane_h+MUNTIN_HEIGHT)
        box(label + "_Glass_" + str(i+1), (mid_x, sash_center_y, z0+pane_h/2),
            (inner_w, GLASS_THICKNESS, pane_h), glass, pivot, 0)
        if i < 2:
            zbar = z0 + pane_h + MUNTIN_HEIGHT/2
            box(label + "_Muntin_" + str(i+1), (mid_x, sash_center_y, zbar),
                (inner_w, SASH_DEPTH, MUNTIN_HEIGHT), paint, pivot)
    # 유리 안쪽 테두리에 가는 선형 몰딩을 추가한다.
    bead = min(0.006, SASH_STILE*0.2, pane_h*0.1)
    for i in range(3):
        z0 = SASH_STILE + i*(pane_h+MUNTIN_HEIGHT)
        for n, x in (("Outer", direction*(SASH_STILE+bead/2)),
                     ("Inner", direction*(SASH_WIDTH-SASH_STILE-bead/2))):
            box(f"{label}_Pane_{i+1}_Bead_{n}", (x, sash_center_y-SASH_DEPTH/2-bead/2, z0+pane_h/2),
                (bead, bead, pane_h), paint, pivot)
        for n, z in (("Bottom", z0+bead/2), ("Top", z0+pane_h-bead/2)):
            box(f"{label}_Pane_{i+1}_Bead_{n}", (mid_x, sash_center_y-SASH_DEPTH/2-bead/2, z),
                (inner_w-2*bead, bead, bead), paint, pivot)
    for i, z in enumerate((SASH_HEIGHT*0.18, SASH_HEIGHT*0.82), 1):
        # 축과 고정판은 고정 프레임에 남고, 창짝판과 일부 너클은 창짝과 함께 회전한다.
        world_x = side * opening_half
        world_z = sash_bottom + z
        cylinder(f"{label}_Hinge_{i}_Pin", (world_x, hinge_y, world_z),
                 HINGE_RADIUS*0.55, HINGE_LENGTH, metal)
        box(f"{label}_Hinge_{i}_Frame_Leaf", (world_x+side*0.014, hinge_y+0.007, world_z),
            (0.028, 0.004, HINGE_LENGTH*0.78), metal)
        box(f"{label}_Hinge_{i}_Sash_Leaf", (direction*0.014, 0.007, z),
            (0.028, 0.004, HINGE_LENGTH*0.78), metal, pivot)
        for j in range(3):
            zz = z + (j-1)*HINGE_LENGTH*0.25
            if j == 1:
                cylinder(f"{label}_Hinge_{i}_Sash_Knuckle", (0, 0, zz),
                         HINGE_RADIUS, HINGE_LENGTH*0.23, metal, pivot)
            else:
                cylinder(f"{label}_Hinge_{i}_Frame_Knuckle_{j+1}", (world_x, hinge_y, sash_bottom+zz),
                         HINGE_RADIUS, HINGE_LENGTH*0.23, metal)

make_sash("Left_Sash", -1)
make_sash("Right_Sash", 1)

# 투명 유리는 렌더 엔진과 뷰포트 표시 모드에 따라 다르게 보일 수 있다.
# 각 창짝 피벗의 Z 회전을 0으로 바꾸면 닫힌 상태를 확인할 수 있다.
