# API endpoints

Documentacion funcional de los endpoints expuestos por el proyecto (apps `ecommerce`, `agents`, `scheduling`, `commerce` y `sales`). Todas las rutas estan bajo prefijo `/api/`. Autenticacion por JWT (Bearer) y paginacion PageNumber (`count`, `next`, `previous`, `results`).

## Autenticacion (JWT + Djoser)
- `POST /api/token/` body: `{"username": "...", "password": "..."}` -> `{"access": "...", "refresh": "..."}`
- `POST /api/token/refresh/` body: `{"refresh": "..."}` -> `{"access": "..."}`
- `POST /api/token/verify/` body: `{"token": "..."}` -> 200 si es valido.
- `POST /api/token/blacklist/` body: `{"refresh": "..."}` -> 200 (revoca refresh).
- Djoser base: `/api/auth/` (registro, activacion, reset password, cambio de password/email) segun configuracion djoser.

## Users app (cuentas)
- `GET/POST /api/cuentas/` lista/crea. Body POST: `{"user": user_id, "nombre": "...", "nombre_usuario": "...", "contrasena": "..."}` -> 201 con objeto.
- `GET/PATCH/DELETE /api/cuentas/{id}/`

## Ecommerce app (catálogo)

### Tiendas
- `GET/POST /api/tiendas/` Body POST: `{"nombre": "...", "descripcion": "", "cuenta": cuenta_id}`
- `GET/PATCH/DELETE /api/tiendas/{id}/`

### Categorias
- `GET/POST /api/categorias/` Body: `{"nombre":"...","esta_activa":true,"descripcion":"","descripcion_prompt":"","regla":regla_id|null,"logica_venta":""}`
- `GET/PATCH/DELETE /api/categorias/{id}/`

### Productos
- `GET/POST /api/productos/` Body: `{"nombre":"...","precio":"10.00","esta_activa":true,"descripcion":"","descripcion_prompt":"","stock":0,"agendable":true}`
- `GET/PATCH/DELETE /api/productos/{id}/`
- Acciones:
  - `GET /api/productos/total/` -> `{"total": <int>}`
  - `GET /api/productos/por-categoria/?categoria_id=<id>` -> lista paginada de productos

### Relaciones producto/categoria
- `GET/POST /api/producto-categorias/` Body: `{"producto": producto_id, "categoria": categoria_id}`
- `GET/PATCH/DELETE /api/producto-categorias/{id}/`
### Relaciones categoria/tienda
- `GET/POST /api/categoria-tiendas/` Body: `{"categoria": categoria_id, "tienda": tienda_id}`
- `GET/PATCH/DELETE /api/categoria-tiendas/{id}/`

### Reglamentos y reglas
- `GET/POST /api/reglamentos/` Body: `{"nombre":"..."}`
- `GET/PATCH/DELETE /api/reglamentos/{id}/`
- `GET/POST /api/reglas/` Body: `{"reglamento": reglamento_id, "orden":1, "texto":"...", "esta_seleccionable":true}`
- `GET/PATCH/DELETE /api/reglas/{id}/`

### Agendas (reservas vinculadas a productos)
- `GET/POST /api/agendas/` Body: `{"inicio":"2025-12-07T15:00:00Z","fin":"2025-12-07T16:00:00Z","cliente_id":1,"producto": producto_id}`
- `GET/PATCH/DELETE /api/agendas/{id}/`

## Agents app (flujos y agentes)

### Flujos de agente
- `GET/POST /api/flujos/` Body: `{"nombre": "...", "nombre_comercial": "...", "descripcion": "", "tienda": tienda_id}`
- `GET/PATCH/DELETE /api/flujos/{id}/`

### Agentes
- `GET/POST /api/agentes/` Body: `{"nombre": "...", "tienda": tienda_id, "flujo_agente": flujo_id, "tipo_agente": tipo_id, "modelo_ia": modelo_id, "reglamento": reglamento_id|null, "logica": ""}`
- `GET/PATCH/DELETE /api/agentes/{id}/`

### Relaciones con productos/categorías
- `GET/POST /api/producto-flujos/` Body: `{"producto": producto_id, "flujo_agente": flujo_id}`
- `GET/PATCH/DELETE /api/producto-flujos/{id}/`
- `GET/POST /api/categoria-flujos/` Body: `{"categoria": categoria_id, "flujo_agente": flujo_id}`
- `GET/PATCH/DELETE /api/categoria-flujos/{id}/`

### Modelos IA y tipos de agente
- `GET/POST /api/modelos-ia/` Body: `{"nombre":"..."}`; `GET/PATCH/DELETE /api/modelos-ia/{id}/`
- `GET/POST /api/tipos-agente/` Body: `{"nombre":"..."}`; `GET/PATCH/DELETE /api/tipos-agente/{id}/`

### Reglamentos y reglas
- `GET/POST /api/reglamentos/` Body: `{"nombre":"..."}`
- `GET/PATCH/DELETE /api/reglamentos/{id}/`
- `GET/POST /api/reglas/` Body: `{"reglamento": reglamento_id, "orden":1, "texto":"...", "esta_seleccionable":true}`
- `GET/PATCH/DELETE /api/reglas/{id}/`

### Logs de agente (solo lectura admin)
- `GET /api/agent-sessions/` lista sesiones (read-only)
- `GET /api/agent-messages/` lista mensajes con `session` relacionado

## Scheduling app

### Recursos reservables
- `GET/POST /api/recursos/` Body: `{"nombre":"Sala A","descripcion":"","zona_horaria":"UTC","capacidad":1,"esta_activo":true}`
- `GET/PATCH/DELETE /api/recursos/{id}/`

