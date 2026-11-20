from .._imports import *
from .._consts import *
from ..funcs import *



class StudentQueryDialogGetPersonMixin:
    def _get_person(self, person_id):
        if get_server_url():
            try:
                from network.client import api_person
                data = api_person(person_id)
                return type('Person', (), data)()
            except Exception:
                return None
        else:
            session = get_session()
            try:
                return session.query(Person).filter(Person.id == person_id).first()
            finally:
                session.close()
