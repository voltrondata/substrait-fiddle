
# Substrait Fiddle

An online tool to share, debug, and prototype [Substrait](https://substrait.io/) plans


## Features

- Code a substrait plan in `JSON`/`SQL` or upload a file.
- [Validate](https://github.com/substrait-io/substrait-validator) a substrait plan on specified override levels.
- Visualize the generated substrait plan and save it as SVG or PNG.
- Explore the plan's relations and their constituent properties


## Installation

Clone the github repository

```
git clone https://github.com/voltrondata/substrait-fiddle.git
cd substrait-fiddle/
```
Fiddle requires the [FastAPI back-end](https://github.com/voltrondata/substrait-fiddle/api) for APIs. Prior installation and operation of the service is required.
### API Service
To run it in PROD, use the complete URL, and set the environment variable. This step can be ignored in local development, 
where the default user and port is used.

```
// for PROD
export PROD_MONGO_URL=url

cd api/
pip install -r requirements.txt
uvicorn app:app --reload --port 9090 
```
or, just run the server as a docker container.
```
docker build -t substrait-fiddle-backend .
docker run -d -p 9090:9090 substrait-fiddle-backend
```
Now, let's run the client service for the web application.

### Client Service
Install the requirements
```
cd ../client/
npm install
```

Compile and hot-reload for development

```
npm run dev
```

Compile and minify for production

```
npm run build
```

Preview the production
```
npm run preview
```
## Testing

### Client Service

Run the Cypress E2E test in GUI mode
```
npm run cypress:open
```
Run the Cypress E2E test in headless mode
```
npm run cypress:headless
```
Run the Vitest for unit and component testing
```
npm run test
```

### API Service
Run Pytest for testing various APIs
```
pytest test.py
```

## Documentation

View the auto-generated documentation for the [API Service](https://github.com/voltrondata/substrait-fiddle/api) through the Swagger UI. Once the application startup is complete, visit `http://127.0.0.1:9090/docs`

## License

[Apache-2.0 license](https://github.com/voltrondata/substrait-fiddle/blob/main/LICENSE)

