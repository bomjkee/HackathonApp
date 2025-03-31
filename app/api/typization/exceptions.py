from fastapi import status, HTTPException


# Недостаточно прав
ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Недостаточно прав'
)
"""Выбрасывается, если у пользователя недостаточно прав для выполнения действия."""


# Ошибка аутентификации
AuthException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Ошибка аутентификации"
)
"""Выбрасывается, если аутентификация не удалась."""


# Пользователь уже существует
UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует'
)
"""Выбрасывается, если при регистрации обнаружено, что пользователь с таким именем пользователя уже существует."""



# Пользователь не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Пользователь не найден'
)
"""Выбрасывается, если пользователь с указанным ID или email не найден."""


# Пользователь не зарегистрирован в приложении
UserNotRegisteredToApp = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Вы не зарегистрированы в приложении, зарегистрируйтесь чтобы продолжить'
)
"""Выбрасывается, если в пользователь не зарегистрировался в приложении."""


# Не найден ID пользователя
NoUserIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID пользователя'
)
"""Выбрасывается, если ID пользователя не найден в базе данных."""


# Команды не найдены
TeamsNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Команды не найдены'
)
"""Выбрасывается, если не найдено ни одной команды, соответствующей критериям поиска."""


# Команда не найдена
TeamNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Команда не найдена'
)
"""Выбрасывается, если команда с указанным ID не найдена."""


# Команда закрытая
TeamCloseException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Команда закрытая'
)
"""Выбрасывается, если команда закрытая."""


# Команда уже существует
TeamNameAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Команда с таким именем уже существует"
)
"""Выбрасывается, если при создании команды обнаружено, что команда с таким именем уже существует."""


# Команда у данного пользователя существует
MemberInTeamException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Вы уже состоите в команде на этом хакатоне"
)
"""Выбрасывается, если пользователь уже является участником указанной команды."""


# Не найден ID команды
NoTeamIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID команды'
)
"""Выбрасывается, если в запросе отсутствует ID команды."""


# Превышено максимальное количество участников команды
MaxTeamMembersExceededException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Команда достигла максимального количества участников, разрешенного для хакатона"
)
"""Выбрасывается, если при добавлении участника в команду превышено максимальное количество участников."""


# Участник команды не найден
MemberNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Участник команды не найден'
)
"""Выбрасывается, если участник команды с указанным ID не найден."""



# Участник команды не найден
TeamEmptyException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='В команде нет участников, она не действительна'
)
"""Выбрасывается, если в команде нет участников."""


# Хакатоны не найдены
HackathonsNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Хакатоны не найдены'
)
"""Выбрасывается, если не найдено ни одного хакатона, соответствующего критериям поиска."""


# Хакатон не найден
HackathonNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Хакатон не найден'
)
"""Выбрасывается, если хакатон с указанным ID не найден."""


# Не найден ID хакатона
NoHackathonIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID хакатона'
)
"""Выбрасывается, если в запросе отсутствует ID хакатона."""


#Приглашение уже существует
InvitationAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Данный пользователь уже приглашен"
)
"""Выбрасывается, если приглашение для данного пользователя уже существует."""


# Приглашение не найдено
InvitationNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Приглашение не найдено"
)
"""Выбрасывается, если приглашение с указанным ID не найдено."""



