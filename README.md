# py-boletus

Proyecto antiguo de analisis de combinaciones de Bonoloto, actualizado para usar `mise` y `uv`.

## Requisitos

- `mise` para fijar las herramientas del proyecto
- `uv` para gestionar el entorno y las dependencias

Si ya tienes `mise`, este repo fija:

- `python 3.14.4`
- `uv` en su ultima version disponible

## Primer uso

```bash
mise install
uv sync
```

Esto crea el entorno virtual en `.venv/` y resuelve las dependencias definidas en `pyproject.toml`.

## Ejecutar scripts

```bash
uv run python update_data.py
uv run python test_data.py
uv run python reducida_test.py
uv run python oh_fortuna.py
```

Si prefieres usar `python` directamente, primero activa el entorno virtual:

```bash
source .venv/bin/activate
python oh_fortuna.py
```

## Estructura de dependencias

La fuente de verdad de dependencias ya no es `requirements.txt`, sino `pyproject.toml`.

## Troubleshooting

### `mise install` falla con `Python installation is missing a lib directory`

Ese error aparece con versiones antiguas de `mise` al intentar instalar algunos builds precompilados de Python 3.14 en macOS.

Actualiza `mise` y vuelve a ejecutar la instalacion:

```bash
brew upgrade mise
mise --version
mise install
uv sync
```

Si tu `mise` sigue siendo anterior a `v2026.3.10`, conviene actualizarlo antes de depurar nada mas.

### `ModuleNotFoundError` despues de `uv sync`

`uv sync` instala dependencias dentro de `.venv/`. Si luego ejecutas `python3 script.py`, es posible que estes usando el Python global del sistema y no el del proyecto.

Usa una de estas dos opciones:

```bash
uv run python oh_fortuna.py
```

```bash
source .venv/bin/activate
python oh_fortuna.py
```
