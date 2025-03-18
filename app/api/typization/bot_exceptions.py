from loguru import logger

class UserNotFoundException(Exception):
    """Исключение, выбрасываемое, если пользователь не найден."""

    def __init__(self, user_id: int = None, message: str = None):
        self.user_id = user_id
        default_message = f"Пользователь с ID {user_id} не найден." if user_id else "Пользователь не найден."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class TeamNotFoundException(Exception):
    """Исключение, выбрасываемое, если команда не найдена."""

    def __init__(self, team_id: int = None, message: str = None):
        self.team_id = team_id
        default_message = f"Команда с ID {team_id} не найдена." if team_id else "Команда не найдена."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class InvitationNotFoundException(Exception):
    """Исключение, выбрасываемое, если приглашение не найдено."""

    def __init__(self, invite_id: int = None, message: str = None):
        self.invite_id = invite_id
        default_message = f"Приглашение с ID {invite_id} не найдено." if invite_id else "Приглашение не найдено."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class MaxTeamMembersExceededException(Exception):
    """Исключение, выбрасываемое, если превышено максимальное количество участников в команде."""

    def __init__(self, team_id: int = None, max_members: int = None, message: str = None):
        self.team_id = team_id
        self.max_members = max_members
        default_message = f"Превышено максимальное количество участников ({max_members}) в команде с ID {team_id}." if team_id and max_members else "Превышено максимальное количество участников в команде."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class UserNotRegisteredForApp(Exception):
    """Исключение, выбрасываемое, если пользователь не зарегистрирован в приложении."""

    def __init__(self, user_id: int = None, message: str = None):
        self.user_id = user_id
        default_message = f"Пользователь с ID {user_id} не зарегистрирован в приложении." if user_id else "Пользователь не зарегистрирован в приложении."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class HackathonNotFoundException(Exception):
    """Исключение, выбрасываемое, если хакатон не найден."""

    def __init__(self, hackathon_id: int = None, message: str = None):
        self.hackathon_id = hackathon_id
        default_message = f"Хакатон с ID {hackathon_id} не найден." if hackathon_id else "Хакатон не найден."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class HackathonsNotFoundException(Exception):
    """Исключение, выбрасываемое, если хакатоны не найден."""

    def __init__(self, message: str = None):
        default_message = f"Хакатоны не найдены."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class PermissionDeniedException(Exception):
    """Исключение, выбрасываемое, когда у пользователя нет прав."""

    def __init__(self, user_id: int = None, permission: str = None, message: str = None):
        self.user_id = user_id
        self.permission = permission
        default_message = f"У пользователя с ID {user_id} нет прав на выполнение этого действия (требуется: {permission})." if user_id and permission else "Нет прав на выполнение этого действия."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class InvalidInputException(Exception):
    """Исключение, выбрасываемое, если введены неверные данные."""

    def __init__(self, field: str = None, message: str = None):
        self.field = field
        default_message = f"Неверные данные в поле: {field}." if field else "Неверные данные."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class CommandFailedException(Exception):
    """Исключение, выбрасываемое, если не удалось выполнить команду."""

    def __init__(self, command: str = None, message: str = None):
        self.command = command
        default_message = f"Не удалось выполнить команду: {command}." if command else "Не удалось выполнить команду."
        self.message = message or default_message
        super().__init__(self.message)
        logger.error(self.message)


class StateException(Exception):
    """Исключение, выбрасываемое, если бот находится в неверном состоянии."""

    def __init__(self, expected_state: str = None, current_state: str = None, message: str = None):
        self.expected_state = expected_state
        self.current_state = current_state
        default_message = f"Неверное состояние бота. Ожидалось: {expected_state}, текущее: {current_state}." if expected_state and current_state else "Неверное состояние бота."
        self.message = message or default_message
        super().__init__(self.message)
        logger.warning(self.message)


class ServiceUnavailableException(Exception):
    """Исключение, выбрасываемое, если сервис недоступен."""

    def __init__(self, service_name: str = None, message: str = None):
        self.service_name = service_name
        default_message = f"Сервис {service_name} недоступен." if service_name else "Сервис недоступен."
        self.message = message or default_message
        super().__init__(self.message)
        logger.error(self.message)

# Команда у данного пользователя существует
class MemberInTeamAlreadyExistsException(Exception):

    def __init__(self, message: str = None):
        default_message = "Пользователь уже состоит в команде"
        self.message = message or default_message
        super().__init__(self.message)
        logger.error(self.message)
"""Выбрасывается, если пользователь уже является участником команды."""
