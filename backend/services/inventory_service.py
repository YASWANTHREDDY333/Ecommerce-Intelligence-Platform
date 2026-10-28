from typing import List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.schemas import InventorySummary, InventoryAlertResponse, InventoryItemResponse
from backend.services.analytics_service import invalidate_cache

class InventoryService:

    @staticmethod
    def get_summary(db: Session) -> InventorySummary:
        query = text("""
            SELECT 
                COUNT(*) as total_skus,
                SUM(CASE WHEN current_stock <= safety_stock THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN current_stock > safety_stock AND current_stock <= reorder_level THEN 1 ELSE 0 END) as low_stock_count,
                SUM(CASE WHEN current_stock > reorder_level THEN 1 ELSE 0 END) as healthy_count
            FROM inventory
        """)
        row = db.execute(query).fetchone()
        open_alerts = db.execute(text("SELECT COUNT(*) FROM inventory_alerts WHERE alert_status = 'OPEN'")).scalar() or 0

        return InventorySummary(
            total_skus=int(row[0]) if row else 0,
            critical_count=int(row[1]) if row else 0,
            low_stock_count=int(row[2]) if row else 0,
            healthy_count=int(row[3]) if row else 0,
            open_alerts_count=open_alerts
        )

    @staticmethod
    def get_alerts(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        alert_type: Optional[str] = None,
        alert_status: Optional[str] = None
    ) -> Tuple[List[InventoryAlertResponse], int]:
        where_clauses = []
        if alert_type:
            where_clauses.append(f"ia.alert_type = '{alert_type}'")
        if alert_status:
            where_clauses.append(f"ia.alert_status = '{alert_status}'")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = text(f"SELECT COUNT(*) FROM inventory_alerts ia {where_sql}")
        total_count = db.execute(count_sql).scalar() or 0

        query = text(f"""
            SELECT 
                ia.alert_id,
                ia.product_id,
                COALESCE(p.product_category_name_english, 'Unknown') as category,
                ia.alert_type,
                ia.current_stock,
                ia.reorder_level,
                ia.recommended_reorder_quantity,
                ia.alert_message,
                ia.alert_status
            FROM inventory_alerts ia
            LEFT JOIN products p ON ia.product_id = p.product_id
            {where_sql}
            ORDER BY 
                CASE WHEN ia.alert_type = 'CRITICAL' THEN 1 ELSE 2 END,
                ia.recommended_reorder_quantity DESC
            LIMIT {limit} OFFSET {offset}
        """)
        rows = db.execute(query).fetchall()
        result = [
            InventoryAlertResponse(
                alert_id=int(r[0]),
                product_id=r[1],
                category=r[2].replace("_", " ").title(),
                alert_type=r[3],
                current_stock=int(r[4]),
                reorder_level=int(r[5]),
                recommended_reorder_quantity=int(r[6]),
                alert_message=r[7],
                alert_status=r[8]
            ) for r in rows
        ]
        return result, total_count

    @staticmethod
    def get_items(
        db: Session,
        search: Optional[str] = None,
        stock_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[InventoryItemResponse], int]:
        where_clauses = []
        if search:
            clean_search = search.replace("'", "''").strip()
            where_clauses.append(f"(inv.product_id LIKE '%{clean_search}%' OR p.product_category_name_english LIKE '%{clean_search}%')")
        
        if stock_status == "CRITICAL":
            where_clauses.append("inv.current_stock <= inv.safety_stock")
        elif stock_status == "LOW":
            where_clauses.append("inv.current_stock > inv.safety_stock AND inv.current_stock <= inv.reorder_level")
        elif stock_status == "HEALTHY":
            where_clauses.append("inv.current_stock > inv.reorder_level")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = text(f"""
            SELECT COUNT(*) 
            FROM inventory inv
            LEFT JOIN products p ON inv.product_id = p.product_id
            {where_sql}
        """)
        total_count = db.execute(count_sql).scalar() or 0

        query = text(f"""
            SELECT 
                inv.product_id,
                COALESCE(p.product_category_name_english, 'Unknown') as category,
                inv.current_stock,
                inv.reorder_level,
                inv.safety_stock,
                inv.average_daily_sales,
                inv.supplier_lead_time_days
            FROM inventory inv
            LEFT JOIN products p ON inv.product_id = p.product_id
            {where_sql}
            ORDER BY inv.current_stock ASC
            LIMIT {limit} OFFSET {offset}
        """)
        rows = db.execute(query).fetchall()
        result = []
        for r in rows:
            c_stock = int(r[2])
            r_level = int(r[3])
            s_stock = int(r[4])
            if c_stock <= s_stock:
                status = "CRITICAL"
            elif c_stock <= r_level:
                status = "LOW"
            else:
                status = "HEALTHY"

            result.append(InventoryItemResponse(
                product_id=r[0],
                category=r[1].replace("_", " ").title(),
                current_stock=c_stock,
                reorder_level=r_level,
                safety_stock=s_stock,
                average_daily_sales=float(r[5]),
                supplier_lead_time_days=int(r[6]),
                stock_status=status
            ))
        return result, total_count

    @staticmethod
    def update_alert_status(db: Session, alert_id: int, new_status: str) -> bool:
        stmt = text("""
            UPDATE inventory_alerts 
            SET alert_status = :new_status 
            WHERE alert_id = :alert_id
        """)
        res = db.execute(stmt, {"new_status": new_status, "alert_id": alert_id})
        db.commit()
        invalidate_cache("overview_kpis")
        return res.rowcount > 0

    @staticmethod
    def restock_product(db: Session, product_id: str, quantity: int) -> bool:
        update_inv = text("""
            UPDATE inventory 
            SET current_stock = current_stock + :qty,
                last_updated = NOW()
            WHERE product_id = :product_id
        """)
        db.execute(update_inv, {"qty": quantity, "product_id": product_id})

        # Update or resolve matching alerts
        resolve_alerts = text("""
            UPDATE inventory_alerts
            SET current_stock = current_stock + :qty,
                alert_status = 'RESOLVED'
            WHERE product_id = :product_id
        """)
        db.execute(resolve_alerts, {"qty": quantity, "product_id": product_id})
        db.commit()
        invalidate_cache()
        return True
