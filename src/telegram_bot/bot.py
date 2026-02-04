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

# Track active processing sessions to prevent duplicate runs
_active_sessions: set[str] = set()

# AI Dream Team - personas for each phase
PHASE_PERSONAS = {
    1: {
        "name": "Steve Bobs",
        "emoji": "🍎",
        "greeting": "Привет! Я Steve Bobs.\n\nРасскажи мне свою идею — я помогу превратить её в insanely great продукт.\n\nОтправь команду:\n<code>/run &lt;твоя идея&gt;</code>",
        "completion": "🍎 <b>Steve Bobs</b>\n\nОтличная идея! Я создал бизнес-анализ.\nИзучи документы и дай знать, готов ли двигаться дальше.",
    },
    2: {
        "name": "Smarty Vegan",
        "emoji": "🥗",
        "greeting": "Привет! Я Smarty Vegan, product manager.\n\nSteve Bobs передал мне твою идею. Моя задача — превратить её в здоровый, органический MVP без лишних фич.\n\nТолько самое необходимое для первой версии!",
        "completion": "🥗 <b>Smarty Vegan</b>\n\nГотово! User stories и MVP scope созданы.\nВсё по методологии — чисто и понятно.",
    },
    3: {
        "name": "Johnny Vibe",
        "emoji": "🎨",
        "greeting": "Привет! Я Johnny Vibe, дизайнер.\n\nПродукт без великолепного дизайна — это просто код.\nДавай создадим что-то beautiful!",
        "completion": "🎨 <b>Johnny Vibe</b>\n\nДизайн готов! Каждый пиксель на своём месте.\nЭто будет выглядеть потрясающе.",
    },
    4: {
        "name": "Linus Codevalds",
        "emoji": "⚙️",
        "greeting": "Я Linus Codevalds, tech lead.\n\nТеперь моя очередь. Спроектируем надёжную архитектуру.\nБез костылей, только чистая инженерия.",
        "completion": "⚙️ <b>Linus Codevalds</b>\n\nАрхитектура спроектирована. Система будет масштабироваться.\nПроверь техническую документацию.",
    },
    5: {
        "name": "Dave Railsman",
        "emoji": "💻",
        "greeting": "Привет! Я Dave Railsman, CTO.\n\nПора писать код. Будем делать быстро, но правильно.\nConvention over configuration!",
        "completion": "💻 <b>Dave Railsman</b>\n\nКод написан! Чистый, тестируемый, готовый к деплою.\nПосмотри что получилось.",
    },
    6: {
        "name": "Kelly Cloudtower",
        "emoji": "☁️",
        "greeting": "Привет! Я Kelly Cloudtower, DevOps engineer.\n\nПора настроить инфраструктуру и CI/CD.\nВсё будет автоматизировано и в облаках.",
        "completion": "☁️ <b>Kelly Cloudtower</b>\n\nИнфраструктура готова! Kubernetes, мониторинг, автодеплой.\nПродукт готов к запуску.",
    },
    7: {
        "name": "Kelly Cloudtower",
        "emoji": "☁️",
        "greeting": "Я Kelly Cloudtower, продолжаю работу.\n\nТеперь QA и тесты. Проверим каждый сценарий.",
        "completion": "☁️ <b>Kelly Cloudtower</b>\n\nТесты пройдены! Багов не найдено.\nМожем уверенно двигаться дальше.",
    },
    8: {
        "name": "Bruce Securer",
        "emoji": "🔐",
        "greeting": "Привет! Я Bruce Securer, security expert.\n\nБезопасность — это не опция. Проверим все уязвимости.\nХакеры не пройдут!",
        "completion": "🔐 <b>Bruce Securer</b>\n\nSecurity audit завершён. Все уязвимости закрыты.\nПродукт защищён.",
    },
    9: {
        "name": "Andy Chain",
        "emoji": "📈",
        "greeting": "Привет! Я Andy Chain, growth engineer.\n\nПора запускать! Настроим аналитику и метрики.\nБудем расти экспоненциально.",
        "completion": "📈 <b>Andy Chain</b>\n\nАналитика настроена! Метрики собираются.\nГотовы к запуску.",
    },
    10: {
        "name": "Andy Chain",
        "emoji": "📈",
        "greeting": "Я Andy Chain, финальная стадия!\n\nМасштабируем продукт и настраиваем SRE.\n99.9% uptime гарантирован.",
        "completion": "📈 <b>Andy Chain</b>\n\n🎉 Поздравляю! Продукт готов к production!\n\nВся команда AI Dream Team поработала на отлично.\nТеперь твоя очередь — завоёвывай рынок!",
    },
}

