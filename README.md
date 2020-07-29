# HalfAPI


This Python-based ASGI application aims to provide the core functionality to
multiple API domains.

It's developed at the [LIRMM](https://lirmm.fr) in Montpellier, France.

The name "halfAPI" comes from the deep relationship between it and
[halfORM](https://gite.lirmm.fr/newsi/halfORM), a project authored by
[Joël Maizi](https://gite.lirmm.fr/maizi).

You'll need a database with the API details. You can find the database model in halfapi/models/api.sql

**TODO :** include a token generation tool for testing purpose.


## Dependencies

- python3
- python3-pip
- libgit2-dev


## Installing


With local folder :

`pip3 install -r requirements.txt .[cli]`


From the repository :

`pip3 install git+ssh://git@gite.lirmm.fr:malves/halfapi.git[cli]`


## CLI usage


## Running

### Development mode

In the project's folder :

`halfapi run`


### Production

The production server may use different init systems. As our main server is Debian-based, we use systemd services to manage the api server. Find the right service files and configure them properly in order to make your production setup perfect.


```
cp conf/systemd/lirmm_api* /etc/systemd/system/
systemctl daemon-reload
systemctl start lirmm_api
```


To make it start at boot :


`systemctl enable lirmm_api`



To get the logs :


```
journalctl -f --unit lirmm_api

```


## Testing

### Installing

pip3 install .[cli][tests]

### Running

pytest -v
