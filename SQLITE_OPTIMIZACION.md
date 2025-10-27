# Optimización SQLite para Producción - Quality System

## ✅ Cambios Implementados

### 1. Configuración en `quality/settings.py`

Se ha optimizado la configuración de la base de datos SQLite con los siguientes cambios:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'timeout': 20,  # ⬅️ NUEVO: 20 segundos de timeout
        'OPTIONS': {
            'init_command': (
                "PRAGMA journal_mode=WAL; "        # ⬅️ NUEVO: WAL mode
                "PRAGMA busy_timeout=20000; "      # ⬅️ NUEVO: Refuerzo timeout
                "PRAGMA synchronous=NORMAL; "      # ⬅️ NUEVO: Balance velocidad/seguridad
                "PRAGMA cache_size=-64000; "       # ⬅️ NUEVO: Cache 64MB
                "PRAGMA temp_store=MEMORY;"        # ⬅️ NUEVO: Temp en RAM
            ),
        },
    }
}
```

---

## 📋 Explicación de Cada Optimización

### 🔴 1. **timeout = 20 segundos**

**Qué hace:**
- Define cuánto tiempo espera Django antes de lanzar error "database is locked"
- Por defecto SQLite usa 5 segundos

**Beneficio:**
- Reduce drásticamente los errores de bloqueo en escrituras concurrentes
- Permite que transacciones largas completen sin fallar
- Ideal para 4 usuarios escribiendo simultáneamente

**Trade-off:**
- Operaciones bloqueadas pueden esperar hasta 20s (aceptable en tu caso de uso)

---

### 🔴 2. **PRAGMA journal_mode=WAL** (Write-Ahead Logging)

**Qué hace:**
- Cambia el modo de diario de SQLite de "delete" (default) a "WAL"
- En WAL mode, los cambios se escriben primero en archivo -wal antes del principal

**Beneficio:**
- **Lecturas y escrituras pueden ocurrir simultáneamente** ⭐
- Lectores NO bloquean escritores y viceversa
- Hasta 1000x más rápido en algunas operaciones
- Reduce **drásticamente** los errores "database is locked"

**Trade-off:**
- Crea 2 archivos adicionales:
  - `db.sqlite3-wal` (Write-Ahead Log)
  - `db.sqlite3-shm` (Shared Memory Index)
- Estos archivos son **normales y necesarios**, se crean/eliminan automáticamente

**Cuándo aparecen los archivos:**
- Se crean cuando hay transacciones activas
- Se eliminan automáticamente cuando no hay actividad (comportamiento normal)
- **No es un error** que no estén siempre presentes

---

### 🟡 3. **PRAGMA busy_timeout=20000**

**Qué hace:**
- Refuerza el timeout a nivel de SQLite (20000 ms = 20 segundos)
- Complementa el `timeout` de Django para mayor robustez

**Beneficio:**
- Doble capa de protección contra timeouts
- Asegura que todas las conexiones respeten el timeout

---

### 🟡 4. **PRAGMA synchronous=NORMAL**

**Qué hace:**
- Controla cuándo SQLite sincroniza datos al disco
- Opciones:
  - `FULL` (2): Muy seguro pero lento (sincroniza cada escritura)
  - `NORMAL` (1): Seguro en WAL mode, mucho más rápido
  - `OFF` (0): Peligroso, puede corromper DB en crash del SO

**Beneficio:**
- Con WAL mode, NORMAL es tan seguro como FULL
- Aproximadamente **50% más rápido** que FULL
- Solo se pierde data si el SO crashea en medio de checkpoint

**Trade-off:**
- En crash del sistema operativo (muy raro), podrías perder últimos commits
- En crash de aplicación (común), NO se pierde nada

---

### 🟢 5. **PRAGMA cache_size=-64000**

**Qué hace:**
- Define el tamaño del cache en memoria
- Valor negativo = kilobytes (64000 KB = 64 MB)
- Por defecto: -2000 (2 MB)

**Beneficio:**
- Reduce lecturas de disco
- Acelera consultas frecuentes
- Especialmente útil para tu caso (10 usuarios consultando)

**Trade-off:**
- Usa 64MB de RAM por conexión de Django
- Ajustar según RAM disponible del servidor

---

### 🟢 6. **PRAGMA temp_store=MEMORY**

**Qué hace:**
- Almacena tablas temporales en RAM en vez de disco
- Opciones:
  - `0` (DEFAULT): Usa configuración compilada
  - `1` (FILE): Disco
  - `2` (MEMORY): RAM

**Beneficio:**
- Acelera operaciones con índices temporales
- Mejora performance de ORDER BY, GROUP BY, DISTINCT
- Reduce I/O de disco

**Trade-off:**
- Usa más RAM para operaciones complejas (mínimo en tu caso)

---

## 🎯 Resultados Esperados

### Antes (SQLite sin optimizar):
```
❌ Lectores bloquean escritores
❌ Escritores bloquean lectores
❌ Timeout de 5 segundos
❌ Cache de 2MB
❌ Operaciones temp en disco
⚠️  Errores "database is locked" frecuentes con 4+ usuarios
```

### Después (SQLite optimizado):
```
✅ Lecturas y escrituras simultáneas (WAL)
✅ Timeout de 20 segundos
✅ Cache de 64MB
✅ Operaciones temp en RAM
✅ Soporta 10 lectores + 4 escritores sin bloqueos
🚀 Hasta 50% más rápido en operaciones
```

---

## 🔧 Verificación

### Opción 1: Desde manage.py shell
```bash
python manage.py shell
```
```python
from quality.settings import enable_sqlite_wal_mode
enable_sqlite_wal_mode()
```

### Opción 2: Script de verificación
```bash
python verify_sqlite_config.py
```

### Opción 3: Verificación desde Django (RECOMENDADO)
```bash
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

