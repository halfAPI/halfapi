#!/usr/bin/env python3
# builtins
import csv
from datetime import date
from io import TextIOBase, StringIO

# asgi framework
from starlette.responses import Response

class NotFoundResponse(Response):
    """ The 404 Not Found default Response  
    """
    def __init__(self):
        super().__init__(status_code=404)

class ForbiddenResponse(Response):
    """ The 401 Not Found default Response  
    """
    def __init__(self):
        super().__init__(status_code = 401)

class CSVResponse(Response):
    def __init__(self, obj):
        
        with StringIO() as csv_file:
            csv_obj = csv.writer(csv_file, dialect="excel")
            csv_obj.writerows([elt.values() for elt in obj])
            filename = f'Personnels_LIRMM-{date.today()}.csv'

            super().__init__(
                content=csv_file.getvalue(),
                headers={ 
                    'Content-Type': 'text/csv; charset=UTF-8',
                    'Content-Disposition': f'attachment; filename="{filename}"'},
                status_code = 200)
