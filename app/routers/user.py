from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from app.db.dao_models import UserDAO, StudentDAO, NonStudentDAO
from app.requests.user import RBUser, RBIsStudent
from app.responses.user import SUser, SStudent, SNonStudent


router = APIRouter(tags=['Работа с пользователями'])


@router.get("/", summary="Получить всех студентов")
async def get_all_students() -> List[SUser]:
    users = await UserDAO.find_all()
    return [SUser.from_orm(user) for user in users]


@router.get("/{id}", summary="Получить одного студента по id", response_model=SUser)
async def get_user_by_id(user_id: int) -> SUser:
    user = await UserDAO.find_one_or_none(tg_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Студент с ID {user_id} не найден!")
    return SUser.from_orm(user)


@router.post("/add_info")
async def add_user_info(user: RBIsStudent) -> SUser:
    user_date = await UserDAO.find_one_or_none(tg_id=user.id)
    if user_date:
        student = await StudentDAO.find_one_or_none(id=user.id)
        non_student = await NonStudentDAO.find_one_or_none(id=user.id)
        if student or non_student:
            raise HTTPException(status_code=400, detail="User has already added information.")

        if user.is_student:
            if user.group:
                await StudentDAO.add(id=user.id, group=user.group)
                student = await StudentDAO.find_one_or_none(id=user.id)
                return SUser(
                    tg_id=user_date.tg_id,
                    username=user_date.username,
                    first_name=user_date.first_name,
                    last_name=user_date.last_name,
                    is_student=SStudent.from_orm(student)
                )
            else:
                raise HTTPException(status_code=400, detail="Group must be provided for a student.")
        else:
            if user.passport:
                await NonStudentDAO.add(id=user.id, passport=user.passport)
                non_student = await NonStudentDAO.find_one_or_none(id=user.id)
                return SUser(
                    tg_id=user_date.tg_id,
                    username=user_date.username,
                    first_name=user_date.first_name,
                    last_name=user_date.last_name,
                    is_not_student=SNonStudent.from_orm(non_student)
                )
            else:
                raise HTTPException(status_code=400, detail="Passport must be provided for a non-student.")
    else:
        raise HTTPException(status_code=400, detail="User not found.")

