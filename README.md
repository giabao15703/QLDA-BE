# NextPro Core API

# API
- djangorestframework

# Auth
- django-rest-auth
- django-allauth
# Create Master Admin
    - Create user with user_type is amdin in table users_user
    - Create permission in table users_groups_permissions with role is 1  and group_id is null
    - In table users_user_permission create permission  with user_id and  permission_id 

# Run Unit Test
    docker-compose exec core pytest
    docker-compose exec core py.test -s

# Code Coverage
    - Run Code Coverage:
        docker-compose exec core pytest --cov

    - Check the report Coverage:
        docker-compose exec core coverage report

# set up and start server in local
    - install pyenv
        mac os: https://github.com/pyenv/pyenv
        window: https://github.com/pyenv-win/pyenv-win
    - install make
        mac os: https://formulae.brew.sh/formula/make
        window: https://gnuwin32.sourceforge.net/packages/make.htm
    - install docker desktop

    - run commands     
        docker compose up -d
        makemigrations.sh
        migrations.sh
        cd project
        ../loaddata.sh
        cd ..

        pyenv install 3.7.4
        pyenv global 3.7.4
        pyenv local 3.7.4

    - check if python is the right version:
        python -V
    
    - if it's right version continue with below commands:
        for window: make run-window
        for mac: make run
    