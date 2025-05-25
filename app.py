import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ast
from datetime import datetime
import os

st.set_page_config(page_title="TSLA Dashboard", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("TSLA_data.csv")
        df.columns = df.columns.str.strip().str.lower()

        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp'])
        else:
            st.error("❌ No 'timestamp' column found.")
            return pd.DataFrame()

        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        def parse_list(x):
            try:
                return ast.literal_eval(x) if isinstance(x, str) else []
            except:
                return []

        df['support_list'] = df['support'].apply(parse_list)
        df['resistance_list'] = df['resistance'].apply(parse_list)
        df['direction'] = df['direction'].fillna('None').astype(str).str.upper()

        return df.dropna(subset=['open', 'high', 'low', 'close']).sort_values('date')

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame()

def candlestick_chart(df, max_rows=100):
    fig = go.Figure(go.Candlestick(
        x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='green', decreasing_line_color='red', name='TSLA'
    ))

    trimmed_df = df.tail(max_rows)

    for _, row in trimmed_df.iterrows():
        if row['support_list']:
            fig.add_shape(type="rect", x0=row['date'], x1=row['date'],
                          y0=min(row['support_list']), y1=max(row['support_list']),
                          fillcolor="rgba(0,255,0,0.2)", line=dict(width=0), layer="below")
        if row['resistance_list']:
            fig.add_shape(type="rect", x0=row['date'], x1=row['date'],
                          y0=min(row['resistance_list']), y1=max(row['resistance_list']),
                          fillcolor="rgba(255,0,0,0.2)", line=dict(width=0), layer="below")

    signals = {'LONG': 'triangle-up', 'SHORT': 'triangle-down', 'NONE': 'circle'}
    for direction, symbol in signals.items():
        subset = trimmed_df[trimmed_df['direction'] == direction]
        if subset.empty:
            continue
        y = (subset['low'] * 0.98) if direction == 'LONG' else \
            (subset['high'] * 1.02) if direction == 'SHORT' else \
            (subset['high'] + subset['low']) / 2
        fig.add_trace(go.Scatter(x=subset['date'], y=y, mode='markers',
                                 marker=dict(symbol=symbol, size=10,
                                             color='green' if direction == 'LONG' else
                                                   'red' if direction == 'SHORT' else
                                                   'yellow'),
                                 name=direction, showlegend=True))

    fig.update_layout(title='TSLA Chart (Last 100 Rows)',
                      yaxis_title='Price ($)', xaxis_title='Date',
                      xaxis_rangeslider_visible=False)
    return fig

@st.cache_resource
def init_gemini():
    import google.generativeai as genai
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Use safe model name to avoid 404 error
        return genai.GenerativeModel("models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error(f"Gemini init error: {e}")
        return None

def ask_ai(question, summary):
    model = init_gemini()
    if not model:
        return "❌ Gemini model unavailable. Check your API key."

    try:
        prompt = f"""
        You are an expert stock analyst. Use the TSLA summary below to answer the question briefly and clearly:

        Summary:
        {summary}

        Question:
        {question}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini AI error: {e}"

def main():
    st.title("📈 TSLA Trading Dashboard")
    st.write("📂 Current working directory:", os.getcwd())

    st.write("📥 Loading TSLA data...")
    df = load_data()

    if df.empty:
        st.error("⚠️ Could not load or process the TSLA_data.csv file.")
        return

    st.success("✅ Data loaded successfully.")
    stats = f"Records: {len(df)}, Range: {df['date'].min().date()} to {df['date'].max().date()}"
    st.write(stats)

    st.write("📊 Generating candlestick chart...")
    with st.spinner("Rendering chart..."):
        st.plotly_chart(candlestick_chart(df), use_container_width=True)

    with st.expander("🤖 Ask Gemini AI"):
        summary = f"{stats}, Close: ${df['close'].iloc[-1]:.2f}, LONG: {len(df[df['direction'] == 'LONG'])}, SHORT: {len(df[df['direction'] == 'SHORT'])}"
        q = st.selectbox("Sample Questions", [
            "How many LONG vs SHORT signals?",
            "What’s the highest TSLA price?",
            "Which month was most volatile?"
        ])
        if st.button("Ask AI"):
            with st.spinner("Thinking..."):
                st.write(ask_ai(q, summary))

if __name__ == "__main__":
    main()
