from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import io

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

PLANTILLA = Path(__file__).parent / "plantilla.html"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []

REPORTE = []  # lista donde se guardan los pedazos del HTML


def seccion(titulo):
    """Agrega un título grande al reporte (ej: '1. Explorar')."""
    REPORTE.append(f"<h2>{titulo}</h2>")


def bloque(subtitulo, contenido):
    """Agrega un subtítulo y su contenido al reporte."""
    REPORTE.append(f"<h3>{subtitulo}</h3>{contenido}")


def guardar_reporte():
    """Lee la plantilla, pone los resultados en el hueco y guarda reporte.html."""
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    html = plantilla.replace("<!-- CONTENIDO -->", "".join(REPORTE))
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "reporte.html").write_text(html, encoding="utf-8")
    print("Reporte guardado en Data/processed/reporte.html")


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })

#---------------------------------------------------------------
#UNO - HECHO
#---------------------------------------------------------------
def explorar(df):
    """PASO 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    # TODO 1: imprimir shape, info(), describe() y value_counts() de las columnas indicadas.
    seccion("1. Explorar")

    bloque("shape", f"<p>{df.shape}</p>")

    buffer = io.StringIO()
    df.info(buf=buffer)
    bloque("info()", f"<pre>{buffer.getvalue()}</pre>")

    bloque("describe()", df.describe().to_html())

    for col in ["programa", "jornada", "genero", "estado"]:
        bloque(f"value_counts() de {col}", df[col].value_counts().to_frame().to_html())

#---------------------------------------------------------------
#DOS - HECHO
#---------------------------------------------------------------

def auditar(df):
    """PASO 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    # TODO 2: imprimir cada uno de los conteos de problemas.
    seccion("2. Auditar")

    # 1. Nulos reales: celdas vacías, por columna
    nulos = df.isnull().sum()
    nulos = nulos[nulos > 0]  # solo las columnas que tienen nulos
    bloque("Nulos reales", nulos.to_frame("nulos").to_html())

    # 2. Faltantes disfrazados: valores que significan "sin dato"
    guiones_asist = (df["asistencia_pct"] == "-").sum()
    guiones_horas = (df["horas_trabajo_semana"] == "-").sum()
    dist_999 = (df["distancia_km"] == 999).sum()
    bloque("Faltantes disfrazados",
           f"<p>Guiones en asistencia_pct: {guiones_asist}<br>"
           f"Guiones en horas_trabajo_semana: {guiones_horas}<br>"
           f"Valores 999 en distancia_km: {dist_999}</p>")

    # 3. Formato inconsistente: números con símbolo %
    con_porcentaje = df["asistencia_pct"].str.contains("%", regex=False).sum()
    bloque("Símbolo % en asistencia_pct", f"<p>{con_porcentaje} celdas</p>")

    # 4. Valores imposibles
    edad_mal = ((df["edad"] < 15) | (df["edad"] > 60)).sum()
    prom_mal = (df["promedio_acumulado"] > 5).sum()
    horas = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")  # copia temporal, no cambia df
    horas_mal = (horas > 100).sum()
    bloque("Valores imposibles",
           f"<p>Edades fuera de 15 a 60 años: {edad_mal}<br>"
           f"Promedios mayores a 5: {prom_mal}<br>"
           f"Horas de trabajo mayores a 100 por semana: {horas_mal}</p>")

    # 5. Duplicados: filas idénticas en todas las columnas
    duplicados = df.duplicated().sum()
    bloque("Filas duplicadas", f"<p>{duplicados} filas</p>")

    # 6. Fechas en formato DD/MM/AAAA (las que tienen '/')
    fechas_dd = df["fecha_matricula"].str.contains("/", regex=False).sum()
    bloque("Fechas en formato DD/MM/AAAA", f"<p>{fechas_dd} de {len(df)} fechas</p>")

#---------------------------------------------------------------
#TRES
#---------------------------------------------------------------

def convertir_numericos(df):
    """PASO 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    # TODO 3: convertir asistencia_pct, horas_trabajo_semana y distancia_km a número.
    return df

#---------------------------------------------------------------
#CUATRO
#---------------------------------------------------------------

def unificar_categorias(df):
    """PASO 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    # TODO 4: unificar las escrituras de programa, jornada, genero y ciudad_procedencia.
    return df


#---------------------------------------------------------------
#CINCO
#---------------------------------------------------------------

def convertir_fechas(df):
    """PASO 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    # TODO 5: convertir fecha_matricula a fecha con los dos formatos.
    return df

#---------------------------------------------------------------
#SEIS
#---------------------------------------------------------------

def eliminar_duplicados(df):
    """PASO 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    # TODO 6: eliminar duplicados, registrar la decisión y devolver el dataframe.
    return df

#---------------------------------------------------------------
#SIETE
#---------------------------------------------------------------

def tratar_faltantes(df):
    """PASO 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # TODO 7: tratar los nulos de promedio_acumulado, ciudad_procedencia y tipo_colegio.
    return df


#---------------------------------------------------------------
#OCHO
#---------------------------------------------------------------

def tratar_imposibles(df):
    """PASO 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # TODO 8: tratar edad, promedio_acumulado y horas_trabajo_semana, con sus justificaciones.
    return df

#---------------------------------------------------------------
#NUEVE
#---------------------------------------------------------------

def crear_variables(df):
    """PASO 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    # TODO 9: crear las columnas desertor y cuartil_asistencia.
    return df


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    # TODO 10: dibujar, guardar en GRAFICOS / "mapa_faltantes.png" y mostrar.
    pass


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    # TODO 11: dibujar los cuatro boxplots, guardar en GRAFICOS / "distribuciones_antes_despues.png" y mostrar.
    pass


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    # TODO 12: dibujar la tasa por programa, guardar en GRAFICOS / "tasa_desercion_por_programa.png" y mostrar.
    pass


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    # TODO 13: dibujar la tasa por cuartil, guardar en GRAFICOS / "tasa_desercion_por_asistencia.png" y mostrar.
    pass

#---------------------------------------------------------------
#DIEZ
#---------------------------------------------------------------


def responder_preguntas(df):
    """PASO 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    # TODO 14: responder las cinco preguntas con groupby() y agg().
    pass

#---------------------------------------------------------------
#ONCE
#---------------------------------------------------------------

def guardar(df):
    """PASO 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)
    guardar_reporte()


if __name__ == "__main__":
    main()


#open Data/processed/reporte.html