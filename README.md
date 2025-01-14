# bytte OS Backend

Bytte es un ERP para restaurantes. Este documento explica cómo montar y utilizar el servidor backend de Bytte OS.

## Requisitos

- Node.js (versión 14 o superior)
- npm (versión 6 o superior)
- MongoDB (versión 4 o superior)

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu-usuario/bytte-backend.git
    cd bytte-backend
    ```

2. Instala las dependencias:
    ```bash
    npm install
    ```

3. Configura las variables de entorno:
    Crea un archivo `.env` en la raíz del proyecto y añade las siguientes variables:
    ```env
    PORT=3000
    MONGODB_URI=mongodb://localhost:27017/bytte
    JWT_SECRET=tu_secreto_jwt
    ```

## Uso

1. Inicia el servidor:
    ```bash
    npm start
    ```

2. El servidor estará corriendo en `http://localhost:3000`.

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
