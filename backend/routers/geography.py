from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import GeoMapState
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/geography", tags=["Geospatial Intelligence"])

STATE_COORDINATES = {
    "SP": (-23.5505, -46.6333),
    "RJ": (-22.9068, -43.1729),
    "MG": (-19.9245, -43.9352),
    "RS": (-30.0346, -51.2177),
    "PR": (-25.4284, -49.2733),
    "SC": (-27.5954, -48.5480),
    "BA": (-12.9777, -38.5016),
    "DF": (-15.7942, -47.8822),
    "GO": (-16.6869, -49.2648),
    "ES": (-20.3155, -40.3128),
    "PE": (-8.0476, -34.8770),
    "CE": (-3.7319, -38.5267),
    "PA": (-1.4558, -48.4902),
    "MT": (-15.6014, -56.0979),
    "MA": (-2.5387, -44.2828),
    "MS": (-20.4697, -54.6201),
    "PB": (-7.1195, -34.8450),
    "PI": (-5.0919, -42.8034),
    "RN": (-5.7945, -35.2110),
    "AL": (-9.6658, -35.7350),
    "SE": (-10.9472, -37.0731),
    "TO": (-10.2491, -48.3243),
    "RO": (-8.7619, -63.9039),
    "AM": (-3.1190, -60.0217),
    "AC": (-9.9753, -67.8249),
    "AP": (0.0356, -51.0705),
    "RR": (2.8235, -60.6758)
}

@router.get("/map-data", response_model=List[GeoMapState], summary="Get state geolocation center points and delivery metrics")
def get_map_data(db: Session = Depends(get_db)):
    metrics = AnalyticsService.get_state_metrics(db)
    result: List[GeoMapState] = []

    for m in metrics:
        lat, lng = STATE_COORDINATES.get(m.state, (-14.235, -51.925))
        sla = "DELAYED" if m.late_rate > 10.0 else "OPTIMAL" if m.late_rate < 5.0 else "STANDARD"
        result.append(GeoMapState(
            state=m.state,
            lat=lat,
            lng=lng,
            customer_count=m.customer_count,
            orders_count=m.orders_count,
            total_revenue=m.total_revenue,
            avg_delivery_days=m.avg_delivery_days,
            late_rate=m.late_rate,
            sla_status=sla
        ))
    return result
