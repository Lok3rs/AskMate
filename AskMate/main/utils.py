import os
import secrets

from PIL import Image
from flask_login import current_user
from flask import current_app


def save_picture(form_picture, static_dir_name, output_size):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, '../static', static_dir_name, picture_fn)
    # Resize picture before save
    output_size = output_size
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    # Deleting previous picture
    prev_picture = os.path.join(current_app.root_path, '../static', static_dir_name, current_user.image_file)
    if os.path.exists(prev_picture) and not current_user.image_file == "default.jpg":
        os.remove(prev_picture)
    return picture_fn
