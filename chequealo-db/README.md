# chequealo-db

Base de datos pública que usa la app Chequealo para reconocer malware y enlaces peligrosos conocidos.
Se genera cada día con datos de MalwareBazaar y URLhaus (abuse.ch).

## Pasos para ponerlo en marcha

1. En GitHub crea un repositorio **público** llamado `chequealo-db` y sube el contenido de esta carpeta.
2. En el repositorio: **Settings → Secrets and variables → Actions → New repository secret**.
   - Nombre: `ABUSECH_AUTH_KEY`
   - Valor: tu Auth-Key de abuse.ch (nunca la escribas en un archivo).
3. Pestaña **Actions → Actualizar base de Chequealo → Run workflow** para generar la primera versión.
   Si falla, abre el registro de la ejecución y copia el error.
4. En la app, abre `LocalDb.kt` y cambia `TU_USUARIO` por tu usuario de GitHub en `BASE_URL`.
5. Vuelve a compilar la app.

La app descarga `meta.json` una vez al día y solo baja el resto si hay una versión nueva.
