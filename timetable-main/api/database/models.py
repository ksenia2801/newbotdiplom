from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Time
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///schedule.sqlite')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(), unique=True, index=True)
    faculty = Column(String())
    group = Column(String())
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, faculty, group):
        self.name = name
        self.faculty = faculty
        self.group = group


class Faculty(Base):
    __tablename__ = "faculties"

    faculty_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String())
    tag = Column(String(), unique=True)

    def __init__(self, name, tag):
        self.name = name
        self.tag = tag


class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(), unique=True)
    course = Column(Integer())

    def __init__(self, course, name):
        self.course = course
        self.name = name


class Day(Base):
    __tablename__ = 'days'

    day_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(), unique=True)

    def __init__(self, name):
        self.name = name


class TimeCell(Base):
    __tablename__ = 'time_cells'

    time_cell_id = Column(Integer(), primary_key=True, index=True)
    cell_num = Column(Integer(), unique=True)
    time_from = Column(Time())
    time_to = Column(Time())

    def __init__(self, cell_num, time_from, time_to):
        self.cell_num = cell_num
        self.time_from = time_from
        self.time_to = time_to


class DisciplineType(Base):
    __tablename__ = 'discipline_types'

    discipline_type_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(), unique=True)

    def __init__(self, name):
        self.name = name


class Discipline(Base):
    __tablename__ = 'disciplines'

    discipline_id = Column(Integer(), primary_key=True, index=True)
    type_id = Column(Integer(), ForeignKey('discipline_types.discipline_type_id'))
    name = Column(String(), nullable=False)

    discipline_type = relationship('DisciplineType', backref=backref('disciplines'))

    __table_args__ = (UniqueConstraint('type_id', 'name'),)

    def __init__(self, name, type_id):
        self.name = name
        self.type_id = type_id


class Teacher(Base):
    __tablename__ = 'teachers'

    teacher_id = Column(Integer(), primary_key=True, index=True)
    full_name = Column(String(), nullable=False, unique=True)

    def __init__(self, full_name):
        self.full_name = full_name


class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Lesson(Base):
    __tablename__ = 'lessons'

    lesson_id = Column(Integer(), primary_key=True, index=True)
    discipline_id = Column(Integer(), ForeignKey('disciplines.discipline_id'))
    teacher_id = Column(Integer(), ForeignKey('teachers.teacher_id'))
    room_id = Column(Integer(), ForeignKey('rooms.room_id'))

    discipline = relationship('Discipline', backref=backref('lessons'))
    teacher = relationship('Teacher', backref=backref('lessons'))
    room = relationship('Room', backref=backref('lessons'))

    __table_args__ = (UniqueConstraint('discipline_id', 'teacher_id', 'room_id'),)

    def __init__(self, discipline, teacher, room):
        self.discipline = discipline
        self.teacher = teacher
        self.room = room


class Timetable(Base):
    __tablename__ = 'timetable'

    timetable_id = Column(Integer(), primary_key=True, index=True)
    faculty_id = Column(Integer(), ForeignKey('faculties.faculty_id'))
    group_id = Column(Integer(), ForeignKey('groups.group_id'))
    week_num = Column(Integer())
    day_id = Column(Integer(), ForeignKey('days.day_id'))
    time_cell_id = Column(Integer(), ForeignKey('time_cells.time_cell_id'))
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'))
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    faculty = relationship('Faculty', backref=backref('timetable'))
    group = relationship('Group', backref=backref('timetable'))
    day = relationship('Day', backref=backref('timetable'))
    time_cell = relationship('TimeCell', backref=backref('timetable'))
    lesson = relationship('Lesson', backref=backref('timetable'))

    __table_args__ = (UniqueConstraint('faculty_id', 'group_id', 'week_num', 'day_id', 'time_cell_id',),)

    def __init__(self, week_num: int, faculty: Faculty, group: Group, day: Day, time_cell: TimeCell, lesson: Lesson):
        self.week_num = week_num
        self.faculty = faculty
        self.group = group
        self.day = day
        self.time_cell = time_cell
        self.lesson = lesson


Base.metadata.create_all(engine)
