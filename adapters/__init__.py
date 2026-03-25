"""
Sky-Net Protocol Adapters
─────────────────────────
Базовый класс и фабрика для протокольных адаптеров.
Каждый адаптер умеет: install, generate configs, add/remove clients, get traffic.
"""

import subprocess
import json
import os
import logging

log = logging.getLogger("sky-net.adapters")


class ProtocolAdapter:
    """Базовый класс для всех VPN-адаптеров."""

    PROTOCOL_NAME = "base"

    def __init__(self, db_conn=None):
        self.db = db_conn

    def check_binaries(self, binaries: list):
        """Проверка наличия необходимых программ в системе."""
        for b in binaries:
            if subprocess.run(["which", b], capture_output=True).returncode != 0:
                raise Exception(f"Программа '{b}' не найдена. Установите её для работы протокола {self.PROTOCOL_NAME}.")

    def install(self, server_ip: str):
        """Установить необходимые пакеты/контейнеры на сервере."""
        raise NotImplementedError

    def generate_keypair(self) -> dict:
        """Сгенерировать пару ключей (приватный/публичный)."""
        raise NotImplementedError

    def generate_server_config(self, inbound: dict) -> str:
        """Создать файл конфигурации сервера."""
        raise NotImplementedError

    def generate_client_config(self, client: dict, inbound: dict) -> str:
        """Создать конфиг клиента (.conf или .ovpn)."""
        raise NotImplementedError

    def add_client(self, client: dict, inbound: dict) -> bool:
        """Добавить клиента в работающий VPN."""
        raise NotImplementedError

    def remove_client(self, client: dict, inbound: dict) -> bool:
        """Удалить клиента."""
        raise NotImplementedError

    def toggle_client(self, client: dict, inbound: dict, enable: bool) -> bool:
        """Включить/выключить клиента."""
        raise NotImplementedError

    def get_traffic(self, inbound: dict) -> list:
        """Получить список {public_key/username, tx, rx} для всех клиентов."""
        raise NotImplementedError

    def start(self, inbound: dict) -> bool:
        """Запустить VPN-интерфейс."""
        raise NotImplementedError

    def stop(self, inbound: dict) -> bool:
        """Остановить VPN-интерфейс."""
        raise NotImplementedError

    def restart(self, inbound: dict) -> bool:
        """Перезапустить VPN-интерфейс."""
        self.stop(inbound)
        return self.start(inbound)

    def is_running(self, inbound: dict) -> bool:
        """Проверка, запущен ли интерфейс/сервис."""
        raise NotImplementedError

    def _run(self, cmd: list, check: bool = True) -> str:
        """Выполнить shell-команду и вернуть stdout."""
        log.info(f"[{self.PROTOCOL_NAME}] exec: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.error(f"[{self.PROTOCOL_NAME}] failed: {e.cmd} | err: {e.stderr}")
            raise Exception(f"Ошибка команды: {e.stderr or str(e)}")


class AdapterFactory:
    """Фабрика адаптеров — возвращает экземпляр по имени протокола."""

    _registry: dict = {}

    @classmethod
    def register(cls, protocol_name: str, adapter_class):
        cls._registry[protocol_name] = adapter_class

    @classmethod
    def get(cls, protocol_name: str, db_conn=None) -> ProtocolAdapter:
        adapter_class = cls._registry.get(protocol_name)
        if not adapter_class:
            raise ValueError(f"Unknown protocol: {protocol_name}. "
                             f"Available: {list(cls._registry.keys())}")
        return adapter_class(db_conn)

    @classmethod
    def available_protocols(cls) -> list:
        return list(cls._registry.keys())
