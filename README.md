# Substrait Fiddle Back-end

APIs for Substrait Fiddle

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
Run the server
```bash
uvicorn app:app --reload
```
## Documentation
View the auto-generated documentation through the Swagger UI. Once the application startup is complete, visit `http://127.0.0.1:8000/docs`

## License

[Apache-2.0 license](https://github.com/sanjibansg/substrait-fiddle-backend/blob/main/LICENSE)
