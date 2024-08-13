import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats


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
    # Título centrado
    st.markdown("<h1 style='text-align: center;'>Análisis del Sector de Telecomunicaciones en Argentina</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>por Adrián Lazzarini</h1>", unsafe_allow_html=True)

    # Imagen centrada y redimensionada
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
    st.header("Observaciones:")

    st.write("""
    - **Crecimiento Nacional**: La velocidad media de internet aumentó de 3.62 Mbps (2014) a 139.15 Mbps (2024), un crecimiento del 3,744%.

    - **Disparidades Regionales**:
      - CABA lidera con 229.94 Mbps (2024).
      - Región Pampeana y Centro muestran buen desarrollo.
      - NOA y NEA presentan retraso considerable.  

    - **Evolución Temporal**: Aceleración notable desde 2017, con aumento de la brecha entre regiones.

    - **Desafíos**: 
      1. Abordar la **brecha digital** entre regiones.
      2. Implementar políticas para equidad en acceso y calidad.
      3. Aprovechar oportunidades de crecimiento en regiones menos desarrolladas.

    - **Conclusión**: Crecimiento impresionante pero con desigualdades regionales significativas. Necesidad de estrategias para un desarrollo digital equitativo.
    """)

    # Sección 2: Distribución de accesos por tecnologías
    st.header('Distribución de Accesos por Tecnologías')

    # Preparar los datos
    df_accesos = dfs['Accesos Por Tecnología'].copy()
    df_accesos['Fecha'] = pd.to_datetime(df_accesos['Año'].astype(str) + '-' + (df_accesos['Trimestre']*3-2).astype(str).str.zfill(2) + '-01')
    tecnologias = ['ADSL', 'Cablemodem', 'Fibra óptica', 'Wireless', 'Otros']

    # Calcular el total nacional
    df_total_nacional = df_accesos.groupby('Fecha')[tecnologias].sum().reset_index()
    df_total_nacional['Provincia'] = 'Total Nacional'

    # Combinar datos provinciales y nacionales
    df_accesos = pd.concat([df_accesos, df_total_nacional])

    # Crear selectbox para elegir provincia
    provincias = ['Total Nacional'] + sorted(df_accesos['Provincia'].unique().tolist())
    provincia_seleccionada = st.selectbox('Seleccione una provincia o el total nacional:', provincias)

    # Filtrar datos para la provincia seleccionada
    df_filtrado = df_accesos[df_accesos['Provincia'] == provincia_seleccionada]

    # Crear gráfico interactivo con Plotly
    fig = go.Figure()

    for tech in tecnologias:
        fig.add_trace(go.Scatter(
            x=df_filtrado['Fecha'],
            y=df_filtrado[tech],
            mode='lines',
            name=tech
        ))

    fig.update_layout(
        title=f'Evolución de Accesos por Tecnología - {provincia_seleccionada}',
        xaxis_title='Fecha',
        yaxis_title='Número de Accesos',
        legend_title='Tecnología',
        height=600,
        width=1000
    )

    st.plotly_chart(fig)

    # Mostrar estadísticas adicionales
    ultimo_periodo = df_filtrado[df_filtrado['Fecha'] == df_filtrado['Fecha'].max()]
    st.write(f"Estadísticas para {provincia_seleccionada} en el último período ({ultimo_periodo['Fecha'].iloc[0].strftime('%Y-%m')})")
    for tech in tecnologias:
        st.write(f"{tech}: {ultimo_periodo[tech].iloc[0]:,.0f} accesos")
    st.write(f"Total: {ultimo_periodo['Total'].iloc[0]:,.0f} accesos")

    # Gráfico de área apilada
    df_prop = df_total_nacional[tecnologias].div(df_total_nacional[tecnologias].sum(axis=1), axis=0)
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

    # Sección 4: Informe resumido de la evolución de tecnologías de internet
    st.header('Evolución de Tecnologías de Internet en Argentina (2014-2024)')

    st.subheader('Tendencias Principales')

    st.write("""
    1. **Distribución de Tecnologías:**
    - 2014: Predominio de ADSL y Cablemodem.
    - 2024: Liderazgo de Cablemodem y Fibra Óptica, con ADSL en declive.

    2. **Disparidad en Adopción de Fibra Óptica:**
    - Concentración en provincias más pobladas (Buenos Aires, Córdoba, Santa Fe).
    - Menor penetración en provincias menos pobladas o remotas.
    """)

    st.subheader('Implicaciones')

    st.write("""
    1. **Mejora en Calidad de Servicio:** La transición hacia Fibra Óptica y Cablemodem implica un aumento general en la velocidad y calidad de conexiones.
    2. **Desafíos de Equidad:** Necesidad de políticas focalizadas para reducir la brecha digital entre regiones.
    3. **Oportunidades de Mercado:** Potencial de crecimiento en áreas con baja penetración de tecnologías avanzadas.
    4. **Obsolescencia Tecnológica:** Necesidad de estrategias para la transición de usuarios de ADSL a tecnologías más modernas.
    """)
    # Sección 5: Distribución de Velocidades entre Provincias
    st.header("Distribución de Velocidades entre Provincias")

    # Cargar y preparar los datos
    df_prov = dfs['Accesos por velocidad']
    velocidades_prov = [col for col in df_prov.columns if 'bps' in col.lower() or 'mbps' in col.lower()]

    # Seleccionar el último período disponible
    ultimo_periodo = df_prov[df_prov['Año'] == df_prov['Año'].max()]
    ultimo_periodo = ultimo_periodo[ultimo_periodo['Trimestre'] == ultimo_periodo['Trimestre'].max()]

    # Calcular el porcentaje de cada velocidad por provincia
    for velocidad in velocidades_prov:
        ultimo_periodo[f'{velocidad} %'] = ultimo_periodo[velocidad] / ultimo_periodo['Total'] * 100

    # Top 5 provincias con mayor número de accesos
    top_5_provincias = ultimo_periodo.nlargest(5, 'Total')

    # Selector para comparar provincias
    provincias_seleccionadas = st.multiselect(
        "Selecciona provincias para comparar:",
        options=ultimo_periodo['Provincia'].unique(),
        default=top_5_provincias['Provincia'].tolist()[:2]
    )

    if provincias_seleccionadas:
        fig_comparacion = go.Figure()
        
        for provincia in provincias_seleccionadas:
            datos_provincia = ultimo_periodo[ultimo_periodo['Provincia'] == provincia]
            fig_comparacion.add_trace(go.Bar(
                x=velocidades_prov,
                y=datos_provincia[velocidades_prov].iloc[0],
                name=provincia
            ))
        
        fig_comparacion.update_layout(
            title=f'Comparación de Distribución de Velocidades entre Provincias Seleccionadas',
            xaxis_title='Velocidad',
            yaxis_title='Número de Accesos',
            barmode='group'
        )
        
        st.plotly_chart(fig_comparacion)
    else:
        st.write("Por favor, selecciona al menos una provincia para comparar.")

    # Sección 6: Ingresos vs Penetración y Velocidad
    st.header("Análisis de Ingresos vs Penetración y Velocidad")

    # Preparar datos
    df_ingresos = dfs['Ingresos ']
    df_ingresos['Fecha'] = pd.to_datetime(df_ingresos['Año'].astype(str) + 'Q' + df_ingresos['Trimestre'].astype(str))

    df_penetracion = dfs['Penetracion-hogares']
    df_penetracion['Fecha'] = pd.to_datetime(df_penetracion['Año'].astype(str) + 'Q' + df_penetracion['Trimestre'].astype(str))
    df_penetracion = df_penetracion.groupby('Fecha')['Accesos por cada 100 hogares'].mean().reset_index()

    df_velocidad = dfs['Velocidad % por prov']
    df_velocidad['Fecha'] = pd.to_datetime(df_velocidad['Año'].astype(str) + 'Q' + df_velocidad['Trimestre'].astype(str))
    df_velocidad = df_velocidad.groupby('Fecha')['Mbps (Media de bajada)'].mean().reset_index()

    df_combinado = pd.merge(df_ingresos, df_penetracion, on='Fecha')
    df_combinado = pd.merge(df_combinado, df_velocidad, on='Fecha')

    # Calcular correlaciones
    corr_ingresos_penetracion = df_combinado['Ingresos (miles de pesos)'].corr(df_combinado['Accesos por cada 100 hogares'])
    corr_ingresos_velocidad = df_combinado['Ingresos (miles de pesos)'].corr(df_combinado['Mbps (Media de bajada)'])

    st.write(f"Correlación entre Ingresos y Penetración: {corr_ingresos_penetracion:.2f}")
    st.write(f"Correlación entre Ingresos y Velocidad: {corr_ingresos_velocidad:.2f}")

    # Gráficos de dispersión
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_combinado['Accesos por cada 100 hogares'],
        y=df_combinado['Ingresos (miles de pesos)'],
        mode='markers',
        name='Ingresos vs Penetración'
    ))

    fig.add_trace(go.Scatter(
        x=df_combinado['Mbps (Media de bajada)'],
        y=df_combinado['Ingresos (miles de pesos)'],
        mode='markers',
        name='Ingresos vs Velocidad'
    ))

    fig.update_layout(
        title='Ingresos vs Penetración y Velocidad',
        xaxis_title='Penetración (Accesos por 100 hogares) / Velocidad (Mbps)',
        yaxis_title='Ingresos (miles de pesos)',
        height=600,
        width=800
    )

    st.plotly_chart(fig)

    # Análisis de regresión
    slope_penetracion, intercept_penetracion, r_value_penetracion, p_value_penetracion, std_err_penetracion = stats.linregress(df_combinado['Accesos por cada 100 hogares'], df_combinado['Ingresos (miles de pesos)'])

    slope_velocidad, intercept_velocidad, r_value_velocidad, p_value_velocidad, std_err_velocidad = stats.linregress(df_combinado['Mbps (Media de bajada)'], df_combinado['Ingresos (miles de pesos)'])

    st.subheader("Resultados de la Regresión Lineal")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Ingresos vs Penetración:")
        st.write(f"Pendiente: {slope_penetracion:.2f}")
        st.write(f"Intersección: {intercept_penetracion:.2f}")
        st.write(f"R-cuadrado: {r_value_penetracion**2:.2f}")
        st.write(f"Valor p: {p_value_penetracion:.4f}")

    with col2:
        st.write("Ingresos vs Velocidad:")
        st.write(f"Pendiente: {slope_velocidad:.2f}")
        st.write(f"Intersección: {intercept_velocidad:.2f}")
        st.write(f"R-cuadrado: {r_value_velocidad**2:.2f}")
        st.write(f"Valor p: {p_value_velocidad:.4f}")

    st.write("""
    ### Interpretación de Resultados

    1. **Correlaciones**: 
    - La correlación entre Ingresos y Penetración es positiva y moderada.
    - La correlación entre Ingresos y Velocidad es más fuerte, indicando una relación más estrecha.

    2. **Regresión Lineal**:
    - Tanto la Penetración como la Velocidad muestran una relación estadísticamente significativa con los Ingresos (valores p < 0.05).
    - La Velocidad explica una mayor proporción de la variabilidad en los Ingresos (R-cuadrado más alto) en comparación con la Penetración.

    3. **Implicaciones**:
    - Mejorar la velocidad del servicio podría tener un impacto más significativo en los ingresos que aumentar la penetración.
    - Sin embargo, ambos factores son importantes y deben considerarse en las estrategias de crecimiento.

    4. **Consideraciones adicionales**:
    - Pueden existir otros factores no considerados en este análisis que influyan en los ingresos.
    - La relación puede no ser estrictamente lineal, y podrían existir efectos de interacción entre la penetración y la velocidad.
    """)
   
    # Sección 6: Provincias por Velocidad y Penetración
    st.header("Top 5 Provincias por Velocidad y Penetración")

    # Obtener el último año y trimestre disponible
    ultimo_anio = max(dfs['Velocidad % por prov']['Año'].max(), dfs['Penetracion-hogares']['Año'].max())
    ultimo_trimestre = max(
        dfs['Velocidad % por prov'][dfs['Velocidad % por prov']['Año'] == ultimo_anio]['Trimestre'].max(),
        dfs['Penetracion-hogares'][dfs['Penetracion-hogares']['Año'] == ultimo_anio]['Trimestre'].max()
    )

    # Filtrar los datos más recientes
    velocidad_reciente = dfs['Velocidad % por prov'][
        (dfs['Velocidad % por prov']['Año'] == ultimo_anio) & 
        (dfs['Velocidad % por prov']['Trimestre'] == ultimo_trimestre)
    ].sort_values('Mbps (Media de bajada)', ascending=False).head()

    penetracion_reciente = dfs['Penetracion-hogares'][
        (dfs['Penetracion-hogares']['Año'] == ultimo_anio) & 
        (dfs['Penetracion-hogares']['Trimestre'] == ultimo_trimestre)
    ].sort_values('Accesos por cada 100 hogares', ascending=False).head()

    # Crear gráfico interactivo
    fig = go.Figure()

    # Añadir barras para velocidad
    fig.add_trace(go.Bar(
        x=velocidad_reciente['Provincia'],
        y=velocidad_reciente['Mbps (Media de bajada)'],
        name='Velocidad (Mbps)',
        marker_color='blue'
    ))

    # Añadir barras para penetración
    fig.add_trace(go.Bar(
        x=penetracion_reciente['Provincia'],
        y=penetracion_reciente['Accesos por cada 100 hogares'],
        name='Penetración (Accesos por 100 hogares)',
        marker_color='green',
        visible='legendonly'
    ))

    # Actualizar el diseño
    fig.update_layout(
        title=f'Top 5 Provincias por Velocidad y Penetración (Año {ultimo_anio}, Trimestre {ultimo_trimestre})',
        xaxis_title='Provincia',
        yaxis_title='Valor',
        barmode='group',
        height=500,
        width=800
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Mostrar tabla con datos
    st.subheader("Datos detallados")
    col1, col2 = st.columns(2)

    with col1:
        st.write("Top 5 por Velocidad")
        st.dataframe(velocidad_reciente[['Provincia', 'Mbps (Media de bajada)']])

    with col2:
        st.write("Top 5 por Penetración")
        st.dataframe(penetracion_reciente[['Provincia', 'Accesos por cada 100 hogares']])

    # Breve conclusión
    st.subheader("Observaciones:")
    st.write("""
    El análisis del top 5 de provincias por velocidad y penetración de internet revela interesantes patrones:

    1. **Liderazgo de Capital Federal**: Encabeza tanto en velocidad como en penetración, evidenciando una infraestructura digital avanzada.
    2. **Diversidad geográfica**: Provincias como San Luis y Tierra del Fuego muestran un desempeño notable, sugiriendo que el desarrollo digital no se limita a las áreas más pobladas.
    3. **Relación velocidad-penetración**: Aunque hay cierta correlación, no todas las provincias con alta velocidad tienen necesariamente alta penetración, y viceversa.
    4. **Desafío de equidad**: Las diferencias entre las provincias top y el resto del país indican la necesidad de políticas para reducir la brecha digital.

    Estos resultados subrayan la importancia de estrategias diferenciadas por provincia para mejorar tanto la velocidad como la penetración de internet, considerando las características únicas de cada región.
    """)


elif page == "KPIs":
    st.title("Indicadores Clave de Desempeño (KPIs)")
    st.header("KPI 1: Aumento proyectado en acceso a Internet")
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

    # KPI 2: Incremento en la Adopción de Fibra Óptica
    st.header("KPI 2: Incremento en la Adopción de Fibra Óptica")

    df_fibra = dfs['Accesos Por Tecnología'].copy()

    # Manejar valores nulos antes de crear la columna Fecha
    df_fibra['Año'] = df_fibra['Año'].fillna(0).astype(int)
    df_fibra['Trimestre'] = df_fibra['Trimestre'].fillna(0).astype(int)

    # Crear la columna Fecha solo para filas con Año y Trimestre válidos
    df_fibra['Fecha'] = pd.to_datetime(
        df_fibra[df_fibra['Año'] != 0].apply(
            lambda row: f"{row['Año']}-{row['Trimestre']*3-2:02d}-01", 
            axis=1
        ),
        format='%Y-%m-%d',
        errors='coerce'
    )

    # Eliminar filas donde no se pudo crear una fecha válida
    df_fibra = df_fibra.dropna(subset=['Fecha'])

    df_fibra = df_fibra.sort_values(['Fecha', 'Provincia'])

    def calcular_incremento_fibra(grupo):
        grupo['Incremento_FO'] = grupo['Fibra óptica'].pct_change() * 100
        return grupo

    df_fibra = df_fibra.groupby('Provincia').apply(calcular_incremento_fibra).reset_index(drop=True)
    ultimo_periodo_fibra = df_fibra[df_fibra['Fecha'] == df_fibra['Fecha'].max()]

    # Preparar datos para el gráfico
    df_grafico = ultimo_periodo_fibra.copy()
    df_grafico['Objetivo'] = 5  # 5% de incremento como objetivo
    df_grafico['Exceso'] = df_grafico['Incremento_FO'].apply(lambda x: max(x - 5, 0))
    df_grafico['Deficit'] = df_grafico['Incremento_FO'].apply(lambda x: min(x - 5, 0))
    df_grafico = df_grafico.sort_values('Incremento_FO', ascending=True)

    # Crear gráfico
    fig = go.Figure()

    # Añadir barras para el déficit (si existe)
    fig.add_trace(go.Bar(
        y=df_grafico['Provincia'],
        x=df_grafico['Deficit'],
        name='Por debajo del objetivo',
        orientation='h',
        marker_color='red',
        base=0
    ))

    # Añadir barras para el objetivo
    fig.add_trace(go.Bar(
        y=df_grafico['Provincia'],
        x=df_grafico['Objetivo'],
        name='Objetivo (5%)',
        orientation='h',
        marker_color='yellow',
        base=0
    ))

    # Añadir barras para el exceso (si existe)
    fig.add_trace(go.Bar(
        y=df_grafico['Provincia'],
        x=df_grafico['Exceso'],
        name='Por encima del objetivo',
        orientation='h',
        marker_color='green',
        base=5  # Comienza donde termina el objetivo
    ))

    # Configurar el diseño
    fig.update_layout(
        title='Incremento en Adopción de Fibra Óptica por Provincia (Último Trimestre)',
        xaxis_title='Incremento (%)',
        yaxis_title='Provincia',
        barmode='relative',
        height=800,
        width=1000
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Estadísticas adicionales
    provincias_cumplen = df_grafico[df_grafico['Incremento_FO'] >= 5]['Provincia'].tolist()
    provincias_no_cumplen = df_grafico[df_grafico['Incremento_FO'] < 5]['Provincia'].tolist()
    promedio_incremento = df_grafico['Incremento_FO'].mean()
    provincia_mayor_incremento = df_grafico.loc[df_grafico['Incremento_FO'].idxmax(), 'Provincia']
    mayor_incremento = df_grafico['Incremento_FO'].max()
    provincia_menor_incremento = df_grafico.loc[df_grafico['Incremento_FO'].idxmin(), 'Provincia']
    menor_incremento = df_grafico['Incremento_FO'].min()
    # Título principal
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>Estadísticas de Incremento en la Adopción de Fibra Óptica</h3>", unsafe_allow_html=True)

    # Provincias que cumplen el objetivo
    st.markdown("<h6>Provincias que cumplen el objetivo (>= 5% de incremento):</h6>", unsafe_allow_html=True)
    st.write(f"<ul style='margin-left: 20px;'><li>{'</li><li>'.join(provincias_cumplen)}</li></ul>", unsafe_allow_html=True)

    # Provincias que no cumplen el objetivo
    st.markdown("<h6>Provincias que no cumplen el objetivo (< 5% de incremento):</h6>", unsafe_allow_html=True)
    st.write(f"<ul style='margin-left: 20px;'><li>{'</li><li>'.join(provincias_no_cumplen)}</li></ul>", unsafe_allow_html=True)

    # Promedio de incremento
    st.markdown(f"<h6>Promedio de incremento en adopción de Fibra Óptica: <span>{promedio_incremento:.2f}%</span></h6>", unsafe_allow_html=True)

    # Provincia con mayor incremento
    st.markdown(f"<h6>Provincia con mayor incremento: <span>{provincia_mayor_incremento} ({mayor_incremento:.2f}%)</span></h6>", unsafe_allow_html=True)

    # Provincia con menor incremento
    st.markdown(f"<h6>Provincia con menor incremento: <span>{provincia_menor_incremento} ({menor_incremento:.2f}%)</span></h6>", unsafe_allow_html=True)
    # KPI 3: Reducción de la Brecha Digital entre Provincias
    st.header("KPI 3: Reducción de la Brecha Digital entre Provincias")

    df_velocidad = dfs['Velocidad % por prov'].copy()
    df_velocidad['Fecha'] = pd.to_datetime(df_velocidad['Año'].astype(str) + '-' + (df_velocidad['Trimestre']*3-2).astype(str).str.zfill(2) + '-01')
    df_velocidad = df_velocidad.sort_values(['Fecha', 'Provincia'])

    def calcular_brecha_digital(grupo):
        velocidad_max = grupo['Mbps (Media de bajada)'].max()
        velocidad_min = grupo['Mbps (Media de bajada)'].min()
        return velocidad_max - velocidad_min

    df_brecha = df_velocidad.groupby('Fecha').apply(calcular_brecha_digital).reset_index()
    df_brecha.columns = ['Fecha', 'Brecha_Digital']

    # Calcular el objetivo (reducción del 10% cada trimestre)
    df_brecha['Objetivo'] = df_brecha['Brecha_Digital'].iloc[0] * (0.9 ** ((df_brecha.index) / 4))

    # Crear el gráfico
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Añadir la línea de brecha digital real
    fig.add_trace(
        go.Scatter(x=df_brecha['Fecha'], y=df_brecha['Brecha_Digital'], name="Brecha Digital Real"),
        secondary_y=False,
    )

    # Añadir la línea de objetivo
    fig.add_trace(
        go.Scatter(x=df_brecha['Fecha'], y=df_brecha['Objetivo'], name="Objetivo (Reducción 10% trimestral)", line=dict(dash='dash')),
        secondary_y=False,
    )

    # Resaltar el último período
    ultimo_periodo = df_brecha.iloc[-1]
    fig.add_trace(
        go.Scatter(x=[ultimo_periodo['Fecha']], y=[ultimo_periodo['Brecha_Digital']], 
                mode='markers', marker=dict(size=10, color='red'), name="Último Período"),
        secondary_y=False,
    )

    # Configurar el diseño
    fig.update_layout(
        title_text="Evolución de la Brecha Digital entre Provincias",
        xaxis_title="Fecha",
        yaxis_title="Brecha Digital (Mbps)",
        height=600,
        width=1000
    )

    # Mostrar el gráfico
    st.plotly_chart(fig)

    # Calcular y mostrar estadísticas
    ultimo_periodo = df_brecha.iloc[-1]
    penultimo_periodo = df_brecha.iloc[-2]
    reduccion_brecha = (penultimo_periodo['Brecha_Digital'] - ultimo_periodo['Brecha_Digital']) / penultimo_periodo['Brecha_Digital'] * 100
    objetivo_cumplido = reduccion_brecha >= 10

    st.write(f"Brecha digital en el último período: {ultimo_periodo['Brecha_Digital']:.2f} Mbps")
    st.write(f"Reducción de la brecha respecto al período anterior: {reduccion_brecha:.2f}%")
    st.write(f"Objetivo de reducción: 10% trimestral")
    st.write(f"¿Se cumplió el objetivo? {'Sí' if objetivo_cumplido else 'No'}")

    if objetivo_cumplido:
        st.write("La brecha digital se ha reducido más de lo esperado.")
    elif reduccion_brecha > 0:
        st.write("La brecha digital se ha reducido, pero no alcanzó el objetivo del 10%.")
    elif reduccion_brecha < 0:
        st.write("La brecha digital ha aumentado.")
    else:
        st.write("La brecha digital se ha mantenido constante.")
    
elif page == "Conclusiones":
    st.title("Conclusiones del Análisis")

    st.write("""
    **El servicio de Internet es un sector en crecimiento y en expansión constante, acompañado del surgimiento de nuevas tecnólogias asociadas (que potencian este auge) la convierten en una inversión con un ratio de riesgo/rentabilidad muy bueno.** 
             
    A pesar de esto es imprescindible abordar las inversiones futuras con una perspectiva más amplia para evitar la sobresaturación del mercado. Para ello destacamos los siguientes puntos:

    1. **Crecimiento Asimétrico:**
       - La velocidad de internet ha crecido un 2554.36% entre 2014 y 2024.
       - La penetración de internet en hogares aumentó un 99.04% en el mismo período.
       - Esto sugiere un enfoque en **mejorar la calidad del servicio más que en expandir la cobertura**.

    2. **Impacto Económico de la Velocidad:**
       - La velocidad de internet muestra una correlación más fuerte con los ingresos del sector (R-cuadrado: 0.83) 
         que la penetración (R-cuadrado: 0.58).
       - Invertir en infraestructura para aumentar la velocidad podría ser más rentable que simplemente expandir la cobertura.

    3. **Brecha Digital Geográfica:**
       - Existe una significativa disparidad en la adopción y calidad de internet entre las diferentes provincias.
       - Las áreas urbanas, especialmente la Capital Federal, tienden a tener mejor conectividad.

    4. **Evolución de las Tecnologías:**
       - Se observa una transición desde tecnologías más antiguas como ADSL hacia opciones más modernas como la fibra óptica.
       - Esta transición no es uniforme en todas las provincias, contribuyendo a la brecha digital.

    5. **Desafíos para la Universalización del Servicio:**
       - A pesar del crecimiento significativo, aún existen desafíos para lograr una cobertura universal de 
         internet de alta velocidad en Argentina.
       - Las diferencias geográficas y socioeconómicas siguen siendo factores importantes que influyen en el 
         acceso y la calidad del servicio.

    Estas conclusiones ofrecen una visión integral del estado y la evolución del sector de internet en Argentina, 
    destacando tanto los logros como los desafíos pendientes en términos de acceso, calidad y equidad del servicio.
    """)

    # correr streamlit en local:
    # streamlit run streamlit.py
