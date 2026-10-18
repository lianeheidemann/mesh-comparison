import numpy as np


def add_default_lights(scene):
    import pyrender

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)

    poses = []
    poses.append(np.eye(4))

    p2 = np.eye(4)
    p2[:3, 3] = [2, 2, 2]
    poses.append(p2)

    p3 = np.eye(4)
    p3[:3, 3] = [-2, -2, 2]
    poses.append(p3)

    for p in poses:
        scene.add(light, pose=p)


def render_ortho_rgba(mesh, camera_cfg, bg_color, width=1600, height=1200, smooth=True):
    """Render ``mesh`` with an orthographic camera and return the RGBA image (uint8)."""
    import pyrender

    scene = pyrender.Scene(
        bg_color=np.asarray(bg_color, dtype=np.float32),
        ambient_light=np.array([0.35, 0.35, 0.35, 1.0])
    )

    scene.add(pyrender.Mesh.from_trimesh(mesh, smooth=smooth))

    cam = pyrender.OrthographicCamera(
        xmag=camera_cfg["xmag"],
        ymag=camera_cfg["ymag"],
        znear=0.01,
        zfar=camera_cfg["zfar"]
    )
    scene.add(cam, pose=camera_cfg["pose"])
    add_default_lights(scene)

    renderer = pyrender.OffscreenRenderer(viewport_width=width, viewport_height=height)
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    renderer.delete()

    return color
