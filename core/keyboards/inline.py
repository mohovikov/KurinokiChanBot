from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


def get_proposal_keyboard(group_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="💚 Согласен", callback_data=f"marry_accept:{group_id}"
        ),
        InlineKeyboardButton(
            text="💔 Отказать", callback_data=f"marry_reject:{group_id}"
        ),
    )
    builder.adjust(2)
    return builder.as_markup()
