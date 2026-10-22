from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- ESQUEMAS DE USUARIO ---
class UserBase(BaseModel):
    nombre_completo: str
    email: str
    rol: str = "VENDEDOR"

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    activo: bool
    creado_en: datetime
    class Config:
        from_attributes = True


# --- ESQUEMAS DE PRODUCTO / REPUESTO ---
class ProductBase(BaseModel):
    sku: str
    nombre: str
    descripcion: Optional[str] = None
    categoria: str = "Repuestos"
    precio_compra: float = Field(default=0.0, ge=0)
    precio_venta: float = Field(default=0.0, ge=0)
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=3, ge=0)
    es_servicio: bool = False

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    activo: bool
    class Config:
        from_attributes = True


# --- ESQUEMAS DE VENTA ---
class SaleItemCreate(BaseModel):
    product_id: int
    cantidad: int = Field(gt=0)

class SaleCreate(BaseModel):
    cliente_nombre: str = "Cliente General"
    cliente_ci_nit: Optional[str] = None
    placa_vehiculo: Optional[str] = None
    metodo_pago: str = "EFECTIVO"
    usuario_id: Optional[int] = None
    items: List[SaleItemCreate]

class SaleItemOut(BaseModel):
    id: int
    product_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    id: int
    cliente_nombre: str
    cliente_ci_nit: Optional[str] = None
    placa_vehiculo: Optional[str] = None
    total_venta: float
    metodo_pago: str
    fecha_venta: datetime
    items: List[SaleItemOut] = []
    class Config:
        from_attributes = True


# --- ESQUEMAS DE COMPRA ---
class PurchaseItemCreate(BaseModel):
    product_id: int
    cantidad: int = Field(gt=0)
    costo_unitario: float = Field(ge=0)

class PurchaseCreate(BaseModel):
    proveedor_nombre: str
    proveedor_nit: Optional[str] = None
    numero_factura: Optional[str] = None
    usuario_id: Optional[int] = None
    items: List[PurchaseItemCreate]

class PurchaseItemOut(BaseModel):
    id: int
    product_id: int
    cantidad: int
    costo_unitario: float
    subtotal: float
    class Config:
        from_attributes = True

class PurchaseOut(BaseModel):
    id: int
    proveedor_nombre: str
    proveedor_nit: Optional[str] = None
    numero_factura: Optional[str] = None
    total_compra: float
    fecha_compra: datetime
    items: List[PurchaseItemOut] = []
    class Config:
        from_attributes = True


# --- ESQUEMA DE KARDEX / MOVIMIENTO ---
class InventoryMovementOut(BaseModel):
    id: int
    product_id: int
    tipo_movimiento: str
    cantidad: int
    stock_anterior: int
    stock_posterior: int
    referencia_origen: Optional[str] = None
    motivo: Optional[str] = None
    fecha: datetime
    class Config:
        from_attributes = True
