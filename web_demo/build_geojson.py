import json
import os
from pathlib import Path

import pandas as pd


def _pick_street_image(sample_id: str) -> str | None:
    base = Path("data") / "svi_images"
    if not base.exists():
        return None

    preferred = base / f"{sample_id}_0.jpg"
    if preferred.exists():
        return f"../data/svi_images/{preferred.name}"

    matches = sorted(base.glob(f"{sample_id}_*.jpg"))
    if matches:
        return f"../data/svi_images/{matches[0].name}"
    return None


def build_points_geojson():
    agg_path = Path("data") / "aggregated_features.csv"
    if not agg_path.exists():
        raise FileNotFoundError(str(agg_path))

    df = pd.read_csv(agg_path)
    df["id"] = df["id"].astype(str)

    res_path = Path("data") / "model_results" / "residuals.csv"
    if res_path.exists():
        res = pd.read_csv(res_path)
        res["id"] = res["id"].astype(str)
        df = df.merge(res[["id", "residual"]], on="id", how="left")
    else:
        df["residual"] = pd.NA

    df["pred_LST"] = df["LST"] - df["residual"]

    q_hi = df["LST"].quantile(0.9)
    q_lo = df["LST"].quantile(0.1)

    def qclass(v: float) -> str:
        if v >= q_hi:
            return "hot"
        if v <= q_lo:
            return "cold"
        return "normal"

    df["quantile_class"] = df["LST"].apply(qclass)
    df["street_image"] = df["id"].apply(_pick_street_image)

    features = []
    for _, row in df.iterrows():
        lat = float(row["lat"])
        lon = float(row["lon"])
        props = row.to_dict()
        props["lat"] = lat
        props["lon"] = lon
        for k, v in list(props.items()):
            if pd.isna(v):
                props[k] = None
            elif isinstance(v, (pd.Timestamp,)):
                props[k] = str(v)
            elif isinstance(v, (float, int, str, bool)) or v is None:
                pass
            else:
                try:
                    props[k] = float(v)
                except Exception:
                    props[k] = str(v)

        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}

    out_dir = Path("web_demo") / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "points.geojson"
    out_path.write_text(json.dumps(geojson, ensure_ascii=False), encoding="utf-8")
    
    # Also write as JS for easier embedding in Streamlit/Static sites
    js_path = out_dir / "points_data.js"
    js_content = f"window.pointsData = {json.dumps(geojson, ensure_ascii=False)};"
    js_path.write_text(js_content, encoding="utf-8")
    
    return out_path


if __name__ == "__main__":
    out = build_points_geojson()
    print(f"Wrote {out}")

