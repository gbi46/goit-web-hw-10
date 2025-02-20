docker compose up -d
docker run -d --name postgres_container_1 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=567234 -e POSTGRES_DB=contacts_db -p 5432:5432 postgres
python authors/manage.py runserver