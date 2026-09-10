import streamlit as st
import requests
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("📊 Empleo en Plantas de Proceso")
st.markdown("### Se realizará el analisis del empleo en plantas de proceso en Chile en el año 2011")
st.write("Se utilizará la API de https://datos.gob.cl/group")

response = requests.get(f"https://datos.gob.cl/api/3/action/datastore_search?resource_id=a4164bdc-38ce-4972-bd0d-04372f1234ce&limit=1000000")
if response.status_code == 200:
  st.write("✅ Comunicacion OK")
else:
  st.write("❌ Error en la comunicacion")

try:
    # 1. Convertimos la respuesta de la API a un diccionario de Python
    data_json = response.json()

    # 2. En la API de datos.gob.cl, los registros reales están guardados en:

    if 'result' in data_json and 'records' in data_json['result']:
        df = pd.DataFrame(data_json['result']['records'])
        total_duplicados = df.duplicated().sum()
        df = df.rename(columns= {"ANO":"AÑO","Genero":"Género","Region":"Región","Funcion":"Función","CLASE_INDUSTRIA_II":"Clase_Industria"})
        st.metric(label="Registros Duplicados Detectados", value=int(total_duplicados))
        st.markdown("#### Vista previa de los datos extraídos:")
        st.dataframe(df.head(10)) # Streamlit mostrará las 10 primeras filas de la tabla interactiva perfectamente
        st.success("✅ Datos cargados exitosamente")
    else:
        st.error("❌ La estructura de la API no contiene los registros esperados.")
        st.write(data_json) # Muestra el JSON para inspeccionar si la búsqueda falló

    #3.- Visualizaciones con Plotly"
    st.header("Visualizaciones con Plotly")
    with st.container():
          col1, col2 = st.columns(2)
          with col1:
           #4.- Grafico de torta"
           st.subheader("Grafico de Torta de Empleabilidad por Género año 2011")
           df['Ocupados'] = pd.to_numeric(df['Ocupados'], errors='coerce')
           ax = df.groupby('Género')['Ocupados'].sum().reset_index()

           # Creamos el gráfico de pastel corregido
           fig = px.pie(ax,
           values="Ocupados",
           names="Género",
           #title="Empleabilidad por Género año 2011",
           hole=0.3) # Esto lo convierte en un gráfico de dona muy elegante

           st.plotly_chart(fig, use_container_width=True)


          with col2:

            st.subheader("Gráfico de Barras por Región y Género")
            st.write("Cantidad de trabajadores ocupados por Región, divididos por género")

             # 1. Aseguramos que la columna Ocupados sea numérica
            df['Ocupados'] = pd.to_numeric(df['Ocupados'], errors='coerce')

            # 2. Agrupamos por Región Y Género al mismo tiempo, sumando los Ocupados
            df_agrupado = df.groupby(['Región', 'Género'])['Ocupados'].sum().reset_index()

            # 3. Creamos el gráfico con Plotly usando color='Género' (que funciona igual que el hue de seaborn)
            fig = px.bar(
            df_agrupado,
            x="Región",
            y="Ocupados",
            color="Género",  # <- este es el simil del Hue visto en clases para Seaborn! Separa las barras por colores según el género
            title="Ocupados por Región y Género",
            barmode="group", # Coloca las barras de hombre y mujer una al lado de la otra (usa "stack" si las quieres apiladas)
            labels={'Ocupados': 'Total Trabajadores'}
            )

            # 4. Le pedimos a Streamlit que dibuje el objeto de Plotly
            st.plotly_chart(fig, use_container_width=True)

    st.header("Visualizaciones con Seaborn")
    with st.container():
          col1, col2 = st.columns(2)
          with col1:
           st.subheader("Ocupados,Función y Clase de Industria")
           fig, ax = plt.subplots(figsize=(15, 8))
           ax = sns.scatterplot(x="Función",
                        y = "Ocupados",
                        hue = "Clase_Industria",
                        palette="coolwarm",
                        data = df)
           ax.set_title("Ocupados, Función y Clase de Industria")
           ax.set_xlabel("Función")
           ax.set_ylabel("Ocupados")
           st.pyplot(fig)
          with col2:
            # 4. Le pedimos a Streamlit que dibuje el objeto de Seaborn

            st.subheader("Ocupados, Clase de Industria por Trimestre")
            fig, ax = plt.subplots(figsize=(15, 8))
            ax = sns.scatterplot(x="Trimestre",
                        y = "Ocupados",
                        hue = "Clase_Industria",
                        palette="coolwarm",
                        data = df)
            ax.set_title("Ocupados, Clase de Industria por Trimestre")
            ax.set_xlabel("Clase de Industria")
            ax.set_ylabel("Ocupados")
            st.pyplot(fig)

             
    st.subheader("Histograma de Ocupados en Pymes")
    df_pymes = df[(df["Ocupados"] > 0) & (df["Ocupados"] <= 20)]
    fig, ax = plt.subplots(figsize=(13, 5))

    df_pymes["Ocupados"].plot(
       kind="hist",
       bins=20,
       ax=ax,
       color="#2b7bba",
       edgecolor="white",
      title="Distribución de Ocupados en PyMEs"
    )

    media_pyme = df_pymes["Ocupados"].mean()
    mediana_pyme = df_pymes["Ocupados"].median()
    plt.axvline(media_pyme, color="r", linestyle="--", label=f"Media PyME: {media_pyme:.1f}")
    plt.axvline(mediana_pyme, color="g", linestyle="-.", label=f"Mediana PyME: {mediana_pyme:.1f}")

    ax.set_xlabel("Cantidad de Ocupados")
    ax.set_ylabel("Frecuencia (Cantidad de Registros)")
    plt.xlim(1, 20)
    plt.xticks(range(1, 21))
    plt.legend()
    st.pyplot(fig)
    
    st.subheader("Histograma de Ocupados en Grandes Empresas")
    df_gempresas = df[(df["Ocupados"] > 0) & (df["Ocupados"] >= 20)]
    fig, ax = plt.subplots(figsize=(13, 5))
    df_gempresas["Ocupados"].plot(
       kind="hist",
       bins=25,
       ax=ax,
       color="#e67e22",
       edgecolor="white",
      title="Distribución de Ocupados en Grandes Empresas"
    )

    media_gempresas = df_gempresas["Ocupados"].mean()
    mediana_gempresas = df_gempresas["Ocupados"].median()
    plt.axvline(media_gempresas, color="r", linestyle="--", label=f"Media Grandes Empresas: {media_gempresas:.1f}")
    plt.axvline(mediana_gempresas, color="g", linestyle="-.", label=f"Mediana Grandes Empresas: {mediana_gempresas:.1f}")
    ax.set_xlabel("Cantidad de Ocupados")
    ax.set_ylabel("Frecuencia (Cantidad de Registros)")
    max_valor = int(df_gempresas["Ocupados"].max()) if len(df_gempresas) > 0 else 100
    plt.xlim(20, max_valor + 20)  
    plt.legend()
    st.pyplot(fig)

    st.subheader("Gráfico de Violín")
    fig, ax = plt.subplots(figsize=(15, 8))
    sns.violinplot(x="Clase_Industria",
                y = "Ocupados",
                data = df)
    ax.set_title("Ocupados por Clase de Industria")
    ax.set_xlabel("Clase de Industria")
    ax.set_ylabel("Ocupados")
    st.pyplot(fig)
    #6. Sección Interactiva
    st.header("Sección Interactiva y gráficos con Plotly")
    st.subheader("Puede seleccionar el tipo gráfico y la columnas")
     #Selector de dataframe
    dataset_choice = st.radio(
         "Se Selecciona por defecto la Base de Datos",
        ["Empleo en Planta de Procesos 2011"]
     )
    if dataset_choice == "Empleo en Planta de Procesos 2011":
          df_selection = df
     #Selector de Visualización
          chart_type = st.selectbox(
         "Selecciona el tipo de gráfico",
         ["Barras","Dispersión","Línea"]
     )

     #Selector de datos
    lista_columnas =  list(df_selection.columns)
    default_x = lista_columnas.index('Función') if 'Función' in df_selection else 0
    default_y = lista_columnas.index('Ocupados') if 'Ocupados' in df_selection else 0
    x_axis= st.selectbox(
         "Selecciona el eje X",lista_columnas,index=default_x)
    y_axis = st.selectbox(
         "Selecciona el eje Y",lista_columnas,index=default_y)
    try:
           if  chart_type == "Barras":
              fig = px.bar(df_selection, x=x_axis, y=y_axis)
           elif chart_type == "Dispersión":
              fig = px.scatter(df_selection, x=x_axis, y=y_axis)
           else:
              fig = px.line(df_selection, x=x_axis, y=y_axis)
           fig.update_xaxes(tickangle=45)
           st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ No se pudo generar el gráfico seleccionado. Asegúrate de elegir una columna numérica para el eje Y (como 'Ocupados'). Detalle: {e}")




except Exception as e:
     st.error(f"❌ Error al cargar los datos: {str(e)}")
     st.error("Por favor,verifica que los archivos existan en la carpeta ´data` y tengan el formato correcto.")
