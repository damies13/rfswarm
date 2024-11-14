import base64
import os


def save_html_embeded_image(base64_string: str, img_name: str, output_folder: str):
    decoded_data = base64.b64decode(base64_string)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img_name =  (img_name+"_image.png").replace(" ", "_")
    file_name = os.path.join(output_folder, img_name)

    with open(file_name, 'wb') as file:
        file.write(decoded_data)

    return file_name
