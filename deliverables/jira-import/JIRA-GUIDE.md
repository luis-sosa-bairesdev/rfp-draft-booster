# 📖 Guía de Jira - RFP Draft Booster

## 🎯 Estado Actual del Proyecto

### Épicas (2)
- ✅ **SCRUM-21**: [EPIC] Project Setup & Infrastructure - **Finalizada**
- ✅ **SCRUM-32**: [EPIC] PDF Processing & Upload - **Finalizada**

### Sprint 1
- **Estado:** ✅ CERRADO (Closed)
- **Fecha inicio:** 2025-11-03
- **Fecha fin:** 2025-11-10
- **Issues:** 38 total (2 Epics + 36 Tasks)

---

## 🔍 Cómo Ver el Sprint Cerrado

### Opción 1: Ver Sprint Report (Recomendado)

1. Ve al tablero: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1

2. En el menú izquierdo, haz clic en **"Reports"** (Reportes)

3. Selecciona **"Sprint Report"**

4. En el desplegable de Sprint, selecciona **"SCRUM Sprint 1"**

5. Verás:
   - Issues completadas
   - Issues no completadas
   - Velocidad del Sprint
   - Burn-down chart

### Opción 2: Ver en Backlog

1. Ve a: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog

2. Haz scroll hacia abajo hasta encontrar **"Completed Sprints"** (Sprints Completados)

3. Haz clic en la flecha para expandir **"SCRUM Sprint 1"**

4. Verás todas las issues que estaban en ese Sprint

---

## ❓ Por Qué No Veo "User Stories"

### El Problema

Cuando creamos las issues en Jira, se crearon como tipo **"Task"** (Tarea) en lugar de **"Story"** (Historia).

**Estado actual:**
- ✅ 2 Epics
- ❌ 0 User Stories
- ✅ 36 Tasks (muchos deberían ser Stories)

### ¿Por Qué Pasó Esto?

En Jira, cuando usamos la API para crear issues, el tipo por defecto es "Task" si no especificamos explícitamente "Story". Las Tasks funcionan perfectamente, pero en metodología Scrum tradicional:

- **Stories** = Requisitos funcionales desde la perspectiva del usuario
- **Tasks** = Sub-tareas técnicas para implementar una Story

### ¿Es un Problema?

**NO necesariamente**. Las Tasks funcionan igual que las Stories para este proyecto. Ambas:
- ✅ Se pueden asignar a Sprints
- ✅ Se pueden marcar como completadas
- ✅ Aparecen en el tablero
- ✅ Tienen el mismo workflow

La diferencia es principalmente **semántica** y de **reportes**.

### Solución (Opcional)

Si quieres cambiar Tasks a Stories, puedo crear un script para:
1. Identificar qué Tasks deberían ser Stories
2. Cambiar su tipo de "Task" a "Story"

**¿Quieres que haga esto?** (Toma unos minutos)

---

## 📊 Cómo Ver las Issues en el Tablero

### Tablero Principal

https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1

**Problema:** Si el Sprint 1 está cerrado, no verás las issues en el tablero principal.

**Solución:** Necesitas crear un **nuevo Sprint** (Sprint 2) para ver issues en el tablero activo.

### Backlog

https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog

Aquí verás:
- Issues sin asignar a Sprint (parte superior)
- Sprints activos (medio)
- Sprints cerrados (parte inferior, colapsados)

---

## 🚀 Próximos Pasos Recomendados

### 1. Verificar Issues Actuales

**Comando:**
```bash
cd deliverables/jira-import
python3 verify_jira_status.py
```

Esto te mostrará todas las issues y su estado actual.

### 2. Ver Sprint 1 Cerrado

**URL Directa:**
https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/reports/burndown?sprint=1

### 3. Crear Sprint 2 para Epic 3

Si quieres empezar Epic 3 (LLM Requirements), necesitamos:
1. Crear Sprint 2
2. Mover las nuevas issues a Sprint 2
3. Iniciar el Sprint

---

## 📝 Scripts Disponibles

Tenemos varios scripts de automatización:

| Script | Función |
|--------|---------|
| `verify_jira_status.py` | Ver estado actual de todas las issues |
| `list_epics.py` | Listar todas las épicas |
| `cleanup_old_epics.py` | Borrar épicas duplicadas |
| `move_epics_to_sprint.py` | Mover épicas y stories a un Sprint |
| `close_sprint.py` | Cerrar un Sprint |
| `update_epic2_done.py` | Actualizar Epic 2 a Done |
| `fix_epic1_status.py` | Actualizar Epic 1 a Done |

---

## ❓ Preguntas Frecuentes

### ¿Por qué no veo issues en el tablero principal?

**Respuesta:** El tablero Scrum solo muestra issues del Sprint **activo**. Como Sprint 1 está cerrado, las issues no aparecen. Necesitas:
- Crear un nuevo Sprint, o
- Ver el Sprint cerrado en Reports → Sprint Report

### ¿Cómo veo las Épicas completadas?

**Opciones:**
1. **Backlog:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog
2. **Buscar directamente:**
   - SCRUM-21: https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-21
   - SCRUM-32: https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-32
3. **JQL Query:**
   ```
   project = SCRUM AND type = Epic ORDER BY key ASC
   ```

### ¿Puedo "reabrir" el Sprint 1?

**NO.** Una vez cerrado un Sprint, no se puede reabrir en Jira. Pero puedes:
- Ver sus reportes
- Mover issues no terminadas a un nuevo Sprint
- Aprender de las métricas para futuros Sprints

---

## 🔗 Enlaces Útiles

- **Tablero:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1
- **Backlog:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog
- **Sprint Report:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/reports/burndown?sprint=1
- **Epic 1 (SCRUM-21):** https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-21
- **Epic 2 (SCRUM-32):** https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-32

---

**¿Tienes más preguntas?** Puedo ayudarte a:
1. Cambiar Tasks a Stories
2. Crear Sprint 2
3. Ver reportes específicos
4. Cualquier otra configuración de Jira



