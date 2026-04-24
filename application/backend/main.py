from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent.parent
MODEL_PATH = PROJECT_ROOT / "model" / "model.pkl"
OUTPUT_DIR = PROJECT_ROOT / "output"
SELECTED_FEATURES_PATH = OUTPUT_DIR / "selected_features.pkl"
LABEL_ENCODERS_PATH = OUTPUT_DIR / "label_encoders.pkl"
SCALER_PATH = OUTPUT_DIR / "scaler.pkl"

TARGET_COLUMN_CANDIDATES = {
    "failure_flag",
    "stress_level",
    "suitability_score",
}

# Fallback dari notebook cleaning jika file selected_features belum ada.
DEFAULT_SELECTED_FEATURES = [
    "suitability_score",
    "stress_level",
    "ph_stress_flag",
    "thermal_regime",
    "soil_temp_c",
    "moisture_regime",
    "air_temp_c",
    "nutrient_balance",
    "soil_moisture_pct",
    "moisture_limit_dry",
    "salinity_ec",
    "moisture_limit_wet",
    "buffering_capacity",
    "soil_ph",
    "cation_exchange_capacity",
    "bulk_density",
    "soil_type",
    "organic_matter_pct",
]


def _load_optional(path: Path) -> Any | None:
    if not path.exists():
        return None
    return joblib.load(path)


def _get_feature_names(model: Any) -> list[str]:
    if SELECTED_FEATURES_PATH.exists():
        loaded = joblib.load(SELECTED_FEATURES_PATH)
        if isinstance(loaded, list) and loaded:
            return [str(x) for x in loaded]

    model_features = getattr(model, "feature_names_in_", None)
    if model_features is not None:
        return [str(x) for x in model_features]

    return DEFAULT_SELECTED_FEATURES.copy()


def _infer_feature_type(name: str) -> str:
    if name in {"location_id", "soil_type", "moisture_regime", "thermal_regime", "nutrient_balance", "plant_category"}:
        return "categorical"
    return "numeric"


class PredictionInput(BaseModel):
    features: dict[str, Any] = Field(..., description="Pasangan feature_name -> value")


class BatchPredictionInput(BaseModel):
    items: list[PredictionInput]


app = FastAPI(
    title="Agro Environmental Prediction API",
    version="1.0.0",
    description="API backend untuk prediksi failure_flag pada data agro-environmental.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    raise RuntimeError(f"Gagal memuat model dari {MODEL_PATH}: {exc}") from exc

selected_features = _get_feature_names(model)
label_encoders = _load_optional(LABEL_ENCODERS_PATH)
scaler = _load_optional(SCALER_PATH)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Backend is running"}


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "features_count": len(selected_features),
    }


@app.get("/model-info")
def model_info() -> dict[str, Any]:
    classes = getattr(model, "classes_", None)

    return {
        "problem_type": "classification",
        "target": "failure_flag",
        "target_labels": [str(x) for x in classes] if classes is not None else ["0", "1"],
        "features": [
            {
                "name": name,
                "type": _infer_feature_type(name),
                "required": True,
            }
            for name in selected_features
        ],
        "has_scaler": scaler is not None,
        "has_label_encoders": label_encoders is not None,
    }


def _coerce_value(value: Any, feature_name: str) -> Any:
    # Value dibiarkan apa adanya untuk fitur kategorikal.
    if _infer_feature_type(feature_name) == "categorical":
        return value

    if value is None or value == "":
        raise ValueError(f"Feature '{feature_name}' tidak boleh kosong")

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Feature '{feature_name}' harus numerik") from exc


def _prepare_frame(raw_features: dict[str, Any]) -> pd.DataFrame:
    missing = [f for f in selected_features if f not in raw_features]
    if missing:
        raise ValueError(f"Feature wajib belum lengkap: {missing}")

    row: dict[str, Any] = {}
    for feature in selected_features:
        row[feature] = _coerce_value(raw_features.get(feature), feature)

    frame = pd.DataFrame([row], columns=selected_features)

    # Jika ada scaler terpisah hasil cleaning notebook, gunakan sebelum inferensi.
    if scaler is not None:
        transformed = scaler.transform(frame)
        frame = pd.DataFrame(transformed, columns=selected_features)

    return frame


def _predict_single(raw_features: dict[str, Any]) -> dict[str, Any]:
    frame = _prepare_frame(raw_features)

    prediction = model.predict(frame)[0]
    result: dict[str, Any] = {
        "prediction": int(prediction) if isinstance(prediction, (np.integer, int)) else prediction,
    }

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(frame)[0]
        result["probabilities"] = [float(x) for x in proba]
        if len(proba) > 1:
            result["failure_probability"] = float(proba[-1])

    return result


@app.post("/predict")
def predict(payload: PredictionInput) -> dict[str, Any]:
    try:
        return _predict_single(payload.features)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@app.post("/predict/batch")
def predict_batch(payload: BatchPredictionInput) -> dict[str, Any]:
    if not payload.items:
        raise HTTPException(status_code=400, detail="Payload items tidak boleh kosong")

    results: list[dict[str, Any]] = []
    for idx, item in enumerate(payload.items, start=1):
        try:
            pred = _predict_single(item.features)
            pred["index"] = idx
            results.append(pred)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Error pada item ke-{idx}: {exc}") from exc

    return {"count": len(results), "results": results}
