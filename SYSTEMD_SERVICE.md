# Управление сервисом Levi's Bot через systemd

## Автозапуск настроен! ✅

Бот настроен как systemd пользовательский сервис и будет автоматически:
- ✅ Запускаться при загрузке системы
- ✅ Перезапускаться при сбоях (через 10 секунд)
- ✅ Записывать логи в файлы

## Команды управления

### Проверить статус бота
```bash
systemctl --user status leviru_bot.service
```

### Запустить бота
```bash
systemctl --user start leviru_bot.service
```

### Остановить бота
```bash
systemctl --user stop leviru_bot.service
```

### Перезапустить бота
```bash
systemctl --user restart leviru_bot.service
```

### Отключить автозапуск
```bash
systemctl --user disable leviru_bot.service
```

### Включить автозапуск
```bash
systemctl --user enable leviru_bot.service
```

### Посмотреть логи
```bash
# Последние 50 строк
journalctl --user -u leviru_bot.service -n 50

# Следить за логами в реальном времени
journalctl --user -u leviru_bot.service -f

# Логи также сохраняются в файлы:
tail -f ~/Документы/Работа/@irina_er1_form/bot.log
tail -f ~/Документы/Работа/@irina_er1_form/bot_error.log
```

### Перезагрузить конфигурацию после изменений
```bash
systemctl --user daemon-reload
systemctl --user restart leviru_bot.service
```

## Файлы сервиса

**Файл конфигурации сервиса:**
`~/.config/systemd/user/leviru_bot.service`

**Рабочая директория:**
`~/Документы/Работа/@irina_er1_form/`

**Логи:**
- `~/Документы/Работа/@irina_er1_form/bot.log` - основные логи
- `~/Документы/Работа/@irina_er1_form/bot_error.log` - логи ошибок

## Особенности

- **Автоматический перезапуск**: Бот автоматически перезапустится через 10 секунд после сбоя
- **Запуск при загрузке**: Включен lingering, бот запустится даже без входа пользователя в систему
- **Логирование**: Все логи сохраняются в файлы и доступны через journalctl

## Обновление бота

После обновления кода бота просто перезапустите сервис:
```bash
systemctl --user restart leviru_bot.service
```

## Удаление сервиса

Если нужно удалить автозапуск:
```bash
systemctl --user stop leviru_bot.service
systemctl --user disable leviru_bot.service
rm ~/.config/systemd/user/leviru_bot.service
systemctl --user daemon-reload
```

