import asyncio
import logging
import sqlite3
import random
import difflib
import os
from datetime import datetime, timedelta
from typing import List, Optional, Union

# --- LOCALIZATION ---
LEXICON = {
    'ru': {
        'start': "👋 Привет, {name}!\n\n🎬 Добро пожаловать в бот для поиска фильмов и сериалов.\n👨‍💻 Разработчик: @honex_napike\n\nПожалуйста, выберите язык интерфейса:",
        'main_menu': "🎬 Главное меню:",
        'btn_movies': "🎬 Фильмы",
        'btn_series': "📺 Сериалы",
        'btn_favs': "❤️ Избранное",
        'btn_history': "🕒 История",
        'btn_random': "🎁 Случайный фильм",
        'btn_stats': "📊 Статистика",
        'btn_back': "🏠 Главное меню",
        'search_prompt': "🔍 Введи название или код фильма для поиска:",
        'series_list': "🎬 Список доступных сериалов:",
        'favs_empty': "❤️ Список избранного пуст.",
        'history_empty': "🕒 История просмотров пуста.",
        'sub_required': "⚠️ Для использования бота необходимо подписаться на следующие каналы:",
        'admin_panel': "🔐 Админ-панель:",
        'stats_text': "📊 **Статистика бота:**\n\n👥 Пользователей: {u}\n🎬 Фильмов: {m}\n📺 Сериалов: {s}",
        'fav_added': "❤️ Добавлено в избранное",
        'broadcast_announcement': "📣 **ОБЪЯВЛЕНИЕ**",
        'fav_removed': "💔 Удалено из избранного",
        'btn_watch': "🎬 Смотреть",
        'btn_remove': "❌ Удалить",
        'lang_selected': "✅ Язык изменен на Русский!",
        'not_found': "❌ По запросу '{q}' ничего не найдено.",
        'results_title': "🔎 Результаты поиска:",
        'fuzzy_label': "🤔 Возможно: ",
        'empty_seasons': "⚠️ У этого сериала ещё нет сезонов.",
        'empty_episodes': "⚠️ В этом сезоне ещё нет серий.",
        'season_label': "📅 Сезон ",
        'episode_label': "🎞 Серия ",
        'genre_label': "🎭 Жанр",
        'views_label': "👁 Просмотров",
        'movie_label': "Фильм",
        'series_label': "Сериал",
        'season_select': "📅 Выберите сезон:",
        'episode_select': "🎞 Выберите серию:",
        'empty_content': "🎬 Контент пока не добавлен.",
        'btn_check': "✅ Проверить подписку",
        'sub_error': "❌ Вы всё ещё не подписаны!",
        'new_content_alert': "🆕 **Новинка: {title}**\n\n📝 {desc}\n\n🎭 Жанр: {genre}\n\n🎬 Смотрите прямо сейчас в боте!",
        'btn_watch_now': "🎬 Смотреть",
        'btn_next': "➡️ Вперед",
        'btn_prev': "⬅️ Назад",
        'page_label': "Страница {p}",
        'btn_search_cat': "🔍 Поиск",
        'genre_🍿 Экшен': "🍿 Экшен",
        'genre_🤣 Комедия': "🤣 Комедия",
        'genre_😱 Ужасы': "😱 Ужасы",
        'genre_🎭 Драма': "🎭 Драма",
        'genre_🌌 Фантастика': "🌌 Фантастика",
        'genre_🔪 Триллер': "🔪 Триллер",
        'genre_🧸 Мультфильм': "🧸 Мультфильм",
        'genre_🕵️ Детектив': "🕵️ Детектив",
        'admin_auto_sub_shared': "🤖 Бот добавлен в канал '{title}' (ID: {id})\nВыберите тип подписки:",
        'admin_auto_sub_error': "⚠️ Ошибка получения информации о канале: {e}",
        'channel_post_footer': "🎬 Смотрите прямо сейчас в боте!",
        'inline_watch_in_bot': "Смотреть в боте",
        'btn_backup_caption': "📦 **Database Backup**\n📅 {d}",
        'backup_error': "❌ Файл базы данных не найден.",
        'admin_auto_sub_success': "✅ **Канал автоматически добавлен в список подписок!**\n\n📢 Название: **{title}**\n📢 ID: `{id}`\n🔗 Ссылка: {link}",
        'admin_bot_added_member': "🔔 Бот добавлен в канал **{title}** как участник.\nЧтобы он автоматически добавился в список подписок, назначьте его **администратором**.",
        'btn_add_movie': "➕ Добавить фильм",
        'btn_add_series': "➕ Добавить сериал",
        'btn_broadcast': "📣 Рассылка",
        'btn_sub_mgr': "⛓ Подписки",
        'btn_manage_content': "📁 Контент",
        'btn_movie_channel': "📺 Канал бота",
        'btn_full_stats': "📈 Статистика",
        'btn_delete': "🗑 Удалить",
        'btn_rate': "⭐ Оценить",
        'btn_share': "🔗 Поделиться",
        'btn_subscribe': "🔔 Уведомлять о новых сериях",
        'btn_unsubscribe': "🔕 Не уведомлять",
        'btn_top_movies': "🔥 Топ-10 фильмов",
        'btn_top_series': "🔝 Топ-10 сериалов",
        'rating_prompt': "✨ Оцените контент по 10-балльной шкале:",
        'rating_success': "✅ Спасибо! Ваша оценка: {r}",
        'sub_success': "🔔 Вы подписались на обновления этого сериала!",
        'unsub_success': "🔕 Уведомления отключены.",
        'new_episode_alert': "🆕 В сериале **{title}** вышла новая серия!\n\nСмотрите скорее в боте 🍿",
        'top_title': "🏆 **ТОП-10 {t}**\n\n",
        'rating_label': "⭐️ Рейтинг",
        'admin_stats_full_msg': "📈 **Полная статистика:**\n\n👥 Пользователи: **{u}**\n🎬 Фильмы: **{m}**\n📺 Сериалы: **{s}**\n\n👁 Всего просмотров: **{v}**\n❤️ Всего в избранном: **{f}**\n\n📅 Срез: {d}",
        'admin_manage_content_msg': "📁 **Управление контентом:**\nВыберите категорию или используйте поиск:",
        'admin_manage_movies_title': "🎬 **Управление фильмами (Всего: {total}):**",
        'admin_manage_series_title': "📺 **Управление сериалами (Всего: {total}):**",
        'admin_search_prompt': "🔎 Введите название или код контента для поиска:",
        'admin_movie_channel_setup_msg': "🎬 **Настройка Кино-канала**\n\n{id_info}\n\nЧтобы изменить канал, отправьте его **ID** или **перешлите сообщение** из этого канала мне.",
        'admin_add_movie_title_prompt': "⌨️ Введите название фильма:",
        'admin_add_movie_desc_prompt': "⌨️ Введите описание фильма:",
        'admin_add_movie_genre_prompt': "🎭 Выберите жанр фильма:",
        'admin_add_movie_preview_prompt': "✅ Выбран жанр: {genre}. \n🖼 Отправьте превью (фото) для фильма:",
        'admin_add_movie_file_prompt': "🎥 Отправьте видео-файл фильма:",
        'admin_add_movie_code_prompt': "⌨️ Введите уникальный код для фильма (например, 101):",
        'admin_add_movie_success_msg': "✅ Фильм успешно добавлен!",
        'broadcast_prompt_msg': "📣 Введите текст рассылки:",
        'broadcast_done_msg': "✅ Рассылка завершена! Получили {count} пользователей.",
        'sub_mgr_title_msg': "⚙️ Управление обязательными подписками:",
        'btn_add_sub_manual': "➕ Добавить вручную (ID)",
        'btn_add_sub_auto': "➕ Добавить канал (Бот -> Админ)",
        'admin_manage_movie_item_msg': "🎬 **Фильм: {title}**\nКод: {id}\n\nЧто вы хотите сделать?",
        'admin_manage_series_item_msg': "📺 **Сериал: {title}**\n\nЧто вы хотите сделать?",
        'btn_delete': "🗑 Удалить",
        'admin_delete_movie_confirm': "✅ Фильм удален",
        'admin_delete_series_confirm': "✅ Сериал и все его сезоны/эпизоды удалены",
        'admin_add_series_title_prompt': "⌨️ Введите название сериала:",
        'admin_add_series_desc_prompt': "⌨️ Введите описание сериала:",
        'admin_add_series_success_msg': "✅ Сериал '{title}' создан! Теперь добавьте сезон. Введите номер сезона (число):",
        'admin_add_season_prompt': "✅ Сезон {num} добавлен! Теперь введите номер серии (число):",
        'admin_add_episode_file_prompt': "🎥 Отправьте видео-файл серии:",
        'admin_add_episode_success_msg': "✅ Серия добавлена! Добавить еще одну? Просто отправьте номер новой серии или напишите /start для выхода.",
        'admin_add_sub_id_prompt': "⌨️ Введите ID канала (например, -100...):",
        'admin_add_sub_name_prompt': "⌨️ Введите название канала:",
        'admin_add_sub_type_prompt': "📝 Выберите тип канала:",
        'btn_type_public': "🌐 Публичный",
        'btn_type_private': "🔒 Приватный (по заявке)",
        'admin_add_sub_link_prompt': "⌨️ Введите ссылку на канал (инвайт-ссылка):",
        'admin_add_sub_success': "✅ Канал добавлен в список обязательных!",
        'admin_remove_sub_confirm': "✅ Канал удален",
        'admin_movie_channel_id_info': "Текущий ID: `{id}`",
        'admin_movie_channel_not_set': "Канал не установлен.",
        'admin_movie_channel_set_success': "✅ Кино-канал успешно установлен: `{id}`",
        'admin_movie_channel_error': "⚠️ Пожалуйста, введите корректный ID или перешлите сообщение из канала.",
        'btn_vip': "💎 VIP Подписка",
        'vip_menu': "💎 **VIP Подписка**\n\nVIP-статус дает:\n✅ Просмотр без обязательных подписок\n✅ Ранний доступ к новинкам\n✅ Отсутствие рекламы\n\nВыберите срок подписки:",
        'vip_price_item': "{months} мес. — {price} UZS",
        'vip_price_1year': "1 год — {price} UZS",
        'vip_select_method': "💳 Выберите способ оплаты:",
        'vip_card_info': "💳 **Оплата картой (UZCARD/HUMO)**\n\nПереведите **{price} UZS** на карту:\n`{card}`\n\nПосле оплаты отправьте **скриншот чека** боту. Админ проверит и подтвердит оплату.",
        'vip_receipt_received': "✅ Чек получен! Ожидайте подтверждения администратором.",
        'vip_stars_info': "🌟 **Оплата через Telegram Stars**\n\nСтоимость: {price} Stars",
        'admin_new_payment': "🔔 **Новая оплата!**\n\nПользователь: @{username} ({id})\nТариф: {plan}\nСумма: {price} UZS\nМетод: {method}",
        'vip_activated': "✅ **VIP-подписка активирована!**\nСрок действия до: {date}\nПриятного просмотра! 🍿",
        'vip_rejected': "❌ Ваша оплата была отклонена администратором.",
        'admin_vip_settings_msg': "💎 **Настройки VIP**\n\nЗдесь вы можете изменить цены и платежные реквизиты.",
        'btn_vip_prices': "💰 Изменить цены",
        'btn_vip_merchants': "💳 Настройка карт/мерчантов",
        'btn_vip_history': "📜 История платежей",
        'sub_required_vip': "⚠️ Для использования бота необходимо подписаться на каналы ИЛИ приобрести VIP подписку (без подписок навсегда).",
        'btn_buy_vip': "💎 Купить VIP",
        'vip_uzs': "сум"
    },
    'en': {
        'start': "👋 Hello, {name}!\n\n🎬 Welcome to the Movies & Series bot.\n👨‍💻 Developer: @honex_napike\n\nPlease select your interface language:",
        'main_menu': "🎬 Main Menu:",
        'btn_movies': "🎬 Movies",
        'btn_series': "📺 Series",
        'btn_favs': "❤️ Favorites",
        'btn_history': "🕒 History",
        'btn_random': "🎁 Random Movie",
        'btn_stats': "📊 Statistics",
        'btn_back': "🏠 Main Menu",
        'search_prompt': "🔍 Enter a title or code to search:",
        'series_list': "🎬 Available Series:",
        'favs_empty': "❤️ Your Favorites list is empty.",
        'history_empty': "🕒 Your History is empty.",
        'sub_required': "⚠️ You must subscribe to the following channels to use the bot:",
        'admin_panel': "🔐 Admin Panel:",
        'stats_text': "📊 **Bot Statistics:**\n\n👥 Users: {u}\n🎬 Movies: {m}\n📺 Series: {s}",
        'fav_added': "❤️ Added to Favorites",
        'broadcast_announcement': "📣 **ANNOUNCEMENT**",
        'fav_removed': "💔 Removed from Favorites",
        'btn_watch': "🎬 Watch",
        'btn_remove': "❌ Remove",
        'lang_selected': "✅ Language set to English!",
        'not_found': "❌ Nothing found for '{q}'.",
        'results_title': "🔎 Search Results:",
        'fuzzy_label': "🤔 Maybe: ",
        'empty_seasons': "⚠️ No seasons available for this series.",
        'empty_episodes': "⚠️ No episodes available in this season.",
        'season_label': "📅 Season ",
        'episode_label': "🎞 Episode ",
        'genre_label': "🎭 Genre",
        'views_label': "👁 Views",
        'movie_label': "Movie",
        'series_label': "Series",
        'season_select': "📅 Select Season:",
        'episode_select': "🎞 Select Episode:",
        'empty_content': "🎬 Content not added yet.",
        'btn_check': "✅ Check Subscription",
        'sub_error': "❌ You are still not subscribed!",
        'new_content_alert': "🆕 **New: {title}**\n\n📝 {desc}\n\n🎭 Genre: {genre}\n\n🎬 Watch now in the bot!",
        'btn_watch_now': "🎬 Watch",
        'btn_next': "➡️ Next",
        'btn_prev': "⬅️ Previous",
        'page_label': "Page {p}",
        'btn_search_cat': "🔍 Search",
        'genre_🍿 Экшен': "🍿 Action",
        'genre_🤣 Комедия': "🤣 Comedy",
        'genre_😱 Ужасы': "😱 Horror",
        'genre_🎭 Драма': "🎭 Drama",
        'genre_🌌 Фантастика': "🌌 Sci-Fi",
        'genre_🔪 Триллер': "🔪 Thriller",
        'genre_🧸 Мультфильм': "🧸 Cartoon",
        'genre_🕵️ Детектив': "🕵️ Detective",
        'admin_auto_sub_shared': "🤖 Bot added to channel '{title}' (ID: {id})\nSelect subscription type:",
        'admin_auto_sub_error': "⚠️ Error getting channel info: {e}",
        'channel_post_footer': "🎬 Watch now in the bot!",
        'inline_watch_in_bot': "Watch in Bot",
        'btn_backup_caption': "📦 **Database Backup**\n📅 {d}",
        'backup_error': "❌ Database file not found.",
        'admin_auto_sub_success': "✅ **Channel automatically added to sub list!**\n\n📢 Title: **{title}**\n🆔 ID: `{id}`\n🔗 Link: {link}",
        'admin_bot_added_member': "🔔 Bot added to channel **{title}** as a member.\nTo add it to auto-subscriptions, make it an **administrator**.",
        'btn_add_movie': "➕ Add Movie",
        'btn_add_series': "➕ Add Series",
        'btn_broadcast': "📣 Broadcast",
        'btn_sub_mgr': "⛓ Subscriptions",
        'btn_manage_content': "📁 Content",
        'btn_movie_channel': "📺 Bot Channel",
        'btn_full_stats': "📈 Statistics",
        'btn_delete': "🗑 Delete",
        'btn_rate': "⭐ Rate",
        'btn_share': "🔗 Share",
        'btn_subscribe': "🔔 Notify about new episodes",
        'btn_unsubscribe': "🔕 Mute notifications",
        'btn_top_movies': "🔥 Top-10 Movies",
        'btn_top_series': "🔝 Top-10 Series",
        'rating_prompt': "✨ Rate this content on a 10-point scale:",
        'rating_success': "✅ Thank you! Your rating: {r}",
        'sub_success': "🔔 You have subscribed to updates for this series!",
        'unsub_success': "🔕 Notifications disabled.",
        'new_episode_alert': "🆕 A new episode has been released for **{title}**!\n\nWatch it now in the bot 🍿",
        'top_title': "🏆 **TOP-10 {t}**\n\n",
        'rating_label': "⭐️ Rating",
        'admin_stats_full_msg': "📈 **Full Statistics:**\n\n👥 Users: **{u}**\n🎬 Movies: **{m}**\n📺 Series: **{s}**\n\n👁 Total Views: **{v}**\n❤️ Total Favorites: **{f}**\n\n📅 Date: {d}",
        'admin_manage_content_msg': "📁 **Manage Content:**\nSelect category or use search:",
        'admin_manage_movies_title': "🎬 **Movies Management (Total: {total}):**",
        'admin_manage_series_title': "📺 **Series Management (Total: {total}):**",
        'admin_search_prompt': "🔎 Enter title or code to search content:",
        'admin_movie_channel_setup_msg': "🎬 **Movie Channel Setup**\n\n{id_info}\n\nTo change the channel, send its **ID** or **forward a message** from it to me.",
        'admin_add_movie_title_prompt': "⌨️ Enter movie title:",
        'admin_add_movie_desc_prompt': "⌨️ Enter movie description:",
        'admin_add_movie_genre_prompt': "🎭 Select movie genre:",
        'admin_add_movie_preview_prompt': "✅ Genre selected: {genre}. \n🖼 Send preview (photo) for the movie:",
        'admin_add_movie_file_prompt': "🎥 Send video file for the movie:",
        'admin_add_movie_code_prompt': "⌨️ Enter unique code for the movie (e.g., 101):",
        'admin_add_movie_success_msg': "✅ Movie successfully added!",
        'broadcast_prompt_msg': "📣 Enter broadcast text:",
        'broadcast_done_msg': "✅ Broadcast completed! Received by {count} users.",
        'sub_mgr_title_msg': "⚙️ Mandatory Subscriptions Management:",
        'btn_add_sub_manual': "➕ Add Manually (ID)",
        'btn_add_sub_auto': "➕ Add Channel (Bot -> Admin)",
        'admin_manage_movie_item_msg': "🎬 **Movie: {title}**\nCode: {id}\n\nWhat do you want to do?",
        'admin_manage_series_item_msg': "📺 **Series: {title}**\n\nWhat do you want to do?",
        'btn_delete': "🗑 Delete",
        'admin_delete_movie_confirm': "✅ Movie deleted",
        'admin_delete_series_confirm': "✅ Series and all its seasons/episodes deleted",
        'admin_add_series_title_prompt': "⌨️ Enter series title:",
        'admin_add_series_desc_prompt': "⌨️ Enter series description:",
        'admin_add_series_success_msg': "✅ Series '{title}' created! Now add a season. Enter season number (digit):",
        'admin_add_season_prompt': "✅ Season {num} added! Now enter episode number (digit):",
        'admin_add_episode_file_prompt': "🎥 Send video file for the episode:",
        'admin_add_episode_success_msg': "✅ Episode added! Add another one? Just send new episode number or type /start to exit.",
        'admin_add_sub_id_prompt': "⌨️ Enter channel ID (e.g., -100...):",
        'admin_add_sub_name_prompt': "⌨️ Enter channel name:",
        'admin_add_sub_type_prompt': "📝 Select channel type:",
        'btn_type_public': "🌐 Public",
        'btn_type_private': "🔒 Private (by request)",
        'admin_add_sub_link_prompt': "⌨️ Enter channel link (invite link):",
        'admin_add_sub_success': "✅ Channel added to mandatory list!",
        'admin_remove_sub_confirm': "✅ Channel removed",
        'admin_movie_channel_id_info': "Current ID: `{id}`",
        'admin_movie_channel_not_set': "Channel not set.",
        'admin_movie_channel_set_success': "✅ Movie channel successfully set: `{id}`",
        'admin_movie_channel_error': "⚠️ Please enter a valid ID or forward a message from the channel.",
        'btn_vip': "💎 VIP Subscription",
        'vip_menu': "💎 **VIP Subscription**\n\nVIP status gives:\n✅ Viewing without mandatory subscriptions\n✅ Early access to new releases\n✅ No ads\n\nSelect subscription period:",
        'vip_price_item': "{months} months — {price} UZS",
        'vip_price_1year': "1 year — {price} UZS",
        'vip_select_method': "💳 Select payment method:",
        'vip_card_info': "💳 **Card Payment (UZCARD/HUMO)**\n\nTransfer **{price} UZS** to card:\n`{card}`\n\nAfter payment, send a **screenshot of the receipt** to the bot. Admin will check and confirm the payment.",
        'vip_receipt_received': "✅ Receipt received! Waiting for admin confirmation.",
        'vip_stars_info': "🌟 **Telegram Stars Payment**\n\nPrice: {price} Stars",
        'admin_new_payment': "🔔 **New Payment!**\n\nUser: @{username} ({id})\nPlan: {plan}\nPrice: {price} UZS\nMethod: {method}",
        'vip_activated': "✅ **VIP Subscription Activated!**\nValid until: {date}\nEnjoy watching! 🍿",
        'vip_rejected': "❌ Your payment was rejected by the admin.",
        'admin_vip_settings_msg': "💎 **VIP Settings**\n\nHere you can change prices and payment details.",
        'btn_vip_prices': "💰 Change Prices",
        'btn_vip_merchants': "💳 Configure Cards/Merchants",
        'btn_vip_history': "📜 Payment History",
        'sub_required_vip': "⚠️ To use the bot, you must subscribe to channels OR purchase a VIP subscription.",
        'btn_buy_vip': "💎 Buy VIP",
        'vip_uzs': "UZS"
    },
    'uz': {
        'start': "👋 Salom, {name}!\n\n🎬 Filmlar va Seriallar botiga xush kelibsiz.\n👨‍💻 Dasturchi: @honex_napike\n\nIltimos, interfeys tilini tanlang:",
        'main_menu': "🎬 Asosiy Menyu:",
        'btn_movies': "🎬 Filmlar",
        'btn_series': "📺 Seriallar",
        'btn_favs': "❤️ Sevimlilar",
        'btn_history': "🕒 Tarix",
        'btn_random': "🎁 Tasodifiy film",
        'btn_stats': "📊 Statistika",
        'btn_back': "🏠 Asosiy Menyu",
        'search_prompt': "🔍 Qidirish uchun nom yoki kodni kiriting:",
        'series_list': "🎬 Mavjud seriallar ro'yxati:",
        'favs_empty': "❤️ Sevimlilar ro'yxati bo'sh.",
        'history_empty': "🕒 Ko'rishlar tarixi bo'sh.",
        'sub_required': "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
        'admin_panel': "🔐 Admin Panel:",
        'stats_text': "📊 **Bot statistikasi:**\n\n👥 Foydalanuvchilar: {u}\n🎬 Filmlar: {m}\n📺 Seriallar: {s}",
        'fav_added': "❤️ Sevimlilarga qo'shildi",
        'broadcast_announcement': "📣 **E'LON**",
        'fav_removed': "💔 Sevimlilardan o'chirildi",
        'btn_watch': "🎬 Ko'rish",
        'btn_remove': "❌ O'chirish",
        'lang_selected': "✅ Til O'zbekchaga o'zgartirildi!",
        'not_found': "❌ '{q}' bo'yicha hech narsa topilmadi.",
        'results_title': "🔎 Qidiruv natijalari:",
        'fuzzy_label': "🤔 Balki: ",
        'empty_seasons': "⚠️ Bu serialda hali fasllar yo'q.",
        'empty_episodes': "⚠️ Bu faslda hali qismlar yo'q.",
        'season_label': "📅 Fasl ",
        'episode_label': "🎞 Qism ",
        'genre_label': "🎭 Janr",
        'views_label': "👁 Ko'rishlar",
        'movie_label': "Film",
        'series_label': "Serial",
        'season_select': "📅 Faslni tanlang:",
        'episode_select': "🎞 Qismni tanlang:",
        'empty_content': "🎬 Kontent hali qo'shilmagan.",
        'btn_check': "✅ Obunani tekshirish",
        'sub_error': "❌ Siz hali obuna bo'lmagansiz!",
        'new_content_alert': "🆕 **Yangi: {title}**\n\n📝 {desc}\n\n🎭 Janr: {genre}\n\n🎬 Botda hozir tomosha qiling!",
        'btn_watch_now': "🎬 Ko'rish",
        'btn_next': "➡️ Keyingi",
        'btn_prev': "⬅️ Oldingi",
        'page_label': "Sahifa {p}",
        'btn_search_cat': "🔍 Qidiruv",
        'genre_🍿 Экшен': "🍿 Ekshn",
        'genre_🤣 Комедия': "🤣 Komediya",
        'genre_😱 Ужасы': "😱 Qo'rqinchli",
        'genre_🎭 Дrama': "🎭 Drama",
        'genre_🌌 Фантастика': "🌌 Fantastika",
        'genre_🔪 Триллер': "🔪 Triller",
        'genre_🧸 Мультфильм': "🧸 Multfilm",
        'genre_🕵️ Detektiv': "🕵️ Detektiv",
        'notify_content_added': "🆕 **Yangi kontent qo'shildi!**\n\n🎬 **{title}**\n📝 {description}\n\nBotda hozir tomosha qiling!",
        'inline_search': "🔍 Qidirish...",
        'admin_auto_sub_shared': "🤖 Bot '{title}' kanaliga qo'shildi (ID: {id})\nObuna turini tanlang:",
        'admin_auto_sub_error': "⚠️ Kanal ma'lumotlarini olishda xato: {e}",
        'channel_post_footer': "🎬 Botda hozir tomosha qiling!",
        'inline_watch_in_bot': "Botda ko'rish",
        'btn_backup_caption': "📦 **Database Backup**\n📅 {d}",
        'backup_error': "❌ Ma'lumotlar bazasi fayli topilmadi.",
        'admin_auto_sub_success': "✅ **Kanal majburiy obunalar ro'yxatiga avtomatik qo'shildi!**\n\n📢 Nomi: **{title}**\n🆔 ID: `{id}`\n🔗 Link: {link}",
        'admin_bot_added_member': "🔔 Bot **{title}** kanaliga a'zo sifatida qo'shildi.\nUni majburiy obunalar ro'yxatiga qo'shish uchun **administrator** qiling.",
        'btn_add_movie': "➕ Film qo'shish",
        'btn_add_series': "➕ Serial qo'shish",
        'btn_broadcast': "📣 Xabar yuborish",
        'btn_sub_mgr': "⛓ Obunalar",
        'btn_manage_content': "📁 Kontentlar",
        'btn_movie_channel': "📺 Bot kanali",
        'btn_full_stats': "📈 Statistika",
        'btn_delete': "🗑 O'chirish",
        'btn_rate': "⭐ Baholash",
        'btn_share': "🔗 Ulashish",
        'btn_subscribe': "🔔 Yangi qismlar haqida bildirishnoma",
        'btn_unsubscribe': "🔕 Bildirishnomalarni o'chirish",
        'btn_top_movies': "🔥 Top-10 Kinolar",
        'btn_top_series': "🔝 Top-10 Seriallar",
        'rating_prompt': "✨ 10 ballik tizimda baholang:",
        'rating_success': "✅ Rahmat! Sizning bahoyingiz: {r}",
        'sub_success': "🔔 Siz ushbu serial yangilanishlariga obuna bo'ldingiz!",
        'unsub_success': "🔕 Bildirishnomalar o'chirildi.",
        'new_episode_alert': "🆕 **{title}** serialida yangi qism chiqdi!\n\nBotda hozir tomosha qiling 🍿",
        'top_title': "🏆 **TOP-10 {t}**\n\n",
        'rating_label': "⭐️ Reyting",
        'admin_stats_full_msg': "📈 **To'liq statistika:**\n\n👥 Foydalanuvchilar: **{u}**\n🎬 Filmlar: **{m}**\n📺 Seriallar: **{s}**\n\n👁 Jami ko'rishlar: **{v}**\n❤️ Jami sevimlilar: **{f}**\n\n📅 Sana: {d}",
        'admin_manage_content_msg': "📁 **Kontentni boshqarish:**\nKategoriyani tanlang yoki qidiruvdan foydalaning:",
        'admin_manage_movies_title': "🎬 **Filmlarni boshqarish (Jami: {total}):**",
        'admin_manage_series_title': "📺 **Seriallarni boshqarish (Jami: {total}):**",
        'admin_search_prompt': "🔎 Kontentni qidirish uchun nom yoki kodni kiriting:",
        'admin_movie_channel_setup_msg': "🎬 **Kino kanalini sozlash**\n\n{id_info}\n\nKanalni o'zgartirish uchun uning **ID**sini yuboring yoki undagi **xabarni menga yo'llang**.",
        'admin_add_movie_title_prompt': "⌨️ Film nomini kiriting:",
        'admin_add_movie_desc_prompt': "⌨️ Film tavsifini kiriting:",
        'admin_add_movie_genre_prompt': "🎭 Film janrini tanlang:",
        'admin_add_movie_preview_prompt': "✅ Janr tanlandi: {genre}. \n🖼 Film uchun prevyu (foto) yuboring:",
        'admin_add_movie_file_prompt': "🎥 Film video faylini yuboring:",
        'admin_add_movie_code_prompt': "⌨️ Film uchun unikal kodni kiriting (masalan, 101):",
        'admin_add_movie_success_msg': "✅ Film muvaffaqiyatli qo'shildi!",
        'broadcast_prompt_msg': "📣 Xabar matnini kiring:",
        'broadcast_done_msg': "✅ Xabar yuborish yakunlandi! {count} foydalanuvchi qabul qildi.",
        'sub_mgr_title_msg': "⚙️ Majburiy obunalarni boshqarish:",
        'btn_add_sub_manual': "➕ Qo'lda qo'shish (ID)",
        'btn_add_sub_auto': "➕ Kanal qo'shish (Bot -> Admin)",
        'admin_manage_movie_item_msg': "🎬 **Film: {title}**\nKod: {id}\n\nNima qilmoqchisiz?",
        'admin_manage_series_item_msg': "📺 **Serial: {title}**\n\nNima qilmoqchisiz?",
        'btn_delete': "🗑 O'chirish",
        'admin_delete_movie_confirm': "✅ Film o'chirildi",
        'admin_delete_series_confirm': "✅ Serial va uning barcha fasl/qismlari o'chirildi",
        'admin_add_series_title_prompt': "⌨️ Serial nomini kiriting:",
        'admin_add_series_desc_prompt': "⌨️ Serial tavsifini kiriting:",
        'admin_add_series_success_msg': "✅ '{title}' seriali yaratildi! Endi fasl qo'shing. Fasl raqamini kiriting (son):",
        'admin_add_season_prompt': "✅ {num}-fasl qo'shildi! Endi qism raqamini kiriting (son):",
        'admin_add_episode_file_prompt': "🎥 Qism video faylini yuboring:",
        'admin_add_episode_success_msg': "✅ Qism qo'shildi! Yana qo'shasizmi? Yangi qism raqamini yuboring yoki chiqish uchun /start deb yozing.",
        'admin_add_sub_id_prompt': "⌨️ Kanal ID sini kiriting (masalan, -100...):",
        'admin_add_sub_name_prompt': "⌨️ Kanal nomini kiriting:",
        'admin_add_sub_type_prompt': "📝 Kanal turini tanlang:",
        'btn_type_public': "🌐 Ochiq (Public)",
        'btn_type_private': "🔒 Yopiq (Private)",
        'admin_add_sub_link_prompt': "⌨️ Kanal linkini yuboring (taklifnoma linki):",
        'admin_add_sub_success': "✅ Kanal majburiy obunalar ro'yxatiga qo'shildi!",
        'admin_remove_sub_confirm': "✅ Kanal o'chirildi",
        'admin_movie_channel_id_info': "Joriy ID: `{id}`",
        'admin_movie_channel_not_set': "Kanal o'rnatilmagan.",
        'admin_movie_channel_set_success': "✅ Kino kanali muvaffaqiyatli o'rnatildi: `{id}`",
        'admin_movie_channel_error': "⚠️ Iltimos, to'g'ri ID kiriting yoki kanaldan xabarni yo'llang.",
        'btn_vip': "💎 VIP Obuna",
        'vip_menu': "💎 **VIP Obuna**\n\nVIP-status imkoniyatlari:\n✅ Majburiy obunalarsiz foydalanish\n✅ Yangi filmlarni birinchilardan bo'lib ko'rish\n✅ Reklamasiz\n\nObuna muddatini tanlang:",
        'vip_price_item': "{months} oy — {price} UZS",
        'vip_price_1year': "1 yil — {price} UZS",
        'vip_select_method': "💳 To'lov usulini tanlang:",
        'vip_card_info': "💳 **Karta orqali to'lov (UZCARD/HUMO)**\n\nKartaga **{price} UZS** o'tkazing:\n`{card}`\n\nTo'lovdan so'ng **chek rasmini** botga yuboring. Admin to'lovni tekshirib tasdiqlaydi.",
        'vip_receipt_received': "✅ Chek qabul qilindi! Admin tasdiqlashini kuting.",
        'vip_stars_info': "🌟 **Telegram Stars orqali to'lov**\n\nNarxi: {price} Stars",
        'admin_new_payment': "🔔 **Yangi to'lov!**\n\nFoydalanuvchi: @{username} ({id})\nTarif: {plan}\nSumma: {price} UZS\nUsul: {method}",
        'vip_activated': "✅ **VIP-obuna faollashtirildi!**\nAmal qilish muddati: {date} gacha\nYoqimli tomosha! 🍿",
        'vip_rejected': "❌ To'lovingiz admin tomonidan rad etildi.",
        'admin_vip_settings_msg': "💎 **VIP Sozlamalari**\n\nBu yerda narxlarni va to'lov rekvizitlarini o'zgartirishingiz mumkin.",
        'btn_vip_prices': "💰 Narxlarni o'zgartirish",
        'btn_vip_merchants': "💳 Karta/Merchants sozlash",
        'btn_vip_history': "📜 To'lovlar tarixi",
        'sub_required_vip': "⚠️ Botdan foydalanish uchun kanallarga obuna bo'ling YOKI VIP obuna sotib oling (umrbod obunalarsiz).",
        'btn_buy_vip': "💎 VIP sotib olish",
        'vip_uzs': "UZS"
    }
}

