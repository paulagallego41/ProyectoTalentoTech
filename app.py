import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

################################################
###### CARGA, PREPROCESAMIENTO Y ANÁLISIS ######
################################################
def cargar_datos():
    df = pd.read_csv('./data/PresuntosSuicidios.csv', encoding='utf-8-sig')
    
    # Eliminar filas con valores nulos
    df_limpio = df.dropna()
    
    # Asegurar que las columnas categóricas sean string
    columnas_str = ['Departamento del hecho DANE', 'Ciclo Vital', 'Sexo de la victima', 
                    'Escenario del Hecho', 'Mecanismo Causal de la Lesion Fatal', 'Razon del Suicidio']
    
    for col in columnas_str:
        df_limpio[col] = df_limpio[col].astype(str)
    
    return df_limpio

df = cargar_datos()

### CÁLCULOS GENERALES
num_registros = len(df)
num_columnas = len(df.columns)
df_con_depto = df[df['Departamento del hecho DANE'] != 'Sin informacion']
num_departamentos = df_con_depto['Departamento del hecho DANE'].nunique()
num_anios = df['Año del hecho'].nunique()
anio_min = int(df['Año del hecho'].min())
anio_max = int(df['Año del hecho'].max())

### ANÁLISIS POR CICLO VITAL
df_ciclo = df['Ciclo Vital'].value_counts().reset_index()
df_ciclo.columns = ['Ciclo Vital', 'Cantidad']

### ANÁLISIS POR GÉNERO
df_genero = df['Sexo de la victima'].value_counts().reset_index()
df_genero.columns = ['Sexo', 'Cantidad']
df_genero['Porcentaje'] = (df_genero['Cantidad'] / df_genero['Cantidad'].sum() * 100).round(1)

### ANÁLISIS POR GÉNERO Y CICLO VITAL
df_genero_ciclo = df.groupby(['Ciclo Vital', 'Sexo de la victima']).size().reset_index(name='Cantidad')

### ANÁLISIS TEMPORAL
df_temporal = df.groupby('Año del hecho').size().reset_index(name='Cantidad')
df_temporal = df_temporal.sort_values('Año del hecho')

# Calcular indicadores para años específicos
años_indicadores = [2021, 2022, 2023, 2024]
indicadores = {}
deltas = {}

for año in años_indicadores:
    if año in df_temporal['Año del hecho'].values:
        indicadores[año] = int(df_temporal[df_temporal['Año del hecho'] == año]['Cantidad'].values[0])
    else:
        indicadores[año] = 0

# Calcular deltas
for i, año in enumerate(años_indicadores):
    if i > 0:
        año_anterior = años_indicadores[i-1]
        if indicadores[año_anterior] > 0:
            deltas[año] = ((indicadores[año] - indicadores[año_anterior]) / indicadores[año_anterior])
        else:
            deltas[año] = 0
    else:
        deltas[año] = 0

### ANÁLISIS POR DEPARTAMENTO Y AÑO
df_depto_anio = df.groupby(['Departamento del hecho DANE', 'Año del hecho']).size().reset_index(name='Cantidad')
# Eliminar valores NaN y ordenar
lista_deptos = df['Departamento del hecho DANE'].dropna().unique().tolist()
lista_deptos.sort()

### ANÁLISIS DE ESCENARIOS
df_escenario = df['Escenario del Hecho'].value_counts().head(10).reset_index()
df_escenario.columns = ['Escenario', 'Cantidad']

### ANÁLISIS DE MECANISMOS
df_mecanismo = df['Mecanismo Causal de la Lesion Fatal'].value_counts().head(10).reset_index()
df_mecanismo.columns = ['Mecanismo', 'Cantidad']

### ANÁLISIS DE RAZONES
df_razones = df['Razon del Suicidio'].value_counts().head(10).reset_index()
df_razones.columns = ['Razón', 'Cantidad']

