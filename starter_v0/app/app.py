from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import (  # noqa: E402
    execute_tool_call,
    now_iso,
    run_model_tool_loop,
    trim_history,
    write_transcript,
)
from providers import make_provider  # noqa: E402
from providers.base import ToolCall  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402

ARTIFACTS_DIR = ROOT / "artifacts"
PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]


def init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("transcript", None)
    st.session_state.setdefault("transcript_path", None)


def new_transcript(provider: str, model: str | None) -> tuple[dict[str, Any], Path]:
    artifact_version = build_artifact_version("v0", PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"v0_{provider}_{timestamp}"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "system_prompt": str(PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def execute_ui_tool(call: ToolCall) -> dict[str, Any]:
    if call.name == "send":
        return {
            "tool": call.name,
            "args": call.args,
            "result": {
                "error": "action_blocked",
                "message": "Telegram sending is disabled in this UI. No message was sent.",
            },
        }
    return execute_tool_call(call)


def render_message(message: dict[str, Any]) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tool_events"):
            with st.expander("Chi tiết các tool đã gọi"):
                st.json(message["tool_events"])
        if message.get("status") == "provider_error":
            st.error(message["error"])
        if message.get("action_blocked"):
            st.warning("Tool gửi Telegram đã bị chặn; không có tin nhắn nào được gửi.")


def main() -> None:
    st.set_page_config(page_title="Research Agent · v0", page_icon="🔎", layout="centered")
    init_state()

    st.title("Research Agent")
    st.caption("Giao diện thử nghiệm Streamlit · baseline v0")

    with st.sidebar:
        st.subheader("Cấu hình")
        provider_name = st.selectbox(
            "Provider",
            PROVIDERS,
            index=0,
            disabled=bool(st.session_state.messages),
        )
        model_override = st.text_input(
            "Model (để trống dùng mặc định)",
            value="",
            placeholder="openai/gpt-4o-mini",
            disabled=bool(st.session_state.messages),
        )
        st.caption("Prompt và tools được nạp từ artifacts của v0.")
        st.warning("Gửi Telegram bị tắt trong giao diện demo.")
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            st.session_state.messages = []
            st.session_state.transcript = None
            st.session_state.transcript_path = None
            st.rerun()

    try:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(TOOLS_PATH)
        openai_tools = to_openai_tools(tool_declarations)
    except Exception as exc:
        st.error(f"Không thể tải cấu hình baseline v0: {type(exc).__name__}: {exc}")
        st.stop()

    for message in st.session_state.messages:
        render_message(message)

    user_text = st.chat_input("Bạn muốn tìm hiểu điều gì?")
    if not user_text:
        if st.session_state.transcript_path:
            st.caption(f"Transcript: {st.session_state.transcript_path}")
        return

    user_message = {"role": "user", "content": user_text}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(user_text)

    response_status = st.status("Đang xử lý câu hỏi...", expanded=True)
    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1
        if st.session_state.transcript
        else 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        if st.session_state.transcript is None:
            transcript, transcript_path = new_transcript(
                provider_name,
                model_override.strip() or None,
            )
            st.session_state.transcript = transcript
            st.session_state.transcript_path = str(transcript_path)

        provider = make_provider(provider_name)
        selected_model = model_override.strip() or getattr(provider, "default_model", None)
        transcript = st.session_state.transcript
        transcript["model"] = selected_model
        history = [
            {"role": item["role"], "content": item["content"]}
            for item in st.session_state.messages[:-1]
        ]
        result = run_model_tool_loop(
            provider=provider,
            messages=[
                {"role": "system", "content": system_prompt},
                *trim_history(history, 5),
                user_message,
            ],
            tools=openai_tools,
            model=selected_model,
            max_tool_rounds=4,
            tool_executor=execute_ui_tool,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        assistant_message = {
            "role": "assistant",
            "content": assistant_text,
            "tool_events": result["tool_events"],
            "action_blocked": any(
                isinstance(event.get("result"), dict)
                and event["result"].get("error") == "action_blocked"
                for event in result["tool_events"]
            ),
        }
        st.session_state.messages.append(assistant_message)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        turn_record.update({
            "status": "provider_error",
            "error": error,
            "assistant_text": None,
            "ended_at": now_iso(),
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Không thể hoàn tất yêu cầu: {error}",
            "status": "provider_error",
            "error": error,
        })

    if st.session_state.transcript is not None:
        turn_record["ended_at"] = now_iso()
        st.session_state.transcript["turns"].append(turn_record)
        try:
            write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)
        except OSError as exc:
            st.error(f"Không thể lưu transcript: {type(exc).__name__}: {exc}")

    response_status.update(label="Đã nhận phản hồi", state="complete", expanded=False)
    render_message(st.session_state.messages[-1])


if __name__ == "__main__":
    main()
