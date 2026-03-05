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


        # -------------------------
        # AGRUPAR DATOS SEGÚN RANGO
        # -------------------------
        rango_dias = (df_filtrado["fecha"].max() - df_filtrado["fecha"].min()).days

        # Detectar intervalo original
        intervalo = df_filtrado["fecha"].diff().median()
        intervalo_minutos = intervalo.total_seconds() / 60

        # Solo agrupar si los datos son muy densos (menos de 15 min)
        if intervalo_minutos < 15:
            if rango_dias <= 2:
                df_filtrado = df_filtrado.set_index("fecha").resample("10min").mean().reset_index()
            elif rango_dias <= 7:
                df_filtrado = df_filtrado.set_index("fecha").resample("30min").mean().reset_index()
            else:
                df_filtrado = df_filtrado.set_index("fecha").resample("1h").mean().reset_index()

        cantidad_puntos = len(df_filtrado)

        # Solo agregamos si hay demasiados puntos
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

        

        # -------------------------
        # MÉTRICAS
        # -------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Temperatura Promedio (°C)",
                round(df_filtrado["temperatura"].mean(), 2)
            )

        with col2:
            st.metric(
                "Humedad Promedio (%)",
                round(df_filtrado["humedad"].mean(), 2)
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

        

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")