# Filtrar "Sin informacion" si está en el top
df_razones_filtrado = df[df['Razon del Suicidio'] != 'Sin informacion']['Razon del Suicidio'].value_counts().head(10).reset_index()
df_razones_filtrado.columns = ['Razón', 'Cantidad']

################################################
################# VISUALIZACIÓN ################
################################################

##############  CONFIGURACIÓN DE LA PÁGINA  ##############
st.set_page_config(
    page_title='Análisis de Suicidios en Colombia',
    page_icon='📊',
    layout='wide'
)

# CSS personalizado
st.markdown(
    '''
    <style>
        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
        }
        .stMetric {
            background-color: #000;
            padding: 10px;
            border-radius: 5px;
        }
        h1 {
            color: #1f77b4;
        }
        h2 {
            color: #2c3e50;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
        }
         [data-testid="stMarkdownContainer"] p {
            font-size: 1.2rem !important;
        }
        h3 {
            color: #34495e;
        }
    </style>
    ''', unsafe_allow_html=True
)

##############  INTRODUCCIÓN  ##############
st.title('Colombia y el Suicidio: Comportamiento y Determinantes')
st.markdown('### Período 2015-2024')

with st.container(border=True):
    st.markdown("""
    #### Contexto
    
    El suicidio es un problema de salud pública que afecta a comunidades en todo el mundo. En Colombia, 
    comprender los patrones, tendencias y factores asociados a estos casos es fundamental para el diseño 
    de políticas públicas efectivas de prevención.
    
    #### Objetivos del Análisis
    
    Este dashboard interactivo tiene como propósito:
    - Identificar los grupos poblacionales más vulnerables
    - Analizar la variabilidad de los hechos en el transcurso de los años
    - Determinar los escenarios y mecanismos más frecuentes
    - Comprender los principales factores asociados
    
    #### Alcance
    
    - **Temporal:** 2015 - 2024 (9 años)
    - **Geográfico:** Todo el territorio colombiano
    - **Fuente:** Datos oficiales procesados y limpiados
    """)

st.markdown("---")

##############  DESCRIPCIÓN DEL DATASET  ##############

st.header('Descripción del Dataset')

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Total de Registros', f'{num_registros:,}', border=True)
    
    with col2:
        st.metric('Variables Analizadas', num_columnas, border=True)
    
    with col3:
        st.metric('Departamentos', num_departamentos, border=True,
              help='Incluye los 32 departamentos + Bogotá D.C.')
    
    with col4:
        st.metric('Período de Análisis', f'{anio_min}-{anio_max}', border=True)
    
    if st.checkbox(' Mostrar detalles de la fuente de los datos'):
        st.info("""
        **Fuente de Datos:** Instituto Nacional de Medicina Legal y Ciencias Forenses de Colombia
        
        **Procesamiento:** Los datos han sido limpiados y procesados eliminando registros incompletos. 
        Se analizaron 15,115 casos completos de un total de 26,541 registros originales.
        
        **Variables incluidas:** Año del hecho, Ciclo Vital, Sexo, País de Nacimiento, Departamento, 
        Escenario del Hecho, Mecanismo Causal y Razón del Suicidio.
        """)
    
    with st.expander('Ver muestra del conjunto de datos'):
        st.dataframe(df, use_container_width=True)


##############  PREGUNTA 1: CICLO VITAL  ##############

st.header('¿En qué etapa del ciclo vital se presenta con mayor frecuencia el suicidio?')

