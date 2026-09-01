from __future__ import annotations

from typing import Any, Iterable

import pandas as pd
import streamlit as st


def render_dataframe(data: Iterable[Any], columns: list[str] | None = None, title: str = "Data"):
    st.subheader(title)
    if not data:
        st.info("No data available.")
        return
    df = pd.DataFrame(data)
    if columns:
        df = df[columns]
    st.dataframe(df)
