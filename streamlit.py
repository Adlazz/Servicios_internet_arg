import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Análisis del Sector de Telecomunicaciones en Argentina", layout="wide")

# Función para cargar los datos
@st.cache_resource
def load_data():
    with open('dfs_data.pkl', 'rb') as file:
        return pickle.load(file)

# Cargar los datos
dfs = load_data()

# Función para convertir fecha a formato trimestre-YYYY
def fecha_a_trimestre(fecha):
    return f"Q{fecha.quarter}-{fecha.year}"

# Barra lateral
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Inicio", "Análisis", "KPIs", "Conclusiones"])

if page == "Inicio":
    st.title("Análisis del Sector de Telecomunicaciones en Argentina")
    # Inserta la imagen de portada
    st.image("images/portada.jpeg")
    
    st.write("""
    Bienvenido al dashboard de análisis del sector de telecomunicaciones en Argentina.
    
    ## Contexto y Objetivos
    Este proyecto tiene como objetivo examinar la evolución del sector de telecomunicaciones en Argentina, 
    centrándose específicamente en la penetración de internet y la velocidad de conexión en las diferentes 
    provincias del país desde 2014 hasta 2024.

    ## Desarrollo del Trabajo
    El análisis se llevó a cabo siguiendo estos pasos:
    1. Recolección de datos de la página oficial de ENACOM.
    2. Limpieza y preparación de los datos.
    3. Análisis exploratorio de datos (EDA) para identificar tendencias y patrones.
    4. Creación de visualizaciones interactivas para presentar los hallazgos.
    5. Formulación de conclusiones basadas en el análisis realizado.

    ## Fuente de Datos
    Los datos utilizados en este análisis fueron obtenidos de la Entidad Nacional de Comunicaciones (ENACOM) 
    de Argentina. ENACOM proporciona datos abiertos sobre el sector de telecomunicaciones, incluyendo 
    estadísticas sobre acceso a internet, velocidades de conexión y distribución geográfica de los servicios.

    Puedes explorar más detalles en las secciones de Análisis y Conclusiones.
    """)

elif page == "Análisis":
    st.title("Análisis Detallado")

    # Sección 1: Comparación interactiva entre provincias (ahora principal)
    st.header('Comparación Interactiva de Provincias')

    # Radio button para seleccionar la métrica
    metrica = st.radio(
        "Seleccione la métrica a comparar:",
        ('Velocidad de Internet', 'Penetración en Hogares', 'Penetración en Población')
    )

    # Preparar datos para el slider
    if metrica == 'Velocidad de Internet':
        df_metrica = dfs['Velocidad % por prov']
        y_column = 'Mbps (Media de bajada)'
        y_label = 'Velocidad (Mbps)'
    elif metrica == 'Penetración en Hogares':
        df_metrica = dfs['Penetracion-hogares']
        y_column = 'Accesos por cada 100 hogares'
        y_label = 'Accesos por cada 100 hogares'
    else:  # Penetración en Población
        df_metrica = dfs['Penetración-poblacion']
        y_column = 'Accesos por cada 100 hab'
        y_label = 'Accesos por cada 100 habitantes'

    df_metrica['Fecha'] = pd.to_datetime(df_metrica['Año'].astype(str) + 'Q' + df_metrica['Trimestre'].astype(str))
    
    trimestres = sorted(df_metrica['Fecha'].unique())
    trimestres_str = [fecha_a_trimestre(fecha) for fecha in trimestres]

    # Crear slider para seleccionar rango de trimestres
    st.write("Selecciona el rango de trimestres:")
    rango_trimestres = st.select_slider(
        "",
        options=trimestres_str,
        value=(trimestres_str[0], trimestres_str[-1])
    )

    # Convertir los trimestres seleccionados de vuelta a fechas
    trimestre_inicio = trimestres[trimestres_str.index(rango_trimestres[0])]
    trimestre_fin = trimestres[trimestres_str.index(rango_trimestres[1])]

    # Filtrar datos por el rango de trimestres seleccionado
    df_metrica_filtrado = df_metrica[(df_metrica['Fecha'] >= trimestre_inicio) & (df_metrica['Fecha'] <= trimestre_fin)]

    provincias = list(df_metrica_filtrado['Provincia'].unique())
    provincias.append('Media Nacional')

    provincia1 = st.selectbox('Selecciona la primera provincia', provincias, index=0)
    provincia2 = st.selectbox('Selecciona la segunda provincia', provincias, index=1)

    df_metrica_nacional = df_metrica_filtrado.groupby('Fecha')[y_column].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))

    def plot_provincia(provincia, ax):
        if provincia == 'Media Nacional':
            df_metrica_nacional.plot(x='Fecha', y=y_column, ax=ax, label='Media Nacional')
        else:
            df_metrica_filtrado[df_metrica_filtrado['Provincia'] == provincia].plot(x='Fecha', y=y_column, ax=ax, label=provincia)

    plot_provincia(provincia1, ax)
    plot_provincia(provincia2, ax)

    mostrar_media_nacional = st.checkbox('Mostrar siempre la Media Nacional')
    if mostrar_media_nacional and 'Media Nacional' not in [provincia1, provincia2]:
        plot_provincia('Media Nacional', ax)

    plt.title(f'Comparación de {metrica} entre Provincias')
    plt.legend()
    ax.set_xlabel('Fecha')
    ax.set_ylabel(y_label)
    st.pyplot(fig)

     # Resumen del análisis
    st.header("Resumen: Análisis de Internet en Argentina (2014-2024)")

    st.write("""
    - **Crecimiento Nacional**: La velocidad media de internet aumentó de 3.62 Mbps (2014) a 139.15 Mbps (2024), un crecimiento del 3,744%.

    - **Disparidades Regionales**:
      - CABA lidera con 229.94 Mbps (2024).
      - Región Pampeana y Centro muestran buen desarrollo.
      - NOA y NEA presentan retraso considerable.

    - **Factores Clave**: Desarrollo económico, urbanización, políticas regionales e inversión en infraestructura.

    - **Evolución Temporal**: Aceleración notable desde 2017, con aumento de la brecha entre regiones.

    - **Desafíos**: 
      1. Abordar la brecha digital entre regiones.
      2. Implementar políticas para equidad en acceso y calidad.
      3. Aprovechar oportunidades de crecimiento en regiones menos desarrolladas.

    - **Conclusión**: Crecimiento impresionante pero con desigualdades regionales significativas. Necesidad de estrategias para un desarrollo digital equitativo.
    """)

