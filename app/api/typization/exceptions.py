from fastapi import status, HTTPException

# Недостаточно прав
ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Недостаточно прав'
)

# Ошибка аутентификации
AuthException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Ошибка аутентификации"
)


# Пользователь уже существует
UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует'
)


# Пользователь не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Пользователь не найден'
)

# Отсутствует идентификатор пользователя
UserIdNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Отсутствует идентификатор пользователя'
)


# Не найден ID пользователя
NoUserIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID пользователя'
)

# Команды не найдены
TeamsNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Команды не найдены'
)

# Команда не найдена
TeamNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Команда не найдена'
)


# Команда уже существует
TeamNameAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Команда с таким именем уже существует"
)

# Команда у данного пользователя существует
TeamAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="У вас уже есть команда"
)


# Не найден ID команды
NoTeamIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID команды'
)


# Превышено максимальное количество участников команды
MaxTeamMembersExceededException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Команда достигла максимального количества участников, разрешенного для хакатона"
)


# Участник команды не найден
MemberNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Участник команды не найден'
)

# Хакатоны не найдены
HackathonsNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Хакатоны не найдены'
)

# Хакатон не найден
HackathonNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Хакатон не найден'
)


# Не найден ID хакатона
NoHackathonIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID хакатона'
)


#Приглашение уже существует
InvitationAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Данный пользователь уже приглашен"
)

# Приглашение не найдено
InvitationNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Приглашение не найдено"
)

# Пользователь не зарегистрирован на хакатон
UserNotRegisteredForHackathon = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Пользователь не зарегистрирован на хакатон"
)