"""Input checks derived from the project dataset and model schema."""
from .schema import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS


def validate_feedback(values, data):
    errors=[]
    for col in CATEGORICAL_COLUMNS:
        if values.get(col) not in set(data[col].dropna().unique()):
            errors.append(f"Choose a valid value for {col}.")
    for col in NUMERIC_COLUMNS:
        try: value=float(values[col])
        except (KeyError,TypeError,ValueError):
            errors.append(f"Enter a valid value for {col}."); continue
        if not float(data[col].min()) <= value <= float(data[col].max()):
            errors.append(f"{col} is outside the range represented in the project dataset.")
    return errors
