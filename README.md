# bytte OS Backend

Bytte es un ERP para restaurantes. Este documento explica cómo montar y utilizar el servidor backend de Bytte OS.

## Requisitos

- Python (versión 3.8 o superior)
- MySQL

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu-usuario/bytte-backend.git
    cd bytte-backend
    ```

2. Crea y activa un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configura las variables de entorno:
    Crea un archivo `.env` en la raíz del proyecto y añade las siguientes variables:
    ```env
    PORT=8000
    DB_HOST=srv1618.hstgr.io
    DB_USER=u637372565_anomaly
    DB_PASSWORD=Bytte-Back-2024
    DB_NAME=u637372565_bytte_db
    ```

## Uso

1. Inicia el servidor:
    ```bash
    uvicorn Application.ApiBytte:app --reload
    ```

2. El servidor estará corriendo en `http://localhost:8000`.

## Endpoints

- `GET /api/restaurants` - Obtener la lista de restaurantes
- `POST /api/restaurants` - Crear un nuevo restaurante
- `PUT /api/restaurants/:id` - Actualizar un restaurante
- `DELETE /api/restaurants/:id` - Eliminar un restaurante

## Contribuir

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT.
