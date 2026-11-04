# 🍬 Gomilandia – Tienda Web Profesional en Python (Flask + SQLite)

¡Bienvenido al nuevo sistema web de **Gomilandia**! La página fue transformada de un archivo HTML estático con datos temporales a una **aplicación web profesional en Python**, conectada a una **base de datos SQLite real** y con integración directa a WhatsApp y un panel de administración completo.

---

## 🌟 Mejoras Principales Implementadas

1. **Pasaje a Formato Python (Flask + SQLite)**:
   - Los productos y pedidos ya no se pierden al cerrar el navegador: se guardan en la base de datos `gomilandia.db`.
   - Soporte para crear, editar y eliminar productos con subida de fotos reales desde el panel.
   - Historial de pedidos con métricas en tiempo real (total recaudado en ARS, cantidad de ventas, métodos de pago).

2. **Fotografía de Producto Profesional y Branding**:
   - Generación de logo adorable y fotos de alta definición para cada producto (Sweet Cup, Corazón Gomilandia, Sweet Shot, Picada Gomi Mix, Ensalada Gomilandia).
   - Se eliminaron las rutas rotas que apuntaban a carpetas inexistentes.

3. **Corrección de Errores Técnicos y Visuales**:
   - Se reparó el botón flotante de WhatsApp que tenía el SVG dañado.
   - Efectos de partículas de gomitas flotantes en el Hero (`🍬, 🍭, 💖, 🌈, 🐻`).
   - Carrito interactivo con selección de ocasión de tarjeta dedicatoria (**Cumpleaños**, **Regalo**, **Con amor**, **Otra**) y mensaje personalizado.
   - Mensaje de WhatsApp preformateado y limpio que se genera con 1 solo clic.

---

## 📁 Estructura del Proyecto

```text
gomilandia/
├── app.py                  # Servidor backend en Python (Flask, Base de Datos, APIs)
├── gomilandia.db           # Base de datos SQLite (se genera y actualiza automáticamente)
├── templates/
│   └── index.html          # Plantilla principal moderna y responsive
├── static/
│   ├── css/
│   │   └── styles.css      # Sistema de diseño, paleta candy boutique, animaciones
│   ├── js/
│   │   └── app.js          # Lógica interactiva del carrito, checkout y panel admin
│   ├── img/                # Fotos de productos en alta resolución y logotipo
│   │   ├── logo.jpg
│   │   ├── sweet_cup.jpg
│   │   ├── mini_cup.jpg
│   │   ├── sweet_shot.jpg
│   │   ├── corazon.jpg
│   │   ├── picada.jpg
│   │   └── ensalada.jpg
│   └── uploads/            # Fotos que subas desde el panel de administración
└── gomilandia.html         # Archivo HTML original (conservado como respaldo)
```

---

## 🚀 Cómo Ejecutar la Aplicación

Tenés dos formas muy sencillas de iniciar la tienda:

### Opción 1 (La más fácil): Doble clic en el ejecutable
Simplemente hacé doble clic en el archivo:
📁 **`iniciar_gomilandia.bat`**

Esto automáticamente:
1. Detecta tu versión de Python instalada.
2. Comprueba e instala dependencias (Flask).
3. Abre la tienda en tu navegador predeterminado.
4. Mantiene el servidor corriendo en la consola.

---

### Opción 2: Desde la Terminal / Consola
En la terminal o PowerShell dentro de la carpeta del proyecto:
```bash
python app.py
```
*(Si tu terminal no reconoce `python`, ejecutá: `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" app.py`)*

---

### 🌐 Direcciones de Acceso:
- **Tienda Pública**: 👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
- **Panel Administrador**: 👉 **[http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)**
  - **Usuario**: `gomilandia`
  - **Contraseña**: `gomitas2026`

---

## 🔐 Apartado Exclusivo para el Administrador (`/admin`)

Diseñado especialmente para la gestión diaria del emprendimiento:

👉 **URL de acceso directo**: **[http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)**
- **Usuario**: `gomilandia`
- **Contraseña**: `gomitas2026`

### 1. 🍬 Control de Stock, Precios, Descripciones y Fotos:
- **Botón de Stock en 1 Clic**: Cada producto tiene su interruptor interactivo (`🟢 En Stock` / `🔴 Sin Stock`). Al presionarlo, el producto se pausa inmediatamente en la tienda pública sin recargar la página.
- **En la Tienda Pública**: Los productos sin stock se muestran con una insignia destacada `🚫 Sin Stock`, la foto se atenúa sutilmente y el botón se deshabilita para evitar que los clientes ordenen productos agotados.
- **Edición Completa**: Podés cambiar el nombre, precio en ARS, categoría, emoji, descripción y subir una nueva foto con vista previa instantánea.
- **Agregar Productos Nuevos**: Creá nuevas presentaciones (vasos, cajas, bandejas) que se guardan directamente en la base de datos.

### 2. 📊 Monitoreo de Movimientos de la App:
- **Tarjetas de Métricas en Vivo**:
  - 💰 **Total Facturado ($ ARS)**: Sumatoria de todos los pedidos confirmados.
  - 📦 **Total de Pedidos**: Cantidad total de compras registradas.
  - ⏳ **Pedidos Pendientes**: Pedidos listos para coordinar o despachar.
  - 🚫 **Productos Sin Stock**: Cuántos productos tenés pausados actualmente.
- **Buscador y Filtros**: Buscá pedidos por nombre de cliente, teléfono o productos comprados. Filtrá por estado (`Todos`, `Pendientes`, `Entregados`, `Cancelados`).
- **Gestión de Estados**: Cambiá el estado de un pedido (`⏳ Pendiente` ➔ `✅ Entregado` ➔ `❌ Cancelado`) desde un selector rápido.
- **Botón Directo a WhatsApp**: Para escribirle al cliente con un solo clic y coordinar el retiro o la entrega.
