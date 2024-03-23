# Team 2 Web Project

```bash
alembic revision --autogenerate -m 'Init'
```

```bash
alembic upgrade head
```

```bash
uvicorn main:app --host localhost --port 8000 --reload
```


```bash
poetry add sphinx -G dev
```

```bash
sphinx-quickstart docs
```


```bash
make html
```

```bash
pytest --cov
```