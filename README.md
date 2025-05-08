# Sistema de Inventario - BizzTrackPro

Un sistema completo de gestión de inventario desarrollado con PyQt6, diseñado para pequeñas y medianas empresas.

## Características

### Gestión de Inventario

- Visualización completa del inventario
- Agregar nuevos productos
- Actualizar productos existentes
- Búsqueda por ID, nombre o número de serie
- Control de stock automático

### Gestión de Clientes

- Base de datos completa de clientes
- Agregar nuevos clientes
- Actualizar información de clientes
- Búsqueda por nombre, ID o RTN
- Historial de compras por cliente

### Facturación

- Generación de facturas
- Vista previa antes de generar
- Cálculo automático de ISV
- Historial completo de facturas
- Opciones para imprimir o guardar en formato texto

### Reportes

- Reportes de ventas por período
- Historial de compras por cliente
- Estadísticas de ventas
- Exportación e impresión de reportes

### Respaldo y Seguridad

- Sistema de backup automático
- Respaldos por correo electrónico
- Restauración de backups
- Protección con login

## Requisitos

- Python 3.8 o superior
- PyQt6
- SQLite3
- Conexión a Internet (para backups por email)

## Instalación

1. Clone el repositorio:

```bash
git clone https://github.com/yourusername/inventory-management.git
cd inventory-management
```

2. Instale las dependencias:

```bash
pip install -r requirements.txt
```

3. Configure el archivo de configuración:

- Abra la aplicación
- Vaya a "Configuración"
- Configure los datos de la empresa
- Configure el correo para backups

## Uso

1. Inicie la aplicación:

```bash
python main.py
```

2. Inicie sesión con sus credenciales

3. Navegue por las diferentes secciones:

- Inventario
- Clientes
- Facturación
- Reportes
- Configuración

## Configuración de Backup

El sistema utiliza Gmail para enviar backups. Para configurarlo:

1. Configure una cuenta de Gmail
2. Active la autenticación de dos factores
3. Genere una contraseña de aplicación
4. Use estas credenciales en la configuración de backup

## Estructura de Archivos

```
inventory-management/
├── main.py              # Punto de entrada principal
├── database.py          # Gestión de base de datos
├── login.py             # Sistema de autenticación
├── backup_manager.py    # Gestión de backups
├── settings_manager.py  # Gestión de configuración
├── currency_formatter.py # Formateo de moneda
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

## Soporte

Para soporte técnico o reportar problemas, por favor abra un issue en el repositorio de GitHub.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles.

## Contribuir

Las contribuciones son bienvenidas. Por favor, lea CONTRIBUTING.md para detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.
