import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Ambiental", layout="wide")

st.title("📊 Dashboard de Monitoreo Ambiental")

st.markdown("Carga un archivo CSV para visualizar temperatura y humedad.")

# -------------------------
# CARGA DE ARCHIVO
# -------------------------
archivo = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])

if archivo is not None:

    try:
        # Intentar leer con diferentes encodings
        try:
            df = pd.read_csv(archivo, encoding="utf-8")
        except:
            df = pd.read_csv(archivo, encoding="latin-1")

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Renombrar columnas para facilitar manejo
        df = df.rename(columns={
            "Marca de Tiempo": "fecha",
            "TEMPERATURA (Â°C)": "temperatura",
            "TEMPERATURA (°C)": "temperatura",
            "HUMEDAD RELATIVA (%)": "humedad"
        })

        # Convertir fecha
        df["fecha"] = pd.to_datetime(
            df["fecha"],
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )

        # Ordenar
        df = df.sort_values("fecha")

        # -------------------------
        # FILTRO POR FECHA
        # -------------------------
        col1, col2 = st.columns(2)

        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicial",
                value=df["fecha"].min().date()
            )

        with col2:
            fecha_fin = st.date_input(
                "Fecha final",
                value=df["fecha"].max().date()
            )

        df_filtrado = df[
            (df["fecha"] >= pd.to_datetime(fecha_inicio)) &
            (df["fecha"] <= pd.to_datetime(fecha_fin))
        ]

        df_extremos = df_filtrado.copy()


        # -------------------------
        # VALORES EXTREMOS
        # -------------------------

        # Temperatura
        temp_max = df_extremos.loc[df_extremos["temperatura"].idxmax()]
        temp_min = df_extremos.loc[df_extremos["temperatura"].idxmin()]

        # Humedad
        hum_max = df_extremos.loc[df_extremos["humedad"].idxmax()]
        hum_min = df_extremos.loc[df_extremos["humedad"].idxmin()]
        
        # -------------------------
        # MODO DE VISUALIZACIÓN
        # -------------------------

        modo = st.radio(
            "Modo de visualización:",
            ["Datos optimizados","Datos originales"],
            horizontal=True
        )
        

        # -------------------------
        # AGRUPAR SOLO SI EL USUARIO LO ELIGE
        # -------------------------

        if modo == "Datos optimizados":

            cantidad_puntos = len(df_filtrado)

            if cantidad_puntos > 2000:

                rango_dias = (df_filtrado["fecha"].max() - df_filtrado["fecha"].min()).days

                if rango_dias <= 2:
                    frecuencia = "10min"
                elif rango_dias <= 7:
                    frecuencia = "30min"
                else:
                    frecuencia = "1h"

                df_filtrado = (
                    df_filtrado
                    .set_index("fecha")
                    .resample(frecuencia)
                    .mean()
                    .reset_index()
                )

                st.caption(f"Datos agrupados cada {frecuencia}. Mostrando {len(df_filtrado)} puntos.")
            else:
                st.caption(f"Mostrando {len(df_filtrado)} puntos (no fue necesario agrupar).")

        else:
            st.caption(f"Mostrando {len(df_filtrado)} puntos originales.")

        

        # -------------------------
        # MÉTRICAS
        # -------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Temperatura Promedio (°C)",
                round(df_extremos["temperatura"].mean(), 2)
            )

        with col2:
            st.metric(
                "Humedad Promedio (%)",
                round(df_extremos["humedad"].mean(), 2)
            )

        
        
            

        # -------------------------
        # GRÁFICA DOBLE EJE
        # -------------------------

        fig = go.Figure()

        # Línea Temperatura (eje izquierdo)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["fecha"],
                y=df_filtrado["temperatura"],
                name="Temperatura (°C)",
                line=dict(color="orange"),
                yaxis="y1"
            )
        )

        # Línea Humedad (eje derecho)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["fecha"],
                y=df_filtrado["humedad"],
                name="Humedad Relativa (%)",
                line=dict(color="blue"),
                yaxis="y2"
            )
        )

        fig.update_layout(
            title="Temperatura y Humedad Relativa",
            xaxis=dict(title="Fecha"),
            yaxis=dict(
                title="Temperatura (°C)",
                side="left"
            ),
            yaxis2=dict(
                title="Humedad Relativa (%)",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0.01, y=0.99),
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Valores extremos en el rango seleccionado")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🌡 Temperatura")
            st.write(f"🔺 Máxima: {temp_max['temperatura']:.2f} °C")
            st.write(f"🕒 Fecha: {temp_max['fecha']}")
            st.write(f"🔻 Mínima: {temp_min['temperatura']:.2f} °C")
            st.write(f"🕒 Fecha: {temp_min['fecha']}")

        with col2:
            st.markdown("### 💧 Humedad Relativa")
            st.write(f"🔺 Máxima: {hum_max['humedad']:.2f} %")
            st.write(f"🕒 Fecha: {hum_max['fecha']}")
            st.write(f"🔻 Mínima: {hum_min['humedad']:.2f} %")
            st.write(f"🕒 Fecha: {hum_min['fecha']}")
                

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")