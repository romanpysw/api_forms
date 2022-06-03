from fastapi import FastAPI
from databases import Database

from pydantic import ValidationError
from models import FormField, FormTemplate, FormRecord

app = FastAPI()

database = Database("sqlite:///sqlite/form.db")


######################################################################################

form_field_separator = ';=%$%=;'


@app.on_event("startup")
async def database_connect() -> None:
    """Подключение к базе данных при старте приложения"""

    await database.connect()


@app.on_event("shutdown")
async def database_disconnect() -> None:
    """Отключение от базы данных при заврешении приложения"""

    await database.disconnect()


@app.post('/post_form')
async def post_form(form_template:FormTemplate) -> dict:
    """Запись формы в БД от клиента"""

    try:
        fields = ""
        for field in form_template.fields:
            fields += field.json() + form_field_separator
        fields = fields[:-len(form_field_separator)]

        query = f""" INSERT INTO form_template (form_uid, author, time, name, fields)
                    VALUES ({form_template.form_uid}, '{form_template.author}', 
                            {form_template.time}, '{form_template.name}',
                            '{str(fields)}');"""

        await database.execute(query=query)

        return {'jsonrpc': '2.0', 'result': [], 'id': form_template.form_uid}

    except ValidationError as e:

        return {'jsonrpc': '2.0', 'result': [], 'error': [{'code':1000},{'msg':'Bad Form!'},{'data':e.__doc__}], 'id': form_template.form_uid}


@app.get('/get_form')
async def get_form(form_uid:int) -> dict:
    """Поиск формы в БД по form_uid"""

    query = f""" SELECT form_uid, author, time, name, fields FROM form_template
                 WHERE form_uid={form_uid};"""

    db_response = await database.fetch_one(query=query)

    if db_response:
        db_form_fields = db_response[4].split(form_field_separator)

        for i in range(len(db_form_fields)):
            db_form_fields[i] = FormField.parse_raw(db_form_fields[i])

        form_template = FormTemplate(   form_uid=db_response[0],
                                        author=db_response[1],
                                        time=db_response[2],
                                        name=db_response[3],
                                        fields=db_form_fields)

        return {'jsonrpc': '2.0', 'result': [form_template], 'id': form_uid}

    else:
        return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}


@app.get('/del_form')
async def delete_form(form_uid:int) -> dict:
    """Удаление формы из БД по form_uid"""

    query = f""" DELETE FROM form_template WHERE form_uid={form_uid};"""
    await database.execute(query=query)
    return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}


@app.post('/update_form')
async def update_form(form_uid:int,  name:str, form_template:FormTemplate) -> dict:
    """Обновление записи формы в БД по form_uid"""

    try:
        fields = ""
        for field in form_template.fields:
            fields += field.json() + form_field_separator
        fields = fields[:-len(form_field_separator)]
        query = f""" UPDATE form_template 
                    SET time={form_template.time}, name='{form_template.name}', fields='{str(fields)}'
                    WHERE form_uid={form_uid} AND author='{name}';"""
        await database.execute(query=query)
        return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}

    except ValidationError as e:
        return {'jsonrpc': '2.0', 'result': [], 'error': [{'code':1000},{'msg':'Bad Form!'},{'data':e.__doc__}], 'id': form_uid}


@app.post('/post_record')
async def post_record(record:FormRecord) -> dict:
    """Запись ответа но форму в БД"""

    try:
        values = ""
        for value in record.value:
            values += value.json() + form_field_separator
        values = values[:-len(form_field_separator)]
        query = f""" INSERT INTO form_record (form_uid, author, time, fields)
                    VALUES ({record.form_uid}, '{record.author}', 
                            {record.time}, '{str(values)}');"""
        await database.execute(query=query)
        return {'jsonrpc': '2.0', 'result': [], 'id': record.form_uid}

    except ValidationError as e:
        return {'jsonrpc': '2.0', 'result': [], 'error': [{'code':1000},{'msg':'Bad Form!'},{'data':e.__doc__}], 'id': record.form_uid}


@app.get('/get_records')
async def get_records(form_uid:int) -> dict:
    """Получение всех ответов на форму из БД по form_uid"""

    query = f""" SELECT form_uid, author, time, fields FROM form_record
                 WHERE form_uid={form_uid};"""

    values = []
    to_ret = []

    db_response = await database.fetch_all(query=query)

    if db_response:

        for i in range(len(db_response)):
            values = db_response[i][-1].split(form_field_separator)
            for j in range(len(values)):
                values[j] = FormField.parse_raw(values[j])
            # print(db_response[i])
            to_ret.append(FormRecord(   form_uid=db_response[i][0], 
                                        author=db_response[i][1],
                                        time=db_response[i][2],
                                        value=values))
            del values

        return {'jsonrpc': '2.0', 'result': to_ret, 'id': form_uid}

    else:

        return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}


@app.get('/get_record')
async def get_record(form_uid:int, name:str) -> dict:
    """Получение ответа на форму из БД по form_uid и name автора ответа"""

    query = f""" SELECT form_uid, author, time, fields FROM form_record    
                 WHERE form_uid={form_uid} AND author='{name}';"""

    values = []
    to_ret = []

    db_response = await database.fetch_all(query=query)

    if db_response:

        for i in range(len(db_response)):
            values = db_response[i][-1].split(form_field_separator)
            for j in range(len(values)):
                values[j] = FormField.parse_raw(values[j])
            # print(db_response[i])
            to_ret.append(FormRecord(   form_uid=db_response[i][0], 
                                        author=db_response[i][1],
                                        time=db_response[i][2],
                                        value=values))
            del values

        return {'jsonrpc': '2.0', 'result': to_ret, 'id': form_uid}
    
    else:
        return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}


@app.post('/update_record')
async def update_record(form_uid:int, name:str, new_record:FormRecord) -> dict:
    """Обновление записи ответа по form_uid и name автора ответа"""

    try:
        values = ""
        for value in new_record.value:
            values += value.json() + form_field_separator
        values = values[:-len(form_field_separator)]
        query = f""" UPDATE form_record
                    SET time={new_record.time}, fields='{str(values)}'
                    WHERE form_uid={form_uid} AND author='{name}';"""
        await database.execute(query=query)

        return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}
    
    except ValidationError as e:

        return {'jsonrpc': '2.0', 'result': [], 'error': [{'code':1000},{'msg':'Bad Form!'},{'data':e.__doc__}], 'id': form_uid}


@app.get('/del_record')
async def delete_record(form_uid:int, name:str) -> dict:
    """Удаление ответа на форму по form_uid и name автора ответа"""

    query = f""" DELETE FROM form_record WHERE form_uid={form_uid} AND author='{name}';"""

    await database.execute(query=query)

    return {'jsonrpc': '2.0', 'result': [], 'id': form_uid}


