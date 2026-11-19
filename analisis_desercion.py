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
    seccion("3. Convertir columnas a número")

    # --- asistencia_pct: quitar % y convertir '-' en nulo ---
    con_porcentaje = df["asistencia_pct"].str.contains("%", regex=False).sum()
    guiones_asist = (df["asistencia_pct"] == "-").sum()

    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"], errors="coerce")

    registrar("convertir_numericos", "asistencia_pct", "quitar símbolo %", con_porcentaje,
              "El % es solo formato peroo el número es el mismo y se necesita como número para calcular.")
    registrar("convertir_numericos", "asistencia_pct", "guion '-' a nulo", guiones_asist,
              "El guion significa 'sin dato' --> nulo real para que pandas lo reconozca.")

    # --- horas_trabajo_semana: convertir '-' en nulo ---
    guiones_horas = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")

    registrar("convertir_numericos", "horas_trabajo_semana", "guion '-' a nulo", guiones_horas,
              "El guion significa 'sin dato' --> nulo real para que pandas lo reconozca.")

    # --- distancia_km: 999 es un faltante disfrazado ---
    dist_999 = (df["distancia_km"] == 999).sum()
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)

    registrar("convertir_numericos", "distancia_km", "999 a nulo", dist_999,
              "999 es un código de 'sin dato', no una distancia real; dejarlo inflaría el promedio.")

    # --- Reporte: cómo quedaron las tres columnas ---
    columnas = ["asistencia_pct", "horas_trabajo_semana", "distancia_km"]
    resumen = pd.DataFrame({
        "tipo": df[columnas].dtypes.astype(str),
        "nulos": df[columnas].isnull().sum(),
    })
    bloque("Tipo y nulos después de convertir", resumen.to_html())
    bloque("Estadísticas después de convertir", df[columnas].describe().round(2).to_html())

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
    seccion("4. Unificar categorías")

    # Variantes que encontramos con value_counts(), ya en minúsculas, y su forma correcta
    variantes = {
        "programa": {"ingenieria de sistemas": "Ingeniería de Sistemas",
                     "psicologia": "Psicología"},
        "jornada": {},
        "genero": {"m": "Masculino", "f": "Femenino"},
        "ciudad_procedencia": {"bogota": "Bogotá", "medellin": "Medellín"},
    }

    for col, valores_validos in VALIDOS.items():
        antes = df[col].copy()

        # 1. Normalizar: quitar espacios y pasar a minúsculas
        df[col] = df[col].str.strip().str.lower()

        # 2. Diccionario: cada valor válido en minúscula -> su forma correcta, más las variantes
        diccionario = {v.lower(): v for v in valores_validos}
        diccionario.update(variantes[col])
        df[col] = df[col].replace(diccionario)

        # 3. Contar cuántas celdas cambiaron (sin contar los nulos)
        cambiaron = (antes != df[col]) & antes.notna()
        registrar("unificar_categorias", col, "unificar escritura", cambiaron.sum(),
                  "Eran el mismo valor escrito distinto (mayúsculas, tildes o abreviaturas); "
                  "sin unificar, un mismo grupo se contaría como varios.")

        # 4. Reporte: cómo quedó la columna
        bloque(f"{col} después de unificar ({cambiaron.sum()} celdas corregidas)",
               df[col].value_counts(dropna=False).to_frame().to_html())

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
    seccion("5. Convertir fechas")

    texto = df["fecha_matricula"]

    # 1. Intentar cada formato por separado (lo que no coincide queda como NaT)
    fechas_iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")  # 2023-05-04
    fechas_dmy = pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")  # 13/07/2023

    # 2. Contar cuántas venían en DD/MM/AAAA (no eran ISO pero sí DD/MM)
    en_dmy = (fechas_iso.isna() & fechas_dmy.notna()).sum()

    # 3. Juntar: donde la ISO quedó vacía, usar la DD/MM
    df["fecha_matricula"] = fechas_iso.fillna(fechas_dmy)

    # 4. Verificar que no quedó ninguna sin convertir
    sin_convertir = df["fecha_matricula"].isna().sum()

    registrar("convertir_fechas", "fecha_matricula", "convertir DD/MM/AAAA a fecha", en_dmy,
              "La misma columna tenía dos formatos; con formato explícito no se confunden "
              "día y mes, y la columna queda como fecha para poder calcular con ella.")

    bloque("Resultado de la conversión",
           f"<p>Fechas en formato AAAA-MM-DD: {fechas_iso.notna().sum()}<br>"
           f"Fechas en formato DD/MM/AAAA: {en_dmy}<br>"
           f"Fechas sin convertir: {sin_convertir}<br>"
           f"Tipo final de la columna: {df['fecha_matricula'].dtype}<br>"
           f"Rango: {df['fecha_matricula'].min().date()} a {df['fecha_matricula'].max().date()}</p>")

    ejemplo = pd.DataFrame({"texto original": texto, "fecha convertida": df["fecha_matricula"]}).head(8)
    bloque("Ejemplo: antes y después", ejemplo.to_html())

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
    seccion("6. Eliminar duplicados")

    filas_antes = len(df)
    duplicados = df.duplicated().sum()
    ids_repetidos = df["id_estudiante"].duplicated().sum()

    df = df.drop_duplicates().reset_index(drop=True)

    registrar("eliminar_duplicados", "todas", "eliminar filas duplicadas", duplicados,
              "Son filas idénticas en todas las columnas, incluido id_estudiante: es el mismo "
              "estudiante registrado dos veces. Dejarlas lo contaría doble en las tasas.")

    bloque("Resultado",
           f"<p>Filas antes: {filas_antes}<br>"
           f"Filas duplicadas eliminadas: {duplicados}<br>"
           f"Filas después: {len(df)}<br>"
           f"id_estudiante repetidos antes de eliminar: {ids_repetidos}<br>"
           f"id_estudiante repetidos después de eliminar: {df['id_estudiante'].duplicated().sum()}</p>")

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
    seccion("7. Tratar faltantes")

    columnas = ["promedio_acumulado", "ciudad_procedencia", "tipo_colegio", "motivo_retiro"]
    nulos_antes = df[columnas].isnull().sum()

    # --- promedio_acumulado: eliminar las filas sin nota ---
    sin_promedio = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("tratar_faltantes", "promedio_acumulado", "eliminar filas", sin_promedio,
              "Una nota no se puede inventar. Imputar el promedio pondría a todos en la media "
              "y escondería justo a los estudiantes con bajo rendimiento, que importan para la deserción.")

    # --- ciudad_procedencia y tipo_colegio: marcar como 'Sin dato' ---
    for col in ["ciudad_procedencia", "tipo_colegio"]:
        faltan = df[col].isnull().sum()
        df[col] = df[col].fillna("Sin dato")
        registrar("tratar_faltantes", col, "reemplazar nulo por 'Sin dato'", faltan,
                  "Es un dato descriptivo: eliminar la fila perdería sus demás datos, e inventar "
                  "una ciudad o colegio sería falso. 'Sin dato' conserva la fila y es honesto.")

    # --- motivo_retiro: los nulos son esperados, no se tocan ---
    sin_motivo = df["motivo_retiro"].isnull().sum()
    no_desertores = (df["estado"] != "desertor").sum()
    registrar("tratar_faltantes", "motivo_retiro", "dejar como nulo", 0,
              f"No es un error: la columna solo aplica a desertores. Los {sin_motivo} nulos "
              f"coinciden con los {no_desertores} estudiantes activos o graduados.")

    # --- Reporte: nulos antes y después ---
    resumen = pd.DataFrame({
        "nulos antes": nulos_antes,
        "nulos después": df[columnas].isnull().sum(),
    })
    bloque("Nulos antes y después", resumen.to_html())
    bloque("Comprobación de motivo_retiro",
           f"<p>Nulos en motivo_retiro: {sin_motivo}<br>"
           f"Estudiantes que no son desertores: {no_desertores}</p>")
    bloque("Filas que quedan", f"<p>{len(df)} estudiantes</p>")

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
    seccion("Tabla de decisiones")
    bloque("Decisiones de limpieza", pd.DataFrame(DECISIONES).to_html(index=False))
    guardar(df)
    guardar_reporte()


if __name__ == "__main__":
    main()


#open Data/processed/reporte.html