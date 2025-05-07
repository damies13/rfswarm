from PIL import Image


def convert_image_to_black_and_white(image_path: str):
	"""Convert given image to black and white.
	All colours except white will be converted to black."""
	image = Image.open(image_path)
	gray_image = image.convert("L")
	bw_image = gray_image.point(lambda x: 0 if x < 255 else 255, '1')
	bw_image.save(image_path)
