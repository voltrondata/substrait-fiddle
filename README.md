
# Substrait Fiddle
Visualize a [Substrait](https://substrait.io/) plan

## Features

- Code a substrait plan in `JSON`/`SQL` or upload a file.
- [Validate](https://github.com/substrait-io/substrait-validator) a substrait plan on specified override levels.
- Visualize the generated substrait plan and save it as SVG or PNG.
- Explore the plan's relations and their constituent properties


## Installation

Fiddle requires the [substrait-fiddle-backend](https://github.com/sanjibansg/substrait-fiddle-backend) for APIs. Prior installation and execution of the service is required.

Clone the github repository

```
git clone https://github.com/sanjibansg/substrait-fiddle.git
cd substrait-fiddle/
```

Install the requirements

```
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
    
## License

[Apache-2.0 license](https://github.com/sanjibansg/substrait-fiddle-backend/blob/main/LICENSE)

