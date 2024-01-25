# Project Enigma

Django-based blog site

## Installation

Create .env file in the root of the project where manage.py is located and set the following variables:

```properties
EMAIL_SYSTEM_EMAIL="your@email.com"
EMAIL_SYSTEM_PASSWORD="your_password"
SECRET_KEY="secret_key"
DJANGO_DEBUG=True
```

These variables are optional, but EMAIL_SYSTEM_EMAIL and EMAIL_SYSTEM_PASSWORD is required for password restore
functionality.

### Install python requirements:

```shell
pip install -r requirements.txt
```

And finally, run the server.

```shell
python manage.py runserver
```

## Example images:

#### Main page

![Sample Image](./Images/main_page.png)

#### Create Post page

![Sample Image](./Images/add_post.png)

#### Post page

![Sample Image](./Images/added_post.png)

#### Login page

![Sample Image](./Images/login_page.png)

#### Mini profile

![Sample Image](./Images/mini_profile.png)

#### Profile page

![Sample Image](./Images/profile_page.png)

