from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

commands_help_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Помощь по командам", callback_data="help_commands"
            )
        ]
    ]
)

back_to_mainpage_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Вернуться на главную", callback_data="start")]
    ]
)
