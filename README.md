# VERTEZ GROUP

Sitio estático multilingüe (ES / FR / EN).

- `/` redirige al idioma guardado (por defecto español).
- `/es`, `/fr`, `/en`: inicio, 8 divisiones, `/asistente` (asistente con voz) y `/admin` (panel de mando).
- Contenidos dinámicos (noticias, eventos, vídeos, fotos, portada) en Supabase: ver `supabase/schema.sql`
  y rellenar `assets/config.js` con la URL y la clave pública del proyecto.
- Despliegue: Vercel, sin build (Framework Preset: Other).
