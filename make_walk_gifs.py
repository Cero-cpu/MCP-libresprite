import sys
from PIL import Image
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

from generate_topdown_walk import down_imgs, up_imgs, right_imgs, left_imgs, W, H

def make_gif(imgs, name, duration=140):
    upscaled = [im.resize((W * 6, H * 6), Image.NEAREST) for im in imgs]
    quantized = [im.convert('RGB').quantize(colors=32, method=2) for im in upscaled]
    quantized[0].save(
        f"{TARGET_DIR}/{name}.gif",
        save_all=True, append_images=quantized[1:],
        loop=0, duration=duration, optimize=False
    )

make_gif(down_imgs, "walk_down")
make_gif(up_imgs, "walk_up")
make_gif(right_imgs, "walk_right")
make_gif(left_imgs, "walk_left")

# Combined 4-direction demo GIF (48x48 scaled to 288x288)
combo_frames = []
for i in range(4):
    c_img = Image.new('RGBA', (W * 2, H * 2), (240, 240, 245, 255))
    c_img.paste(down_imgs[i], (0, 0), down_imgs[i])
    c_img.paste(up_imgs[i], (W, 0), up_imgs[i])
    c_img.paste(right_imgs[i], (0, H), right_imgs[i])
    c_img.paste(left_imgs[i], (W, H), left_imgs[i])
    c_img_up = c_img.resize((W * 2 * 6, H * 2 * 6), Image.NEAREST)
    combo_frames.append(c_img_up.convert('RGB').quantize(colors=48, method=2))

combo_frames[0].save(
    f"{TARGET_DIR}/walk_all_demo.gif",
    save_all=True, append_images=combo_frames[1:],
    loop=0, duration=150, optimize=False
)
combo_frames[0].save(
    f"{BRAIN}/walk_all_demo.gif",
    save_all=True, append_images=combo_frames[1:],
    loop=0, duration=150, optimize=False
)

print("GIFs generated successfully")

