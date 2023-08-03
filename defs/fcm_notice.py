from firebase_admin import messaging
from mipac import (
    NotificationAchievement,
    NotificationFollowRequest,
    NotificationFollow,
    NotificationReaction,
    Note,
    NotificationNote,
)

from defs.notice import achievement_map
from glover import web_domain

from fcm_init import google_app


def check_fcm_token(token: str) -> bool:
    message = messaging.Message(
        notification=messaging.Notification(
            title="Misskey Telegram Bridge",
            body="FCM Test",
        ),
        token=token,
    )
    try:
        messaging.send(message, app=google_app)
        return True
    except Exception:
        return False


def send_fcm_message(token: str, title: str, body: str, img: str = None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=img,
        ),
        token=token,
    )
    messaging.send(message, app=google_app)


def gen_image_url(url: str) -> str:
    return f"https://{web_domain}/1.jpg?url={url}"


def send_fcm_user_followed(token: str, notice: NotificationFollow):
    title = notice.user.nickname
    body = "关注了你"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_follow_request(token: str, notice: NotificationFollowRequest):
    title = notice.user.nickname
    body = "请求关注你"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_follow_request_accept(token: str, notice: NotificationFollowRequest):
    title = notice.user.nickname
    body = "接受了你的关注请求"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_achievement_earned(
    token: str,
    notice: NotificationAchievement,
):
    name, desc, note = achievement_map.get(notice.achievement, ("", "", ""))
    title = "你获得了新成就！"
    body = f"{name}：{desc} {f'- {note}' if note else ''}"
    send_fcm_message(token, title, body)


def format_notice_note(note: Note):
    text = ""
    if note.content:
        text = note.content
    if note.reply:
        text += f" RE: {note.reply.content}"
    if note.renote:
        text += f" QT: {note.renote.content}"
    if len(text) >= 100:
        text = text[:100] + "..."
    return text.strip()


def send_fcm_reaction(
    token: str,
    notice: NotificationReaction,
):
    title = notice.user.nickname
    body = f"{notice.reaction} 了你的推文\n{format_notice_note(notice.note)}"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_mention(
    token: str,
    notice: NotificationNote,
):
    title = notice.user.nickname
    body = f"提到了你\n{format_notice_note(notice.note)}"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_reply(
    token: str,
    notice: NotificationNote,
):
    title = notice.user.nickname
    body = f"回复了你\n{format_notice_note(notice.note)}"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_renote(
    token: str,
    notice: NotificationNote,
):
    title = notice.user.nickname
    body = f"转发了你的推文\n{format_notice_note(notice.note)}"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)


def send_fcm_quote(
    token: str,
    notice: NotificationNote,
):
    title = notice.user.nickname
    body = f"引用了你的推文\n{format_notice_note(notice.note)}"
    image = gen_image_url(notice.user.avatar_url)
    send_fcm_message(token, title, body, image)
