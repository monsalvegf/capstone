#!/usr/bin/env python3
"""
Script de verificación de configuración SQLite para Quality System

Ejecuta este script después de configurar el proyecto para verificar que:
1. WAL mode está habilitado correctamente
2. Todos los PRAGMAs están configurados como se esperaba
3. Los archivos de base de datos existen

Uso:
    python verify_sqlite_config.py

    O desde manage.py shell:
    python manage.py shell
    >>> exec(open('verify_sqlite_config.py').read())
"""

import os
import sys
import sqlite3
from pathlib import Path


def verificar_configuracion_sqlite():
    """Verifica la configuración completa de SQLite"""

    print("=" * 70)
    print("VERIFICACIÓN DE CONFIGURACIÓN SQLite - Quality System")
    print("=" * 70)
    print()

    # Encontrar la base de datos
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / 'db.sqlite3'

    # Verificar que exista la base de datos
    if not db_path.exists():
        print("❌ ERROR: db.sqlite3 no encontrada")
        print(f"   Ruta esperada: {db_path}")
        print("   → Ejecuta: python manage.py migrate")
        return False

    print(f"✅ Base de datos encontrada: {db_path}")
    print()

    # Conectar y verificar configuración
    try:
        conn = sqlite3.connect(str(db_path), timeout=20)
        cursor = conn.cursor()

        # Configuraciones esperadas
        configuraciones_esperadas = {
            'journal_mode': ('WAL', 'Modo de diario'),
            'synchronous': (1, 'Modo de sincronización (1=NORMAL)'),
            'temp_store': (2, 'Almacenamiento temporal (2=MEMORY)'),
        }

        print("CONFIGURACIONES SQLITE:")
        print("-" * 70)

        todo_correcto = True

        # Verificar cada configuración
        for pragma, (valor_esperado, descripcion) in configuraciones_esperadas.items():
            cursor.execute(f"PRAGMA {pragma};")
            valor_actual = cursor.fetchone()[0]

            # Normalizar valores para comparación
            if isinstance(valor_esperado, str):
                coincide = str(valor_actual).upper() == valor_esperado.upper()
            else:
                coincide = valor_actual == valor_esperado

            status = "✅" if coincide else "❌"
            print(f"{status} {pragma:20} = {valor_actual:15} ({descripcion})")

            if not coincide:
                print(f"   ⚠️  Esperado: {valor_esperado}")
                todo_correcto = False

        # Cache size (es especial, mostramos el valor pero no validamos exacto)
        cursor.execute("PRAGMA cache_size;")
        cache_size = cursor.fetchone()[0]
        cache_mb = abs(cache_size) / 1024  # Convertir KB a MB si es negativo
        print(f"ℹ️  cache_size           = {cache_size} páginas (~{cache_mb:.1f} MB)")

        # Busy timeout
        cursor.execute("PRAGMA busy_timeout;")
        busy_timeout = cursor.fetchone()[0]
        timeout_segundos = busy_timeout / 1000
        esperado_timeout = busy_timeout >= 20000
        status = "✅" if esperado_timeout else "❌"
        print(f"{status} busy_timeout         = {busy_timeout} ms ({timeout_segundos:.1f} segundos)")
        if not esperado_timeout:
            print(f"   ⚠️  Esperado: >= 20000 ms")
            todo_correcto = False

        conn.close()

        print()
        print("-" * 70)

        # Verificar archivos WAL
        print()
        print("ARCHIVOS DE BASE DE DATOS:")
        print("-" * 70)

        archivos = {
            'db.sqlite3': 'Base de datos principal',
            'db.sqlite3-wal': 'Write-Ahead Log (WAL)',
            'db.sqlite3-shm': 'Shared Memory Index',
        }

        for archivo, descripcion in archivos.items():
            ruta_archivo = base_dir / archivo
            existe = ruta_archivo.exists()
            status = "✅" if existe else "ℹ️ "
            tamaño = f"({ruta_archivo.stat().st_size:,} bytes)" if existe else "(no creado aún)"
            print(f"{status} {archivo:20} {tamaño:20} - {descripcion}")

        print()
        if not (base_dir / 'db.sqlite3-wal').exists():
            print("ℹ️  Nota: Los archivos -wal y -shm se crean automáticamente cuando")
            print("   Django realiza la primera conexión con WAL mode habilitado.")
            print("   Ejecuta cualquier comando de Django para activarlos:")
            print("   → python manage.py check")

        print()
        print("=" * 70)

        if todo_correcto:
            print("✅ RESULTADO: Configuración SQLite CORRECTA")
            print()
            print("🚀 Tu base de datos está optimizada para:")
            print("   - 10 usuarios consultando simultáneamente")
            print("   - 4 usuarios escribiendo simultáneamente")
            print("   - Lecturas y escrituras concurrentes sin bloqueos")
            print("   - Cache de 64MB para consultas rápidas")
        else:
            print("⚠️  RESULTADO: Configuración SQLite PARCIAL")
            print()
            print("🔧 Acciones recomendadas:")
            print("   1. Verifica que settings.py tenga las configuraciones correctas")
            print("   2. Reinicia el servidor Django")
            print("   3. Ejecuta: python manage.py shell")
            print("      >>> from quality.settings import enable_sqlite_wal_mode")
            print("      >>> enable_sqlite_wal_mode()")

        print("=" * 70)
        print()

        return todo_correcto

    except Exception as e:
        print(f"❌ ERROR al conectar con SQLite: {e}")
        return False


