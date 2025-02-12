Hi! This is the backend repo for the cs-connections app.

The main page of the project can be found at: [frontend repo](https://github.com/ethan-fong/cs-connections)

## Dev Info

All the views are under /connections_app

They are split into admin_views.py, student_views.py and instructor_views.py

#### Admin Views
Superuser endpoints that can create courses and edit in any course

#### Student Views
A freely accesesible public API to fetch game info (read-only) and stats in any course

#### Instructor Views
Endpoints to check if the user is logged in (via cookies) and what games are in each course. Also allows instructors to delete games within their own courses

Note: Instructor accounts and the superuser account can upload games with a published=true field and also delete games within the same course

## Additional Dev Info

When developing locally, you can make use of the accounts in dev_accts.txt to test authentication/authorization features