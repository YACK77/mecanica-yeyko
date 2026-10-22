# Sistema de Gestión y Control Operativo para "Mecánica Yeyko"

**Proyecto de Grado - UDABOL (Ingeniería de Sistemas)**  
**Postulante:** Ivan Chiri Lupinta  
**Stack:** FastAPI + PostgreSQL (Supabase BaaS)  

---

## Estructura del Proyecto

```plaintext
d:\mecanica yeyko\
└── backend/
    ├── .env             # Credenciales y conexión a Supabase
    ├── database.py      # Motor de SQLAlchemy y sesión con Supabase
    ├── models.py        # 5 Tablas del Modelo de Dominio Mínimo
    ├── schemas.py       # Validaciones con Pydantic v2
    ├── main.py          # API REST con FastAPI (Endpoints transaccionales)
    └── requirements.txt # Dependencias de Python
```

---

## Instrucciones de Ejecución Rápida

1. **Abrir la terminal en la carpeta backend:**
   ```bash
   cd "d:\mecanica yeyko\backend"
   ```

2. **Iniciar el servidor local con recarga automática:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Ver la documentación y probar el sistema:**
   Abre en tu navegador web:
   👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

4. **Ver las tablas en Supabase:**
   Inicia sesión en [https://supabase.com](https://supabase.com) y entra en la sección **Table Editor**. Verás las tablas:
   - `products` (Repuestos e inventario)
   - `sales` (Ventas a clientes de Mecánica Yeyko)
   - `sale_items` (Detalle de repuestos por venta)
   - `purchases` (Compras a distribuidores)
   - `purchase_items` (Detalle de compras)
   - `inventory_movements` (Kardex físico y auditoría)
   - `users` (Usuarios y roles)