# Sección 2: Distribución de accesos por tecnologías
    st.header('Distribución de Accesos por Tecnologías')

    # Preparar los datos
    df_totales = dfs['Totales Accesos Por Tecnología']
    df_totales['Fecha'] = pd.to_datetime(df_totales['Año'].astype(str) + '-' + (df_totales['Trimestre']*3).astype(str) + '-01')
    df_totales = df_totales.set_index('Fecha')
    tecnologias = ['ADSL', 'Cablemodem', 'Fibra óptica', 'Wireless', 'Otros']

    # Gráfico de evolución de accesos
    fig, ax = plt.subplots(figsize=(15, 8))
    for tech in tecnologias:
        ax.plot(df_totales.index, df_totales[tech], label=tech)

    ax.set_title('Evolución de Accesos por Tecnología a Nivel Nacional')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Número de Accesos')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Gráfico de área apilada
    df_prop = df_totales[tecnologias].div(df_totales[tecnologias].sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(15, 8))
    df_prop.plot.area(stacked=True, ax=ax)
    ax.set_title('Proporción de Accesos por Tecnología a Nivel Nacional')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Proporción de Accesos')
    ax.legend(title='Tecnología', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

    # Sección 3: Acceso de fibra óptica por provincia
    st.header('Acceso de Fibra Óptica por Provincia')

    # Preparar los datos
    df_prov = dfs['Accesos Por Tecnología']
    ultimo_anio = df_prov['Año'].max()
    ultimo_trimestre = df_prov[df_prov['Año'] == ultimo_anio]['Trimestre'].max()

    ultimo_periodo = df_prov[(df_prov['Año'] == ultimo_anio) & (df_prov['Trimestre'] == ultimo_trimestre)]
    ultimo_periodo = ultimo_periodo.sort_values('Fibra óptica', ascending=False)

    ultimo_periodo['Porcentaje_FO'] = ultimo_periodo['Fibra óptica'] / ultimo_periodo['Total'] * 100

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.barplot(data=ultimo_periodo, y='Provincia', x='Fibra óptica', ax=ax)

    # Añadir etiquetas de valor a las barras
    for i, v in enumerate(ultimo_periodo['Fibra óptica']):
        ax.text(v + 0.1, i, f'{v:,.0f}', va='center')

    # Añadir una segunda serie para mostrar el porcentaje
    ax2 = ax.twiny()
    sns.scatterplot(data=ultimo_periodo, y='Provincia', x='Porcentaje_FO', ax=ax2, color='red', s=100)

    # Configurar los ejes
    ax.set_xlabel('Número de Accesos de Fibra Óptica')
    ax2.set_xlabel('Porcentaje de Fibra Óptica (%)')

    plt.title(f'Accesos de Fibra Óptica por Provincia (Último período: {ultimo_anio} Q{ultimo_trimestre})')
    plt.tight_layout()
    st.pyplot(fig)

    # Mostrar estadísticas adicionales
    st.write(f"Período analizado: Año {ultimo_anio}, Trimestre {ultimo_trimestre}")
    st.write(f"Provincia con más accesos de Fibra Óptica: {ultimo_periodo.iloc[0]['Provincia']} ({ultimo_periodo.iloc[0]['Fibra óptica']:,.0f} accesos)")
    st.write(f"Provincia con menos accesos de Fibra Óptica: {ultimo_periodo.iloc[-1]['Provincia']} ({ultimo_periodo.iloc[-1]['Fibra óptica']:,.0f} accesos)")
    st.write(f"Promedio de accesos de Fibra Óptica por provincia: {ultimo_periodo['Fibra óptica'].mean():,.0f}")
    st.write(f"Mediana de accesos de Fibra Óptica por provincia: {ultimo_periodo['Fibra óptica'].median():,.0f}")

    # Sección 4: Informe resumido de la evolución de tecnologías de internet
    st.header('Evolución de Tecnologías de Internet en Argentina (2014-2024)')

    st.subheader('Tendencias Principales')

    st.write("""
    1. **Transición Tecnológica Nacional:**
    - Declive significativo de ADSL desde 2014.
    - Auge del Cablemodem como tecnología dominante desde 2018.
    - Crecimiento exponencial de la Fibra Óptica desde 2019, superando al ADSL en 2022.

    2. **Distribución de Tecnologías:**
    - 2014: Predominio de ADSL y Cablemodem.
    - 2024: Liderazgo de Cablemodem y Fibra Óptica, con ADSL en declive.

    3. **Variaciones Regionales:**
    - Buenos Aires y Córdoba: Patrones similares al nacional.
    - Mendoza y Tucumán: Adopción acelerada de Fibra Óptica, superando otras tecnologías.

    4. **Disparidad en Adopción de Fibra Óptica:**
    - Concentración en provincias más pobladas (Buenos Aires, Córdoba, Santa Fe).
    - Menor penetración en provincias menos pobladas o remotas.
    """)

    st.subheader('Observaciones Adicionales')

    st.write("""
    - **Wireless y Otras Tecnologías:** No varía mucho su penetración, es constante, indicando nichos específicos de mercado.
    - **Brecha Tecnológica:** Evidente entre provincias centrales y periféricas, reflejando desigualdades en infraestructura.
    - **Velocidad de Transición:** Varía significativamente entre provincias, sugiriendo diferentes niveles de inversión y políticas de desarrollo.
    """)

    st.subheader('Implicaciones')

    st.write("""
    1. **Mejora en Calidad de Servicio:** La transición hacia Fibra Óptica y Cablemodem implica un aumento general en la velocidad y calidad de conexiones.
    2. **Desafíos de Equidad:** Necesidad de políticas focalizadas para reducir la brecha digital entre regiones.
    3. **Oportunidades de Mercado:** Potencial de crecimiento en áreas con baja penetración de tecnologías avanzadas.
    4. **Obsolescencia Tecnológica:** Necesidad de estrategias para la transición de usuarios de ADSL a tecnologías más modernas.
    """)

    st.subheader('Conclusión')

    st.write("""
    La evolución tecnológica del internet en Argentina muestra un claro patrón de modernización, con un rápido crecimiento de tecnologías más avanzadas como la Fibra Óptica. Sin embargo, esta evolución no es uniforme en todo el país, evidenciando desafíos persistentes en términos de equidad digital y desarrollo de infraestructura. El futuro del sector dependerá de cómo se aborden estas disparidades y se fomente la adopción de tecnologías de alta velocidad en todas las regiones.
    """)

elif page == "KPIs":
    st.title("Indicadores Clave de Desempeño (KPIs)")

    # KPI principal: Aumento proyectado en acceso a Internet
    df = dfs['Penetracion-hogares'].copy()
    df['Fecha'] = pd.to_datetime(df['Año'].astype(str) + '-' + (df['Trimestre']*3-2).astype(str).str.zfill(2) + '-01')
    df = df.sort_values(['Fecha', 'Provincia'])

    def calcular_kpi(grupo):
        grupo['KPI'] = ((grupo['Accesos por cada 100 hogares'].shift(-1) - grupo['Accesos por cada 100 hogares']) / grupo['Accesos por cada 100 hogares']) * 100
        return grupo

    df = df.groupby('Provincia').apply(calcular_kpi).reset_index(drop=True)

    # Seleccionar el penúltimo período para mostrar la proyección al último período conocido
    penultimo_periodo = df[df['Fecha'] == df['Fecha'].unique()[-2]]

    # Asegurarse de que tenemos datos para mostrar
    if not penultimo_periodo.empty:
        # Calcular la diferencia con respecto al objetivo del 2%
        penultimo_periodo['Diferencia_Objetivo'] = penultimo_periodo['KPI'] - 2

        # Crear un gráfico de barras con dos series
        fig_kpi = go.Figure()

        # Añadir barras para el KPI
        fig_kpi.add_trace(go.Bar(
            x=penultimo_periodo['Provincia'],
            y=penultimo_periodo['KPI'],
            name='Aumento proyectado',
            marker_color='blue'
        ))

        # Añadir barras para la diferencia con el objetivo
        fig_kpi.add_trace(go.Bar(
            x=penultimo_periodo['Provincia'],
            y=penultimo_periodo['Diferencia_Objetivo'],
            name='Diferencia con objetivo (2%)',
            marker_color=['green' if x >= 0 else 'red' for x in penultimo_periodo['Diferencia_Objetivo']]
        ))

        # Configurar el diseño del gráfico
        fig_kpi.update_layout(
            title='KPI: Aumento proyectado en acceso a Internet por provincia (próximo trimestre)',
            xaxis_title='Provincia',
            yaxis_title='Porcentaje (%)',
            barmode='group',
            xaxis_tickangle=-45,
            width=1000,
            height=600
        )

        # Mostrar el gráfico
        st.plotly_chart(fig_kpi)

        st.write(f"Promedio de aumento proyectado: {penultimo_periodo['KPI'].mean():.2f}%")
        st.write(f"Provincia con mayor aumento proyectado: {penultimo_periodo.loc[penultimo_periodo['KPI'].idxmax(), 'Provincia']} ({penultimo_periodo['KPI'].max():.2f}%)")
        st.write(f"Provincia con menor aumento proyectado: {penultimo_periodo.loc[penultimo_periodo['KPI'].idxmin(), 'Provincia']} ({penultimo_periodo['KPI'].min():.2f}%)")

        # Mostrar los datos en una tabla
        st.write("Datos del KPI por provincia:")
        tabla_kpi = penultimo_periodo[['Provincia', 'KPI', 'Diferencia_Objetivo']].sort_values('KPI', ascending=False)
        tabla_kpi['Cumple Objetivo'] = tabla_kpi['KPI'] >= 2
        st.dataframe(tabla_kpi.style.format({
            'KPI': '{:.2f}%',
            'Diferencia_Objetivo': '{:.2f}%'
        }).applymap(lambda x: 'background-color: lightgreen' if x else 'background-color: lightsalmon', subset=['Cumple Objetivo']))

    else:
        st.write("No hay suficientes datos para calcular el KPI proyectado.")

    st.title("KPIs del Sector de Telecomunicaciones")

    
elif page == "Conclusiones":
    st.title("Conclusiones del Análisis")

    st.write("""
    Basándonos en el análisis realizado, hemos llegado a las siguientes conclusiones:

    1. **Crecimiento Asimétrico:**
       - La velocidad de internet ha crecido un 2554.36% entre 2014 y 2024.
       - La penetración de internet en hogares aumentó un 99.04% en el mismo período.
       - Esto sugiere un enfoque en mejorar la calidad del servicio más que en expandir la cobertura.

    2. **Impacto Económico de la Velocidad:**
       - La velocidad de internet muestra una correlación más fuerte con los ingresos del sector (R-cuadrado: 0.84) 
         que la penetración (R-cuadrado: 0.56).
       - Invertir en infraestructura para aumentar la velocidad podría ser más rentable que simplemente expandir la cobertura.

    3. **Brecha Digital Geográfica:**
       - Existe una significativa disparidad en la adopción y calidad de internet entre las diferentes provincias.
       - Las áreas urbanas, especialmente la Capital Federal, tienden a tener mejor conectividad.

    4. **Evolución de las Tecnologías:**
       - Se observa una transición desde tecnologías más antiguas como ADSL hacia opciones más modernas como la fibra óptica.
       - Esta transición no es uniforme en todas las provincias, contribuyendo a la brecha digital.

    5. **Punto de Inflexión en 2017:**
       - Se identificó un punto de inflexión alrededor de 2017, donde tanto la penetración como la velocidad 
         comenzaron a crecer más rápidamente.

    6. **Desafíos para la Universalización del Servicio:**
       - A pesar del crecimiento significativo, aún existen desafíos para lograr una cobertura universal de 
         internet de alta velocidad en Argentina.
       - Las diferencias geográficas y socioeconómicas siguen siendo factores importantes que influyen en el 
         acceso y la calidad del servicio.

    Estas conclusiones ofrecen una visión integral del estado y la evolución del sector de internet en Argentina, 
    destacando tanto los logros como los desafíos pendientes en términos de acceso, calidad y equidad del servicio.
    """)

    # correr streamlit en local:
    # streamlit run streamlit.py
