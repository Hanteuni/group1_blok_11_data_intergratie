import json
import psycopg2
from typing import Optional, Any, List, TypeVar, Type, Callable, cast
from datetime import date
import sys

T = TypeVar("T")

def from_none(x: Any) -> Any:
    """ Helper function for asserting if the parameter type is None
    :param x: The type to assert
    :return: x is None
    """
    assert x is None
    return x

def from_str(x: Any) -> str:
    """ Helper function for asserting if the parameter type is String
    :param x: The type to assert
    :return: x is String
    """
    assert isinstance(x, str)
    return x

def from_union(fs, x):
    """ Helper function for splitting a union
    :param x: The union to split
    :return: Splitted union or False
    """
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False

def is_type(t: Type[T], x: Any) -> T:
    """ Helper function for asserting if x is an instance of type t
    :param x: The type to assert
    :param t: The type with which x is asserted
    :return: x is type t
    """
    assert isinstance(x, t)
    return x

def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    """ Helper function for asserting if x is an instance of type t from a list
    :param x: The type to assert
    :param t: The type with which x is asserted
    :return: list with x's is type t
    """
    assert isinstance(x, list)
    return [f(y) for y in x]

def to_class(c: Type[T], x: Any) -> dict:
    """ Helper function for casting x to type t
    :param x: The type to to cast
    :param t: The type to which x has to be casted
    :return: x as t if castable
    """
    assert isinstance(x, c)
    return cast(Any, x).to_dict()

class Profile:
    birth_year: Optional[int]
    birth_month: Optional[int]
    sex: Optional[str]
    ethnicity: Optional[str]

    def __init__(self, birth_year: Optional[int], birth_month: Optional[int], sex: Optional[str], ethnicity: Optional[str]) -> None:
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.sex = sex
        self.ethnicity = ethnicity

    @staticmethod
    def from_dict(obj: Any) -> 'Profile':
        assert isinstance(obj, dict)
        birth_year = from_union([from_none, lambda x: int(from_str(x))], obj.get("birth_year"))
        birth_month = from_union([from_none, lambda x: int(from_str(x))], obj.get("birth_month"))
        sex = from_union([from_str, from_none], obj.get("Sex"))
        ethnicity = from_union([from_str, from_none], obj.get("Ethnicity"))
        return Profile(birth_year, birth_month, sex, ethnicity)

    def to_dict(self) -> dict:
        result: dict = {}
        result["birth_year"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.birth_year)
        result["birth_month"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.birth_month)
        result["Sex"] = from_union([from_str, from_none], self.sex)
        result["Ethnicity"] = from_union([from_str, from_none], self.ethnicity)
        return result

class Pgpc:
    profile: Optional[Profile]
    conditions_or_symptoms: Optional[List[str]]

    def __init__(self, profile: Optional[Profile], conditions_or_symptoms: Optional[List[str]]) -> None:
        self.profile = profile
        self.conditions_or_symptoms = conditions_or_symptoms

    @staticmethod
    def from_dict(obj: Any) -> 'Pgpc':
        assert isinstance(obj, dict)
        profile = from_union([Profile.from_dict, from_none], obj.get("Profile"))
        conditions_or_symptoms = from_union([lambda x: from_list(from_str, x), from_none], obj.get("Conditions_or_symptoms"))
        return Pgpc(profile, conditions_or_symptoms)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Profile"] = from_union([lambda x: to_class(Profile, x), from_none], self.profile)
        result["Conditions_or_symptoms"] = from_union([lambda x: from_list(from_str, x), from_none], self.conditions_or_symptoms)
        return result

class PgpcInformation:
    pgpc_1: Optional[Pgpc]
    pgpc_11: Optional[Pgpc]
    pgpc_21: Optional[Pgpc]

    def __init__(self, pgpc_1: Optional[Pgpc], pgpc_11: Optional[Pgpc], pgpc_21: Optional[Pgpc]) -> None:
        self.pgpc_1 = pgpc_1
        self.pgpc_11 = pgpc_11
        self.pgpc_21 = pgpc_21

    @staticmethod
    def from_dict(obj: Any) -> 'PgpcInformation':
        assert isinstance(obj, dict)
        pgpc_1 = from_union([Pgpc.from_dict, from_none], obj.get("PGPC-1"))
        pgpc_11 = from_union([Pgpc.from_dict, from_none], obj.get("PGPC-11"))
        pgpc_21 = from_union([Pgpc.from_dict, from_none], obj.get("PGPC-21"))
        return PgpcInformation(pgpc_1, pgpc_11, pgpc_21)

    def to_dict(self) -> dict:
        result: dict = {}
        result["PGPC-1"] = from_union([lambda x: to_class(Pgpc, x), from_none], self.pgpc_1)
        result["PGPC-11"] = from_union([lambda x: to_class(Pgpc, x), from_none], self.pgpc_11)
        result["PGPC-21"] = from_union([lambda x: to_class(Pgpc, x), from_none], self.pgpc_21)
        return result

def pgpc_information_from_dict(s: Any) -> PgpcInformation:
    return PgpcInformation.from_dict(s)

def pgpc_information_to_dict(x: PgpcInformation) -> Any:
    return to_class(PgpcInformation, x)

def main(file):
    """ Function which extracts the pgpc data from the created JSON file. It converts the data structure into the object oriented models described above. It will then insert these models into the postgreSQL database.
    :param file: The JSON file containing the pgpc data
    """
    with open(file,'r') as file:
        json_string = file.read()
        result = pgpc_information_from_dict(json.loads(json_string))

        conn = psycopg2.connect(host="145.74.104.145", dbname="postgres", user="j3_g1", password="Blaat1234")

        pgpc_sources = {1: result.pgpc_1, 11: result.pgpc_11, 21: result.pgpc_21}

        print(pgpc_sources)

        cursor = conn.cursor()

        for id, pgpc in pgpc_sources.items():
            if pgpc is None:
                continue

            cursor.execute("INSERT INTO PERSON(person_id, year_of_birth, month_of_birth, gender_source_value, ethnicity_source_value, gender_concept_id, race_concept_id, ethnicity_concept_id) \
                VALUES ({}, {}, {}, \'{}\', \'{}\', {}, {}, {})".format(
                id, pgpc.profile.birth_year, pgpc.profile.birth_month, pgpc.profile.sex, pgpc.profile.ethnicity, 1, 1, 1))

            con_occ_id = id
            for cond in pgpc.conditions_or_symptoms:
                cursor.execute("INSERT INTO CONDITION_OCCURRENCE(condition_occurrence_id, person_id, condition_concept_id, condition_start_date, condition_type_concept_id, condition_source_value) \
                                VALUES ({}, {}, {}, \'{}\', {}, \'{}\')".format(
                                    con_occ_id, id, 0, date.today(), 0, cond
                                ))
                con_occ_id += 1
            
        conn.commit()


if __name__ == "__main__":
    if (len(sys.argv) == 1):
        print("Json file parameter missing, aborting.")
        quit()
    
    main(sys.argv[1])
    
