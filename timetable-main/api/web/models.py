from pydantic import BaseModel
from pydantic import validator


class GetTimetableApiRequest(BaseModel):
    faculty_tag: str
    group_name: str
    week_num: int
    day_num: int

    @validator('day_num')
    def day_num_must_be_from_1_to_7(cls, v):
        if v < 1 or v > 7:
            raise ValueError('day_num must be from 1 to 7')
        return v


class SetTimetableApiRequest(BaseModel):
    faculty_tag: str
    group_name: str
    week_num: int
    day_num: int
    time_cell_num: int
    discipline_type: str
    discipline_name: str
    teacher_full_name: str
    room_name: str

    @validator('day_num')
    def day_num_must_be_from_1_to_7(cls, v):
        if v < 1 or v > 7:
            raise ValueError('day_num must be from 1 to 7')
        return v

    @validator('time_cell_num')
    def time_cell_num_must_be_from_1_to_7(cls, v):
        if v < 1 or v > 7:
            raise ValueError('time_cell_num must be from 1 to 7')
        return v


class ResetTimetableApiRequest(BaseModel):
    token: str

    @validator('token')
    def valid_clear_token(cls, v):
        if v != '123456789':
            raise ValueError('incorrect clear token')
        return v
