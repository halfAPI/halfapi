#!/usr/bin/env python3
from starlette.exceptions import HTTPException
from .responses import CSVResponse

"""
This is the *query* library that contains all the useful functions to treat our
queries
"""

def parse_query(q: str = ""):
    """
    Returns the fitting Response object according to query parameters.

    The parse_query function handles the following arguments in the query 
    string : format, limit, and offset
    It returns a callable function that returns the desired Response object.

        Parameters:
            q (str): The query string "q" parameter, in the format
                key0:value0|...|keyN:valueN

        Returns:
            Callable[[half_orm.model.Model], Response]

        Available query arguments:
            format:
                - csv
                - json
            limit: int > 0
            offset: int > 0


        Examples:

            >>> parse_query()
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('format:csv')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('format:json')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('format:csv|limit:10')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('format:csv|offset:10')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('format:csv|limit:10|offset:10')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('limit:10')
            <function parse_query.<locals>.select at 0x...>

            >>> parse_query('limit=10')
            Traceback (most recent call last):
                ...
            fastapi.exceptions.HTTPException: 400


    """

    params = {}
    if len(q) > 0:
        try:
            split_ = lambda x : x.split(':')
            params = dict(map(split_, q.split('|')))
        except ValueError:
            raise HTTPException(400)
        split_ = lambda x : x.split(':')
        params = dict(map(split_, q.split('|')))

    def select(obj):

        if 'limit' in params and int(params['limit']) > 0:
            obj.limit(int(params['limit']))

        if 'offset' in params and int(params['offset']) > 0:
            obj.offset(int(params['offset']))

        if 'format' in params and params['format'] == 'csv':
            return CSVResponse([elt for elt in obj.select()])

        return [elt for elt in obj.select()]

    return select
