#!/bin/bash

# Скрипт для установки Docker и Docker Compose на Linux (Ubuntu/Debian)

set -e

echo "=== Установка Docker и Docker Compose ==="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Обновление списка пакетов
echo "Обновление списка пакетов..."
apt-get update

# Установка необходимых зависимостей
echo "Установка зависимостей..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавление официального GPG ключа Docker
echo "Добавление GPG ключа Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Настройка репозитория Docker
echo "Настройка репозитория Docker..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker Engine, Docker CLI и Containerd
echo "Установка Docker..."
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Запуск и включение Docker
echo "Запуск службы Docker..."
systemctl start docker
systemctl enable docker

# Добавление текущего пользователя в группу docker (чтобы не использовать sudo)
if [ -n "$SUDO_USER" ]; then
    echo "Добавление пользователя $SUDO_USER в группу docker..."
    usermod -aG docker $SUDO_USER
    echo "ВНИМАНИЕ: Вам нужно выйти и войти снова, чтобы изменения вступили в силу."
fi

# Проверка установки
echo ""
echo "=== Проверка установки ==="
docker --version
docker compose version

echo ""
echo "=== Установка завершена! ==="
echo "Docker и Docker Compose успешно установлены."
echo ""
echo "Если вы были добавлены в группу docker, выполните:"
echo "  newgrp docker"
echo "или перезайдите в систему."

