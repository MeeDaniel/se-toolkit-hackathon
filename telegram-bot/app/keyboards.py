from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard with statistics options"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 My Statistics", callback_data="stats_overview"),
        ],
        [
            InlineKeyboardButton(text="📈 Correlations", callback_data="stats_correlations"),
        ],
        [
            InlineKeyboardButton(text="📋 Recent Excursions", callback_data="stats_excursions"),
        ],
        [
            InlineKeyboardButton(text="🔄 Refresh Data", callback_data="stats_refresh"),
        ],
    ])


def get_excursions_pagination_keyboard(offset: int, has_more: bool) -> InlineKeyboardMarkup:
    """Keyboard for paginating through excursions"""
    buttons = []
    if offset > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"excursions_{max(0, offset - 10)}"))
    if has_more:
        buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"excursions_{offset + 10}"))
    
    buttons.append(InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu"))
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])
