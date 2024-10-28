import os

from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from pandas import read_excel


def read_all_xlsx_sheets(xlsx_path: str) -> list:
    return load_workbook(xlsx_path, keep_links=False).sheetnames


def read_all_xlsx_text_data(xlsx_path: str) -> list:
    """
    Read all xlsx text data from all sheets.
    """
    wb = load_workbook(xlsx_path, keep_links=False)

    xlsx_tables = []
    for sheet in wb.sheetnames:
        sheet_content = read_xlsx_text_data_from_sheet(xlsx_path, sheet)
        xlsx_tables.append(sheet_content)

    print(xlsx_tables)
    return xlsx_tables


def read_xlsx_text_data_from_sheet(xlsx_path: str, sheet_name: str) -> list:
    """
    Read xlsx text data from given xlsx sheet.
    """
    all_excel_data_frame = read_excel(xlsx_path, sheet_name, keep_default_na=False, na_values=['NaN'])
    excel_data_list = all_excel_data_frame.values.tolist()

    for row_n in range(len(excel_data_list) - 1, -1, -1):
        for cell_n in range(len(excel_data_list[row_n]) - 1, -1, -1):
            if excel_data_list[row_n][cell_n] == "":
                excel_data_list[row_n].pop(cell_n)

        if len(excel_data_list[row_n]) == 0:
            excel_data_list.pop(row_n)

    return excel_data_list


def extract_image_from_xlsx_sheet(xlsx_path: str, xlsx_sheet: str, cell_id: str, output_folder: str, show_image: bool = False):
    """
    Extract an image from XLSX file from a given cell in specified sheet.
    Returns name of the saved image.
    """
    wb = load_workbook(xlsx_path, keep_links=False)
    sheet = wb[xlsx_sheet]
    try:
        image_loader = SheetImageLoader(sheet)
    except Exception as e:
        raise AssertionError("Error in SheetImageLoader:", e)
    try:
        image = image_loader.get(cell_id)
    except Exception as e:
        print(f"Cell {cell_id} doesn't contain an image. Exception: {e}")
        return 0
    if show_image:
        image.show()
    img_name = (xlsx_sheet + "_" + cell_id + "_image.png").replace(" ", "_")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image.save(os.path.join(output_folder, img_name))
    print(f"XLSX RFSwarm raport image saved as: {img_name}")

    return img_name
