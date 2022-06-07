from datetime import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from api.web.models import GetTimetableApiRequest, SetTimetableApiRequest
from api.config import Config
from api.utils.singleton import Singleton
from .models import (
    Faculty,
    Group,
    Day,
    TimeCell,
    Discipline,
    DisciplineType,
    Lesson,
    Teacher,
    User,
    Room,
    Timetable
)


class DatabaseException(Exception):
    message = "Database exception"

    def __init__(self, message):
        self.message = message


class Database(metaclass=Singleton):
    def __init__(self):
        self.config = Config()
        engine = create_engine('sqlite:///schedule.sqlite')
        self.session = sessionmaker(bind=engine)()
        self.init_faculties()
        self.init_groups()
        self.init_time_cells()
        self.init_days()
        self.init_discipline_types()

    def add_user(self, name: str, faculty: str, group: str):
        """
        ADD USER
        :param name: username
        :param faculty: faculty name
        :param group: group name
        :return: None
        """
        user = User(name=name, faculty=faculty, group=group)
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def init_faculties(self):
        """
        INIT FACULTIES RECORDS
        :return: None
        """
        faculties = []
        for faculty in self.config.DB_FACULTIES:
            faculties.append(Faculty(**faculty))
        try:
            self.session.bulk_save_objects(faculties)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def init_groups(self):
        """
        INIT GROUP RECORDS
        :return:
        """
        for group in self.config.DB_GROUPS:
            course = group.get('course')
            for name in group.get('items'):
                try:
                    self.session.add(Group(course=course, name=name))
                    self.session.commit()
                except IntegrityError:
                    self.session.rollback()

    def init_days(self):
        """
        INIT DAYS RECORDS
        :return:
        """
        for day in self.config.DB_DAYS:
            try:
                self.session.add(Day(name=day))
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def init_time_cells(self):
        """
        INIT TIME CELLS RECORDS
        :return:
        """
        for cell in self.config.DB_TIME_CELLS:
            try:
                time_from = time(*[int(x) for x in cell.get('from').split(":")])
                time_to = time(*[int(x) for x in cell.get('to').split(":")])
                self.session.add(TimeCell(cell_num=cell.get('cell_num'), time_from=time_from, time_to=time_to))
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def init_discipline_types(self):
        """
        INIT DISCIPLINE TYPES
        :return:
        """
        for name in self.config.DB_DISCIPLINE_TYPES:
            self.session.add(DisciplineType(name=name))
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def search_or_create_discipline(self, disc_type: str, disc_name: str):
        """
        SEARCH OR CREATE DISCIPLINE
        :param disc_type: discipline type, ex: lectures
        :param disc_name: discipline name, ex: physics
        :return: discipline object
        """
        discipline_type = self.session.query(DisciplineType).filter(DisciplineType.name == disc_type).one()
        discipline = Discipline(name=disc_name, type_id=discipline_type.discipline_type_id)
        try:
            self.session.add(discipline)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            discipline = self.session.query(Discipline)\
                .filter(Discipline.name == disc_name, Discipline.discipline_type == discipline_type).one()
        return discipline

    def search_or_create_teacher(self, full_name: str):
        """
        SEARCH OR CREATE TEACHER
        :param full_name: full name for teacher, ex: Ivanov I.A.
        :return: teacher object
        """
        teacher = Teacher(full_name=full_name)
        try:
            self.session.add(teacher)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            teacher = self.session.query(Teacher).filter(Teacher.full_name == full_name).one()
        return teacher

    def search_or_create_room(self, name):
        """
        SEARCH OR CREATE ROOM
        :param name: room name, ex: 1-543
        :return: room object
        """
        room = Room(name=name)
        try:
            self.session.add(room)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            room = self.session.query(Room).filter(Room.name == name).one()
        return room

    def search_or_create_lesson(self, discipline: Discipline, teacher: Teacher, room: Room):
        """
        SEARCH OR CREATE LESSON
        :param discipline: discipline object
        :param teacher: teacher object
        :param room: room object
        :return: lesson object
        """
        lesson = Lesson(discipline=discipline, teacher=teacher, room=room)
        try:
            self.session.add(lesson)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            lesson = self.session.query(Lesson).filter(Lesson.discipline_id == discipline.discipline_id,
                                                       Lesson.teacher_id == teacher.teacher_id,
                                                       Lesson.room_id == room.room_id).one()
        return lesson

    def create_timetable(self,
                         week_num: int,
                         faculty: Faculty,
                         group: Group,
                         day: Day,
                         time_cell: TimeCell,
                         lesson: Lesson):
        timetable = Timetable(week_num=week_num,
                              faculty=faculty,
                              group=group,
                              day=day,
                              time_cell=time_cell,
                              lesson=lesson)
        try:
            self.session.add(timetable)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
        return timetable

    def get_timetable(self, request: GetTimetableApiRequest):
        """
        GET LESSONS BY FACULTY, GROUP, WEEK_NUMBER, DAY_NUMBER
        :param request: dict with faculty, group, week_number, day_number
        :return: list of information about lessons
        """
        try:
            faculty = self.session.query(Faculty).filter(Faculty.tag == request.faculty_tag).one()
        except NoResultFound:
            raise DatabaseException("Faculty not found")
        try:
            group = self.session.query(Group).filter(Group.name == request.group_name).one()
        except NoResultFound:
            raise DatabaseException("Group not found")
        try:
            day = self.session.query(Day).filter(Day.day_id == request.day_num).one()
        except NoResultFound:
            raise DatabaseException("Day not found")
        rows = self.session.query(Timetable).filter(
            Timetable.faculty_id == faculty.faculty_id,
            Timetable.group_id == group.group_id,
            Timetable.week_num == request.week_num,
            Timetable.day_id == day.day_id).all()
        lessons = []
        for row in rows:
            lessons.append({
                'discipline_name': row.lesson.discipline.name,
                'discipline_type': row.lesson.discipline.discipline_type.name,
                'teacher_full_name': row.lesson.teacher.full_name,
                'room_name': row.lesson.room.name,
                'time_cell': {
                    'num': row.time_cell.cell_num,
                    'time_from': str(row.time_cell.time_from),
                    'time_to': str(row.time_cell.time_to)
                }
            })
        return lessons

    def set_timetable(self, request: SetTimetableApiRequest):
        """
        CREATE NEW TIMETABLE RECORD
        :param request: params for creating record
        :return: None
        """
        try:
            faculty = self.session.query(Faculty).filter(Faculty.tag == request.faculty_tag).one()
        except NoResultFound:
            raise DatabaseException("Faculty not found")
        try:
            group = self.session.query(Group).filter(Group.name == request.group_name).one()
        except NoResultFound:
            raise DatabaseException("Group not found")
        try:
            day = self.session.query(Day).filter(Day.day_id == request.day_num).one()
        except NoResultFound:
            raise DatabaseException("Day not found")
        try:
            time_cell = self.session.query(TimeCell).filter(TimeCell.time_cell_id == request.time_cell_num).one()
        except NoResultFound:
            raise DatabaseException("Time cell not found")
        discipline = self.search_or_create_discipline(disc_type=request.discipline_type,
                                                      disc_name=request.discipline_name)
        teacher = self.search_or_create_teacher(full_name=request.teacher_full_name)
        room = self.search_or_create_room(name=request.room_name)
        lesson = self.search_or_create_lesson(discipline=discipline, teacher=teacher, room=room)

        try:
            self.session.query(Timetable).filter(Timetable.week_num == request.week_num,
                                                 Timetable.faculty_id == faculty.faculty_id,
                                                 Timetable.group_id == group.group_id,
                                                 Timetable.day_id == day.day_id,
                                                 Timetable.time_cell_id == time_cell.time_cell_id).one()
            raise DatabaseException("Timetable already created")
        except NoResultFound:
            self.create_timetable(week_num=request.week_num,
                                  faculty=faculty,
                                  group=group,
                                  day=day,
                                  time_cell=time_cell,
                                  lesson=lesson)

    def reset_timetable(self):
        try:
            self.session.query(Discipline).delete()
            self.session.query(Lesson).delete()
            self.session.query(Room).delete()
            self.session.query(Teacher).delete()
            self.session.query(Timetable).delete()
            self.session.commit()
        except Exception as err:
            raise DatabaseException(err)
