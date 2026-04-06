import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services import backend_service
from app.keyboards import (
    get_main_menu_keyboard,
    get_excursions_pagination_keyboard,
    get_back_to_menu_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

# FSM States for password setup
class PasswordSetup(StatesGroup):
    waiting_for_password = State()
    waiting_for_password_confirm = State()


# Store user data in memory (in production, use Redis or database)
user_cache = {}


def get_user_cache(user_id: int) -> dict:
    """Get or initialize user cache"""
    if user_id not in user_cache:
        user_cache[user_id] = {
            "backend_user": None,
        }
    return user_cache[user_id]


async def ensure_user_registered(user_id: int, username: str = None) -> dict:
    """Ensure user is registered in backend"""
    cache = get_user_cache(user_id)
    if cache["backend_user"] is None:
        # Use username if available, otherwise use user_id
        telegram_alias = username if username else f"user_{user_id}"
        # Remove @ prefix if present
        telegram_alias = telegram_alias.lstrip('@')
        cache["backend_user"] = await backend_service.get_or_create_user(user_id, telegram_alias)
    return cache["backend_user"]


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user = await ensure_user_registered(message.from_user.id, message.from_user.username)
    
    # Check if user has password set
    if not user.get("password_protected"):
        # First time user - ask to set password
        await state.set_state(PasswordSetup.waiting_for_password)
        welcome_text = (
            f"🎯 **Welcome to TourStats Bot!**\n\n"
            f"I'm your AI assistant for tour guides. "
            f"Simply send me messages about your excursions and I'll:\n\n"
            f"📝 Extract statistics from your descriptions\n"
            f"📊 Save and analyze your tour data\n"
            f"📈 Find correlations and insights\n\n"
            f"🔐 **First, let's set up a password for your account.**\n"
            f"This password is required to access your data from the web app.\n"
            f"Please send me a password (at least 4 characters):"
        )
    else:
        # Existing user with password
        welcome_text = (
            f"🎯 **Welcome back to TourStats Bot!**\n\n"
            f"I'm your AI assistant for tour guides. "
            f"Simply send me messages about your excursions and I'll:\n\n"
            f"📝 Extract statistics from your descriptions\n"
            f"📊 Save and analyze your tour data\n"
            f"📈 Find correlations and insights\n\n"
            f"Use the menu below to view your statistics, or just chat with me about your tours!"
        )

    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Show main menu"""
    await ensure_user_registered(message.from_user.id, message.from_user.username)
    await message.answer("📱 **Main Menu**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help message"""
    help_text = (
        "📖 **TourStats Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/menu - Show main menu\n"
        "/help - Show this help message\n"
        "/setpassword - Set or change your password\n"
        "/removepassword - Remove password protection\n\n"
        "**How to use:**\n"
        "1. Send me a message about your excursion\n"
        "2. I'll extract statistics and save them\n"
        "3. Use the menu to view your data\n\n"
        "**Example messages:**\n"
        "• 'Just finished a tour with 15 people, mostly young adults around 25'\n"
        "• 'Had 20 tourists, average age 30, very interested in education history'\n"
        "• 'Excursion #26 actually had 25 tourists' (to update existing data)"
    )

    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("setpassword"))
async def cmd_set_password(message: Message, state: FSMContext):
    """Start password setup process"""
    await state.set_state(PasswordSetup.waiting_for_password)
    await message.answer(
        "🔐 **Set New Password**\n\n"
        "Please send me a new password (at least 4 characters).\n"
        "This password will be required to access your data from the web app.\n\n"
        "Send /cancel to cancel."
    )


@router.message(Command("removepassword"))
async def cmd_remove_password(message: Message, state: FSMContext):
    """Remove password protection"""
    try:
        user = await ensure_user_registered(message.from_user.id, message.from_user.username)
        telegram_alias = user["telegram_alias"]
        
        result = await backend_service.remove_password(telegram_alias)
        
        # Update cache
        user_cache[message.from_user.id]["backend_user"]["password_protected"] = False
        
        await state.clear()
        await message.answer("✅ **Password protection removed!**\n\nYour web data is now accessible without a password.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error removing password: {e}")
        await message.answer("❌ Error removing password. Please try again.")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await message.answer("❌ Operation cancelled.", reply_markup=get_main_menu_keyboard())


