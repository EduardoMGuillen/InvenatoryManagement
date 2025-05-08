# Sistema de Gestión de Inventario

Un sistema completo de gestión de inventario desarrollado en Python con PyQt6, diseñado para pequeñas y medianas empresas.

## Características

- **Gestión de Inventario**

  - Añadir, actualizar y eliminar productos
  - Seguimiento de stock en tiempo real
  - Búsqueda rápida por ID, nombre o número de serie

- **Gestión de Clientes**

  - Registro completo de clientes
  - Actualización y eliminación de registros
  - Búsqueda por nombre, ID o RTN

- **Sistema de Facturación**

  - Generación de facturas
  - Cálculo automático de ISV
  - Historial de facturas
  - Impresión de facturas

- **Reportes**

  - Reportes de ventas por período
  - Historial de compras por cliente
  - Exportación de reportes

- **Backup y Seguridad**
  - Sistema de backup automático por correo
  - Restauración de backups
  - Autenticación de usuarios

## Requisitos

- Python 3.8 o superior
- PyQt6
- SQLite3

## Instalación

1. Clone el repositorio:

```bash
git clone https://github.com/your-username/inventory_management.git
cd inventory_management
```

2. Instale las dependencias:

```bash
pip install -r requirements.txt
```

3. Configure el archivo de configuración:

- Copie `config.example.ini` a `config.ini`
- Actualice las configuraciones según sus necesidades

4. Ejecute la aplicación:

```bash
python main.py
```

## Configuración del Sistema de Backup

Para configurar el sistema de backup por correo:

1. Active la autenticación de dos factores en su cuenta de Gmail
2. Genere una contraseña de aplicación
3. Configure los siguientes parámetros en la aplicación:
   - Email de origen (bizztrackpro@gmail.com)
   - Email de destino para backups
   - Frecuencia de backup (diaria/semanal/mensual)

## Estructura del Proyecto

```
inventory_management/
├── main.py              # Punto de entrada principal
├── database.py          # Gestión de base de datos
├── login.py            # Sistema de autenticación
├── backup_manager.py   # Gestión de backups
├── settings_manager.py # Gestión de configuración
├── currency_formatter.py # Formateo de moneda
├── icons/              # Iconos de la aplicación
├── backups/           # Directorio de backups
└── facturas/          # Directorio de facturas
```

## Uso

1. **Inicio de Sesión**

   - Use las credenciales proporcionadas por el administrador

2. **Gestión de Inventario**

   - Navegue a la pestaña "Inventario" para ver todos los productos
   - Use "Agregar Producto" para nuevos items
   - Use "Actualizar Producto" para modificar existentes

3. **Gestión de Clientes**

   - Similar a la gestión de inventario
   - Mantenga registros actualizados de clientes

4. **Facturación**

   - Seleccione cliente
   - Agregue productos
   - Genere e imprima facturas

5. **Reportes**
   - Acceda a reportes desde el menú principal
   - Filtre por fechas según necesidad

## Soporte

Para soporte técnico o reportar problemas:

- Abra un issue en GitHub
- Contacte al equipo de desarrollo

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contribuir

1. Fork el proyecto
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request
