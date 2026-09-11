from typing import Any


def str2bool(val: Any) -> bool:
	"""Convert string/any representation to boolean ('yes', 'true', 't', '1' -> True)."""
	return str(val).lower() in ("yes", "true", "t", "1")
