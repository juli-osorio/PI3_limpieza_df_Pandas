# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos

## Cómo empezar

1. Clona el repositorio y entra a la carpeta del proyecto:

   ```
   git clone <URL-DEL-REPOSITORIO>
   cd <NOMBRE-DE-LA-CARPETA>
   ```

2. Crea y activa un ambiente virtual. Las instrucciones para Windows y Mac/Linux están en `LEEME_ambiente.txt`.

3. Instala las librerías:

   ```
   pip install -r requirements.txt
   ```

4. Ejecuta el script:

   ```
   python analisis_desercion.py
   ```

Ejecuta el comando desde la carpeta del proyecto.

## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal. Tiene un TODO por cada paso.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.
```

Lo que genera el script (`dataset_limpio.csv`, `decisiones.csv` y `graficos/`) aparece en `Data/processed/` al ejecutarlo. Los dos últimos se suben al repositorio, porque son parte de la entrega.

## Qué debes hacer

Completa los TODO de `analisis_desercion.py` en orden. Cada función tiene un docstring con preguntas: respóndelas antes de escribir el código. Cada decisión que tomes debe quedar registrada con `registrar()`.

Cuando termines, el script debe producir:

- `Data/processed/dataset_limpio.csv`: el dataset limpio.
- `Data/processed/decisiones.csv`: la tabla de decisiones.
- `Data/processed/graficos/`: los cuatro gráficos.

La guía del taller (`Taller_Retencion_Estudiantil.docx`) explica cada método antes de usarlo, con ejemplos y errores frecuentes.

## Entrega

Sube tu código completo al repositorio y envía el enlace por el formulario de entrega. La entrega es individual.

El repositorio debe incluir:

- `analisis_desercion.py` con todos los TODO completados.
- `Data/processed/decisiones.csv` y la carpeta `Data/processed/graficos/`.
- Un `README.md` al final de este archivo, con una sección titulada **Mis decisiones y respuestas**. Debe incluir:
  0. El diccionario de datos: la tabla de las 23 columnas con tipo, descripción y rol, completada según el paso 1 de la guía.
  1. Tu diagnóstico de calidad: qué problemas encontraste y en qué columnas.
  2. Tus decisiones de limpieza, con su justificación.
  3. Las respuestas a las cinco preguntas, cada una con el número de estudiantes por grupo.
  4. Tu respuesta a la reflexión sobre asociación y causalidad.
  5. Tu respuesta a la reflexión sobre `motivo_retiro` y la predicción.
  6. Tu respuesta a la reflexión sobre el uso de variables sensibles.

El script debe ejecutarse sin errores desde cero. Cada decisión necesita una justificación, y cada conclusión debe apoyarse en un número del análisis.


---

## Mis decisiones y respuestas

El script `analisis_desercion.py` genera un reporte en HTML con todos los resultados: `Data/processed/reporte.html`. Para verlo, ejecuta el script y abre ese archivo en el navegador. El diseño de la página está en `plantilla.html`.

### 0. Diccionario de datos

| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| id_estudiante | texto | Código único de cada estudiante (EST00001) | identificación |
| programa | categórica | Carrera que estudia | explicativa |
| facultad | categórica | Facultad a la que pertenece el programa | explicativa |
| jornada | categórica | Horario de estudio: Diurna, Nocturna o Fin de semana | explicativa |
| semestre | numérica | Semestre que cursa (1 a 10) | explicativa |
| promedio_acumulado | numérica | Nota promedio de la carrera, en escala de 0 a 5 | explicativa |
| creditos_aprobados | numérica | Créditos que ha aprobado | explicativa |
| materias_reprobadas | numérica | Número de materias que ha perdido | explicativa |
| asistencia_pct | numérica (llega como texto) | Porcentaje de asistencia a clases | explicativa |
| sesiones_tutoria | numérica | Veces que asistió a tutorías | explicativa |
| cambios_programa | numérica | Veces que cambió de carrera (0 o 1) | explicativa |
| estrato | numérica (ordinal) | Estrato socioeconómico de la vivienda (1 a 6) | explicativa |
| beca | categórica | Si recibe beca (sí o no) | explicativa |
| trabaja | categórica | Si trabaja además de estudiar (sí o no) | explicativa |
| horas_trabajo_semana | numérica (llega como texto) | Horas que trabaja por semana | explicativa |
| distancia_km | numérica | Distancia de la casa a la institución, en km | explicativa |
| edad | numérica | Edad en años | explicativa |
| genero | categórica | Femenino o Masculino | explicativa |
| ciudad_procedencia | categórica | Ciudad de donde viene | explicativa |
| tipo_colegio | categórica | Si el colegio de bachillerato fue Público o Privado | explicativa |
| fecha_matricula | fecha (llega como texto) | Fecha en que se matriculó | explicativa |
| estado | categórica | Situación actual: activo, graduado o desertor | resultado |
| motivo_retiro | categórica | Razón del retiro (Económico, Académico, Personal, etc.). Solo aplica a desertores | resultado |

### 1. Diagnóstico de calidad

El dataset original tiene 10.150 filas y 23 columnas.

| Tipo de problema | Columna | Cantidad |
|---|---|---|
| Nulos reales | promedio_acumulado | 304 |
| | distancia_km | 199 |
| | tipo_colegio | 152 |
| | ciudad_procedencia | 103 |
| | motivo_retiro | 6.877 (esperados, ver abajo) |
| Faltantes disfrazados | asistencia_pct (`-`) | 202 |
| | horas_trabajo_semana (`-`) | 2.822 |
| | distancia_km (`999`) | 152 |
| Formato inconsistente | asistencia_pct (con `%`) | 300 |
| | fecha_matricula (DD/MM/AAAA en vez de AAAA-MM-DD) | 3.052 |
| Valores imposibles | edad fuera de 15 a 60 años (12 y 150) | 12 |
| | promedio_acumulado mayor a 5 (45, 62, 78) | 17 |
| | horas_trabajo_semana mayor a 100 (200) | 30 |
| Errores tipográficos | programa (sin tilde) | 260 |
| | jornada (minúsculas y mayúsculas) | 485 |
| | genero (M, F, femenino) | 559 |
| | ciudad_procedencia (BOGOTÁ, Bogota, medellin…) | 542 |
| Duplicados | filas idénticas, incluido id_estudiante | 150 |

- `asistencia_pct` y `horas_trabajo_semana` llegan como texto porque tienen `%` y `-`. Basta una celda que no sea número para que pandas deje toda la columna como texto.
- Los 6.877 nulos de `motivo_retiro` no son errores: hay 3.273 desertores y 3.273 motivos registrados. Los vacíos son estudiantes activos o graduados, a quienes la pregunta no aplica.
- En el mapa de faltantes, `asistencia_pct` y `horas_trabajo_semana` no muestran huecos porque sus faltantes estaban disfrazados con `-`. Por eso `isnull()` no basta para encontrar todos los faltantes.
- El problema que más afecta el análisis son las columnas numéricas guardadas como texto: mientras lo sean, no se pueden calcular promedios, cuartiles ni responder la pregunta 5. Le siguen los promedios en otra escala, que inflaban el promedio general (la desviación estándar bajó de 2,61 a 0,64 al quitarlos).

### 2. Decisiones de limpieza

La tabla completa, con filas afectadas y justificación, está en `Data/processed/decisiones.csv` y al final del reporte HTML.

| Paso | Decisión | Justificación |
|---|---|---|
| Convertir números | Quitar `%` de asistencia; `-` y `999` a nulo; convertir con `pd.to_numeric` | El `%` es solo formato. El `-` y el `999` significan "sin dato" y deben ser nulos reales. |
| Unificar categorías | `strip()` + `lower()` y un diccionario hacia los valores válidos | Eran el mismo valor escrito distinto. Sin unificar, un grupo se contaba como varios. No se unificaron valores distintos: Rionegro no es Medellín y "Otra ciudad" es una categoría propia. |
| Fechas | Convertir cada formato por separado y unirlos con `fillna()` | Con formato explícito no se confunden día y mes (03/04 puede ser 3 de abril o 4 de marzo). |
| Duplicados | Eliminar 150 filas | Repiten también el `id_estudiante`, así que son el mismo estudiante dos veces y lo contarían doble. |
| Promedio nulo | Eliminar 298 filas | Una nota no se puede inventar. Imputar el promedio escondería a los estudiantes de bajo rendimiento. |
| Ciudad y colegio nulos | Reemplazar por "Sin dato" (96 y 145) | Borrar la fila perdería sus demás datos, e inventar el valor sería falso. |
| motivo_retiro nulo | Dejar como nulo | Es esperado: solo aplica a desertores. |
| Edad imposible | Reemplazar por la mediana (22 años), 12 filas | Es un error de digitación. La mediana no se ve afectada por los extremos. |
| Promedio > 5 | Eliminar 15 filas | No se sabe la escala original (45 podría ser 4,5 o 2,25). Adivinar sería inventar la nota. |
| Horas si no trabaja | Poner 0 (2.703 filas) | Si no trabaja, sus horas son 0: el dato se deduce, no falta. |
| Horas > 100 | Reemplazar por la mediana de quienes trabajan (24), 29 filas | 200 horas no caben en una semana. La mediana de todos daría 0 por los que no trabajan. |
| Asistencia nula | Dejar como nulo (197 estudiantes sin cuartil) | Inventar una asistencia sesgaría la pregunta 5. |

Dataset final: **9.687 filas y 25 columnas** (se agregaron `desertor` y `cuartil_asistencia`).

### 3. Respuestas a las cinco preguntas

**Pregunta 1. ¿Qué programa tiene la tasa de deserción más alta?**
Ingeniería Industrial, con **40,2 %** (1.271 estudiantes).

**Pregunta 2. ¿Hay diferencia entre becados y no becados?**
Sí. Los becados desertan **21,9 %** (2.683 estudiantes) y los no becados **36,4 %** (7.004 estudiantes), es una posible causa de por qué los becados desertan menos.

**Pregunta 3. ¿Qué jornada tiene el menor promedio acumulado?**
La **Nocturna**, con **3,46** (2.666 estudiantes), frente a Fin de semana con 3,70 (949) y Diurna con 3,72 (6.072).

**Pregunta 4. ¿Cuántas materias reprobadas tienen los desertores frente a los activos?**
Los desertores tienen en promedio **3,07** materias reprobadas (3.136 estudiantes) y los activos **0,62** (5.692 estudiantes), casi cinco veces menos. Se excluyen los 859 graduados porque la pregunta compara a quienes se fueron con quienes siguen estudiando. Los graduados no pertenecen a ninguno de los dos grupos, y mezclarlos cambiaría el promedio de los no desertores.

**Pregunta 5. ¿La deserción aumenta conforme baja la asistencia?**
Sí:

| Cuartil | Asistencia promedio | Tasa de deserción | Estudiantes |
|---|---|---|---|
| Q1 (más baja) | 73,9 % | 61,9 % | 2.385 |
| Q2 | 84,4 % | 36,7 % | 2.386 |
| Q3 | 91,3 % | 20,7 % | 2.348 |
| Q4 (más alta) | 98,7 % | 9,4 % | 2.371 |

En el cuartil de menor asistencia deserta 6 de cada 10 estudiantes; en el de mayor asistencia, menos de 1 de cada 10.

### 4. Reflexión: asociación y causalidad
- Es posible que los becados deserten menos porque la beca los retiene, sin embargo es una asociación y puede que allí no esté la causa de la retención. Abría que ver más factores, como si trabaja, la situación ecónomica. -->
- Faltar a clase puede ser la causa de la deserción, pero también puede ser un efecto. -->
- Quizas se puedan sacar mejores conclusiones aislando los grupos por personas que trabajan o por situación económica para obtener la causa de la deserción.

### 5. Reflexión: `motivo_retiro` y la predicción

el motivo_retiro no funciona para predecir pq solo se llena despues de que el estudiante se va y con un estudiante activo la columna está vacía. Donde sí sirve es para entender por qué se fueron los que ya se fueron, y con eso diseñar estrategias para que los demás se queden.

### 6. Reflexión: uso de variables sensibles

Las columnas como genero, estrato, edad, ciudad_procedencia y tipo_colegio son datos personales, por lo que hay que tratarlos con cuidado, no cualquiera puede tener acceso a ellos. Estos dicen quién es el estudiante, no lo que hace. Si la institución decide con ellas, puede terminar discriminando y negándole cupos o becas a un grupo solo por de dónde viene y no por su trayectoria: asistencia y rendimiento en las materias.

