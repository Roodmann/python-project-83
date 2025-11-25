#!/usr/bin/env bash
# скачиваем uv и запускаем команду установки зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh

# активация
. $HOME/.local/bin/env

# Makefile
make install

# Установка и настройка базы данных
make install && psql -a -d $DATABASE_URL -f database.sql
