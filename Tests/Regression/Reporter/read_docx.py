import os
import re
import subprocess

from docx import Document
from docx.oxml.shared import OxmlElement, qn
from PIL import Image


def read_paragraphs_docx_file(docx_path: str) -> dict:
    """Read paragraphs docx file and return dictionary."""
    doc = Document(docx_path)

    doc_sections: dict = {}
    current_heading = None

    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith('Heading'):
            current_heading = paragraph.text.strip()
            doc_sections[current_heading] = []

        elif paragraph.text.strip():
            if current_heading:
                doc_sections[current_heading].append(paragraph.text.strip())
            else:
                doc_sections.setdefault('No Heading', []).append(paragraph.text.strip())

    return doc_sections


def update_docx_with_libreoffice(docx_path: str):
    """Not working currently."""
    command = [
        'libreoffice', '--headless', '--convert-to', 'docx',
        '--outdir', os.path.dirname(docx_path), docx_path
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise Exception(f"LibreOffice failed: {process.stderr.decode('utf-8')}")
    else:
        print(f"Document fields updated successfully: {docx_path}")


def update_table_of_contents(docx_path: str):
    """Set updateFields in DOCX file to true."""
    doc = Document(docx_path)

    settings_element = doc.settings.element
    update_fields_element = OxmlElement('w:updateFields')
    update_fields_element.set(qn('w:val'), 'true')

    settings_element.append(update_fields_element)

    doc.save(docx_path)


def convert_image_to_black_and_white(image_path: str):
    """Convert given image to black and white.
    All colours except white will be converted to black."""
    image = Image.open(image_path)
    gray_image = image.convert("L")
    bw_image = gray_image.point(lambda x: 0 if x < 255 else 255, '1')
    bw_image.save(image_path)


def extract_images_from_docx(docx_path: str, output_folder: str, black_and_wite=False) -> list:
    """
    Extract all images from DOCX one by one.
    Returns list of the saved images.
    """
    doc = Document(docx_path)
    saved_images = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img_name = os.path.basename(rel.target_ref)
            img_data = rel.target_part.blob

            with open(os.path.join(output_folder, img_name), "wb") as img_file:
                img_file.write(img_data)
                if black_and_wite:
                    convert_image_to_black_and_white(os.path.join(output_folder, img_name))
                print(f"DOCX RFSwarm raport image saved as: {img_name}")
                saved_images.append(img_name)

    return saved_images


def extract_tables_from_docx(docx_path: str) -> list:
    """
    Extract all tables from DOCX one by one.
    Returns nested lists of tables.
    Note: For RFSwarm DOCX raport the first value of each row will be empty.
    """
    doc = Document(docx_path)
    tables = []

    def iter_unique_row_cells(row):
        """Generate cells in given row skipping empty grid cells."""
        last_cell_tc = None
        for cell in row.cells:
            this_cell_tc = cell._tc
            if this_cell_tc is last_cell_tc:
                continue
            last_cell_tc = this_cell_tc
            yield cell

    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in iter_unique_row_cells(row):
                row_data.append(cell.text)
            table_data.append(row_data)
        tables.append(table_data)

    return tables


def sort_docx_images(docx_images: list) -> list:
    """Sort given list using natural sorting"""
    def natural_sort_key(filename):
        return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', filename)]

    return sorted(docx_images, key=natural_sort_key)
