from dataclasses import dataclass


@dataclass
class PostInfo:
    post_message_id: int  # ID поста, который будет скопирован в Канал
    manage_message_id: int  # ID управляющего сообщения, где все кнопки
    manage_chat_id: int  # ID чата с ботом, где всё настраивается
    channel_id: int  # ID канала
