
# Substrait Fiddle Back-end

APIs for [Substrait Fiddle](https://www.github.com/sanjibansg/substrait-fiddle-frontend)


## Features

- Async API service for validating [substrait](https://substrait.io/) plans and translating queries.
- Uses [DuckDB](https://duckdb.org/docs/extensions/substrait) for producing substrait plans from SQL queries for further validation.



## Installation

Clone the github repository
```bash
git clone https://github.com/sanjibansg/substrait-fiddle-backend.git
cd substrait-fiddle-backend/
```
Install the requirements
```bash
pip install -r requirements.txt
```
Run the server in port `9090`
```bash
uvicorn app:app --reload --port 9090 
```
or, just run the server as a docker container

```bash
docker build -t substrait-fiddle-backend .
docker run -d -p 9090:9090 substrait-fiddle-backend
```

## Documentation

View the auto-generated documentation through the Swagger UI. Once the application startup is complete, visit `http://127.0.0.1:9090/docs`

## License

[Apache-2.0 license](https://github.com/sanjibansg/substrait-fiddle-backend/blob/main/LICENSE)