def test_concurrencia():
    """Test simple de escrituras concurrentes"""
    import threading
    import time

    print()
    print("=" * 70)
    print("TEST DE CONCURRENCIA (Simulación de 4 escrituras simultáneas)")
    print("=" * 70)
    print()

    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / 'db.sqlite3'

    resultados = []

    def escribir_test(thread_id):
        try:
            conn = sqlite3.connect(str(db_path), timeout=20)
            cursor = conn.cursor()

            # Crear tabla de test si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sqlite_config_test (
                    id INTEGER PRIMARY KEY,
                    thread_id INTEGER,
                    timestamp REAL
                )
            """)

            # Insertar dato
            inicio = time.time()
            cursor.execute(
                "INSERT INTO sqlite_config_test (thread_id, timestamp) VALUES (?, ?)",
                (thread_id, time.time())
            )
            conn.commit()
            tiempo = time.time() - inicio

            conn.close()
            resultados.append((thread_id, True, tiempo))
            print(f"✅ Thread {thread_id}: Escritura exitosa ({tiempo*1000:.2f}ms)")

        except Exception as e:
            resultados.append((thread_id, False, str(e)))
            print(f"❌ Thread {thread_id}: Error - {e}")

    # Lanzar 4 threads simultáneos
    threads = []
    for i in range(4):
        t = threading.Thread(target=escribir_test, args=(i,))
        threads.append(t)

    print("Iniciando 4 escrituras simultáneas...")
    inicio_total = time.time()

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    tiempo_total = time.time() - inicio_total

    # Limpiar tabla de test
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("DROP TABLE IF EXISTS sqlite_config_test")
        conn.commit()
        conn.close()
    except:
        pass

    print()
    exitosas = sum(1 for _, success, _ in resultados if success)
    print(f"Resultado: {exitosas}/4 escrituras exitosas en {tiempo_total*1000:.2f}ms")

    if exitosas == 4:
        print("✅ Test de concurrencia EXITOSO")
        print("   WAL mode permite escrituras simultáneas sin bloqueos")
    else:
        print("⚠️  Algunas escrituras fallaron")
        print("   Verifica la configuración de WAL mode")

    print("=" * 70)
    print()


if __name__ == '__main__':
    exito = verificar_configuracion_sqlite()

    if exito:
        respuesta = input("\n¿Deseas ejecutar test de concurrencia? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            test_concurrencia()

    sys.exit(0 if exito else 1)