with st.container(border=True):
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Gráfico de barras horizontales
        fig_ciclo = go.Figure()
        
        fig_ciclo.add_trace(go.Bar(
            y=df_ciclo['Ciclo Vital'],
            x=df_ciclo['Cantidad'],
            orientation='h',
            text=df_ciclo['Cantidad'],
            textposition='auto',
            marker_color='#3498db',
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>'
        ))
        
        fig_ciclo.update_layout(
            title='Distribución de Casos por Ciclo Vital',
            xaxis_title='Número de Casos',
            yaxis_title='',
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        st.plotly_chart(fig_ciclo, use_container_width=True)
    
    with col2:
        # Gráfico de pie
        fig_pie_ciclo = go.Figure(data=[go.Pie(
            labels=df_ciclo['Ciclo Vital'],
            values=df_ciclo['Cantidad'],
            hole=0.4,
            marker_colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        )])
        
        fig_pie_ciclo.update_layout(
            title='Proporción por Ciclo Vital',
            height=400
        )
        
        st.plotly_chart(fig_pie_ciclo, use_container_width=True)
    
    # Insight
    ciclo_mayor = df_ciclo.iloc[0]['Ciclo Vital']
    casos_mayor = df_ciclo.iloc[0]['Cantidad']
    porcentaje_mayor = (casos_mayor / num_registros * 100)
    
    st.info(f"""
    **Hallazgo:** El grupo etario *{ciclo_mayor}* presenta la mayor cantidad de casos 
    con **{casos_mayor:,}** registros, representando el **{porcentaje_mayor:.1f}%** del total.
    """)

##############  PREGUNTA 2: GÉNERO  ##############

st.header('¿Qué género presenta mayor prevalencia de suicidio?')

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras comparativo
        fig_genero = go.Figure()
        
        fig_genero.add_trace(go.Bar(
            x=df_genero['Sexo'],
            y=df_genero['Cantidad'],
            text=df_genero['Cantidad'],
            textposition='auto',
            marker_color=['#3498db', '#e74c3c'],
            hovertemplate='<b>%{x}</b><br>Casos: %{y}<br>Porcentaje: %{customdata}%<extra></extra>',
            customdata=df_genero['Porcentaje']
        ))
        
        fig_genero.update_layout(
            title='Distribución de Casos por Género',
            xaxis_title='Género',
            yaxis_title='Número de Casos',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_genero, use_container_width=True)
    
    with col2:
        # Análisis por género y ciclo vital
        fig_genero_ciclo = px.bar(
            df_genero_ciclo,
            x='Ciclo Vital',
            y='Cantidad',
            color='Sexo de la victima',
            title='Distribución por Género y Ciclo Vital',
            barmode='group',
            color_discrete_map={'Hombre': '#3498db', 'Mujer': '#e74c3c'},
            height=400
        )
        
        fig_genero_ciclo.update_layout(
            xaxis_title='Ciclo Vital',
            yaxis_title='Número de Casos',
            legend_title='Género'
        )
        
        st.plotly_chart(fig_genero_ciclo, use_container_width=True)
    
    # Métricas comparativas
    col3, col4, col5 = st.columns(3)
    
    hombres = df_genero[df_genero['Sexo'] == 'Hombre']['Cantidad'].values[0]
    mujeres = df_genero[df_genero['Sexo'] == 'Mujer']['Cantidad'].values[0]
    ratio = hombres / mujeres
    
    with col3:
        st.metric('Total Hombres', f'{hombres:,}', f"{(hombres/num_registros*100):.1f}%")
    
    with col4:
        st.metric('Total Mujeres', f'{mujeres:,}', f"{(mujeres/num_registros*100):.1f}%")
    
    with col5:
        st.metric('Ratio Hombre/Mujer', f'{ratio:.1f}:1')
    
    st.info(f"""
    **Hallazgo:** Los hombres presentan una prevalencia significativamente mayor, 
    con **{ratio:.1f} casos** por cada caso en mujeres. Esto representa el **{(hombres/num_registros*100):.1f}%** 
    del total de casos.
    """)

##############  PREGUNTA 3: EVOLUCIÓN TEMPORAL  ##############

st.header('¿Cómo ha variado la tasa de suicidio en los últimos años?')

with st.container(border=True):
    st.subheader('Indicadores Anuales (2021-2024)')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label='2021',
            value=f"{indicadores[2021]:,} casos",
            delta=None,
            border=True
        )
    
    with col2:
        st.metric(
            label='2022',
            value=f"{indicadores[2022]:,} casos",
            delta=f"{deltas[2022]:.1%}",
            delta_color="inverse",
            border=True
        )
    
    with col3:
        st.metric(
            label='2023',
            value=f"{indicadores[2023]:,} casos",
            delta=f"{deltas[2023]:.1%}",
            delta_color="inverse",
            border=True
        )
    
    with col4:
        st.metric(
            label='2024',
            value=f"{indicadores[2024]:,} casos",
            delta=f"{deltas[2024]:.1%}",
            delta_color="inverse",
            border=True
        )

