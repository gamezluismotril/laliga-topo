# ⚽ La Liga del Topo 26/27

Sistema de predicción de partidos de La Liga basado en modelos estadísticos, datos históricos y cuotas de mercado.

![La Liga del Topo](icono.png)

---

## 📋 Descripción

**La Liga del Topo 26/27** es un proyecto personal de análisis y predicción de partidos de fútbol, centrado en La Liga española temporada 2026/27.

El sistema combina:

- **Modelo Dixon-Coles ponderado** → predicción de goles y resultado 1X2
- **Modelo Poisson casa/fuera** → córners y tarjetas amarillas
- **Factor árbitro** → ajuste de tarjetas según el colegiado
- **Consenso de cuotas** → blend con el mercado para mayor precisión
- **Cálculo de VALUE** → detección de apuestas con valor esperado positivo

---

## 🎯 Características

### Modelos implementados

| Modelo | Mercado | Validación |
|---|---|---|
| Dixon-Coles ponderado | 1X2, Over/Under goles | ✅ Walk-forward (5 temporadas) |
| Poisson casa/fuera | Córners | ⚠️ Cálculo directo |
| Poisson casa/fuera + árbitro | Amarillas | ⚠️ Cálculo directo |
| Blend con consenso | Todos | ✅ Mejora la precisión |

### Interfaz web (Streamlit)

- **Selector de equipos** y árbitro
- **Cuotas reales** editables
- **32 mercados** calculados por partido
- **Cálculo de value** con semáforo (verde/rojo)
- **Escudos de equipos**
- **Diseño responsive**

---

## 📊 Resultados walk-forward

| Umbral | Apuestas | Accuracy | ROI | Temporadas ganadoras |
|---|---|---|---|---|
| 0.50 | 706 | 64.9% | +0.1% | 2/4 |
| 0.55 | 499 | 71.0% | +3.5% | 2/4 |
| **0.60** | **344** | **77.8%** | **+6.2%** | **3/4** |

**Validación honesta**: 3 de 4 temporadas con ROI positivo usando el filtro de confianza ≥ 0.60.

---

## 🗂️ Estructura del proyecto
