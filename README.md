# Visión General

Esta es una API de chatbot basada en Flask que proporciona capacidades de chat con inteligencia artificial utilizando los modelos de lenguaje de Groq. La aplicación funciona como un contenedor API REST alrededor de la API de Groq, ofreciendo modos de chat básico y pro, capacidades de procesamiento de archivos para PDFs y archivos de texto, y una interfaz web para pruebas y documentación. El sistema soporta múltiples modelos de IA, incluyendo variantes de LLaMA, Mixtral y Gemma, con características como inyección de contexto y análisis de contenido de archivos.

# Preferencias del Usuario

Estilo de comunicación preferido: Lenguaje sencillo y cotidiano.

# Arquitectura del Sistema

## Framework Backend
- **Flask**: Framework web ligero de Python elegido por su desarrollo rápido y diseño orientado a API
- **Arquitectura con Blueprints**: Organización modular de rutas con blueprints separados para funcionalidades de chat y carga de archivos
- **CORS Habilitado**: Configuración de intercambio de recursos entre orígenes para integración con frontends
- **Middleware ProxyFix**: Manejo de cabeceras de proxy para despliegue detrás de proxies inversos

## Diseño de la API
- **Endpoints RESTful**: Estructura limpia de API con `/chat` para conversaciones y `/upload` para procesamiento de archivos
- **Solicitud/Respuesta en JSON**: Formato estandarizado de intercambio de datos
- **Manejo de Errores**: Manejo centralizado de errores con códigos de estado HTTP apropiados
- **Verificación de Salud**: Endpoint `/health` para monitoreo y verificación del despliegue

## Integración con IA
- **Cliente de la API de Groq**: Wrapper personalizado para la API de completado de chat de Groq
- **Soporte Multi-Modelo**: Selección configurable de modelos (LLaMA 3 8B/70B, Mixtral 8x7B, Gemma 7B)
- **Modos de Procesamiento Dual**: Modo básico de consulta única y modo Pro con múltiples consultas de síntesis
- **Inyección de Contexto**: Soporte para contexto adicional en las solicitudes de chat

## Sistema de Procesamiento de Archivos
- **Soporte Multi-Formato**: Capacidad de procesar archivos PDF y TXT
- **Medidas de Seguridad**: Límite de tamaño de archivo (10MB), validación de extensiones y manejo seguro de nombres de archivo
- **Extracción de Contenido**: PyPDF2 para extracción de texto de PDFs, lectura directa de archivos de texto
- **Integración con IA**: Procesamiento opcional con IA del contenido de archivos subidos, con capacidad de responder preguntas

## Gestión de Configuración
- **Variables de Entorno**: Claves API y datos sensibles almacenados en variables de entorno
- **Configuración Centralizada**: Clase única que gestiona todos los ajustes de la aplicación
- **Configuración de Modelos**: Mapeo centralizado de nombres de modelos amigables para el usuario a identificadores de API

## Capa de Validación
- **Validación de Solicitudes**: Validación exhaustiva de entradas para solicitudes de chat y carga de archivos
- **Controles de Seguridad**: Validación de claves API, restricciones de tipo de archivo y límites de longitud de contenido
- **Reporte de Errores**: Mensajes detallados de errores de validación para depuración

## Interfaz Frontend
- **UI con Bootstrap**: Interfaz receptiva con tema oscuro para pruebas de la API
- **Navegación con Pestañas**: Interfaces separadas para chat y carga de archivos
- **Estado en Tiempo Real**: Monitoreo del estado de la API y retroalimentación del estado de las solicitudes
- **Formularios Interactivos**: Formularios fáciles de usar para probar los endpoints de la API

# Dependencias Externas

## Servicio de IA Principal
- **API de Groq**: Proveedor principal de modelos de lenguaje que requiere autenticación mediante clave API
- **Modelos**: LLaMA 3 (8B/70B), Mixtral 8x7B, variantes de Gemma 7B

## Librerías de Python
- **Flask**: Framework web y sistema de enrutamiento
- **Flask-CORS**: Manejo de solicitudes entre orígenes
- **Requests**: Cliente HTTP para comunicación con APIs externas
- **PyPDF2**: Extracción de texto de archivos PDF
- **Werkzeug**: Utilidades WSGI y manejo de archivos

## Dependencias Frontend
- **Bootstrap 5**: Framework de interfaz con tema oscuro
- **Font Awesome**: Biblioteca de iconos
- **Vanilla JavaScript**: Funcionalidad del lado del cliente sin frameworks adicionales

## Herramientas de Desarrollo
- **Logging**: Sistema de registro integrado de Python para depuración y monitoreo
- **Configuración de Entorno**: Gestión de variables de entorno del sistema operativo