with st.container(border=True):
    # Gráfico de evolución temporal completo
    fig_temporal = go.Figure()
    
    fig_temporal.add_trace(go.Scatter(
        x=df_temporal['Año del hecho'],
        y=df_temporal['Cantidad'],
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10),
        name='Casos por año',
        hovertemplate='<b>Año %{x}</b><br>Casos: %{y}<extra></extra>'
    ))
    
    fig_temporal.update_layout(
        title='Evolución Temporal de Casos de Suicidio (2015-2024)',
        xaxis_title='Año',
        yaxis_title='Número de Casos',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_temporal, use_container_width=True)

       # Calcular tendencia
    casos_inicial = df_temporal.iloc[0]['Cantidad']
    casos_final = df_temporal.iloc[-1]['Cantidad']
    variacion_total = ((casos_final - casos_inicial) / casos_inicial) * 100
    
    if variacion_total > 0:
        tendencia = "incremento"
        color = "🔴"
    else:
        tendencia = "disminución"
        color = "🟢"

    st.info(f"""
    **Hallazgo:** En el período 2015-2024 se observa un {tendencia}
    del **{abs(variacion_total):.1f}%** en el número de casos, pasando de **{casos_inicial:,}** 
    casos en 2015 a **{casos_final:,}** casos en 2024.
    """)

    
    # Análisis por departamento
    st.subheader('Comportamiento por Departamento')
    
    depto_seleccionado = st.selectbox(
        'Seleccione un Departamento:',
        options=lista_deptos,
        index=lista_deptos.index('Antioquia') if 'Antioquia' in lista_deptos else 0
    )
    
    df_depto_filtrado = df_depto_anio[df_depto_anio['Departamento del hecho DANE'] == depto_seleccionado]
    
    fig_depto = go.Figure()
    
    fig_depto.add_trace(go.Bar(
        x=df_depto_filtrado['Año del hecho'],
        y=df_depto_filtrado['Cantidad'],
        marker_color='#3498db',
        text=df_depto_filtrado['Cantidad'],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Casos: %{y}<extra></extra>'
    ))
    
    fig_depto.update_layout(
        title=f'Evolución en {depto_seleccionado}',
        xaxis_title='Año',
        yaxis_title='Número de Casos',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_depto, use_container_width=True)

##############  PREGUNTA 4: ESCENARIOS Y MECANISMOS  ##############

