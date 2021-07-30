from .mysql_connector import exec_cmd

def get_last_applications():
    """ Загрузка всех заявок за определенный интервал времени """
    with open('sql/get_applications.sql', 'r') as file:
        cmd = file.read()
    return exec_cmd(cmd)

def get_application(id:int):
    """ Получение заявки по id """
    cmd = f"SELECT * FROM pro_creditup_cab.finplugs_creditup_applications WHERE id = '{id}'"
    return exec_cmd(cmd)