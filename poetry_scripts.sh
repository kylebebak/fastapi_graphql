alias poetry_lint="poetry run mypy . && poetry run flake8 . && poetry run black ."
alias poetry_start="poetry run uvicorn main:app --reload"
