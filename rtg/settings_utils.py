import sys
from pathlib import Path

import tomllib


def load_config(file_path: Path):
    path = Path(file_path)
    try:
        with path.open("rb") as f:
            config = tomllib.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except tomllib.TOMLDecodeError as e:
        print(f"Error: Failed to parse TOML. {e}")
        return None


def get_integer_value(config: dict[str, object], key: str):
    raw_data = config.get(key)
    if (raw_data is None) or (not isinstance(raw_data, int)):
        print(
            f"The config file must have {key} and the value of {key} must be an integer"
        )
        sys.exit(1)

    return raw_data


def get_float_value(config: dict[str, object], key: str):
    raw_data = config.get(key)
    if (raw_data is None) or (not isinstance(raw_data, float)):
        print(f"The config file must have {key} and the value of {key} must be a float")
        sys.exit(1)

    return raw_data


def check_data_text_segment(
    text_origin: int, text_size: int, data_origin: int, data_size: int
) -> bool:
    text_end_in_byte: int = text_origin + text_size * 1024
    data_end_in_byte: int = data_origin + data_size * 1024

    if (
        abs(text_origin - data_end_in_byte) <= 1024 * 2
        or abs(text_end_in_byte - data_origin) <= 1024 * 2
    ):
        print("The Data segment and Text segment must be 1 KB apart!!!")
        return False

    return True


def get_segment_value(
    config: dict[str, object],
    first_key: str,
    second_key: str,
) -> int | None:
    raw_data = config.get(first_key)
    if (raw_data is None) or (not isinstance(raw_data, dict)):
        print(
            f'The config file must have {first_key}.\nThe structure of {first_key} must be:\n[{first_key}]\n{second_key} = "A value"\n...'
        )
        return None

    value = raw_data.get(second_key)
    if value is None:
        print(f"The config file must have {second_key}")
        return None

    if second_key == "SIZE":
        if not isinstance(value, int):
            print(f"The value of {second_key} must be an integer")
            return None

        return value

    if second_key == "ORIGIN":
        try:
            return int(value, 16)
        except ValueError:
            print(f"The value of {second_key} must be a hex string")
            return None

    return None
