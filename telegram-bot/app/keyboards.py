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


def get_excursions_pagination_keyboard(offset: int, has_next: bool, is_first: bool = False) -> InlineKeyboardMarkup:
    """Keyboard for paginating through excursions (5 items per page)"""
    buttons = []
    row = []
    
    # Previous button (not on first page)
    if not is_first:
        prev_offset = max(0, offset - 5)
        row.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"excursions_{prev_offset}"))
    
    # Next button (if there are more items)
    if has_next:
        next_offset = offset + 5
        row.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"excursions_{next_offset}"))
    
    if row:
        buttons.append(row)
    
    # Back to menu button
    buttons.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])
