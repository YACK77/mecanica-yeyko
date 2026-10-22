from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(30), default="VENDEDOR", nullable=False)  # ADMIN, VENDEDOR, ALMACENERO
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), default="Repuestos", nullable=False)
    precio_compra = Column(Float, default=0.0, nullable=False)
    precio_venta = Column(Float, default=0.0, nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=3, nullable=False)
    es_servicio = Column(Boolean, default=False, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    movimientos = relationship("InventoryMovement", back_populates="producto")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_nombre = Column(String(150), nullable=False)
    proveedor_nit = Column(String(30), nullable=True)
    numero_factura = Column(String(50), nullable=True)
    total_compra = Column(Float, default=0.0, nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_compra = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items = relationship("PurchaseItem", back_populates="compra", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    compra = relationship("Purchase", back_populates="items")
    producto = relationship("Product")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String(150), default="Cliente General", nullable=False)
    cliente_ci_nit = Column(String(30), nullable=True)
    placa_vehiculo = Column(String(15), nullable=True)
    total_venta = Column(Float, default=0.0, nullable=False)
    metodo_pago = Column(String(30), default="EFECTIVO", nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_venta = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items = relationship("SaleItem", back_populates="venta", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Sale", back_populates="items")
    producto = relationship("Product")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)  # ENTRADA, SALIDA, AJUSTE
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_posterior = Column(Integer, nullable=False)
    referencia_origen = Column(String(50), nullable=True)  # COMPRA #1, VENTA #2, AJUSTE
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    motivo = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    producto = relationship("Product", back_populates="movimientos")