@router.message(PasswordSetup.waiting_for_password)
async def process_password_setup(message: Message, state: FSMContext):
    """Process password setup"""
    password = message.text.strip()
    
    if len(password) < 4:
        await message.answer("❌ Password must be at least 4 characters. Please try again:")
        return
    
    # Store password and ask for confirmation
    await state.update_data(password=password)
    await state.set_state(PasswordSetup.waiting_for_password_confirm)
    
    await message.answer(
        "🔐 **Confirm Password**\n\n"
        "Please send the same password again to confirm:\n\n"
        "(Send /cancel to cancel)"
    )


@router.message(PasswordSetup.waiting_for_password_confirm)
async def process_password_confirm(message: Message, state: FSMContext):
    """Process password confirmation"""
    confirm_password = message.text.strip()
    state_data = await state.get_data()
    password = state_data.get("password", "")
    
    if password != confirm_password:
        await message.answer("❌ Passwords don't match. Please send the password again:")
        await state.set_state(PasswordSetup.waiting_for_password)
        return
    
    # Set password
    try:
        user = await ensure_user_registered(message.from_user.id, message.from_user.username)
        telegram_alias = user["telegram_alias"]
        
        result = await backend_service.set_password(telegram_alias, password)
        
        # Update cache
        user_cache[message.from_user.id]["backend_user"]["password_protected"] = True
        
        await state.clear()
        await message.answer(
            "✅ **Password set successfully!**\n\n"
            f"This password will be required when accessing your data from the web app.\n\n"
            f"Use the menu below to view your statistics!",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error setting password: {e}")
        await message.answer("❌ Error setting password. Please try again.")
        await state.clear()


@router.message()
async def handle_chat_message(message: Message, state: FSMContext):
    """Handle regular chat messages - forward to AI backend"""
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return
    
    # Check if user is in password setup mode
    current_state = await state.get_state()
    if current_state:
        # User is in FSM state, let the FSM handlers process
        return
    
    try:
        user = await ensure_user_registered(message.from_user.id, message.from_user.username)
        
        # Send message to backend for AI processing
        result = await backend_service.send_message_to_backend(user["id"], message.text)
        
        # Get AI response
        ai_response = result.get("ai_response", "I've processed your message.")
        
        # Add confirmation messages if applicable
        confirmations = []
        if result.get("excursion_stored"):
            confirmations.append("✅ Excursion data saved!")
        if result.get("excursion_updated"):
            updated_id = result.get("updated_excursion_id")
            confirmations.append(f"📝 Excursion #{updated_id} updated!")
        
        # Build response
        response_parts = []
        if confirmations:
            response_parts.extend(confirmations)
            response_parts.append("")  # Empty line
        response_parts.append(ai_response)
        
        response_text = "\n".join(response_parts)
        
        await message.answer(response_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.answer(
            "❌ Sorry, I encountered an error processing your message. Please try again."
        )


@router.callback_query(lambda c: c.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery):
    """Handle back to menu button"""
    await callback.message.edit_text("📱 **Main Menu**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "stats_refresh")
async def callback_stats_refresh(callback: CallbackQuery):
    """Handle refresh statistics button"""
    user = await ensure_user_registered(callback.from_user.id, callback.from_user.username)

    # Clear cache
    user_cache[callback.from_user.id]["backend_user"] = None

    await callback.message.edit_text(
        "🔄 Data refreshed! Use the menu to view your updated statistics.",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer("Data refreshed!")


@router.callback_query(lambda c: c.data == "stats_overview")
async def callback_stats_overview(callback: CallbackQuery):
    """Handle statistics overview button"""
    try:
        user = await ensure_user_registered(callback.from_user.id, callback.from_user.username)

        await callback.answer()

        stats = await backend_service.get_statistics(user["id"])

        if stats["total_excursions"] == 0:
            text = (
                "📊 **Your Statistics**\n\n"
                "No excursions recorded yet.\n"
                "Send me a message about your tour to get started!"
            )
        else:
            text = (
                f"📊 **Your Statistics**\n\n"
                f"📈 **Total Excursions:** {stats['total_excursions']}\n"
                f"👥 **Avg Tourists/Tour:** {stats['avg_tourists_per_excursion']:.1f}\n"
                f"🎂 **Avg Tourist Age:** {stats['avg_age_all']:.1f} years\n"
                f"⚡ **Avg Energy Before:** {stats['avg_vivacity_before']*100:.0f}%\n"
                f"🔥 **Avg Energy After:** {stats['avg_vivacity_after']*100:.0f}%\n"
                f"💻 **Avg IT Interest:** {stats['avg_interest_in_it']*100:.0f}%\n\n"
                f"🏷️ **Top Interests:**\n"
                f"{', '.join(stats['top_interests'][:5]) if stats['top_interests'] else 'None yet'}"
            )

        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_back_to_menu_keyboard())

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        await callback.message.answer(
            "❌ Error loading statistics. Please try again.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()


@router.callback_query(lambda c: c.data == "stats_correlations")
async def callback_stats_correlations(callback: CallbackQuery):
    """Handle correlations button"""
    try:
        user = await ensure_user_registered(callback.from_user.id, callback.from_user.username)

        await callback.answer()

        corr = await backend_service.get_correlations(user["id"])

        if "message" in corr:
            text = (
                f"📈 **Correlations**\n\n"
                f"{corr['message']}\n"
                f"Current excursions: {corr.get('current_count', 0)}"
            )
        else:
            summary = corr.get("summary", {})
            top_corrs = summary.get("most_interesting_correlations", [])

            text = "📈 **Key Insights**\n\n"

            # Add summary
            text += f"👥 Avg Group Size: {summary.get('avg_group_size', 0):.1f}\n"
            text += f"⚡ Avg Energy Boost: +{summary.get('avg_vivacity_boost', 0)*100:.0f}%\n\n"

            if top_corrs:
                text += "**Top Correlations Found:**\n\n"
                for i, corr_item in enumerate(top_corrs[:3], 1):
                    text += f"{i}. **{corr_item['label']}**\n"
                    text += f"   {corr_item['interpretation']}\n\n"
            else:
                text += "No significant correlations found yet. Add more excursions!"

        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_back_to_menu_keyboard())

    except Exception as e:
        logger.error(f"Error getting correlations: {e}")
        await callback.message.answer(
            "❌ Error loading correlations. Please try again.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()


async def send_excursions_page(callback: CallbackQuery, offset: int):
    """Send a page of excursions"""
    user = await ensure_user_registered(callback.from_user.id, callback.from_user.username)

    # Fetch excursions for this page (5 items per page)
    excursions = await backend_service.get_excursions(user["id"], offset=offset, limit=5)

    if not excursions:
        text = "📋 No excursions found."
        keyboard = get_back_to_menu_keyboard()
    else:
        # Check if there are more pages by fetching 1 extra item
        next_check = await backend_service.get_excursions(user["id"], offset=offset + 5, limit=1)
        has_next = len(next_check) > 0
        is_first_page = (offset == 0)

        # Format excursions text
        text = f"📋 **Excursions** (showing {offset + 1}-{offset + len(excursions)})\n\n"

        for i, exc in enumerate(excursions, start=1):
            interests = exc.get("interests_list", "None")
            text += (
                f"**{offset + i}.** #{exc['id']} | {exc['number_of_tourists']} tourists | Age {exc['average_age']:.0f}\n"
                f"⚡ {exc['vivacity_before']*100:.0f}% → {exc['vivacity_after']*100:.0f}% | "
                f"💻 IT: {exc['interest_in_it']*100:.0f}%\n"
                f"🏷️ {interests}\n\n"
            )

        keyboard = get_excursions_pagination_keyboard(offset, has_next, is_first_page)

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "stats_excursions")
async def callback_stats_excursions(callback: CallbackQuery):
    """Handle excursions list button - initial load with offset 0"""
    try:
        await callback.answer()
        await send_excursions_page(callback, offset=0)

    except Exception as e:
        logger.error(f"Error getting excursions: {e}")
        await callback.message.answer(
            "❌ Error loading excursions. Please try again.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()


@router.callback_query(lambda c: c.data.startswith("excursions_"))
async def callback_excursions_pagination(callback: CallbackQuery):
    """Handle excursions pagination"""
    try:
        parts = callback.data.split("_")
        offset = int(parts[1])
        await callback.answer()
        await send_excursions_page(callback, offset=offset)

    except Exception as e:
        logger.error(f"Error getting excursions: {e}")
        await callback.message.answer(
            "❌ Error loading excursions. Please try again.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer()
