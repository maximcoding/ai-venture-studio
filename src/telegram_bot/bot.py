"""Aiogram bot: /start, /help, approval callback with inline buttons."""

import logging
from pathlib import Path
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

APPROVE = "approve"
GO_BACK = "go_back"
VIEW_DOCS = "view_docs"

router = Router(name="approval")

# Set by run_bot so handlers can resume the graph (no custom kwargs in Aiogram)
_graph: Any = None
_default_config: dict[str, Any] = {}


async def _send_artifact_files(message: Message, file_paths: list[str]) -> None:
    """Send artifact files as documents to the user."""
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists() and path.is_file():
            try:
                document = FSInputFile(file_path)
                await message.answer_document(document)
            except Exception as e:
                logger.warning("failed_to_send_file", extra={"file": file_path, "error": str(e)})
                await message.answer(f"⚠️ Could not send file: {path.name}")


def _approval_keyboard(phase: int) -> InlineKeyboardMarkup:
    """Inline buttons for phase approval (per PHASES_INDEX)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ APPROVE", callback_data=f"{APPROVE}:{phase}"),
                InlineKeyboardButton(text="📄 VIEW DOCS", callback_data=f"{VIEW_DOCS}:{phase}"),
            ],
            [InlineKeyboardButton(text="🔙 GO BACK", callback_data=f"{GO_BACK}:{phase}")],
        ]
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start."""
    await message.answer(
        "AI Venture Studio — 10-phase pipeline. Each phase requires your approval in Telegram.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help."""
    await message.answer(
        "Commands: /start, /help, /run. Use /run to start the pipeline; when a phase completes, use the inline buttons to APPROVE or VIEW DOCS.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("run"))
async def cmd_run(message: Message) -> None:
    """Start pipeline for this user; on interrupt, send approval keyboard."""
    if _graph is None:
        await message.answer("Bot not ready (graph not set).")
        return
    thread_id = f"user_{message.from_user.id}" if message.from_user else "default"
    config = {**_default_config, "configurable": {"thread_id": thread_id}}
    try:
        result = await _graph.ainvoke(
            {"messages": [], "current_phase": 0, "approved": False},
            config=config,
        )
        if "__interrupt__" in result and result["__interrupt__"]:
            inter = result["__interrupt__"][0]
            payload = getattr(inter, "value", inter) or {}
            phase = payload.get("phase", 1)
            msg_text = payload.get("message", "Approve to continue.")
            artifact_files = payload.get("artifact_files", [])
            
            # Send artifact files first
            await _send_artifact_files(message, artifact_files)
            
            # Then send message with approval buttons
            await message.answer(msg_text, reply_markup=_approval_keyboard(phase))
        else:
            await message.answer("Pipeline step completed (no interrupt).")
    except Exception as e:
        logger.exception("run_failed")
        await message.answer(f"Run failed: {e}")


@router.callback_query(F.data.startswith(APPROVE))
async def handle_approve(callback: CallbackQuery) -> None:
    """Resume graph with approved=True for the given phase."""
    if not callback.data or _graph is None:
        await callback.answer("Bot not ready.")
        return
    _, phase = callback.data.split(":", 1)
    thread_id = f"user_{callback.from_user.id}" if callback.from_user else "default"
    run_config = {**_default_config, "configurable": {"thread_id": thread_id}}

    from langgraph.types import Command

    # Resume and check if next phase interrupted
    result = await _graph.ainvoke(Command(resume={"approved": True}), run_config)
    await callback.answer("Approved. Pipeline continued.")
    if callback.message:
        await callback.message.edit_text(f"Phase {phase} approved. Pipeline continued.")

    # Check if the next phase also interrupted (phase-to-phase transition)
    if "__interrupt__" in result and result["__interrupt__"]:
        inter = result["__interrupt__"][0]
        payload = getattr(inter, "value", inter) or {}
        next_phase = payload.get("phase", int(phase) + 1)
        msg_text = payload.get("message", "Approve to continue.")
        artifact_files = payload.get("artifact_files", [])
        
        if callback.message:
            # Send artifact files first
            await _send_artifact_files(callback.message, artifact_files)
            
            # Then send message with approval buttons
            await callback.message.answer(msg_text, reply_markup=_approval_keyboard(next_phase))


@router.callback_query(F.data.startswith(GO_BACK))
async def handle_go_back(callback: CallbackQuery) -> None:
    """Ack GO BACK (full rollback logic can be added later)."""
    await callback.answer("Go back: use Time Machine / rollback when implemented.")


@router.callback_query(F.data.startswith(VIEW_DOCS))
async def handle_view_docs(callback: CallbackQuery) -> None:
    """Point user to per-run artifacts folder."""
    thread_id = f"user_{callback.from_user.id}" if callback.from_user else "default"
    artifacts_path = f"artifacts/{thread_id}/docs/"
    await callback.answer("Artifacts are per-run.")
    if callback.message:
        await callback.message.answer(
            f"Your artifacts folder: <code>{artifacts_path}</code>\n"
            "Factory manuals (PHASE_*.md) are in /docs.",
            parse_mode="HTML",
        )


async def run_bot(
    token: str,
    graph: Any,
    pool: Any,
) -> None:
    """Run Aiogram polling. graph and pool are used by approval callbacks."""
    global _graph, _default_config
    _graph = graph
    _default_config = {"configurable": {"thread_id": "default"}}

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
