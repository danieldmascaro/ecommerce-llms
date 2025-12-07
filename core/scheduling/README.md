# Scheduling

App para gestionar recursos reservables, servicios asociados, reglas de disponibilidad recurrente, excepciones puntuales y citas/reservas con intervalos `inicio`/`fin`.

## Modelos

- **RecursoReservable** (`programacion_recurso`): `nombre` (unico), `zona_horaria`, `capacidad`, `esta_activo`, `creado_en/actualizado_en`. Valida zona horaria con ZoneInfo.
- **Servicio** (`programacion_servicio`): `recurso`, `nombre` (unico por recurso), `duracion`, `buffer_antes/buffer_despues`, `esta_activo`.
- **ReglaDisponibilidadRecurrente** (`programacion_regla_disponibilidad`): `recurso`, `servicio` opcional, `dia_semana`, `hora_inicio/hora_fin`, rango `vigente_desde/vigente_hasta`, `esta_activa`.
- **ExcepcionDisponibilidad** (`programacion_excepcion_disponibilidad`): `recurso`, `servicio` opcional, `fecha`, `hora_inicio/hora_fin`, `tipo` (`open`/`closed`), `motivo`, `esta_activa`.
- **Cita** (`programacion_cita`): `recurso`, `servicio`, `producto` opcional, `user` opcional, `titulo`, `inicio/fin`, `estado` (`scheduled`/`cancelled`), `pago_confirmado`, `confirmed_at`, `notas`, `creado_en/actualizado_en`.

## Logica y validaciones clave

- `Cita.clean()` asegura:
  - `fin > inicio`, fechas timezone-aware y mismo dia.
  - Servicio pertenece al recurso y ambos esten activos. Producto, si se envía, debe estar activo.
  - Duracion minima: `(fin - inicio) >= servicio.duracion_total_esperada`.
  - Prevencion de solapes: respeta `capacidad` del recurso.
  - Disponibilidad: bloquea si hay excepcion `closed`; permite si hay excepcion `open` que cubre o alguna regla recurrente vigente cubre `hora_inicio/hora_fin`. Reglas/excepciones pueden ser genericas o especificas por servicio.
- `ReglaDisponibilidadRecurrente.clean()` y `ExcepcionDisponibilidad.clean()` verifican pertenencia del servicio al recurso.
- `RecursoReservable.clean()` valida zona horaria.
- Constraints SQL refuerzan rangos y unicidad.
- Señales:
  - `pre_save` de `Cita` rellena `confirmed_at` cuando `pago_confirmado=True`.
  - `post_save` de `Cita` crea (idempotente) `SaleEvent` `RESERVATION` y `CheckIn` pendiente para el `producto` asociado.

## API (DRF)

Rutas en `core/core/urls.py` con `DefaultRouter`:
- `GET/POST/PUT/PATCH/DELETE /api/recursos/`  `RecursoReservableViewSet`
- `GET/POST/PUT/PATCH/DELETE /api/servicios/`  `ServicioViewSet`
- `GET/POST/PUT/PATCH/DELETE /api/reglas-disponibilidad/`  `ReglaDisponibilidadRecurrenteViewSet`
- `GET/POST/PUT/PATCH/DELETE /api/excepciones-disponibilidad/`  `ExcepcionDisponibilidadViewSet`
- `GET/POST/PUT/PATCH/DELETE /api/citas/`  `CitaViewSet`

Acciones adicionales:
- `POST /api/citas/validar-espacio/`  body: `recurso`, `servicio`, `inicio`, `fin`; valida disponibilidad sin crear cita.
- `POST /api/citas/{id}/cancelar/`  marca la cita como `cancelled`.

Filtros comunes:
- Recursos/servicios: `esta_activo`, `recurso` (en servicios), busqueda por `nombre`.
- Reglas: `recurso`, `servicio`, `dia_semana`, `esta_activa`.
- Excepciones: `recurso`, `servicio`, `fecha`, `tipo`, `esta_activa`.
- Citas: `recurso`, `servicio`, `estado`, rangos `inicio`/`fin`.

### Ejemplo de creacion de cita

```json
{
  "recurso": 1,
  "servicio": 3,
  "titulo": "Demo con cliente",
  "inicio": "2025-12-07T15:00:00Z",
  "fin": "2025-12-07T15:45:00Z",
  "notas": "Revisar requisitos previos"
}
```

La peticion fallara con 400 si:
- El recurso/servicio esta inactivo o no pertenecen entre si.
- No existe regla/excepcion que cubra el rango o hay cierre activo.
- El intervalo solapa con citas confirmadas superando `capacidad`.
- La duracion es menor a la requerida por el servicio (incluyendo buffers).
