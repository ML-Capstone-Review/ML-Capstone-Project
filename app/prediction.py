"""Prediction boundary: accepts notebook-shaped inputs and returns no UI copy."""
from .model import build_input_frame


def predict_feedback(model, values, bounds, numeric, categorical):
    frame=build_input_frame(values,bounds,numeric,categorical)
    return int(model.predict(frame)[0])