from aiogram import Bot, Dispatcher, F, types, BaseMiddleware
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ChatMemberUpdated,
    SwitchInlineQueryChosenChat,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ChosenInlineResult,
    FSInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# --- CONFIGURATION ---
TOKEN = "8348734983:AAGrXxU12F8tCmj_Bh9SDanbIFPH8JKv3jw"
ADMIN_ID = 1686150926  # Change this to your Telegram ID

# --- DATABASE LAYER ---
class Database:
    def __init__(self, db_file: Optional[str] = None):
        # Store DB next to this script to ensure persistence across runs
        if not db_file:
            base_dir = os.path.dirname(__file__)
            db_file = os.path.join(base_dir, "kino_bot.db")
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Users Table (include language column at creation so it's always present)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                registration_date DATETIME,
                language TEXT
            )
        ''')
        
        # Movies Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                genre TEXT,
                file_id TEXT,
                views INTEGER DEFAULT 0,
                created_at DATETIME
            )
        ''')

        # Series Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                genre TEXT,
                views INTEGER DEFAULT 0,
                created_at DATETIME
            )
        ''')

        # Seasons Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS seasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id INTEGER,
                season_number INTEGER,
                FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
            )
        ''')

        # Episodes Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER,
                episode_number INTEGER,
                file_id TEXT,
                FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE
            )
        ''')

        # Favorites Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id INTEGER,
                content_type TEXT, -- 'movie' or 'series'
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # History Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id INTEGER,
                content_type TEXT,
                viewed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Add 'code' columns if they don't exist (Migration)
        try:
            self.cursor.execute("ALTER TABLE movies ADD COLUMN code TEXT")
            self.cursor.execute("ALTER TABLE series ADD COLUMN code TEXT")
        except sqlite3.OperationalError:
            pass # Columns already exist

        # Add 'language' column to users if it doesn't exist
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
        except sqlite3.OperationalError:
            pass

        # Sub Channels Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sub_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE,
                name TEXT,
                type TEXT, -- 'public' or 'private'
                invite_link TEXT
            )
        ''')
        
        # Config Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS series_subscriptions (
                user_id INTEGER,
                series_id INTEGER,
                PRIMARY KEY (user_id, series_id)
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER,
                content_id INTEGER,
                content_type TEXT,
                rating INTEGER,
                PRIMARY KEY (user_id, content_id, content_type)
            )''')
        
        # Migrations for preview_id and vip_until
        try:
            self.cursor.execute("ALTER TABLE movies ADD COLUMN preview_id TEXT")
        except sqlite3.OperationalError: pass
        try:
            self.cursor.execute("ALTER TABLE series ADD COLUMN preview_id TEXT")
        except sqlite3.OperationalError: pass
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN vip_until DATETIME")
        except sqlite3.OperationalError: pass

        # VIP Prices Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                months INTEGER,
                price_uzs INTEGER
            )
        ''')
        
        # Initial prices if empty
        self.cursor.execute("SELECT COUNT(*) FROM vip_prices")
        if self.cursor.fetchone()[0] == 0:
            prices = [(1, 15000), (3, 40000), (6, 75000), (12, 120000)]
            self.cursor.executemany("INSERT INTO vip_prices (months, price_uzs) VALUES (?, ?)", prices)

        # Payments Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_months INTEGER,
                amount_uzs INTEGER,
                method TEXT, -- 'card', 'click', 'payme', 'stars'
                status TEXT, -- 'pending', 'approved', 'rejected'
                receipt_file_id TEXT,
                created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Payment Config Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Initial config
        configs = [
            ('card_number', '0000 0000 0000 0000'),
            ('card_holder', 'F.I.SH'),
            ('click_token', ''),
            ('payme_token', '')
        ]
        for k, v in configs:
            self.cursor.execute("INSERT OR IGNORE INTO payment_config (key, value) VALUES (?, ?)", (k, v))

        self.conn.commit()

    def get_config(self, key: str) -> Optional[str]:
        self.cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_config(self, key: str, value: str):
        self.cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