st.header('¿Cuál es el lugar más frecuente de ocurrencia y el mecanismo utilizado?')

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Escenarios más frecuentes')
        
        fig_escenario = go.Figure()
        
        fig_escenario.add_trace(go.Bar(
            y=df_escenario['Escenario'],
            x=df_escenario['Cantidad'],
            orientation='h',
            text=df_escenario['Cantidad'],
            textposition='auto',
            marker_color='#2ecc71',
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>'
        ))
        
        fig_escenario.update_layout(
            xaxis_title='Número de Casos',
            yaxis_title='',
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        st.plotly_chart(fig_escenario, use_container_width=True)
    
    with col2:
        st.subheader('Mecanismos más utilizados')
        
        fig_mecanismo = go.Figure()
        
        fig_mecanismo.add_trace(go.Bar(
            y=df_mecanismo['Mecanismo'],
            x=df_mecanismo['Cantidad'],
            orientation='h',
            text=df_mecanismo['Cantidad'],
            textposition='auto',
            marker_color='#e67e22',
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>'
        ))
        
        fig_mecanismo.update_layout(
            xaxis_title='Número de Casos',
            yaxis_title='',
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        st.plotly_chart(fig_mecanismo, use_container_width=True)
    
    # Hallazgos
    escenario_principal = df_escenario.iloc[0]['Escenario']
    casos_escenario = df_escenario.iloc[0]['Cantidad']
    mecanismo_principal = df_mecanismo.iloc[0]['Mecanismo']
    casos_mecanismo = df_mecanismo.iloc[0]['Cantidad']
    
    st.info(f"""
    **Hallazgos:**
    - **Escenario más frecuente:** {escenario_principal} con **{casos_escenario:,}** casos 
    ({(casos_escenario/num_registros*100):.1f}% del total)
    - **Mecanismo más utilizado:** {mecanismo_principal} con **{casos_mecanismo:,}** casos 
    ({(casos_mecanismo/num_registros*100):.1f}% del total)
    """)
 
##############  PREGUNTA 5: RAZONES/MOTIVOS  ##############

st.header('¿Cuáles son los principales factores o motivos asociados a los casos?')

with st.container(border=True):
    col1, col2 = st.columns([3, 2])
    
    with col2:
        st.subheader('Filtros de Análisis')
        
        # Opción para incluir o excluir "Sin información"
        incluir_sin_info = st.checkbox('Incluir casos "Sin información"', value=False)
        
        # Filtro por ciclo vital
        ciclo_seleccionado = st.selectbox(
            'Filtrar por Ciclo Vital:',
            options=['Todos'] + sorted(df['Ciclo Vital'].unique())
        )
        
        # Filtro por género
        genero_seleccionado = st.selectbox(
            'Filtrar por Género:',
            options=['Todos', 'Hombre', 'Mujer']
        )
    
    # APLICAR FILTROS AL DATAFRAME
    df_filtrado = df.copy()
    
    if ciclo_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ciclo Vital'] == ciclo_seleccionado]
    
    if genero_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Sexo de la victima'] == genero_seleccionado]
    
    # CALCULAR RAZONES SEGÚN FILTROS
    if incluir_sin_info:
        df_razones_dinamico = df_filtrado['Razon del Suicidio'].value_counts().head(10).reset_index()
    else:
        df_razones_dinamico = df_filtrado[df_filtrado['Razon del Suicidio'] != 'Sin informacion']['Razon del Suicidio'].value_counts().head(10).reset_index()
    
    df_razones_dinamico.columns = ['Razón', 'Cantidad']
    
    with col1:
        st.subheader('Top 10 Razones Asociadas al Suicidio')
        
        # GRÁFICO DINÁMICO QUE SE ACTUALIZA CON LOS FILTROS
        fig_razones = go.Figure()
        
        fig_razones.add_trace(go.Bar(
            y=df_razones_dinamico['Razón'],
            x=df_razones_dinamico['Cantidad'],
            orientation='h',
            text=df_razones_dinamico['Cantidad'],
            textposition='auto',
            marker_color='#9b59b6',
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>'
        ))
        
        fig_razones.update_layout(
            xaxis_title='Número de Casos',
            yaxis_title='',
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        st.plotly_chart(fig_razones, use_container_width=True)
    
    with col2:
        st.markdown("---")
        st.markdown("**Top 5 Razones (según filtros):**")
        
        # Mostrar top 5 en métricas
        top5 = df_razones_dinamico.head(5)
        for idx, row in top5.iterrows():
            st.metric(f"{idx+1}. {row['Razón']}", f"{row['Cantidad']} casos")
    
    # Hallazgo principal
    if len(df_razones_dinamico) > 0:
        razon_principal = df_razones_dinamico.iloc[0]['Razón']
        casos_razon = df_razones_dinamico.iloc[0]['Cantidad']
        
        # Texto dinámico según filtros
        filtro_texto = ""
        if ciclo_seleccionado != 'Todos' or genero_seleccionado != 'Todos':
            filtros_activos = []
            if ciclo_seleccionado != 'Todos':
                filtros_activos.append(f"ciclo vital: {ciclo_seleccionado}")
            if genero_seleccionado != 'Todos':
                filtros_activos.append(f"género: {genero_seleccionado}")
            filtro_texto = f" (filtrado por {', '.join(filtros_activos)})"
        
        st.info(f"""
        **Hallazgo{filtro_texto}:** La razón más frecuente reportada es **"{razon_principal}"** 
        con **{casos_razon:,}** casos. Es importante destacar que un porcentaje significativo 
        de casos no tiene información sobre la razón del suicidio, lo que representa un desafío 
        para las estrategias de prevención.
        """)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados.")

##############  CONCLUSIONES  ##############

st.header('Conclusiones y Recomendaciones')

with st.container(border=True):
    st.markdown("""
    ### Hallazgos Principales
    
    1. **Grupos más vulnerables:**
       - Los adultos (29-59 años) representan el grupo etario con mayor número de casos
       - Los hombres tienen una prevalencia 3.3 veces mayor que las mujeres
    
    2. **Tendencia temporal:**
       - Se observa un incremento sostenido en el período 2015-2024
       - Los años recientes (2022-2024) muestran los valores más altos del período analizado
    
    3. **Patrones de ocurrencia:**
       - La vivienda es el escenario más frecuente de los casos
       - Los generadores de asfixia constituyen el mecanismo más utilizado
    
    4. **Factores asociados:**
       - Los conflictos de pareja y las enfermedades mentales son los motivos más reportados
       - Existe una alta proporción de casos sin información sobre la razón (desafío para prevención)
    
    ### Recomendaciones
    
    1. **Fortalecimiento de sistemas de información:** Mejorar el registro de información sobre 
       las razones asociadas a cada caso
    
    2. **Programas de prevención focalizados:** Diseñar estrategias específicas para hombres adultos 
       y jóvenes, que son los grupos más vulnerables
    
    3. **Atención en salud mental:** Fortalecer los servicios de atención psicológica y psiquiátrica, 
       especialmente en casos de conflictos de pareja y enfermedades mentales
    
    4. **Vigilancia epidemiológica:** Mantener sistemas de monitoreo continuo que permitan detectar 
       cambios en las tendencias y patrones
    
    5. **Intervención en crisis:** Implementar líneas de atención telefónica y servicios de 
       intervención en crisis disponibles 24/7
    
    ### Limitaciones del Estudio
    
    - El 43% de los registros originales fueron excluidos por falta de información completa
    - La alta proporción de casos "sin información" en la razón del suicidio limita el análisis causal
    - Los datos corresponden a casos reportados oficialmente, pudiendo existir subregistro
    
    ### Recursos de Ayuda
    
    **Si tú o alguien que conoces está atravesando una crisis:**
    - 📞 Línea Nacional: 106 (Línea de atención en salud mental)
    - 📞 Línea de la Vida: 01 8000 113 113
    """)


# Footer
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p>Dashboard desarrollado para análisis epidemiológico de suicidios en Colombia</p>
    <p>Datos: 2015-2024 | Fuente: Instituto Nacional de Medicina Legal y Ciencias Forenses</p>
    <p><em>Este análisis tiene fines académicos y de investigación en salud pública</em></p>
    <p>Integrantes del Equipo:</p>
    <p><em>* Mauricio Urrego Ospina</em></p>
    <p><em>* Juliana Andrea Urrego Madrid</em></p>
    <p><em>* Paula Andrea Gallego Higinio</em></p>
</div>
""", unsafe_allow_html=True)