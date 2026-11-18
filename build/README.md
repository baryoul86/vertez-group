# Motor del sitio VERTEZ GROUP

Las páginas de `es/`, `fr/`, `en/` se GENERAN: no se editan a mano.

- `content.py` · `extra.py`: todos los textos (ES / FR / EN).
- `gen.py`: piezas de diseño (cabecera, pie, divisiones, inicio).
- `static.py`: genera el sitio estático en la raíz del repo.
- `site.js`: script del sitio (idioma, mapa, asistente, panel de mando). Se copia a `assets/site.js`.
- `schema.sql`: base de datos Supabase (copiada a `supabase/schema.sql`).
- `img/`: imágenes de origen.

Regenerar:  `cd build && python3 static.py`
Probar en local: `python3 build/serve.py .` y abrir http://127.0.0.1:8765/es
