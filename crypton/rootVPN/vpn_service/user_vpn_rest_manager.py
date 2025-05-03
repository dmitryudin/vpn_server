
from uuid import uuid4
import time
from confluent_kafka import Consumer, Producer, admin
import json
from enum import Enum
import httpx
from httpx import BasicAuth, TimeoutException, HTTPStatusError
from pydantic import BaseModel
import asyncio
from typing import Optional
import logging


logger = logging.getLogger(__name__)

class VPNClientError(Exception):
    """Базовое исключение для ошибок клиента"""
    pass

class VPNUserExistsError(VPNClientError):
    """Пользователь уже существует"""
    pass

class VPNUserNotFoundError(VPNClientError):
    """Пользователь не найден"""
    pass

class VPNUnauthorizedError(VPNClientError):
    """Ошибка аутентификации"""
    pass

class VPNConnectionError(VPNClientError):
    """Ошибка соединения с сервером"""
    pass

class OperationResult(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class VPNUserRestManager:
    def __init__(
        self,
        base_url: str = "http://185.207.67.215:8080",
        username: str = "admin",
        password: str = "securepassword"
    ):
        self.base_url = base_url.rstrip('/')
        self.auth = BasicAuth(username, password)
        self.client = httpx.AsyncClient(
            auth=self.auth,
            timeout=httpx.Timeout(10.0, connect=5.0)
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.client.__aexit__(*args)

    async def _handle_response(self, response: httpx.Response) -> OperationResult:
        try:
            response.raise_for_status()
            return OperationResult(
                success=True,
                message="Operation successful",
                data=response.json()
            )
        except HTTPStatusError as e:
            error_data = e.response.json().get('detail', {})
            
            if e.response.status_code == 401:
                raise VPNUnauthorizedError("Invalid credentials") from e
            if e.response.status_code == 404:
                raise VPNUserNotFoundError(error_data) from e
            if e.response.status_code == 409:
                raise VPNUserExistsError(error_data) from e
            
            return OperationResult(
                success=False,
                message=f"HTTP error: {e.response.status_code} - {error_data}",
                data=error_data
            )

    async def add_user(self, username: str, password: str) -> OperationResult:
        """Добавление пользователя VPN"""
        try:
            response = await self.client.post(
                f"{self.base_url}/users/",
                params={"username": username, "password": password}
            )
            return await self._handle_response(response)
            
        except VPNUnauthorizedError as e:
            raise 
        except TimeoutException as e:
            raise VPNConnectionError("Request timeout") from e
        except httpx.NetworkError as e:
            raise VPNConnectionError("Network error") from e
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )

    async def remove_user(self, username: str) -> OperationResult:
        """Удаление пользователя VPN"""
        try:
            response = await self.client.delete(
                f"{self.base_url}/users/{username}"
            )
            return await self._handle_response(response)
            
        except VPNUnauthorizedError as e:
            raise
        except TimeoutException as e:
            raise VPNConnectionError("Request timeout") from e
        except httpx.NetworkError as e:
            raise VPNConnectionError("Network error") from e
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )

    async def health_check(self) -> OperationResult:
        """Проверка доступности сервиса"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return OperationResult(
                success=True,
                message="Service is available",
                data=response.json()
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Health check failed: {str(e)}"
            )
        
    async def sync_users(self, usernames: list[str]) -> OperationResult:
        """Синхронизация списка пользователей VPN"""
        try:
            response = await self.client.post(
                f"{self.base_url}/users/sync",
                json=usernames
            )

            return await self._handle_response(response)
            
        except VPNUnauthorizedError as e:
            raise 
        except TimeoutException as e:
            raise VPNConnectionError("Request timeout") from e
        except httpx.NetworkError as e:
            raise VPNConnectionError("Network error") from e
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )

# Пример использования
async def main():
    try:
        async with VPNUserRestManager() as client:
            # Проверка здоровья
            health = await client.health_check()
            print(f"Health check: {health.message}")
            
            # Добавление пользователя
            add_result = await client.add_user("test_user", "secure_password")
            if add_result.success:
                print(f"User added: {add_result.data}")
            
            # Попытка добавить существующего пользователя
            try:
                await client.add_user("test_user", "password")
            except VPNUserExistsError as e:
                print(f"Error: {e}")
            
            # Удаление пользователя
            del_result = await client.remove_user("test_user")
            if del_result.success:
                print(f"User removed: {del_result.data}")
            
            # Попытка удалить несуществующего пользователя
            try:
                await client.remove_user("non_existent")
            except VPNUserNotFoundError as e:
                print(f"Error: {e}")
                
    except VPNUnauthorizedError as e:
        print(f"Authentication failed: {e}")
    except VPNConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
   