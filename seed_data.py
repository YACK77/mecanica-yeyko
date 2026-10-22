from database import SessionLocal
import models

def seed():
    db = SessionLocal()
    try:
        # 1. Crear usuario administrador inicial
        admin = db.query(models.User).filter(models.User.email == "admin@mecanicayeyko.com").first()
        if not admin:
            admin = models.User(
                nombre_completo="Ivan Chiri Lupinta",
                email="admin@mecanicayeyko.com",
                password_hash="pbkdf2_sha256$hashed$admin123",  # Demo
                rol="ADMIN",
                activo=True
            )
            db.add(admin)
            print("[OK] Usuario Admin creado: admin@mecanicayeyko.com")

        # 2. Crear repuestos y servicios iniciales del taller
        repuestos = [
            {
                "sku": "ACE-10W40-MOBIL",
                "nombre": "Aceite de Motor Mobil Super 10W-40 (Galón)",
                "descripcion": "Lubricante semisintético de alto rendimiento para motores a gasolina.",
                "categoria": "Lubricantes",
                "precio_compra": 140.00,
                "precio_venta": 190.00,
                "stock_actual": 12,
                "stock_minimo": 4,
                "es_servicio": False
            },
            {
                "sku": "FLT-ACE-HILUX",
                "nombre": "Filtro de Aceite Toyota Hilux / Fortuner",
                "descripcion": "Elemento filtrante original para motor Toyota 1KD / 2GD.",
                "categoria": "Filtros",
                "precio_compra": 35.00,
                "precio_venta": 60.00,
                "stock_actual": 8,
                "stock_minimo": 3,
                "es_servicio": False
            },
            {
                "sku": "PAS-FRN-COROLLA",
                "nombre": "Pastillas de Freno Delanteras Cerámicas",
                "descripcion": "Juego de pastillas de freno delanteras para Toyota Corolla / Caldina.",
                "categoria": "Frenos",
                "precio_compra": 95.00,
                "precio_venta": 150.00,
                "stock_actual": 5,
                "stock_minimo": 2,
                "es_servicio": False
            },
            {
                "sku": "BUJ-NGK-IRIDIUM",
                "nombre": "Bujías de Encendido NGK Iridium BKR6EIX (Pack x4)",
                "descripcion": "Bujías de punta fina de iridio de alta durabilidad.",
                "categoria": "Encendido",
                "precio_compra": 120.00,
                "precio_venta": 180.00,
                "stock_actual": 6,
                "stock_minimo": 2,
                "es_servicio": False
            },
            {
                "sku": "SRV-CAMBIO-ACEITE",
                "nombre": "Servicio de Cambio de Aceite y Filtro + Revisión",
                "descripcion": "Mano de obra calificada en fosa: drenado, cambio de filtro y reseteo.",
                "categoria": "Servicios",
                "precio_compra": 0.00,
                "precio_venta": 50.00,
                "stock_actual": 999,
                "stock_minimo": 0,
                "es_servicio": True
            }
        ]

        for r in repuestos:
            existente = db.query(models.Product).filter(models.Product.sku == r["sku"]).first()
            if not existente:
                prod = models.Product(**r)
                db.add(prod)
                db.flush()
                # Registrar en Kardex el inventario inicial si no es servicio
                if not prod.es_servicio:
                    mov = models.InventoryMovement(
                        product_id=prod.id,
                        tipo_movimiento="ENTRADA",
                        cantidad=prod.stock_actual,
                        stock_anterior=0,
                        stock_posterior=prod.stock_actual,
                        referencia_origen="INVENTARIO_INICIAL",
                        motivo="Poblado inicial para sustentación de Mecánica Yeyko"
                    )
                    db.add(mov)
                print(f"[OK] Repuesto agregado: {r['nombre']} (Stock: {r['stock_actual']})")

        db.commit()
        print("\nBase de datos poblada con exito con datos de Mecanica Yeyko!")
    except Exception as e:
        db.rollback()
        print(f"Error al poblar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