### Servicios
- `GET/POST /api/servicios/` Body: `{"recurso": recurso_id,"nombre":"Consulta","descripcion":"","duracion":"00:30:00","buffer_antes":"00:05:00","buffer_despues":"00:05:00","esta_activo":true}`
- `GET/PATCH/DELETE /api/servicios/{id}/`

### Reglas de disponibilidad recurrente
- `GET/POST /api/reglas-disponibilidad/` Body: `{"recurso": recurso_id,"servicio": servicio_id|null,"dia_semana":0..6,"hora_inicio":"09:00:00","hora_fin":"18:00:00","vigente_desde":null,"vigente_hasta":null,"esta_activa":true}`
- `GET/PATCH/DELETE /api/reglas-disponibilidad/{id}/`

### Excepciones de disponibilidad
- `GET/POST /api/excepciones-disponibilidad/` Body: `{"recurso": recurso_id,"servicio": servicio_id|null,"fecha":"2025-12-07","hora_inicio":"08:00:00","hora_fin":"20:00:00","tipo":"open|closed","motivo":"...","esta_activa":true}`
- `GET/PATCH/DELETE /api/excepciones-disponibilidad/{id}/`

### Citas
- `GET/POST /api/citas/` Body: `{"recurso": recurso_id,"servicio": servicio_id,"producto": producto_id|null,"titulo":"Demo","inicio":"2025-12-07T15:00:00Z","fin":"2025-12-07T15:45:00Z","notas":""}`
- `GET/PATCH/DELETE /api/citas/{id}/`
- Campos adicionales: `user` (FK opcional al comprador), `pago_confirmado` (bool), `confirmed_at` (datetime).
- Acciones:
  - `POST /api/citas/validar-espacio/` Body: `{"recurso": recurso_id,"servicio": servicio_id,"inicio":"...","fin":"..."}` -> `{"detail":"Intervalo disponible para agendar."}` o 400 con detalle de validacion.
  - `POST /api/citas/{id}/cancelar/` -> `{"detail":"Cita cancelada."}` (estado pasa a `cancelled`).
- Filtros relevantes: `?recurso=`, `?servicio=`, `?producto=`, `?estado=scheduled|cancelled`, `?inicio__gte=`, `?inicio__lte=`, `?fin__gte=`, `?fin__lte=`, `?producto__isnull=true|false`.

## Commerce app (carrito, checkout, pagos, check-in)

- `GET /api/commerce/cart/active/?tienda_id=` devuelve (o crea) carrito abierto del usuario.
- `POST /api/commerce/cart/items/` body `{"tienda_id":1,"producto_id":10,"quantity":2}` agrega/incrementa item.
- `PATCH /api/commerce/cart/items/{producto_id}/?tienda_id=` body `{"quantity":3}` actualiza; `DELETE` elimina.
- `GET /api/commerce/cart/summary/?tienda_id=` resumen de items/subtotal.
- `POST /api/commerce/checkout/` body `{"tienda_id":1}` -> crea `Order` pendiente desde carrito.
- `GET /api/commerce/orders/` lista órdenes; `GET /api/commerce/orders/{id}/` detalle con items.
- `POST /api/commerce/orders/{id}/pay/` body `{"provider":"stripe","external_id":"abc"}` marca pagada, descuenta stock, genera venta y check-in si el producto es agendable.
- `GET /api/commerce/checkins/` lista; `POST /api/commerce/checkins/{id}/complete/` marca `done`.
- Query params frecuentes: `tienda_id` en cart/summary/orders/checkins; autenticación JWT requerida en todos.

Ejemplos:
- Checkout:
```json
POST /api/commerce/checkout/
{ "tienda_id": 1 }
// 201
{ "id": 5, "status": "pending", "total": "40.00", "items": [ ... ] }
```
- Pago:
```json
POST /api/commerce/orders/5/pay/
{ "provider": "stripe", "external_id": "pay_123" }
// 200
{ "id": 5, "status": "paid", "paid_at": "2025-12-06T10:00:00Z", ... }
```
- Completar check-in:
```json
POST /api/commerce/checkins/3/complete/
// 200
{ "id": 3, "status": "done", "done_at": "2025-12-06T11:00:00Z", ... }
```

## Sales app (eventos y reportes de venta)

- `GET /api/sales/summary/?tienda_id=&desde=YYYY-MM-DD&hasta=YYYY-MM-DD&group_by=producto|categoria` -> lista agrupada `[{key, unidades, revenue}]`.
- `GET /api/sales/events/` lista eventos de venta; `GET /api/sales/events/{id}/` detalle con items.
- Orígenes de venta (`SaleEvent.source`): `CART_CHECKOUT`, `RESERVATION`, `MANUAL`.

## Flujo reserva pagada → venta → check-in

1. `Cita` ahora puede tener `user` y `pago_confirmado`.  
2. Al guardar una cita con `pago_confirmado=true` y `producto`:
   - Se crea (idempotente) `SaleEvent` con `source=RESERVATION` + `SaleItem`.
   - Se crea `CheckIn` pendiente vinculado a la cita y producto.
3. Idempotencia:
   - Re-guardar la misma cita pagada no duplica ventas ni check-ins.
   - Pagar la misma orden (`/pay/`) no duplica ventas ni descuenta stock extra.

Ejemplo `sales/summary`:
```json
GET /api/sales/summary/?tienda_id=1&desde=2025-12-01&hasta=2025-12-31&group_by=producto
// 200
[
  {"key": "Producto Test", "unidades": 3, "revenue": "60.00"},
  {"key": "Producto Y", "unidades": 1, "revenue": "15.00"}
]
```

## Formato de respuestas paginadas
```
{
  "count": 123,
  "next": "http://.../api/recursos/?page=2",
  "previous": null,
  "results": [
    {...}, {...}
  ]
}
```