# --- SERVICES LAYER ---
class UserService:
    def __init__(self, db: Database):
        self.db = db

    def register_user(self, user_id: int, username: str, full_name: str):
        self.db.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, registration_date) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()

    def user_exists(self, user_id: int) -> bool:
        self.db.cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return self.db.cursor.fetchone() is not None

    def set_language(self, user_id: int, lang: str):
        self.db.cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        self.db.conn.commit()

    def get_language(self, user_id: int) -> str:
        self.db.cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = self.db.cursor.fetchone()
        return row[0] if row and row[0] else 'ru'

    def get_user_count(self) -> int:
        self.db.cursor.execute("SELECT COUNT(*) FROM users")
        return self.db.cursor.fetchone()[0]

    def add_to_favorites(self, user_id: int, content_id: int, content_type: str):
        self.db.cursor.execute(
            "INSERT INTO favorites (user_id, content_id, content_type) VALUES (?, ?, ?)",
            (user_id, content_id, content_type)
        )
        self.db.conn.commit()

    def is_favorite(self, user_id: int, content_id: int, content_type: str) -> bool:
        self.db.cursor.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND content_id = ? AND content_type = ?",
            (user_id, content_id, content_type)
        )
        return self.db.cursor.fetchone() is not None

    def remove_from_favorites(self, user_id: int, content_id: int, content_type: str):
        self.db.cursor.execute(
            "DELETE FROM favorites WHERE user_id = ? AND content_id = ? AND content_type = ?",
            (user_id, content_id, content_type)
        )
        self.db.conn.commit()

    def get_favorites_paged(self, user_id: int, limit: int = 10, offset: int = 0) -> List[dict]:
        # Joined query to get titles
        self.db.cursor.execute("""
            SELECT content_id, content_type, 
            CASE 
                WHEN content_type = 'movie' THEN (SELECT title FROM movies WHERE id = content_id)
                WHEN content_type = 'series' THEN (SELECT title FROM series WHERE id = content_id)
            END as title
            FROM favorites WHERE user_id = ?
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        return [{"id": row[0], "type": row[1], "title": row[2]} for row in self.db.cursor.fetchall()]

    def get_favorites_count(self, user_id: int) -> int:
        self.db.cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,))
        return self.db.cursor.fetchone()[0]

    def add_to_history(self, user_id: int, content_id: int, content_type: str):
        self.db.cursor.execute(
            "INSERT INTO history (user_id, content_id, content_type, viewed_at) VALUES (?, ?, ?, ?)",
            (user_id, content_id, content_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()

    def get_history_paged(self, user_id: int, limit: int = 10, offset: int = 0) -> List[dict]:
        self.db.cursor.execute(
            "SELECT content_id, content_type, viewed_at FROM history WHERE user_id = ? ORDER BY viewed_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
        return [{"id": row[0], "type": row[1], "date": row[2]} for row in self.db.cursor.fetchall()]

    def get_history_count(self, user_id: int) -> int:
        self.db.cursor.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (user_id,))
        return self.db.cursor.fetchone()[0]
class MovieService:
    def __init__(self, db: Database):
        self.db = db

    def add_movie(self, title: str, description: str, genre: str, file_id: str, code: str, preview_id: str = None):
        self.db.cursor.execute(
            "INSERT INTO movies (title, description, genre, file_id, code, preview_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, genre, file_id, code, preview_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()
        return self.db.cursor.lastrowid

    def search_movies(self, query: str) -> List[dict]:
        # Search by code first
        self.db.cursor.execute("SELECT id, title, genre FROM movies WHERE code = ?", (query,))
        code_result = self.db.cursor.fetchone()
        if code_result:
            return [{"id": code_result[0], "title": code_result[1], "genre": code_result[2], "match_type": "exact"}]

        # Exact title or LIKE search
        self.db.cursor.execute(
            "SELECT id, title, genre FROM movies WHERE title LIKE ?", (f"%{query}%",)
        )
        lite_results = [{"id": row[0], "title": row[1], "genre": row[2], "match_type": "like"} for row in self.db.cursor.fetchall()]
        
        if lite_results:
            return lite_results

        # Fuzzy matching
        self.db.cursor.execute("SELECT id, title, genre FROM movies")
        all_movies = self.db.cursor.fetchall()
        movie_titles = [m[1] for m in all_movies]
        close_matches = difflib.get_close_matches(query, movie_titles, n=3, cutoff=0.6)
        
        fuzzy_results = []
        for match in close_matches:
            for m in all_movies:
                if m[1] == match:
                    fuzzy_results.append({"id": m[0], "title": m[1], "genre": m[2], "match_type": "fuzzy"})
                    break
        return fuzzy_results

    def get_movie(self, movie_id: int) -> Optional[dict]:
        self.db.cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
        row = self.db.cursor.fetchone()
        if row:
            self.db.cursor.execute("UPDATE movies SET views = views + 1 WHERE id = ?", (movie_id,))
            self.db.conn.commit()
            return {"id": row[0], "title": row[1], "description": row[2], "genre": row[3], "file_id": row[4], "views": row[5], "preview_id": row[8]}
        return None

    def get_movies_paged(self, limit: int = 10, offset: int = 0) -> List[dict]:
        self.db.cursor.execute("SELECT id, title, genre FROM movies ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
        return [{"id": row[0], "title": row[1], "genre": row[2]} for row in self.db.cursor.fetchall()]

    def get_movies_count(self) -> int:
        self.db.cursor.execute("SELECT COUNT(*) FROM movies")
        return self.db.cursor.fetchone()[0]

    def add_rating(self, user_id: int, movie_id: int, rating: int):
        self.db.cursor.execute(
            "INSERT OR REPLACE INTO ratings (user_id, content_id, content_type, rating) VALUES (?, ?, ?, ?)",
            (user_id, movie_id, 'movie', rating)
        )
        self.db.conn.commit()

    def get_average_rating(self, movie_id: int) -> float:
        self.db.cursor.execute("SELECT AVG(rating) FROM ratings WHERE content_id = ? AND content_type = 'movie'", (movie_id,))
        res = self.db.cursor.fetchone()[0]
        return round(res, 1) if res else 0.0

    def get_top_movies(self, limit: int = 10) -> List[dict]:
        self.db.cursor.execute("""
            SELECT m.id, m.title, AVG(r.rating) as avg_rating 
            FROM movies m 
            JOIN ratings r ON m.id = r.content_id AND r.content_type = 'movie'
            GROUP BY m.id 
            ORDER BY avg_rating DESC 
            LIMIT ?
        """, (limit,))
        return [{"id": row[0], "title": row[1], "rating": round(row[2], 1)} for row in self.db.cursor.fetchall()]

    def get_random_movie(self) -> Optional[dict]:
        self.db.cursor.execute("SELECT id FROM movies")
        ids = [row[0] for row in self.db.cursor.fetchall()]
        if ids:
            return self.get_movie(random.choice(ids))
        return None

class SeriesService:
    def __init__(self, db: Database):
        self.db = db

    def add_series(self, title: str, description: str, genre: str, code: str, preview_id: str = None):
        self.db.cursor.execute(
            "INSERT INTO series (title, description, genre, code, preview_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, genre, code, preview_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()
        return self.db.cursor.lastrowid

    def add_season(self, series_id: int, season_number: int):
        self.db.cursor.execute(
            "INSERT INTO seasons (series_id, season_number) VALUES (?, ?)",
            (series_id, season_number)
        )
        self.db.conn.commit()
        return self.db.cursor.lastrowid

    def add_episode(self, season_id: int, episode_number: int, file_id: str):
        self.db.cursor.execute(
            "INSERT INTO episodes (season_id, episode_number, file_id) VALUES (?, ?, ?)",
            (season_id, episode_number, file_id)
        )
        self.db.conn.commit()

    def get_all_series(self) -> List[dict]:
        self.db.cursor.execute("SELECT id, title, genre FROM series")
        return [{"id": row[0], "title": row[1], "genre": row[2]} for row in self.db.cursor.fetchall()]

    def get_seasons(self, series_id: int) -> List[dict]:
        self.db.cursor.execute("SELECT id, season_number FROM seasons WHERE series_id = ?", (series_id,))
        return [{"id": row[0], "number": row[1]} for row in self.db.cursor.fetchall()]

    def get_episodes(self, season_id: int) -> List[dict]:
        self.db.cursor.execute("SELECT id, episode_number, file_id FROM episodes WHERE season_id = ?", (season_id,))
        return [{"id": row[0], "number": row[1], "file_id": row[2]} for row in self.db.cursor.fetchall()]

    def get_series_paged(self, limit: int = 10, offset: int = 0) -> List[dict]:
        self.db.cursor.execute("SELECT id, title, genre FROM series ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
        return [{"id": row[0], "title": row[1], "genre": row[2]} for row in self.db.cursor.fetchall()]

    def get_series_count(self) -> int:
        self.db.cursor.execute("SELECT COUNT(*) FROM series")
        return self.db.cursor.fetchone()[0]

    def get_series_by_id(self, series_id: int) -> Optional[dict]:
        self.db.cursor.execute("SELECT id, title, description, genre, preview_id FROM series WHERE id = ?", (series_id,))
        row = self.db.cursor.fetchone()
        if row:
            return {"id": row[0], "title": row[1], "description": row[2], "genre": row[3], "preview_id": row[4]}
        return None

    def add_rating(self, user_id: int, series_id: int, rating: int):
        self.db.cursor.execute(
            "INSERT OR REPLACE INTO ratings (user_id, content_id, content_type, rating) VALUES (?, ?, ?, ?)",
            (user_id, series_id, 'series', rating)
        )
        self.db.conn.commit()

    def get_average_rating(self, series_id: int) -> float:
        self.db.cursor.execute("SELECT AVG(rating) FROM ratings WHERE content_id = ? AND content_type = 'series'", (series_id,))
        res = self.db.cursor.fetchone()[0]
        return round(res, 1) if res else 0.0

    def get_top_series(self, limit: int = 10) -> List[dict]:
        self.db.cursor.execute("""
            SELECT s.id, s.title, AVG(r.rating) as avg_rating 
            FROM series s 
            JOIN ratings r ON s.id = r.content_id AND r.content_type = 'series'
            GROUP BY s.id 
            ORDER BY avg_rating DESC 
            LIMIT ?
        """, (limit,))
        return [{"id": row[0], "title": row[1], "rating": round(row[2], 1)} for row in self.db.cursor.fetchall()]

    def subscribe(self, user_id: int, series_id: int):
        self.db.cursor.execute("INSERT OR IGNORE INTO series_subscriptions (user_id, series_id) VALUES (?, ?)", (user_id, series_id))
        self.db.conn.commit()

    def unsubscribe(self, user_id: int, series_id: int):
        self.db.cursor.execute("DELETE FROM series_subscriptions WHERE user_id = ? AND series_id = ?", (user_id, series_id))
        self.db.conn.commit()

    def is_subscribed(self, user_id: int, series_id: int) -> bool:
        self.db.cursor.execute("SELECT 1 FROM series_subscriptions WHERE user_id = ? AND series_id = ?", (user_id, series_id))
        return self.db.cursor.fetchone() is not None

    def get_subscribers(self, series_id: int) -> List[int]:
        self.db.cursor.execute("SELECT user_id FROM series_subscriptions WHERE series_id = ?", (series_id,))
        return [row[0] for row in self.db.cursor.fetchall()]

    def search_series(self, query: str) -> List[dict]:
        # Search by code first
        self.db.cursor.execute("SELECT id, title, genre FROM series WHERE code = ?", (query,))
        code_result = self.db.cursor.fetchone()
        if code_result:
            return [{"id": code_result[0], "title": code_result[1], "genre": code_result[2], "match_type": "exact"}]

        # Exact title or LIKE search
        self.db.cursor.execute(
            "SELECT id, title, genre FROM series WHERE title LIKE ?", (f"%{query}%",)
        )
        lite_results = [{"id": row[0], "title": row[1], "genre": row[2], "match_type": "like"} for row in self.db.cursor.fetchall()]
        
        if lite_results:
            return lite_results

        # Fuzzy matching
        self.db.cursor.execute("SELECT id, title, genre FROM series")
        all_series = self.db.cursor.fetchall()
        series_titles = [m[1] for m in all_series]
        close_matches = difflib.get_close_matches(query, series_titles, n=3, cutoff=0.6)
        
        fuzzy_results = []
        for match in close_matches:
            for s in all_series:
                if s[1] == match:
                    fuzzy_results.append({"id": s[0], "title": s[1], "genre": s[2], "match_type": "fuzzy"})
                    break
        return fuzzy_results

class AdminService:
    def __init__(self, db: Database):
        self.db = db

    def get_stats(self):
        self.db.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = self.db.cursor.fetchone()[0]
        self.db.cursor.execute("SELECT COUNT(*) FROM movies")
        total_movies = self.db.cursor.fetchone()[0]
        self.db.cursor.execute("SELECT COUNT(*) FROM series")
        total_series = self.db.cursor.fetchone()[0]
        return total_users, total_movies, total_series

    def get_all_user_ids(self) -> List[int]:
        self.db.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.db.cursor.fetchall()]

    def add_sub_channel(self, channel_id: str, name: str, channel_type: str, invite_link: str):
        self.db.cursor.execute(
            "INSERT OR REPLACE INTO sub_channels (channel_id, name, type, invite_link) VALUES (?, ?, ?, ?)",
            (channel_id, name, channel_type, invite_link)
        )
        self.db.conn.commit()

    def remove_sub_channel(self, channel_id: str):
        self.db.cursor.execute("DELETE FROM sub_channels WHERE channel_id = ?", (channel_id,))
        self.db.conn.commit()

    def get_sub_channels(self) -> List[dict]:
        self.db.cursor.execute("SELECT channel_id, name, type, invite_link FROM sub_channels")
        return [{"id": row[0], "name": row[1], "type": row[2], "link": row[3]} for row in self.db.cursor.fetchall()]

class VipService:
    def __init__(self, db: Database):
        self.db = db

    def is_vip(self, user_id: int) -> bool:
        self.db.cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
        row = self.db.cursor.fetchone()
        if not row or not row[0]:
            return False
        
        vip_until = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        return vip_until > datetime.now()

    def get_vip_until(self, user_id: int) -> Optional[str]:
        self.db.cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
        row = self.db.cursor.fetchone()
        return row[0] if row else None

    def get_prices(self) -> List[dict]:
        self.db.cursor.execute("SELECT months, price_uzs FROM vip_prices ORDER BY months")
        return [{"months": row[0], "price": row[1]} for row in self.db.cursor.fetchall()]

    def set_price(self, months: int, price: int):
        self.db.cursor.execute("UPDATE vip_prices SET price_uzs = ? WHERE months = ?", (price, months))
        self.db.conn.commit()

    def get_payment_config(self, key: str) -> str:
        self.db.cursor.execute("SELECT value FROM payment_config WHERE key = ?", (key,))
        row = self.db.cursor.fetchone()
        return row[0] if row else ""

    def set_payment_config(self, key: str, value: str):
        self.db.cursor.execute("INSERT OR REPLACE INTO payment_config (key, value) VALUES (?, ?)", (key, value))
        self.db.conn.commit()

    def create_payment(self, user_id: int, plan_months: int, amount: int, method: str, file_id: str = None) -> int:
        self.db.cursor.execute(
            "INSERT INTO payments (user_id, plan_months, amount_uzs, method, status, receipt_file_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, plan_months, amount, method, 'pending', file_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()
        return self.db.cursor.lastrowid

    def get_payment(self, payment_id: int) -> Optional[dict]:
        self.db.cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = self.db.cursor.fetchone()
        if row:
            return {"id": row[0], "user_id": row[1], "months": row[2], "amount": row[3], "method": row[4], "status": row[5], "file_id": row[6]}
        return None

    def update_payment_status(self, payment_id: int, status: str):
        self.db.cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
        self.db.conn.commit()
        
        if status == 'approved':
            payment = self.get_payment(payment_id)
            if payment:
                self.activate_vip(payment['user_id'], payment['months'])

    def activate_vip(self, user_id: int, months: int):
        current_vip = self.get_vip_until(user_id)
        if current_vip:
            start_date = max(datetime.now(), datetime.strptime(current_vip, "%Y-%m-%d %H:%M:%S"))
        else:
            start_date = datetime.now()
        
        import dateutil.relativedelta # Need to check if available or use timedelta
        # Simplified: using 30 days per month if relativedelta is not standard
        from datetime import timedelta
        new_until = start_date + timedelta(days=30 * months)
        
        self.db.cursor.execute("UPDATE users SET vip_until = ? WHERE user_id = ?", (new_until.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        self.db.conn.commit()

# --- FSM STATES ---
class OnboardingStates(StatesGroup):
    selection_language = State()

    add_sub_channel_link = State()

class AdminStates(StatesGroup):
    add_movie_title = State()
    add_movie_desc = State()
    add_movie_genre = State()
    add_movie_preview = State()
    add_movie_file = State()
    add_movie_code = State()
    
    add_series_title = State()
    add_series_desc = State()
    add_series_genre = State()
    add_series_preview = State()
    add_series_code = State()
    
    set_movie_channel = State()
    manage_content_search = State()
    
    add_season_num = State()
    add_episode_num = State()
    add_episode_file = State()

    broadcast = State()
    add_sub_channel_id = State()
    add_sub_channel_name = State()
    add_sub_channel_type = State()
    add_sub_channel_link = State()

class VipStates(StatesGroup):
    select_plan = State()
    select_method = State()
    wait_receipt = State()

class VipAdminStates(StatesGroup):
    edit_price = State()
    edit_config = State()

# --- GENRES ---
GENRES = ["🍿 Экшен", "🤣 Комедия", "😱 Ужасы", "🎭 Драма", "🌌 Фантастика", "🔪 Триллер", "🧸 Мультфильм", "🕵️ Детектив"]

class SearchStates(StatesGroup):
    query = State()

class PaginationStates(StatesGroup):
    movie_page = State()
    series_page = State()

# --- KEYBOARDS ---
def get_lang_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="set_lang_ru")
    builder.button(text="🇺🇸 English", callback_data="set_lang_en")
    builder.button(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz")
    builder.adjust(1)
    return builder.as_markup()

def get_main_menu_kb(lang: str, user_id: int):
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=l['btn_movies'], callback_data="menu_movies"), 
                InlineKeyboardButton(text=l['btn_series'], callback_data="menu_series"))
    builder.row(InlineKeyboardButton(text=l['btn_favs'], callback_data="menu_favs"), 
                InlineKeyboardButton(text=l['btn_history'], callback_data="menu_history"))
    builder.row(InlineKeyboardButton(text=l['btn_random'], callback_data="menu_random"), 
                InlineKeyboardButton(text=l['btn_stats'], callback_data="menu_stats"))
    
    if not vip_service.is_vip(user_id):
        builder.row(InlineKeyboardButton(text=l['btn_vip'], callback_data="vip_menu"))
    
    return builder.as_markup()

def get_admin_kb(lang: str):
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_add_movie'], callback_data="admin_add_movie")
    builder.button(text=l['btn_add_series'], callback_data="admin_add_series")
    builder.button(text=l['btn_broadcast'], callback_data="admin_broadcast")
    builder.button(text=l['btn_sub_mgr'], callback_data="admin_sub_mgr")
    builder.button(text=l['btn_vip_merchants'], callback_data="admin_vip_settings")
    builder.button(text=l['btn_manage_content'], callback_data="admin_manage_content")
    builder.button(text=l['btn_movie_channel'], callback_data="admin_movie_channel")
    builder.button(text=l['btn_full_stats'], callback_data="admin_full_stats")
    builder.adjust(1)
    return builder.as_markup()

def get_sub_mgr_kb(lang: str, channels: List[dict], bot_username: str):
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(text=f"❌ {ch['name']}", callback_data=f"remove_sub_{ch['id']}")
    
    # "Add to channel" button as admin
    add_url = f"https://t.me/{bot_username}?startchannel=true&admin=post_messages+edit_messages+delete_messages+invite_users+manage_chat"
    builder.button(text=l['btn_add_sub_auto'], url=add_url)
    builder.button(text=l['btn_add_sub_manual'], callback_data="admin_add_sub_manual")
    builder.button(text=l['btn_back'], callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def get_back_to_menu_kb(lang: str):
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_back'], callback_data="menu_back")
    return builder.as_markup()

def get_genres_kb(lang: str):
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    for genre in GENRES:
        label = l.get(f"genre_{genre}", genre)
        builder.button(text=label, callback_data=f"genre_{genre}")
    builder.adjust(2)
    return builder.as_markup()

def get_series_list_kb(lang: str, page: int = 1):
    limit = 8
    offset = (page - 1) * limit
    series_list = series_service.get_series_paged(limit, offset)
    total = series_service.get_series_count()
    
    builder = InlineKeyboardBuilder()
    for s in series_list:
        builder.button(text=f"📺 {s['title']} ({s['genre']})", callback_data=f"show_series_{s['id']}")
    builder.adjust(1)
    
    # Pagination row
    l = LEXICON[lang]
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_prev'], callback_data=f"series_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
    
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_next'], callback_data=f"series_page_{page+1}"))
    
    builder.row(*nav_buttons)
    return builder.as_markup()

def get_movies_list_kb(lang: str, page: int = 1):
    limit = 8
    offset = (page - 1) * limit
    movies_list = movie_service.get_movies_paged(limit, offset)
    total = movie_service.get_movies_count()
    
    builder = InlineKeyboardBuilder()
    for m in movies_list:
        builder.button(text=f"🎬 {m['title']} ({m['genre']})", callback_data=f"show_movie_{m['id']}")
    builder.adjust(1)
    
    l = LEXICON[lang]
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_prev'], callback_data=f"movies_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
    
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_next'], callback_data=f"movies_page_{page+1}"))
    
    builder.row(*nav_buttons)
    return builder.as_markup()

# --- BOT INITIALIZATION ---
db = Database()
user_service = UserService(db)
movie_service = MovieService(db)
series_service = SeriesService(db)
admin_service = AdminService(db)
vip_service = VipService(db)

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# --- HANDLERS ---
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject = None):
    # Check for deep links
    if command and command.args:
        args = command.args.split("_")
        if len(args) == 2:
            content_type, content_id = args[0], int(args[1])
            if content_type == 'movie':
                movie = movie_service.get_movie(content_id)
                if movie:
                    user_id = message.from_user.id
                    if not user_service.user_exists(user_id):
                        user_service.register_user(user_id, message.from_user.username, message.from_user.full_name)
                    
                    lang = user_service.get_language(user_id)
                    l = LEXICON[lang]
                    avg_rating = movie_service.get_average_rating(movie['id'])
                    text = f"🍿 **{movie['title']}**\n\n📝 {movie['description']}\n\n{l['genre_label']}: {movie['genre']}\n{l['views_label']}: {movie['views']}\n{l['rating_label']}: ⭐ {avg_rating}"
                    
                    builder = InlineKeyboardBuilder()
                    is_fav = user_service.is_favorite(user_id, movie['id'], 'movie')
                    builder.button(text="💔" if is_fav else "❤️", callback_data=f"toggle_fav_movie_{movie['id']}")
                    builder.button(text=l['btn_rate'], callback_data=f"rate_movie_{movie['id']}")
                    # Using code for share to ensure exact match in inline query
                    movie_data = movie_service.db.cursor.execute("SELECT code FROM movies WHERE id = ?", (movie['id'],)).fetchone()
                    code = movie_data[0] if movie_data else ""
                    builder.button(text=l['btn_share'], switch_inline_query=code)
                    builder.button(text=l['btn_back'], callback_data="menu_back")
                    builder.adjust(2)
                    await bot.send_video(message.chat.id, movie['file_id'], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
                    return
            elif content_type == 'series':
                series_id = content_id
                seasons = series_service.get_seasons(series_id)
                if seasons:
                    user_id = message.from_user.id
                    if not user_service.user_exists(user_id):
                        user_service.register_user(user_id, message.from_user.username, message.from_user.full_name)
                    
                    lang = user_service.get_language(user_id)
                    l = LEXICON[lang]
                    
                    # Also need to fetch title/desc for series
                    db.cursor.execute("SELECT title, description, genre, preview_id, code FROM series WHERE id = ?", (series_id,))
                    row = db.cursor.fetchone()
                    
                    if row:
                        avg_rating = series_service.get_average_rating(series_id)
                        text = f"📺 **{row[0]}**\n\n📝 {row[1]}\n\n{l['genre_label']}: {row[2]}\n{l['rating_label']}: ⭐ {avg_rating}"
                        
                        builder = InlineKeyboardBuilder()
                        for s in seasons:
                            builder.button(text=f"{l['season_label']}{s['number']}", callback_data=f"show_season_{s['id']}")
                        
                        is_fav = user_service.is_favorite(user_id, series_id, 'series')
                        builder.button(text="💔" if is_fav else "❤️", callback_data=f"toggle_fav_series_{series_id}")
                        builder.button(text=l['btn_rate'], callback_data=f"rate_series_{series_id}")
                        
                        is_sub = series_service.is_subscribed(user_id, series_id)
                        builder.button(text=l['btn_unsubscribe'] if is_sub else l['btn_subscribe'], callback_data=f"sub_toggle_{series_id}")
                        
                        # Using code for share
                        code = row[4] if row[4] else ""
                        builder.button(text=l['btn_share'], switch_inline_query=code)
                        builder.button(text=l['btn_back'], callback_data="menu_back")
                        builder.adjust(2)
                        
                        if row[3]: # preview_id
                            await bot.send_photo(message.chat.id, row[3], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
                        else:
                            await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
                        return

    if user_service.user_exists(message.from_user.id):
        user_id = message.from_user.id
        lang = user_service.get_language(user_id)
        l = LEXICON[lang]
        await message.answer(
            l['main_menu'],
            reply_markup=get_main_menu_kb(lang, user_id)
        )
    else:
        user_service.register_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name
        )
        await state.set_state(OnboardingStates.selection_language)
        await message.answer(
            LEXICON['ru']['start'].format(name=message.from_user.full_name),
            reply_markup=get_lang_kb()
        )

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_user_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[2]
    user_id = callback.from_user.id
    user_service.set_language(user_id, lang)
    l = LEXICON[lang]
    await callback.message.edit_text(
        l['start'].format(name=callback.from_user.full_name) + f"\n\n{l['lang_selected']}",
        reply_markup=get_main_menu_kb(lang, user_id)
    )
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "menu_back")
async def process_menu_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    try:
        await callback.message.edit_text(
            l['main_menu'],
            reply_markup=get_main_menu_kb(lang, user_id)
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            l['main_menu'],
            reply_markup=get_main_menu_kb(lang, user_id)
        )
    await callback.answer()

@dp.callback_query(F.data == "menu_movies")
async def movies_menu(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    kb = get_movies_list_kb(lang, 1)
    builder = InlineKeyboardBuilder.from_markup(kb)
    builder.row(InlineKeyboardButton(text=f"🔍 {l['search_prompt']}", callback_data="search_movie_start"))
    # The back button is already in get_movies_list_kb, so no need to add again here.
    
    await callback.message.edit_text(l['btn_movies'], reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "search_movie_start")
async def search_movie_start(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(SearchStates.query)
    await callback.message.edit_text(l['search_prompt'], reply_markup=get_back_to_menu_kb(lang))
    await callback.answer()

@dp.callback_query(F.data.startswith("movies_page_"))
async def movies_page_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    kb = get_movies_list_kb(lang, page)
    builder = InlineKeyboardBuilder.from_markup(kb)
    builder.row(InlineKeyboardButton(text=f"🔍 {l['search_prompt']}", callback_data="search_movie_start"))
    # The back button is already in get_movies_list_kb, so no need to add again here.
    
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "menu_series")
async def series_menu(callback: CallbackQuery):
    await series_page_handler(callback, 1)

@dp.callback_query(F.data.startswith("series_page_"))
async def series_page_handler(callback: Union[CallbackQuery, Message], page: int = None):
    user_id = callback.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    
    if page is None:
        page = int(callback.data.split("_")[2])

    kb = get_series_list_kb(lang, page)
    # The back button is already in get_series_list_kb, so no need to add again here.
    
    if isinstance(callback, CallbackQuery):
        await callback.message.edit_text(l['series_list'], reply_markup=kb)
        await callback.answer()
    else:
        await callback.answer(l['series_list'], reply_markup=kb)

@dp.callback_query(F.data == "menu_random")
async def random_movie(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]

    movie = movie_service.get_random_movie()
    if movie:
        user_service.add_to_history(callback.from_user.id, movie['id'], 'movie')
        avg_rating = movie_service.get_average_rating(movie['id'])
        text = f"🍿 **{movie['title']}**\n\n📝 {movie['description']}\n\n{l['genre_label']}: {movie['genre']}\n{l['views_label']}: {movie['views']}\n{l['rating_label']}: ⭐ {avg_rating}"
        builder = InlineKeyboardBuilder()
        is_fav = user_service.is_favorite(callback.from_user.id, movie['id'], 'movie')
        builder.button(text="💔" if is_fav else "❤️", callback_data=f"toggle_fav_movie_{movie['id']}")
        builder.button(text=l['btn_rate'], callback_data=f"rate_movie_{movie['id']}")
        
        movie_data = movie_service.db.cursor.execute("SELECT code FROM movies WHERE id = ?", (movie['id'],)).fetchone()
        code = movie_data[0] if movie_data else ""
        builder.button(text=l['btn_share'], switch_inline_query=code)
        builder.button(text=l['btn_back'], callback_data="menu_back")
        builder.adjust(2)
        await bot.send_video(callback.message.chat.id, movie['file_id'], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await callback.message.edit_text(l['empty_content'], reply_markup=get_back_to_menu_kb(lang))
    await callback.answer()

@dp.callback_query(F.data == "menu_favs")
async def show_favorites(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    favs = user_service.get_favorites(callback.from_user.id)
    if not favs:
        await callback.message.edit_text(l['favs_empty'], reply_markup=get_back_to_menu_kb(lang))
        await callback.answer()
        return
    
    builder = InlineKeyboardBuilder()
    for item in favs:
        prefix = "🎬" if item['type'] == 'movie' else "📺"
        callback_prefix = "show_movie" if item['type'] == 'movie' else "show_series"
        builder.button(text=f"{prefix} {item['title']}", callback_data=f"{callback_prefix}_{item['id']}")
        builder.button(text="❌", callback_data=f"remove_fav_{item['type']}_{item['id']}")
    
    builder.row(InlineKeyboardButton(text=l['btn_back'], callback_data="menu_back"))
    builder.adjust(2)
    await callback.message.edit_text(f"❤️ **{l['btn_favs']}:**", reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "menu_history")
async def show_history(callback: CallbackQuery):
    await history_page_handler(callback, 1)

@dp.callback_query(F.data.startswith("history_page_"))
async def history_page_handler(callback: CallbackQuery, page: int = None):
    if page is None:
        page = int(callback.data.split("_")[2])
    
    user_id = callback.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    
    limit = 6
    offset = (page - 1) * limit
    history = user_service.get_history_paged(user_id, limit, offset)
    total = user_service.get_history_count(user_id)
    
    if not history and page == 1:
        await callback.message.edit_text(l['history_empty'], reply_markup=get_back_to_menu_kb(lang))
        await callback.answer()
        return
    
    text = f"🕒 **{l['btn_history']}:**\n\n"
    for item in history:
        content_name = "🎬" if item['type'] == 'movie' else "📺"
        # We don't have titles in history table, fetching them might be slow but let's try join in service later
        # For now, let's keep it simple or use a joined query in service
        title = "Content"
        if item['type'] == 'movie':
            m = movie_service.get_movie(item['id'])
            title = m['title'] if m else "???"
        else:
            db.cursor.execute("SELECT title FROM series WHERE id = ?", (item['id'],))
            row = db.cursor.fetchone()
            title = row[0] if row else "???"
            
        text += f"{content_name} **{title}** — {item['date']}\n"
    
    builder = InlineKeyboardBuilder()
    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_prev'], callback_data=f"history_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton(text=l['btn_next'], callback_data=f"history_page_{page+1}"))
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text=l['btn_back'], callback_data="menu_back"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "menu_stats")
async def show_stats(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    u, m, s = admin_service.get_stats()
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_top_movies'], callback_data="top_movies")
    builder.button(text=l['btn_top_series'], callback_data="top_series")
    builder.button(text=l['btn_back'], callback_data="menu_back")
    builder.adjust(1)
    
    await callback.message.edit_text(
        l['admin_stats_full_msg'].format(u=u, m=m, s=s, v="?", f="?", d=datetime.now().strftime('%H:%M')), # Simplified for non-admin
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await state.clear()
        lang = user_service.get_language(message.from_user.id)
        l = LEXICON[lang]
        await message.answer(l['admin_panel'], reply_markup=get_admin_kb(lang))
    else:
        await message.answer("⚠️ У вас нет прав доступа к этой команде.")

async def check_sub(user_id: int, lang: str = 'ru') -> (bool, Optional[InlineKeyboardMarkup]):
    if vip_service.is_vip(user_id):
        return True, None

    channels = admin_service.get_sub_channels()
    if not channels:
        return True, None
    
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    all_subbed = True
    active_channels_count = 0
    
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch['id'], user_id=user_id)
            active_channels_count += 1
            if member.status not in ["member", "administrator", "creator"]:
                all_subbed = False
                builder.button(text=f"🔗 {ch['name']}", url=ch['link'] or "https://t.me/tg")
        except Exception as e:
            # If bot is not admin or channel invalid, we skip it to not block users
            logging.error(f"Error checking sub for {ch['id']}: {e}")
            continue
    
    if all_subbed or active_channels_count == 0:
        return True, None
    
    builder.button(text=l['btn_check'], callback_data="check_subs")
    builder.button(text=l['btn_buy_vip'], callback_data="vip_menu")
    builder.adjust(1)
    return False, builder.as_markup()

@dp.callback_query(F.data == "check_subs")
async def process_check_subs(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    is_sub, kb = await check_sub(user_id, lang)
    if is_sub:
        await callback.message.edit_text(l['main_menu'], reply_markup=get_main_menu_kb(lang, user_id))
    else:
        await callback.answer(l['sub_error'], show_alert=True)
    await callback.answer()

# --- VIP HANDLERS ---
@dp.callback_query(F.data == "vip_menu")
async def show_vip_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    prices = vip_service.get_prices()
    builder = InlineKeyboardBuilder()
    for p in prices:
        label = l['vip_price_item'].format(months=p['months'], price=p['price'])
        if p['months'] == 12:
            label = l['vip_price_1year'].format(price=p['price'])
        builder.button(text=label, callback_data=f"buy_vip_{p['months']}")
    
    builder.button(text=l['btn_back'], callback_data="menu_back")
    builder.adjust(1)
    
    await callback.message.edit_text(l['vip_menu'], reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_vip_"))
async def select_payment_method(callback: CallbackQuery, state: FSMContext):
    months = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    prices = vip_service.get_prices()
    amount = 0
    for p in prices:
        if p['months'] == months:
            amount = p['price']
            break
            
    await state.update_data(buy_months=months, buy_amount=amount)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 UZCARD / HUMO", callback_data="pay_method_card")
    builder.button(text="🔹 Click", callback_data="pay_method_click")
    builder.button(text="🔹 Payme", callback_data="pay_method_payme")
    builder.button(text="🌟 Telegram Stars", callback_data="pay_method_stars")
    builder.button(text=l['btn_back'], callback_data="vip_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(l['vip_select_method'], reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "pay_method_card")
async def pay_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    card = vip_service.get_payment_config('card_number')
    holder = vip_service.get_payment_config('card_holder')
    
    text = l['vip_card_info'].format(price=data['buy_amount'], card=f"{card}\n{holder}")
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_back'], callback_data="vip_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.set_state(VipStates.wait_receipt)
    await callback.answer()

@dp.message(VipStates.wait_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    
    file_id = message.photo[-1].file_id
    payment_id = vip_service.create_payment(user_id, data['buy_months'], data['buy_amount'], 'card', file_id)
    
    await message.answer(l['vip_receipt_received'], reply_markup=get_main_menu_kb(lang, user_id))
    
    # Notify Admin
    admin_l = LEXICON['ru'] # Admin probably speaks RU
    admin_text = admin_l['admin_new_payment'].format(
        username=message.from_user.username or "N/A",
        id=user_id,
        plan=f"{data['buy_months']} мес.",
        price=data['buy_amount'],
        method="Card"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"admin_pay_approve_{payment_id}")
    builder.button(text="❌ Отклонить", callback_data=f"admin_pay_reject_{payment_id}")
    
    await bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=builder.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith("admin_pay_approve_"))
async def admin_pay_approve(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[3])
    payment = vip_service.get_payment(payment_id)
    if payment:
        vip_service.update_payment_status(payment_id, 'approved')
        user_lang = user_service.get_language(payment['user_id'])
        l = LEXICON[user_lang]
        
        vip_until = vip_service.get_vip_until(payment['user_id'])
        await bot.send_message(payment['user_id'], l['vip_activated'].format(date=vip_until))
        
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ ОДОБРЕНО", reply_markup=None)
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_pay_reject_"))
async def admin_pay_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[3])
    payment = vip_service.get_payment(payment_id)
    if payment:
        vip_service.update_payment_status(payment_id, 'rejected')
        user_lang = user_service.get_language(payment['user_id'])
        await bot.send_message(payment['user_id'], LEXICON[user_lang]['vip_rejected'])
        
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ ОТКЛОНЕНО", reply_markup=None)
    await callback.answer()

# --- AUTOMATED PAYMENTS ---
@dp.callback_query(F.data == "pay_method_stars")
async def pay_stars(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    # Simple Stars implementation using Invoice
    # 1 Star is approx $0.02, let's say 1000 UZS = 4 Stars (approx)
    stars_amount = max(1, data['buy_amount'] // 250) 
    
    await bot.send_invoice(
        callback.message.chat.id,
        title=l['btn_vip'],
        description=f"VIP {data['buy_months']} мес.",
        payload=f"vip_{data['buy_months']}",
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=[types.LabeledPrice(label="VIP", amount=stars_amount)],
        reply_markup=None
    )
    await callback.answer()

@dp.callback_query(F.data.in_(["pay_method_click", "pay_method_payme"]))
async def pay_invoice(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split("_")[2]
    data = await state.get_data()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    token = vip_service.get_payment_config(f'{method}_token')
    if not token:
        await callback.answer("⚠️ Мерчант не настроен в админ-панели.", show_alert=True)
        return

    await bot.send_invoice(
        callback.message.chat.id,
        title=l['btn_vip'],
        description=f"VIP {data['buy_months']} мес.",
        payload=f"vip_{data['buy_months']}",
        provider_token=token,
        currency="UZS",
        prices=[types.LabeledPrice(label="VIP", amount=data['buy_amount'] * 100)], # In tiyin
        reply_markup=None
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("vip_"):
        months = int(payload.split("_")[1])
        user_id = message.from_user.id
        vip_service.activate_vip(user_id, months)
        
        lang = user_service.get_language(user_id)
        vip_until = vip_service.get_vip_until(user_id)
        await message.answer(LEXICON[lang]['vip_activated'].format(date=vip_until))
        
        # Log payment
        amount = message.successful_payment.total_amount
        if message.successful_payment.currency != "XTR":
            amount = amount // 100
        vip_service.create_payment(user_id, months, amount, 'auto', 'SUCCESS')

@dp.callback_query(F.data == "admin_vip_settings")
async def admin_vip_settings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_vip_prices'], callback_data="admin_vip_prices_list")
    builder.button(text=l['btn_vip_merchants'], callback_data="admin_vip_merchants_list")
    builder.button(text=l['btn_back'], callback_data="admin_back")
    builder.adjust(1)
    
    await callback.message.edit_text(l['admin_vip_settings_msg'], reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "admin_vip_prices_list")
async def admin_vip_prices_list(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    prices = vip_service.get_prices()
    
    builder = InlineKeyboardBuilder()
    for p in prices:
        builder.button(text=f"{p['months']} мес. — {p['price']} UZS", callback_data=f"admin_edit_price_{p['months']}")
    builder.button(text=l['btn_back'], callback_data="admin_vip_settings")
    builder.adjust(1)
    
    await callback.message.edit_text("💰 **Настройка цен VIP:**", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_edit_price_"))
async def admin_edit_price_start(callback: CallbackQuery, state: FSMContext):
    months = int(callback.data.split("_")[3])
    await state.update_data(edit_months=months)
    await state.set_state(VipAdminStates.edit_price)
    await callback.message.edit_text(f"⌨️ Введите новую цену за {months} мес. (в UZS, только число):")
    await callback.answer()

@dp.message(VipAdminStates.edit_price)
async def process_edit_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Введите корректное число.")
        return
        
    data = await state.get_data()
    price = int(message.text)
    vip_service.set_price(data['edit_months'], price)
    
    await message.answer(f"✅ Цена за {data['edit_months']} мес. установлена: {price} UZS", reply_markup=get_admin_kb(user_service.get_language(message.from_user.id)))
    await state.clear()

@dp.callback_query(F.data == "admin_vip_merchants_list")
async def admin_vip_merchants_list(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Карта (Card)", callback_data="admin_edit_config_card_number")
    builder.button(text="👤 Владелец карты", callback_data="admin_edit_config_card_holder")
    builder.button(text="🔹 Click Token", callback_data="admin_edit_config_click_token")
    builder.button(text="🔹 Payme Token", callback_data="admin_edit_config_payme_token")
    builder.button(text=LEXICON[user_service.get_language(callback.from_user.id)]['btn_back'], callback_data="admin_vip_settings")
    builder.adjust(1)
    
    await callback.message.edit_text("⚙️ **Настройка реквизитов:**", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_edit_config_"))
async def admin_edit_config_start(callback: CallbackQuery, state: FSMContext):
    key = callback.data.replace("admin_edit_config_", "")
    await state.update_data(edit_config_key=key)
    await state.set_state(VipAdminStates.edit_config)
    await callback.message.edit_text(f"⌨️ Введите новое значение для `{key}`:")
    await callback.answer()

@dp.message(VipAdminStates.edit_config)
async def process_edit_config(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data['edit_config_key']
    val = message.text
    vip_service.set_payment_config(key, val)
    
    await message.answer(f"✅ Значение для `{key}` успешно обновлено!", reply_markup=get_admin_kb(user_service.get_language(message.from_user.id)))
    await state.clear()

@dp.callback_query(F.data == "admin_movie_channel")
async def admin_movie_channel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    channel_id = db.get_config("movie_channel_id")
    
    id_info = l['admin_movie_channel_id_info'].format(id=channel_id) if channel_id else l['admin_movie_channel_not_set']
    text = l['admin_movie_channel_setup_msg'].format(id_info=id_info)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_back'], callback_data="admin_back")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.set_state(AdminStates.set_movie_channel)
    await callback.answer()

@dp.message(AdminStates.set_movie_channel)
async def process_set_movie_channel(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    channel_id = None
    if message.forward_from_chat:
        channel_id = str(message.forward_from_chat.id)
    elif message.text and message.text.startswith("-100"):
        channel_id = message.text
    
    if channel_id:
        db.set_config("movie_channel_id", channel_id)
        await message.answer(l['admin_movie_channel_set_success'].format(id=channel_id), parse_mode="Markdown", reply_markup=get_admin_kb(lang))
        await state.clear()
    else:
        await message.answer(l['admin_movie_channel_error'])

# --- MOVIE SEARCH HANDLER ---
@dp.message(SearchStates.query)
async def process_search(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]

    query = message.text
    results = movie_service.search_movies(query)
    
    if not results:
        await message.answer(l['not_found'].format(q=query))
    else:
        builder = InlineKeyboardBuilder()
        for m in results:
            label = f"🎬 {m['title']}"
            if m.get('match_type') == 'fuzzy':
                label = f"{l['fuzzy_label']}{m['title']}"
            builder.button(text=f"{label} ({m['genre']})", callback_data=f"show_movie_{m['id']}")
        builder.adjust(1)
        await message.answer(l['results_title'], reply_markup=builder.as_markup())
    await state.clear()

@dp.callback_query(F.data == "admin_manage_content")
async def admin_manage_content(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_movies'], callback_data="admin_manage_movies_1")
    builder.button(text=l['btn_series'], callback_data="admin_manage_series_1")
    builder.button(text=l['btn_search_cat'] if 'btn_search_cat' in l else "🔍 Поиск", callback_data="admin_manage_search_start")
    builder.button(text=l['btn_back'], callback_data="admin_back")
    builder.adjust(2)
    await callback.message.edit_text(l['admin_manage_content_msg'], reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "admin_manage_search_start")
async def admin_manage_search_start(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(AdminStates.manage_content_search)
    await callback.message.edit_text(l['admin_search_prompt'], reply_markup=InlineKeyboardBuilder().button(text=l['btn_back'], callback_data="admin_manage_content").as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_manage_movies_"))
async def admin_manage_movies_list(callback: CallbackQuery):
    page = int(callback.data.split("_")[3])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    limit = 10
    offset = (page - 1) * limit
    movies = movie_service.get_movies_paged(limit, offset)
    total = movie_service.get_movies_count()
    
    builder = InlineKeyboardBuilder()
    for m in movies:
        builder.button(text=f"🎬 {m['title']}", callback_data=f"manage_movie_{m['id']}")
    builder.adjust(1)
    
    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"admin_manage_movies_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"admin_manage_movies_{page+1}"))
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text=l['btn_back'], callback_data="admin_manage_content"))
    
    await callback.message.edit_text(l['admin_manage_movies_title'].format(total=total), reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_manage_series_"))
async def admin_manage_series_list(callback: CallbackQuery):
    page = int(callback.data.split("_")[3])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    limit = 10
    offset = (page - 1) * limit
    series = series_service.get_series_paged(limit, offset)
    total = series_service.get_series_count()
    
    builder = InlineKeyboardBuilder()
    for s in series:
        builder.button(text=f"📺 {s['title']}", callback_data=f"manage_series_{s['id']}")
    builder.adjust(1)
    
    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"admin_manage_series_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"admin_manage_series_{page+1}"))
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text=l['btn_back'], callback_data="admin_manage_content"))
    
    await callback.message.edit_text(l['admin_manage_series_title'].format(total=total), reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.message(AdminStates.manage_content_search)
async def process_manage_search(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    query = message.text
    movies = movie_service.search_movies(query)
    series = series_service.search_series(query)
    
    if not movies and not series:
        await message.answer(l['not_found'].format(q=query))
        return
        
    builder = InlineKeyboardBuilder()
    for m in movies:
        builder.button(text=f"🎬 {m['title']}", callback_data=f"manage_movie_{m['id']}")
    for s in series:
        builder.button(text=f"📺 {s['title']}", callback_data=f"manage_series_{s['id']}")
    
    builder.adjust(1)
    await message.answer(f"{l['results_title']} '{query}':", reply_markup=builder.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith("manage_movie_"))
async def manage_movie_item(callback: CallbackQuery):
    movie_id = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    movie = movie_service.get_movie(movie_id)
    if movie:
        text = l['admin_manage_movie_item_msg'].format(title=movie['title'], id=movie['id'])
        builder = InlineKeyboardBuilder()
        builder.button(text=l['btn_delete'], callback_data=f"delete_movie_{movie_id}")
        builder.button(text=l['btn_back'], callback_data="admin_manage_movies_1")
        builder.adjust(1)
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("manage_series_"))
async def manage_series_item(callback: CallbackQuery):
    series_id = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    # Manual fetch since service lacks get_series
    db.cursor.execute("SELECT title FROM series WHERE id = ?", (series_id,))
    row = db.cursor.fetchone()
    if row:
        text = l['admin_manage_series_item_msg'].format(title=row[0])
        builder = InlineKeyboardBuilder()
        builder.button(text=l['btn_delete'], callback_data=f"delete_series_{series_id}")
        builder.button(text=l['btn_back'], callback_data="admin_manage_series_1")
        builder.adjust(1)
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_movie_"))
async def delete_movie_exec(callback: CallbackQuery, state: FSMContext):
    movie_id = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    db.cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    db.conn.commit()
    await callback.answer(l['admin_delete_movie_confirm'], show_alert=True)
    await admin_manage_content(callback, state)

@dp.callback_query(F.data.startswith("delete_series_"))
async def delete_series_exec(callback: CallbackQuery, state: FSMContext):
    series_id = int(callback.data.split("_")[2])
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    db.cursor.execute("DELETE FROM series WHERE id = ?", (series_id,))
    db.cursor.execute("DELETE FROM seasons WHERE series_id = ?", (series_id,))
    db.cursor.execute("DELETE FROM episodes WHERE season_id IN (SELECT id FROM seasons WHERE series_id = ?)", (series_id,))
    db.conn.commit()
    await callback.answer(l['admin_delete_series_confirm'], show_alert=True)
    await admin_manage_content(callback, state)

# --- RATING & SUB HANDLERS ---
@dp.callback_query(F.data.startswith("rate_"))
async def show_rating_selection(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    parts = callback.data.split("_")
    ctype = parts[1]
    cid = parts[2]
    
    builder = InlineKeyboardBuilder()
    for i in range(1, 11):
        builder.button(text=str(i), callback_data=f"setrate_{ctype}_{cid}_{i}")
    builder.adjust(5)
    
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer(l['rating_prompt'])

@dp.callback_query(F.data.startswith("setrate_"))
async def process_rating(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    parts = callback.data.split("_")
    ctype = parts[1]
    cid = int(parts[2])
    rate = int(parts[3])
    
    if ctype == 'movie':
        movie_service.add_rating(callback.from_user.id, cid, rate)
        await show_movie_details(callback, cid)
    else:
        series_service.add_rating(callback.from_user.id, cid, rate)
        await show_series_seasons(callback, cid)
    
    await callback.answer(l['rating_success'].format(r=rate))

@dp.callback_query(F.data.startswith("sub_toggle_"))
async def sub_toggle(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    series_id = int(callback.data.split("_")[2])
    
    if series_service.is_subscribed(callback.from_user.id, series_id):
        series_service.unsubscribe(callback.from_user.id, series_id)
        await callback.answer(l['unsub_success'])
    else:
        series_service.subscribe(callback.from_user.id, series_id)
        await callback.answer(l['sub_success'])
    
    await show_series_seasons(callback, series_id)

@dp.callback_query(F.data == "top_movies")
async def show_top_movies(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    top = movie_service.get_top_movies()
    text = l['top_title'].format(t=l['btn_movies'])
    for i, m in enumerate(top, 1):
        text += f"{i}. {m['title']} — ⭐ {m['rating']}\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_back'], callback_data="menu_stats")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "top_series")
async def show_top_series(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    top = series_service.get_top_series()
    text = l['top_title'].format(t=l['btn_series'])
    for i, m in enumerate(top, 1):
        text += f"{i}. {m['title']} — ⭐ {m['rating']}\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_back'], callback_data="menu_stats")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("show_series_"))
async def show_series_seasons(callback: CallbackQuery, series_id_opt: int = None):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    series_id = series_id_opt or int(callback.data.split("_")[2])
    series = series_service.get_series_by_id(series_id) # Assuming a method to get series details by ID
    seasons = series_service.get_seasons(series_id)
    
    if not series:
        await callback.answer(l['not_found'].format(q="?"))
        return

    avg_rating = series_service.get_average_rating(series_id)
    text = f"📺 **{series['title']}**\n\n📝 {series['description']}\n\n{l['genre_label']}: {series['genre']}\n{l['rating_label']}: ⭐ {avg_rating}"
    
    builder = InlineKeyboardBuilder()
    for s in seasons:
        builder.button(text=f"{l['season_label']}{s['number']}", callback_data=f"show_season_{s['id']}")
    
    is_fav = user_service.is_favorite(callback.from_user.id, series_id, 'series')
    builder.button(text="💔" if is_fav else "❤️", callback_data=f"toggle_fav_series_{series_id}")
    builder.button(text=l['btn_rate'], callback_data=f"rate_series_{series_id}")
    
    is_sub = series_service.is_subscribed(callback.from_user.id, series_id)
    builder.button(text=l['btn_unsubscribe'] if is_sub else l['btn_subscribe'], callback_data=f"sub_toggle_{series_id}")
    
    # Using code for share
    series_data = series_service.db.cursor.execute("SELECT code FROM series WHERE id = ?", (series_id,)).fetchone()
    code = series_data[0] if series_data else ""
    builder.button(text=l['btn_share'], switch_inline_query=code)
    
    builder.button(text=l['btn_back'], callback_data="menu_series")
    builder.adjust(2)

    if series['preview_id']:
        await bot.send_photo(callback.message.chat.id, series['preview_id'], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("show_season_"))
async def show_season_episodes(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    season_id = int(callback.data.split("_")[2])
    episodes = series_service.get_episodes(season_id)
    
    if not episodes:
        await callback.answer(l['empty_episodes'])
        return
    
    builder = InlineKeyboardBuilder()
    for e in episodes:
        builder.button(text=f"{l['episode_label']}{e['number']}", callback_data=f"watch_ep_{e['id']}")
    builder.button(text=l['btn_back'], callback_data="menu_series")
    builder.adjust(3)
    await callback.message.edit_text(l['episode_select'], reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("show_movie_"))
async def show_movie_video(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    movie_id = int(callback.data.split("_")[2])
    movie = movie_service.get_movie(movie_id)
    if movie:
        user_service.add_to_history(callback.from_user.id, movie['id'], 'movie')
        avg_rating = movie_service.get_average_rating(movie['id'])
        text = f"🍿 **{movie['title']}**\n\n📝 {movie['description']}\n\n{l['genre_label']}: {movie['genre']}\n{l['views_label']}: {movie['views']}\n{l['rating_label']}: ⭐ {avg_rating}"
        
        builder = InlineKeyboardBuilder()
        is_fav = user_service.is_favorite(callback.from_user.id, movie['id'], 'movie')
        builder.button(text="💔" if is_fav else "❤️", callback_data=f"toggle_fav_movie_{movie['id']}")
        builder.button(text=l['btn_rate'], callback_data=f"rate_movie_{movie['id']}")
        builder.button(text=l['btn_share'], switch_inline_query=f"movie_{movie['id']}")
        builder.button(text=l['btn_back'], callback_data="menu_movies")
        builder.adjust(2)
        
        await bot.send_video(callback.message.chat.id, movie['file_id'], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()
    else:
        await callback.answer(l['not_found'].format(q="?"))

# --- FAVORITES HANDLERS ---
@dp.callback_query(F.data.startswith("toggle_fav_"))
async def toggle_favorite(callback: CallbackQuery):
    parts = callback.data.split("_")
    content_type = parts[2]
    content_id = int(parts[3])
    user_id = callback.from_user.id
    
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    if user_service.is_favorite(user_id, content_id, content_type):
        user_service.remove_from_favorites(user_id, content_id, content_type)
        await callback.answer(l['fav_removed'])
    else:
        user_service.add_to_favorites(user_id, content_id, content_type)
        await callback.answer(l['fav_added'])
    
    # Update button text if possible (for inline messages)
    builder = InlineKeyboardBuilder()
    is_fav = user_service.is_favorite(user_id, content_id, content_type)
    fav_text = "💔" if is_fav else "❤️"
    
    if content_type == 'series':
        seasons = series_service.get_seasons(content_id)
        for s in seasons:
            builder.button(text=f"{l['season_label']}{s['number']}", callback_data=f"show_season_{s['id']}")
        builder.button(text=l['btn_back'], callback_data="menu_series")
        builder.button(text=fav_text, callback_data=f"toggle_fav_series_{content_id}")
        builder.adjust(2)
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    else:
        builder.button(text=fav_text, callback_data=f"toggle_fav_movie_{content_id}")
        builder.button(text=l['btn_back'], callback_data="menu_movies")
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

# --- ADMIN ACTIONS HANDLERS ---
@dp.callback_query(F.data == "admin_add_movie")
async def admin_add_movie_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(AdminStates.add_movie_title)
    await callback.message.answer(l['admin_add_movie_title_prompt'])
    await callback.answer()

@dp.message(AdminStates.add_movie_title)
async def admin_add_movie_title(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(title=message.text)
    await state.set_state(AdminStates.add_movie_desc)
    await message.answer(l['admin_add_movie_desc_prompt'])

@dp.message(AdminStates.add_movie_desc)
async def admin_add_movie_desc(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(description=message.text)
    await state.set_state(AdminStates.add_movie_genre)
    await message.answer(l['admin_add_movie_genre_prompt'], reply_markup=get_genres_kb(lang))

@dp.callback_query(AdminStates.add_movie_genre, F.data.startswith("genre_"))
async def admin_add_movie_genre(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    genre = callback.data.split("_")[1]
    await state.update_data(genre=genre)
    await state.set_state(AdminStates.add_movie_preview)
    await callback.message.edit_text(l['admin_add_movie_preview_prompt'].format(genre=genre))
    await callback.answer()

@dp.message(AdminStates.add_movie_preview, F.photo)
async def admin_add_movie_preview(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(preview_id=message.photo[-1].file_id)
    await state.set_state(AdminStates.add_movie_file)
    await message.answer(l['admin_add_movie_file_prompt'])

@dp.message(AdminStates.add_movie_file)
async def admin_add_movie_file(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    file_id = message.video.file_id if message.video else (message.document.file_id if message.document else (message.text if message.text else None))
    if not file_id:
        await message.answer("⚠️ Пожалуйста, отправьте видео или File ID.")
        return
    await state.update_data(file_id=file_id)
    await state.set_state(AdminStates.add_movie_code)
    await message.answer(l['admin_add_movie_code_prompt'])

@dp.message(AdminStates.add_movie_code)
async def admin_add_movie_code(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    data = await state.get_data()
    movie_id = movie_service.add_movie(data['title'], data['description'], data['genre'], data['file_id'], message.text, data.get('preview_id'))
    await message.answer(l['admin_add_movie_success_msg'], reply_markup=get_main_menu_kb(lang))
    await notify_content_added(movie_id, 'movie')
    await state.clear()

@dp.callback_query(F.data == "admin_add_series")
async def admin_add_series_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(AdminStates.add_series_title)
    await callback.message.answer(l['admin_add_series_title_prompt'])
    await callback.answer()

@dp.message(AdminStates.add_series_title)
async def admin_add_series_title(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(title=message.text)
    await state.set_state(AdminStates.add_series_desc)
    await message.answer(l['admin_add_series_desc_prompt'])

@dp.message(AdminStates.add_series_desc)
async def admin_add_series_desc(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(description=message.text)
    await state.set_state(AdminStates.add_series_genre)
    await message.answer(l['admin_add_movie_genre_prompt'], reply_markup=get_genres_kb(lang))

@dp.callback_query(AdminStates.add_series_genre, F.data.startswith("genre_"))
async def admin_add_series_genre(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    genre = callback.data.split("_")[1]
    await state.update_data(genre=genre)
    await state.set_state(AdminStates.add_series_preview)
    await callback.message.edit_text(l['admin_add_movie_preview_prompt'].format(genre=genre))
    await callback.answer()

@dp.message(AdminStates.add_series_preview, F.photo)
async def admin_add_series_preview(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(preview_id=message.photo[-1].file_id)
    await state.set_state(AdminStates.add_series_code)
    await message.answer(l['admin_add_movie_code_prompt'])

@dp.message(AdminStates.add_series_code)
async def admin_add_series_code(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    data = await state.get_data()
    series_id = series_service.add_series(data['title'], data['description'], data['genre'], message.text, data.get('preview_id'))
    await message.answer(l['admin_add_series_success_msg'].format(title=data['title']))
    await state.update_data(series_id=series_id)
    await state.update_data(title=data['title'], description=data['description'], genre=data['genre']) # and others if needed
    await notify_content_added(series_id, 'series')
    await state.set_state(AdminStates.add_season_num)

@dp.message(AdminStates.add_season_num)
async def admin_add_season(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    if not message.text.isdigit():
        await message.answer("⚠️ Введите число.")
        return
    data = await state.get_data()
    season_id = series_service.add_season(data['series_id'], int(message.text))
    await state.update_data(season_id=season_id)
    await state.set_state(AdminStates.add_episode_num)
    await message.answer(l['admin_add_season_prompt'].format(num=message.text))

@dp.message(AdminStates.add_episode_num)
async def admin_add_episode_num(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    if not message.text.isdigit():
        await message.answer("⚠️ Введите число.")
        return
    await state.update_data(ep_num=int(message.text))
    await state.set_state(AdminStates.add_episode_file)
    await message.answer(l['admin_add_episode_file_prompt'])

@dp.message(AdminStates.add_episode_file)
async def admin_add_episode_file(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    file_id = message.video.file_id if message.video else (message.document.file_id if message.document else (message.text if message.text else None))
    data = await state.get_data()
    series_service.add_episode(data['season_id'], data['ep_num'], file_id)
    await message.answer(l['admin_add_episode_success_msg'], reply_markup=get_main_menu_kb(lang))
    
    # Notify subscribers
    subscribers = series_service.get_subscribers(data['series_id'])
    for sub_id in subscribers:
        try:
            u_lang = user_service.get_language(sub_id)
            ul = LEXICON[u_lang]
            await bot.send_message(sub_id, ul['new_episode_alert'].format(title=data['title']))
        except:
            pass

    await state.set_state(AdminStates.add_episode_num)

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(AdminStates.broadcast)
    await callback.message.answer(l['broadcast_prompt_msg'])
    await callback.answer()

@dp.message(AdminStates.broadcast)
async def admin_broadcast_exec(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    users = admin_service.get_all_user_ids()
    count = 0
    for u_id in users:
        try:
            u_lang = user_service.get_language(u_id)
            ul = LEXICON[u_lang]
            await bot.send_message(u_id, f"{ul['broadcast_announcement']}\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except:
            pass
    await message.answer(l['broadcast_done_msg'].format(count=count))
    await state.clear()

@dp.callback_query(F.data == "admin_sub_mgr")
async def admin_sub_mgr(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    channels = admin_service.get_sub_channels()
    me = await bot.get_me()
    await callback.message.edit_text(l['sub_mgr_title_msg'], reply_markup=get_sub_mgr_kb(lang, channels, me.username))
    await callback.answer()

@dp.callback_query(F.data == "admin_back")
async def process_admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await callback.message.edit_text(l['admin_panel'], reply_markup=get_admin_kb(lang))
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_sub_"))
async def admin_remove_sub(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    channel_id = callback.data.split("_")[2]
    admin_service.remove_sub_channel(channel_id)
    await callback.answer(l['admin_remove_sub_confirm'])
    channels = admin_service.get_sub_channels()
    me = await bot.get_me()
    await callback.message.edit_reply_markup(reply_markup=get_sub_mgr_kb(lang, channels, me.username))

@dp.callback_query(F.data == "admin_add_sub_manual")
async def admin_add_sub_manual(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    await state.set_state(AdminStates.add_sub_channel_id)
    await callback.message.answer(l['admin_add_sub_id_prompt'])
    await callback.answer()

@dp.message(AdminStates.add_sub_channel_id)
async def admin_set_sub_id(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(channel_id=message.text)
    await state.set_state(AdminStates.add_sub_channel_name)
    await message.answer(l['admin_add_sub_name_prompt'])

@dp.message(AdminStates.add_sub_channel_name)
async def admin_set_sub_name(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_sub_channel_type)
    builder = InlineKeyboardBuilder()
    builder.button(text=l['btn_type_public'], callback_data="type_public")
    builder.button(text=l['btn_type_private'], callback_data="type_private")
    await message.answer(l['admin_add_sub_type_prompt'], reply_markup=builder.as_markup())

@dp.callback_query(AdminStates.add_sub_channel_type, F.data.startswith("type_"))
async def admin_set_sub_type(callback: CallbackQuery, state: FSMContext):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    ctype = callback.data.split("_")[1]
    await state.update_data(type=ctype)
    await state.set_state(AdminStates.add_sub_channel_link)
    await callback.message.edit_text(l['admin_add_sub_link_prompt'])
    await callback.answer()

@dp.message(AdminStates.add_sub_channel_link)
async def admin_set_sub_link(message: Message, state: FSMContext):
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    data = await state.get_data()
    admin_service.add_sub_channel(data['channel_id'], data['name'], data['type'], message.text)
    await message.answer(l['admin_add_sub_success'])
    await state.clear()

# --- AUTO ADD HANDLER (Chosen Chat) ---
@dp.message(F.chat_shared)
async def on_chat_shared(message: Message, state: FSMContext):
    chat_id = message.chat_shared.chat_id
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    try:
        chat = await bot.get_chat(chat_id)
        await state.update_data(channel_id=str(chat_id), name=chat.title)
        await state.set_state(AdminStates.add_sub_channel_type)
        builder = InlineKeyboardBuilder()
        builder.button(text=l['btn_type_public'], callback_data="type_public")
        builder.button(text=l['btn_type_private'], callback_data="type_private")
        await message.answer(l['admin_auto_sub_shared'].format(title=chat.title, id=chat_id), reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer(l['admin_auto_sub_error'].format(e=e))

@dp.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):
    if update.new_chat_member.status == "administrator" and update.chat.type == "channel":
        chat_id = str(update.chat.id)
        chat_title = update.chat.title
        
        # Automatically attempt to get or create an invite link
        invite_link = None
        try:
            chat = await bot.get_chat(chat_id)
            invite_link = chat.invite_link
            if not invite_link:
                if chat.username:
                    invite_link = f"https://t.me/{chat.username}"
                else:
                    # Export new invite link if it's a private channel or no link found
                    invite_link = await bot.export_chat_invite_link(chat_id)
        except Exception as e:
            logging.error(f"Error automating channel add: {e}")

        # Add to database automatically
        admin_service.add_sub_channel(chat_id, chat_title, "public", invite_link)
        
        lang = user_service.get_language(ADMIN_ID)
        l = LEXICON[lang]
        await bot.send_message(ADMIN_ID, 
            l['admin_auto_sub_success'].format(title=chat_title, id=chat_id, link=invite_link or '---')
        )
    elif update.new_chat_member.status == "member" and update.chat.type == "channel":
        lang = user_service.get_language(ADMIN_ID)
        l = LEXICON[lang]
        await bot.send_message(ADMIN_ID, 
            l['admin_bot_added_member'].format(title=update.chat.title)
        )

@dp.message(F.text == "🕒 История")
async def show_history(message: Message):
    history = user_service.get_history(message.from_user.id)
    if not history:
        await message.answer("🕒 История пока пуста.")
        return
    
    text = "🕒 **Последние просмотры:**\n\n"
    for item in history:
        content_name = "Фильм" if item['type'] == 'movie' else "Серия"
        val = movie_service.get_movie(item['id']) if item['type'] == 'movie' else {'title': f"ID {item['id']}"}
        title = val['title'] if val else "Удалено"
        text += f"• {content_name}: {title} ({item['date'][:10]})\n"
    await message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_series_list")
async def back_to_series(callback: CallbackQuery):
    await series_menu(callback.message)
    await callback.message.delete()

@dp.callback_query(F.data.startswith("watch_ep_"))
async def watch_episode(callback: CallbackQuery):
    ep_id = int(callback.data.split("_")[2])
    # Fetching episode data
    db.cursor.execute("SELECT file_id, episode_number FROM episodes WHERE id = ?", (ep_id,))
    row = db.cursor.fetchone()
    if row:
        user_service.add_to_history(callback.from_user.id, ep_id, 'series') # Using 'series' type or adding 'episode' type support
        await bot.send_video(callback.message.chat.id, row[0], caption=f"🎞 Серия {row[1]}", parse_mode="Markdown")
        await callback.answer()
    else:
        await callback.answer("Серия не найдена.")

@dp.callback_query(F.data == "menu_favs")
async def favorites_menu_callback(callback: CallbackQuery):
    await show_favorites_paged(callback, 1)

@dp.message(F.text == LEXICON['ru']['btn_favs']) # Handle both RU/EN/UZ texts is tricky, better use F.text.in_(...)
@dp.message(F.text == LEXICON['en']['btn_favs'])
@dp.message(F.text == LEXICON['uz']['btn_favs'])
async def show_favorites_msg(message: Message):
    # This might not work if they use inline but let's keep it for compatibility
    await show_favorites_paged(message, 1)

async def show_favorites_paged(callback: Union[CallbackQuery, Message], page: int = None):
    if page is None:
        page = int(callback.data.split("_")[2])
        
    user_id = callback.from_user.id
    lang = user_service.get_language(user_id)
    l = LEXICON[lang]
    
    limit = 6
    offset = (page - 1) * limit
    favs = user_service.get_favorites_paged(user_id, limit, offset)
    total = user_service.get_favorites_count(user_id)
    
    if not favs and page == 1:
        text = l['favs_empty']
        kb = get_back_to_menu_kb(lang)
    else:
        text = f"❤️ **{l['btn_favs']}:**"
        builder = InlineKeyboardBuilder()
        for item in favs:
            prefix = "🎬" if item['type'] == 'movie' else "📺"
            callback_prefix = "show_movie" if item['type'] == 'movie' else "show_series"
            builder.button(text=f"{prefix} {item['title']}", callback_data=f"{callback_prefix}_{item['id']}")
            builder.button(text="❌", callback_data=f"remove_fav_{item['type']}_{item['id']}_{page}")
        
        builder.adjust(2)
        
        # Pagination
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text=l['btn_prev'], callback_data=f"favs_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(text=l['page_label'].format(p=page), callback_data="ignore"))
        if offset + limit < total:
            nav_buttons.append(InlineKeyboardButton(text=l['btn_next'], callback_data=f"favs_page_{page+1}"))
        builder.row(*nav_buttons)
        builder.row(InlineKeyboardButton(text=l['btn_back'], callback_data="menu_back"))
        kb = builder.as_markup()

    if isinstance(callback, CallbackQuery):
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await callback.answer()
    else:
        await callback.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("favs_page_"))
async def favs_page_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_favorites_paged(callback, page)

@dp.callback_query(F.data.startswith("remove_fav_"))
async def remove_favorite_from_list(callback: CallbackQuery):
    parts = callback.data.split("_")
    content_type = parts[2]
    content_id = int(parts[3])
    page = int(parts[4]) if len(parts) > 4 else 1
    
    user_service.remove_from_favorites(callback.from_user.id, content_id, content_type)
    await callback.answer(LEXICON[user_service.get_language(callback.from_user.id)]['fav_removed'])
    
    # Re-render the current page
    await show_favorites_paged(callback, page)

@dp.callback_query(F.data == "admin_full_stats")
async def admin_full_stats(callback: CallbackQuery):
    lang = user_service.get_language(callback.from_user.id)
    l = LEXICON[lang]
    u, m, s = admin_service.get_stats()
    # Additional stats
    db.cursor.execute("SELECT COUNT(*) FROM history")
    total_views = db.cursor.fetchone()[0]
    db.cursor.execute("SELECT COUNT(*) FROM favorites")
    total_favs = db.cursor.fetchone()[0]
    
    await callback.message.edit_text(
        l['admin_stats_full_msg'].format(
            u=u, m=m, s=s, v=total_views, f=total_favs,
            d=datetime.now().strftime('%d.%m.%Y %H:%M')
        ),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(Command("backup"))
async def cmd_backup(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    lang = user_service.get_language(message.from_user.id)
    l = LEXICON[lang]
    # Send the database file
    db_path = os.path.join(os.path.dirname(__file__), "kino_bot.db")
    if os.path.exists(db_path):
        await message.answer_document(
            FSInputFile(db_path),
            caption=l['btn_backup_caption'].format(d=datetime.now().strftime('%d.%m.%Y %H:%M')),
            parse_mode="Markdown"
        )
    else:
        await message.answer(l['backup_error'])

async def notify_content_added(content_id: int, content_type: str):
    channel_id = db.get_config("movie_channel_id")
    if not channel_id:
        return

    content = None
    if content_type == 'movie':
        content = movie_service.get_movie(content_id)
    else:
        # Fetch series data manually since Service doesn't have a single-get helper yet
        db.cursor.execute("SELECT title, description, genre, preview_id FROM series WHERE id = ?", (content_id,))
        row = db.cursor.fetchone()
        if row:
            content = {"title": row[0], "description": row[1], "genre": row[2], "preview_id": row[3]}

    if not content:
        return

    me = await bot.get_me()
    text = f"🆕 **Новинка / New / Yangi: {content['title']}**\n\n📝 {content['description']}\n\n"
    # For channel post, we can use a multi-language footer or just English
    text += "🎬 Смотрите прямо сейчас в боте!\n🎬 Watch now in the bot!\n🎬 Botda hozir tomosha qiling!"
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 RU", url=f"https://t.me/{me.username}?start={content_type}_{content_id}")
    builder.button(text="🇺🇸 EN", url=f"https://t.me/{me.username}?start={content_type}_{content_id}")
    builder.button(text="🇺🇿 UZ", url=f"https://t.me/{me.username}?start={content_type}_{content_id}")
    builder.adjust(3)
    
    try:
        if content.get('preview_id'):
            await bot.send_photo(channel_id, content['preview_id'], caption=text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        else:
            await bot.send_message(channel_id, text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to post to channel: {e}")

# --- INLINE MODE ---
@dp.inline_query()
async def inline_search(inline_query: InlineQuery):
    query = inline_query.query
    logging.info(f"🔍 Inline query received: '{query}' from {inline_query.from_user.id}")
    
    try:
        if not query:
            # Show some recent/popular movies if query is empty
            movies = movie_service.get_movies_paged(limit=5)
            series = series_service.get_series_paged(limit=5)
        else:
            movies = movie_service.search_movies(query)
            series = series_service.search_series(query)
        
        logging.info(f"Found {len(movies)} movies and {len(series)} series for inline search.")
        
        results = []
        me = await bot.get_me()
        
        lang = user_service.get_language(inline_query.from_user.id)
        l = LEXICON[lang]

        for m in movies:
            results.append(
                InlineQueryResultArticle(
                    id=f"movie_{m['id']}",
                    title=f"🎬 {m['title']}",
                    description=f"{l['genre_label']}: {m['genre']}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"🎬 **{m['title']}**\n\n🎭 {l['genre_label']}: {m['genre']}\n\n🍿 [{l['inline_watch_in_bot']}](https://t.me/{me.username}?start=movie_{m['id']})",
                        parse_mode="Markdown"
                    ),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=l['btn_watch'], url=f"https://t.me/{me.username}?start=movie_{m['id']}")]
                    ])
                )
            )
        
        for s in series:
            results.append(
                InlineQueryResultArticle(
                    id=f"series_{s['id']}",
                    title=f"📺 {s['title']}",
                    description=f"{l['genre_label']}: {s['genre']}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"📺 **{s['title']}**\n\n🎭 {l['genre_label']}: {s['genre']}\n\n🍿 [{l['inline_watch_in_bot']}](https://t.me/{me.username}?start=series_{s['id']})",
                        parse_mode="Markdown"
                    ),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=l['btn_watch'], url=f"https://t.me/{me.username}?start=series_{s['id']}")]
                    ])
                )
            )
        
        if not results:
            results.append(
                InlineQueryResultArticle(
                    id="no_results",
                    title=l['not_found'].format(q=query or "..."),
                    input_message_content=InputTextMessageContent(
                        message_text=l['not_found'].format(q=query or "...")
                    )
                )
            )
        
        logging.info(f"Answering inline query with {len(results)} results.")
        await inline_query.answer(results, cache_time=10, is_personal=True)
    except Exception as e:
        logging.error(f"❌ Error in inline_search: {e}", exc_info=True)

@dp.chosen_inline_result()
async def on_chosen_inline_result(chosen_inline_result: ChosenInlineResult):
    parts = chosen_inline_result.result_id.split("_")
    ctype = parts[0]
    if len(parts) < 2 or not parts[1].isdigit():
        return
    cid = int(parts[1])
    
    if ctype == 'movie':
        # Increment views
        db.cursor.execute("UPDATE movies SET views = views + 1 WHERE id = ?", (cid,))
        db.conn.commit()
    elif ctype == 'series':
        db.cursor.execute("UPDATE series SET views = views + 1 WHERE id = ?", (cid,))
        db.conn.commit()

# --- MIDDLEWARE ---
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get('event_from_user')
        if not user or user.id == ADMIN_ID:
            return await handler(event, data)

        # Skip check for certain commands/callbacks
        if isinstance(event, Message):
            if event.text and (event.text.startswith('/start') or event.text.startswith('/admin')):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            if event.data in ["check_subs", "lang_ru", "lang_en", "lang_uz"] or event.data.startswith("lang_"):
                return await handler(event, data)

        # Perform check
        lang = user_service.get_language(user.id) or 'ru'
        is_sub, kb = await check_sub(user.id, lang)
        
        if not is_sub:
            l = LEXICON[lang]
            msg_text = l.get('sub_required_vip', l['sub_required'])
            if isinstance(event, Message):
                await event.answer(msg_text, reply_markup=kb)
            elif isinstance(event, CallbackQuery):
                await event.message.edit_text(msg_text, reply_markup=kb)
                await event.answer()
            return

        return await handler(event, data)

# --- MAIN LOOP ---
async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Бот запущен...")
    
    # Register Middleware
    dp.message.outer_middleware(SubscriptionMiddleware())
    dp.callback_query.outer_middleware(SubscriptionMiddleware())
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        db.conn.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Бот остановлен.")
