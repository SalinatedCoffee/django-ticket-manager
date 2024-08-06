# Ticket Manager

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

### Overview
A *very* barebones Django application that manages events and user registration, as well as authenticating the registration of a user to an event via TOTPs per the [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) standard.  
A single PostgreSQL instance is used in the persistance layer, where all entities are stored in a single database. The project does not have a functioning frontend (yet) and all communications to and from the server are performed via exposed REST API endpoints.  

#### File Structure

```txt
.
├── README.md
└── ticketmgr
    ├── entityhandler
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── manage.py
    ├── otphandler
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── services.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── requirements.txt
    └── ticketmgr
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
```

#### ERD
![ERD](documents/erd.svg)

#### System Architecture
![Diagram](documents/systemdiagram.svg)
The main application `ticketmgr` relies on two other applications.  
`entityhandler` handles all of the entities used in this project, from persistence in the PostgreSQL instance to inter-entity business logic.  
`otphandler` is responsible for any and all operations related to admission authentication, checking whether a user is truly registered to an event given the uuid of the user, uuid of the event, and the client-generated TOTP.  

### `requirements.txt`

```txt
asgiref==3.5.2
Django==4.1.3
djangorestframework==3.14.0
psycopg2==2.9.5
python-dotenv==0.21.0
pytz==2022.6
sqlparse==0.4.3
typing_extensions==4.4.0
```

### Future Additions I'd Like to Address

- Functioning SPA frontend
- Feature complete API endpoints
- Docker containerization for easy deployment
- Configurable TOTP module
- Enhancements to event registration and attendee authentication
- Refactoring of the domain layer
- Migration to external web server instance
- Enhancements to make TOTP secrets more robust
