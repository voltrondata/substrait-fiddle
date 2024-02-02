FROM python:3.9

RUN apt-get update && apt-get install -y cmake

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./ /api/

RUN --mount=type=secret,id=VITE_SESSION_SECRET \
  cat /run/secrets/VITE_SESSION_SECRET

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--reload", "--port", "9090"]