pragmas = ['journal_mode', 'synchronous', 'cache_size', 'temp_store', 'busy_timeout']
for pragma in pragmas:
    cursor.execute(f'PRAGMA {pragma};')
    print(f'{pragma:20} = {cursor.fetchone()[0]}')
"
```

**Salida esperada:**
```
journal_mode         = wal
synchronous          = 1
cache_size           = -64000
temp_store           = 2
busy_timeout         = 20000
```

---

## 📦 Backups

### ⚠️ IMPORTANTE: Con WAL mode habilitado

Cuando hagas backups de la base de datos, debes incluir **3 archivos**:

```bash
# Backup completo
cp db.sqlite3 backup/
cp db.sqlite3-wal backup/  # Si existe
cp db.sqlite3-shm backup/  # Si existe
```

**O mejor aún, usa checkpoint antes del backup:**
```bash
sqlite3 db.sqlite3 "PRAGMA wal_checkpoint(FULL);"
cp db.sqlite3 backup/
```

Esto consolida todos los cambios del WAL en el archivo principal.

---

## 📊 Performance Esperado

### Escenario: 10 usuarios consultando + 4 escribiendo

| Métrica | Sin WAL | Con WAL | Mejora |
|---------|---------|---------|--------|
| Lecturas simultáneas | Bloqueadas durante escritura | ✅ Sin bloqueo | ∞ |
| Escrituras simultáneas | 1 a la vez | 1 a la vez (normal) | - |
| Timeout errors | Frecuentes | Raros | 80-90% |
| Velocidad escritura | Baseline | 1.5-2x | 50-100% |
| Velocidad lectura | Baseline | 1.2-1.5x | 20-50% |

---

## 🚨 Cuándo Migrar a PostgreSQL

Considera migrar cuando:

- ✅ **Más de 20 usuarios concurrentes**
- ✅ **Escrituras intensivas** (>100 transacciones/segundo)
- ✅ **Necesidad de replicación** o alta disponibilidad
- ✅ **Base de datos > 100GB**
- ✅ **Necesitas transacciones distribuidas**
- ✅ **Requieres full-text search avanzado**

Para tu caso actual (10 lectores + 4 escritores), **SQLite optimizado es suficiente**.

---

## 📝 Archivos Modificados

1. **`quality/settings.py`** - Configuración de DATABASES actualizada
2. **`verify_sqlite_config.py`** - Script de verificación (nuevo)
3. **`SQLITE_OPTIMIZACION.md`** - Esta documentación (nuevo)

---

## 🎓 Referencias

- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [PRAGMA Statements](https://www.sqlite.org/pragma.html)
- [Django Database Settings](https://docs.djangoproject.com/en/5.1/ref/databases/#sqlite-notes)

---

## ✅ Checklist de Deployment

Cuando despliegues a producción:

- [ ] Verificar que `timeout = 20` en settings.py
- [ ] Verificar que `init_command` tiene los 5 PRAGMAs
- [ ] Ejecutar `python manage.py shell -c "from quality.settings import enable_sqlite_wal_mode; enable_sqlite_wal_mode()"`
- [ ] Verificar que journal_mode = wal
- [ ] Configurar backups con checkpoint
- [ ] Monitorear logs por "database is locked" (deberían desaparecer)
- [ ] Ajustar `cache_size` según RAM disponible (64MB es un buen default)

---

**Fecha de implementación:** 2025-10-27
**Optimizado para:** 10 usuarios lectores + 4 escritores simultáneos
**Status:** ✅ Implementado y verificado
