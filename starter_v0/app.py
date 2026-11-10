from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    run_model_tool_loop,
    trim_history,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("Research Agent")
st.caption("Hỏi agent để tìm kiếm và tổng hợp thông tin bằng các tool đã cấu hình.")

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox(
        "Model provider",
        ["openrouter", "openai", "anthropic", "gemini", "ollama"],
    )
    model_name = st.text_input(
        "Model (để trống dùng mặc định)",
        help="Ví dụ: openai/gpt-4o-mini hoặc qwen2.5:7b cho Ollama.",
    ).strip()
    st.caption("API key cần được cấu hình trong starter_v0/.env.")
    if st.button("Xóa hội thoại"):
        st.session_state.history = []
        st.session_state.turns = []
        st.rerun()

st.session_state.setdefault("history", [])
st.session_state.setdefault("turns", [])

for turn in st.session_state.turns:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn["assistant"])
        if turn["tool_events"]:
            with st.expander("Chi tiết tool đã gọi"):
                for event in turn["tool_events"]:
                    st.markdown(f"**{event.get('tool', 'tool')}**")
                    st.json(event)

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("Câu hỏi")
    submitted = st.form_submit_button("Gửi")

if submitted and user_text.strip():
    try:
        system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
        declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
        provider = make_provider(provider_name)
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, 5),
            {"role": "user", "content": user_text.strip()},
        ]
        result: dict[str, Any] = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=to_openai_tools(declarations),
            model=model_name or None,
            max_tool_rounds=4,
        )
        answer = result["assistant_text"]
        tool_events = result["tool_events"]
        st.session_state.history.extend(
            [
                {"role": "user", "content": user_text.strip()},
                {"role": "assistant", "content": answer},
            ]
        )
        st.session_state.turns.append(
            {"user": user_text.strip(), "assistant": answer, "tool_events": tool_events}
        )
        st.rerun()
    except Exception as exc:
        st.error(f"{type(exc).__name__}: {exc}")