router = Router(name="approval")

# Set by run_bot so handlers can resume the graph (no custom kwargs in Aiogram)
_graph: Any = None
_default_config: dict[str, Any] = {}


async def _send_artifact_files(message: Message, file_paths: list[str]) -> None:
    """Send artifact files as documents or photos to the user."""
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists() and path.is_file():
            try:
                # Send images as photos, other files as documents
                if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                    photo = FSInputFile(file_path)
                    await message.answer_photo(photo, caption=path.name)
                else:
                    document = FSInputFile(file_path)
                    await message.answer_document(document)
            except Exception as e:
                logger.warning("failed_to_send_file", extra={"file": file_path, "error": str(e)})
                await message.answer(f"⚠️ Could not send file: {path.name}")


def _approval_keyboard(phase: int, artifact_files: list[str] | None = None) -> InlineKeyboardMarkup:
    """Inline buttons for phase approval (per PHASES_INDEX)."""
    keyboard = []
    
    # Add file buttons first (one per row) - only for non-image files
    if artifact_files:
        for file_path in artifact_files:
            file_name = Path(file_path).name
            # Skip images (they're sent as photos with caption)
            if Path(file_path).suffix.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                keyboard.append([
                    InlineKeyboardButton(text=f"📄 {file_name}", callback_data=f"file:{file_path}")
                ])
    
    # Phase 3 specific buttons (Design Refinement)
    if phase == 3:
        keyboard.extend([
            [
                InlineKeyboardButton(text="✅ APPROVE DESIGN", callback_data=f"{APPROVE}:{phase}"),
                InlineKeyboardButton(text="🔁 REFINE SCREEN", callback_data=f"refine_screen:{phase}"),
            ],
            [
                InlineKeyboardButton(text="🎨 CHANGE THEME", callback_data=f"change_theme:{phase}"),
                InlineKeyboardButton(text="📄 VIEW DOCS", callback_data=f"{VIEW_DOCS}:{phase}"),
            ],
            [InlineKeyboardButton(text="🔙 GO BACK", callback_data=f"{GO_BACK}:{phase}")],
        ])
    else:
        # Standard approval buttons for other phases
        keyboard.extend([
            [
                InlineKeyboardButton(text="✅ APPROVE", callback_data=f"{APPROVE}:{phase}"),
                InlineKeyboardButton(text="📄 VIEW DOCS", callback_data=f"{VIEW_DOCS}:{phase}"),
            ],
            [InlineKeyboardButton(text="🔙 GO BACK", callback_data=f"{GO_BACK}:{phase}")],
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start."""
    team_intro = (
        "🎭 <b>AI Venture Studio — Dream Team</b>\n\n"
        "Я собрал команду лучших экспертов мира, чтобы помочь тебе создать продукт:\n\n"
        "🍎 <b>Steve Bobs</b> — Visionary & Business\n"
        "🥗 <b>Smarty Vegan</b> — Product Manager\n"
        "🎨 <b>Johnny Vibe</b> — UI/UX Designer\n"
        "⚙️ <b>Linus Codevalds</b> — Tech Lead\n"
        "💻 <b>Dave Railsman</b> — CTO & Developer\n"
        "☁️ <b>Kelly Cloudtower</b> — DevOps & QA\n"
        "🔐 <b>Bruce Securer</b> — Security Expert\n"
        "📈 <b>Andy Chain</b> — Growth & SRE\n\n"
        "Каждый эксперт работает на своей фазе и передаёт эстафету следующему.\n\n"
        "Используй <code>/run &lt;твоя идея&gt;</code> чтобы начать!"
    )
    await message.answer(team_intro, parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help."""
    await message.answer(
        "Commands: /start, /help, /run. Use /run to start the pipeline; when a phase completes, use the inline buttons to APPROVE or VIEW DOCS.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("run"))
async def cmd_run(message: Message) -> None:
    """Start pipeline for this user; on interrupt, send approval keyboard.
    
    Usage:
      /run <your business idea>
    
    Example:
      /run Build a SaaS platform for freelancers to manage invoices and track time
    """
    if _graph is None:
        await message.answer("Bot not ready (graph not set).")
        return
    
    # Extract CEO prompt from message text (everything after "/run ")
    ceo_prompt = message.text.replace("/run", "", 1).strip() if message.text else ""
    if not ceo_prompt:
        # Show Steve Bobs greeting
        persona = PHASE_PERSONAS[1]
        await message.answer(
            f"{persona['greeting']}\n\n"
            "Пример:\n"
            "<code>/run Build a SaaS platform for freelancers to manage invoices</code>",
            parse_mode="HTML",
        )
        return
    
    thread_id = f"user_{message.from_user.id}" if message.from_user else "default"
    
    # PROTECTION: Check if already processing for this user
    if thread_id in _active_sessions:
        await message.answer(
            "⚠️ <b>У вас уже есть активная сессия!</b>\n\n"
            "Дождитесь завершения текущей фазы или используйте кнопки APPROVE/GO_BACK.",
            parse_mode=ParseMode.HTML,
        )
        return
    
    # Mark session as active
    _active_sessions.add(thread_id)
    
    # IMMEDIATE FEEDBACK - show processing message
    persona = PHASE_PERSONAS[1]
    processing_msg = await message.answer(
        f"{persona['emoji']} <b>Steve Bobs</b>\n\n"
        f"⏳ Анализирую вашу идею:\n"
        f"<i>\"{ceo_prompt[:100]}{'...' if len(ceo_prompt) > 100 else ''}\"</i>\n\n"
        f"Это займет 30-60 секунд...",
        parse_mode=ParseMode.HTML,
    )
    
    config = {**_default_config, "configurable": {"thread_id": thread_id}}
    try:
        result = await _graph.ainvoke(
            {
                "messages": [],
                "current_phase": 0,
                "approved": False,
                "ceo_prompt": ceo_prompt,
            },
            config=config,
        )
        if "__interrupt__" in result and result["__interrupt__"]:
            inter = result["__interrupt__"][0]
            payload = getattr(inter, "value", inter) or {}
            phase = payload.get("phase", 1)
            msg_text = payload.get("message", "Approve to continue.")
            artifact_files = payload.get("artifact_files", [])
            
            # Delete processing message to keep chat clean
            try:
                await processing_msg.delete()
            except Exception:
                pass  # Ignore if message already deleted or doesn't exist
            
            # Send artifact files first
            await _send_artifact_files(message, artifact_files)
            
            # Then send message with approval buttons
            await message.answer(
                msg_text, 
                reply_markup=_approval_keyboard(phase, artifact_files),
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer("Pipeline step completed (no interrupt).")
    except Exception as e:
        logger.exception("run_failed")
        await message.answer(f"❌ Run failed: {e}")
        
        # Delete processing message on error
        try:
            await processing_msg.delete()
        except Exception:
            pass
    finally:
        # Always remove from active sessions when done (success or error)
        _active_sessions.discard(thread_id)


@router.callback_query(F.data.startswith(APPROVE))
async def handle_approve(callback: CallbackQuery) -> None:
    """Resume graph with approved=True for the given phase."""
    if not callback.data or _graph is None:
        await callback.answer("Bot not ready.")
        return
    
    # IMMEDIATE FEEDBACK - answer callback first!
    await callback.answer("✅ Approved! Processing...")
    
    _, phase = callback.data.split(":", 1)
    thread_id = f"user_{callback.from_user.id}" if callback.from_user else "default"
    run_config = {**_default_config, "configurable": {"thread_id": thread_id}}

    # Show loading state
    if callback.message:
        await callback.message.edit_text(
            f"✅ Phase {phase} approved.\n\n⏳ Processing next phase...",
            reply_markup=None  # Remove buttons to prevent double-clicks
        )

    from langgraph.types import Command

    # Resume and check if next phase interrupted
    result = await _graph.ainvoke(Command(resume={"approved": True}), run_config)

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
            await callback.message.answer(
                msg_text, 
                reply_markup=_approval_keyboard(next_phase, artifact_files),
                parse_mode=ParseMode.HTML
            )


@router.callback_query(F.data.startswith(GO_BACK))
async def handle_go_back(callback: CallbackQuery) -> None:
    """Ack GO BACK (full rollback logic can be added later)."""
    await callback.answer("🔙 Go Back: Time Machine feature coming soon!", show_alert=True)


@router.callback_query(F.data.startswith(VIEW_DOCS))
async def handle_view_docs(callback: CallbackQuery) -> None:
    """Point user to per-run artifacts folder."""
    await callback.answer("📄 Opening docs info...")
    
    thread_id = f"user_{callback.from_user.id}" if callback.from_user else "default"
    artifacts_path = f"artifacts/{thread_id}/docs/"
    
    if callback.message:
        await callback.message.answer(
            f"📁 Your artifacts folder: <code>{artifacts_path}</code>\n\n"
            "📚 Factory manuals (PHASE_*.md) are in <code>/docs</code>.",
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("file:"))
async def handle_file_button(callback: CallbackQuery) -> None:
    """Resend artifact file when user clicks file button."""
    if not callback.data or not callback.message:
        await callback.answer("⚠️ No file path provided.")
        return
    
    # Immediate feedback
    await callback.answer("📄 Sending file...")
    
    # Parse file path from callback data (format: "file:/path/to/file.md")
    file_path = callback.data[5:]  # Remove "file:" prefix
    path = Path(file_path)
    
    if path.exists() and path.is_file():
        try:
            document = FSInputFile(file_path)
            await callback.message.answer_document(document)
        except Exception as e:
            logger.warning("failed_to_resend_file", extra={"file": file_path, "error": str(e)})
            await callback.message.answer(f"⚠️ Could not send file: {path.name}")
    else:
        await callback.message.answer(f"⚠️ File not found: {path.name}")


@router.callback_query(F.data.startswith("refine_screen:"))
async def handle_refine_screen(callback: CallbackQuery) -> None:
    """CEO wants to refine specific screen in Stitch design."""
    if not callback.message:
        await callback.answer("⚠️ Message context lost")
        return
    
    await callback.answer("🔁 Opening refinement mode...")
    
    await callback.message.answer(
        "🎨 <b>Johnny Vibe:</b> Отправь мне инструкцию для уточнения дизайна.\n\n"
        "<b>Примеры (по Stitch best practices):</b>\n"
        "• <code>On homepage, add search bar to header</code>\n"
        "• <code>Change primary CTA button to be larger and use brand blue</code>\n"
        "• <code>Update login screen background to light gradient</code>\n\n"
        "💡 <b>Совет:</b> Меняй 1-2 элемента за раз для лучшего результата.\n"
        "Используй UI/UX термины (button, header, navigation, card).",
        parse_mode=ParseMode.HTML,
    )
    # TODO: Set state to wait for refinement text and pass to phase_3_refine


@router.callback_query(F.data.startswith("change_theme:"))
async def handle_change_theme(callback: CallbackQuery) -> None:
    """CEO wants to change design theme (colors/fonts/borders)."""
    if not callback.message:
        await callback.answer("⚠️ Message context lost")
        return
    
    await callback.answer("🎨 Opening theme editor...")
    
    await callback.message.answer(
        "🎨 <b>Johnny Vibe:</b> Давай изменим тему дизайна!\n\n"
        "<b>Примеры изменений:</b>\n\n"
        "🎨 <b>Цвета:</b>\n"
        "• <code>Change primary color to forest green</code>\n"
        "• <code>Update theme to warm, inviting color palette</code>\n\n"
        "✍️ <b>Шрифты:</b>\n"
        "• <code>Use playful sans-serif font</code>\n"
        "• <code>Change headings to elegant serif font</code>\n\n"
        "📐 <b>Границы:</b>\n"
        "• <code>Make all buttons fully rounded corners</code>\n"
        "• <code>Add 2px solid borders to input fields</code>",
        parse_mode=ParseMode.HTML,
    )
    # TODO: Set state to wait for theme change text and pass to phase_3_theme_change


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
