
from collections import OrderedDict
import re
from typing import Dict, List

from app.config import ENGINE
from sqlalchemy import text

from app.sql_generation.prompt_helpers import schema_prompt, query_prompt

from app.utils import (extract_sql_query_from_yaml, get_assistant_message,
                       get_few_shot_messages)

MSG_WITH_ERROR_TRY_AGAIN = ("""
The SQL query you just generated resulted in the following error message:
---------------------
{error_message}
---------------------

- Provide an explanation of what went wrong and provide the fixed SQL query.

Provide the following YAML. Remember to indent with 4 spaces and use the correct YAML syntax using the following format:
Explanation: |
    (tabbed in) why the error happened
SQL: | 
    (tabbbed in) the SQL query line 1
    (tabbed in) the SQL query line 2
    ...
    
ENSURE TO PROVIDE A | AFTER EACH YAML KEY SO THE YAML GETS PARSED CORRECTLY""")


def make_default_messages(schemas_str: str) -> List[Dict[str, str]]:
    default_messages = []
    default_messages.extend(get_few_shot_messages(mode="text_to_sql"))
    return default_messages


def is_read_only_query(sql_query: str) -> bool:
    """
    Checks if the given SQL query string is read-only.
    Returns True if the query is read-only, False otherwise.
    """
    # List of SQL statements that modify data in the database
    modifying_statements = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', r'\bCREATE\b',
        r'\bALTER\b', r'\bGRANT\b', r'\bTRUNCATE\b', r'\bLOCK\s+TABLES\b', r'\bUNLOCK\s+TABLES\b'
    ]

    # Compile the regex pattern
    pattern = re.compile('|'.join(modifying_statements), re.IGNORECASE)

    # Check if the query contains any modifying statements
    if pattern.search(sql_query):
        return False

    # If no modifying statements are found, the query is read-only
    return True


class NotReadOnlyException(Exception):
    pass


class NullValueException(Exception):
    pass


def execute_sql(sql_query: str):
    if not is_read_only_query(sql_query):
        raise NotReadOnlyException("Only read-only queries are allowed.")

    with ENGINE.connect() as connection:
        connection = connection.execution_options(postgresql_readonly=True)
        with connection.begin():
            result = connection.execute(text(sql_query))

        column_names = list(result.keys())

        rows = [list(r) for r in result.all()]

        results = []
        for row in rows:
            result = OrderedDict()
            for i, column_name in enumerate(column_names):
                result[column_name] = row[i]
            results.append(result)

        result_dict = {
            "column_names": column_names,
            "results": results,
        }
        if results:
            result_dict["column_types"] = [
                type(r).__name__ for r in results[0]]

        return result_dict


def text_to_sql_with_retry(natural_language_query, table_names, k=3, messages=None, examples=[]):
    """
    Tries to take a natural language query and generate valid SQL to answer it K times
    """
    schema_message = [{'role': 'user', 'content': ''}]
    message_history = []
    model = "gpt-3.5-turbo-0301"

    example_messages = [{'role': 'user', 'content': example.get(
        'query', '')} for example in examples]

    if not messages:
        # ask the assistant to rephrase before generating the query
        _, table_content = schema_prompt.get_enums_and_tables(
            table_names)

        schema_message[0]['content'] = table_content

        content = query_prompt.command_prompt_cte(natural_language_query)
        message_history.append({
            "role": "user",
            "content": content
        })
    assistant_message = None
    sql_query = ""

    for _ in range(k):
        yield {'status': 'working', 'step': 'sql', 'state': 'Starting SQL Generation Attempt ' + str(_ + 1) + ' of ' + str(k) + '...'}
        try:
            try:
                payload = example_messages[:3] + \
                    schema_message + message_history
                assistant_message = get_assistant_message(
                    payload, model=model)
            except Exception as assistant_error:
                print('error getting assistant message', assistant_error)
                continue

            sql_data = extract_sql_query_from_yaml(
                assistant_message["message"]["content"])
            sql_query = sql_data["SQL"]

            response = execute_sql(sql_query)

            # Generated SQL query did not produce exception. Return result

            yield {'status': 'success', 'final_answer': True, 'step': 'sql', 'response': response, 'sql_query': sql_query}
            return

        except Exception as e:
            yield {'status': 'working', 'step': 'sql', 'state': 'Error: ' + str(e)}
            try:
                print('error executing sql: ', e)
                message_history.append({
                    "role": "assistant",
                    "content": sql_query
                })
                message_history.append({
                    "role": "user",
                    "content": MSG_WITH_ERROR_TRY_AGAIN.format(error_message=str(e))
                })
            except Exception as exc:
                print('oops, error: ', exc)

    print("Could not generate SQL query after {k} tries.".format(k=k))
    yield {'status': 'error', 'step': 'sql', 'response': None, 'sql_query': None}
