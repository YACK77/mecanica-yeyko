from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
from database import engine, get_db

# Crear tablas automáticamente en la base de datos (Supabase) si no existen
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Advertencia al verificar tablas: {e}")

app = FastAPI(
    title="API Mecánica Yeyko - Gestión, Ventas e Inventario",
    description="Backend oficial para el sistema de control operativo de 'Mecánica Yeyko'. Desarrollado con FastAPI y Supabase PostgreSQL.",
    version="1.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de rutas de archivos estáticos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", tags=["Interfaz Web"])
def read_root():
    """Servir la interfaz web visual amigable de Mecánica Yeyko."""
    posibles_rutas = [
        os.path.join(BASE_DIR, "static", "index.html"),
        os.path.join(BASE_DIR, "index.html"),
        os.path.join(BASE_DIR, "api", "index.html"),
        "static/index.html",
        "index.html"
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                from fastapi.responses import HTMLResponse
                return HTMLResponse(content=f.read())

    return {
        "sistema": "Mecánica Yeyko - Sistema de Gestión y Control Operativo",
        "estado": "En línea",
        "documentacion_swagger": "/docs"
    }




# ==========================================================
# 1. CATÁLOGO E INVENTARIO DE REPUESTOS (products)
# ==========================================================
@app.get("/api/v1/products", response_model=List[schemas.ProductOut], tags=["Inventario"])
def list_products(db: Session = Depends(get_db)):
    """Obtener catálogo completo de repuestos y servicios del taller."""
    return db.query(models.Product).filter(models.Product.activo == True).all()


@app.post("/api/v1/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED, tags=["Inventario"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo repuesto o servicio automotriz en el catálogo."""
    db_product = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if db_product:
        raise HTTPException(
            status_code=400,
            detail=f"El código SKU '{product.sku}' ya está registrado en el inventario."
        )

    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Si se crea con stock inicial mayor a 0, registrar en Kardex
    if new_product.stock_actual > 0:
        mov = models.InventoryMovement(
            product_id=new_product.id,
            tipo_movimiento="ENTRADA",
            cantidad=new_product.stock_actual,
            stock_anterior=0,
            stock_posterior=new_product.stock_actual,
            referencia_origen="INVENTARIO_INICIAL",
            motivo="Carga inicial de producto al catálogo"
        )
        db.add(mov)
        db.commit()

    return new_product


@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductOut, tags=["Inventario"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Consultar un repuesto específico por su ID."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Repuesto no encontrado")
    return product


# ==========================================================
# 2. PROVEEDORES Y COMPRAS (purchases & purchase_items)
# ==========================================================
@app.post("/api/v1/purchases", response_model=schemas.PurchaseOut, status_code=status.HTTP_201_CREATED, tags=["Compras"])
def register_purchase(purchase_in: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    """
    Registrar ingreso de mercancía de proveedores.
    Suma stock a los repuestos y crea el movimiento en Kardex.
    """
    if not purchase_in.items:
        raise HTTPException(status_code=400, detail="La compra debe incluir al menos un repuesto.")

    total_calculado = 0.0
    items_to_create = []
    movements_to_create = []

    try:
        for item in purchase_in.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Repuesto con ID {item.product_id} no existe")

            subtotal = item.cantidad * item.costo_unitario
            total_calculado += subtotal

            stock_anterior = product.stock_actual
            product.stock_actual += item.cantidad
            product.precio_compra = item.costo_unitario  # Actualiza último costo
            stock_posterior = product.stock_actual

            items_to_create.append({
                "product_id": product.id,
                "cantidad": item.cantidad,
                "costo_unitario": item.costo_unitario,
                "subtotal": subtotal
            })

            movements_to_create.append({
                "product_id": product.id,
                "tipo_movimiento": "ENTRADA",
                "cantidad": item.cantidad,
                "stock_anterior": stock_anterior,
                "stock_posterior": stock_posterior
            })

        # Cabecera de compra
        db_purchase = models.Purchase(
            proveedor_nombre=purchase_in.proveedor_nombre,
            proveedor_nit=purchase_in.proveedor_nit,
            numero_factura=purchase_in.numero_factura,
            total_compra=total_calculado,
            usuario_id=purchase_in.usuario_id
        )
        db.add(db_purchase)
        db.flush()

        # Detalle de compra
        for it in items_to_create:
            db_item = models.PurchaseItem(
                purchase_id=db_purchase.id,
                product_id=it["product_id"],
                cantidad=it["cantidad"],
                costo_unitario=it["costo_unitario"],
                subtotal=it["subtotal"]
            )
            db.add(db_item)

        # Kardex
        for mov in movements_to_create:
            db_mov = models.InventoryMovement(
                product_id=mov["product_id"],
                tipo_movimiento=mov["tipo_movimiento"],
                cantidad=mov["cantidad"],
                stock_anterior=mov["stock_anterior"],
                stock_posterior=mov["stock_posterior"],
                referencia_origen=f"COMPRA #{db_purchase.id}",
                motivo=f"Ingreso de proveedor: {purchase_in.proveedor_nombre}"
            )
            db.add(db_mov)

        db.commit()
        db.refresh(db_purchase)
        return db_purchase

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar compra: {str(e)}")


@app.get("/api/v1/purchases", response_model=List[schemas.PurchaseOut], tags=["Compras"])
def list_purchases(db: Session = Depends(get_db)):
    """Listar historial de compras realizadas."""
    return db.query(models.Purchase).order_by(models.Purchase.id.desc()).all()


# ==========================================================
# 3. CLIENTES Y VENTAS / SALIDAS (sales & sale_items)
# ==========================================================
@app.post("/api/v1/sales/checkout", response_model=schemas.SaleOut, status_code=status.HTTP_201_CREATED, tags=["Ventas"])
def checkout_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    """
    Registrar venta a cliente o repuestos usados en un vehículo.
    Valida disponibilidad, descuenta existencias de forma atómica y genera Kardex.
    """
    if not sale_in.items:
        raise HTTPException(status_code=400, detail="La venta debe incluir al menos un producto o servicio.")

    total_calculado = 0.0
    items_to_create = []
    movements_to_create = []

    try:
        # Validación y descuento
        for item in sale_in.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Repuesto ID {item.product_id} no encontrado")

            # Si es un bien físico, verificar y descontar stock
            if not product.es_servicio:
                if product.stock_actual < item.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para '{product.nombre}'. Solicitado: {item.cantidad}, Disponible: {product.stock_actual}"
                    )
                stock_anterior = product.stock_actual
                product.stock_actual -= item.cantidad
                stock_posterior = product.stock_actual

                movements_to_create.append({
                    "product_id": product.id,
                    "tipo_movimiento": "SALIDA",
                    "cantidad": item.cantidad,
                    "stock_anterior": stock_anterior,
                    "stock_posterior": stock_posterior
                })

            subtotal = product.precio_venta * item.cantidad
            total_calculado += subtotal

            items_to_create.append({
                "product_id": product.id,
                "cantidad": item.cantidad,
                "precio_unitario": product.precio_venta,
                "subtotal": subtotal
            })

        # Cabecera de venta
        db_sale = models.Sale(
            cliente_nombre=sale_in.cliente_nombre,
            cliente_ci_nit=sale_in.cliente_ci_nit,
            placa_vehiculo=sale_in.placa_vehiculo,
            total_venta=total_calculado,
            metodo_pago=sale_in.metodo_pago,
            usuario_id=sale_in.usuario_id
        )
        db.add(db_sale)
        db.flush()

        # Detalle de venta
        for it in items_to_create:
            db_item = models.SaleItem(
                sale_id=db_sale.id,
                product_id=it["product_id"],
                cantidad=it["cantidad"],
                precio_unitario=it["precio_unitario"],
                subtotal=it["subtotal"]
            )
            db.add(db_item)

        # Kardex
        for mov in movements_to_create:
            db_mov = models.InventoryMovement(
                product_id=mov["product_id"],
                tipo_movimiento=mov["tipo_movimiento"],
                cantidad=mov["cantidad"],
                stock_anterior=mov["stock_anterior"],
                stock_posterior=mov["stock_posterior"],
                referencia_origen=f"VENTA #{db_sale.id}",
                motivo=f"Venta a: {sale_in.cliente_nombre}" + (f" (Vehículo: {sale_in.placa_vehiculo})" if sale_in.placa_vehiculo else "")
            )
            db.add(db_mov)

        db.commit()
        db.refresh(db_sale)
        return db_sale

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción de venta: {str(e)}")


@app.get("/api/v1/sales", response_model=List[schemas.SaleOut], tags=["Ventas"])
def list_sales(db: Session = Depends(get_db)):
    """Consultar historial de ventas y cobros realizados."""
    return db.query(models.Sale).order_by(models.Sale.id.desc()).all()


# ==========================================================
# 4. KARDEX Y MOVIMIENTOS DE INVENTARIO (inventory_movements)
# ==========================================================
@app.get("/api/v1/movements", response_model=List[schemas.InventoryMovementOut], tags=["Kardex"])
def list_inventory_movements(db: Session = Depends(get_db)):
    """Auditoría de todos los movimientos de inventario (Entradas, Salidas, Ajustes)."""
    return db.query(models.InventoryMovement).order_by(models.InventoryMovement.id.desc()).all()
