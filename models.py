from sqlalchemy import Column, Integer, LargeBinary, String
from db import Base


class Inscripcion(Base):
    __tablename__ = "inscripciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_enc = Column(LargeBinary, nullable=False)
    apellidos_enc = Column(LargeBinary, nullable=False)
    dni_enc = Column(LargeBinary, nullable=False)
    telefono_enc = Column(LargeBinary, nullable=False)
    curso_enc = Column(LargeBinary, nullable=False)
    participo_prev = Column(Integer, nullable=False)  # 0 = no, 1 = sí
    precio_plan = Column(String(50), nullable=False)
