<h1 align="center">Welcome to AIOHTTP-Chat 🌿</h1>

A small chat, running on websockets and based on aiohttp, MongoDB and Jinja2. I hope to add tests here at some point.

<h1 align="center">Installation</h1>

**1.** Clone this repository how you like it.

**2.** Create the required .env file with the following options **(aiohttp-chat/chat/.env)**.
```
SECRET_KEY, MONGO_INITDB_DATABASE, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD
```

By the way, if your `SECRET_KEY` does not fit, you can generate it via `cryptography.fernet.Fernet.generate_key`.

**3.** In addition, you can check the quality of the code if you need it.
```
$ cd chat/
$ poetry install
$ sudo chmod a+x lint.sh
$ ./lint.sh
```

**4.** Launch docker and all needed services.
```
$ docker-compose up --build
```
