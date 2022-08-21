## Getting started with Apache Airflow

- Create a new empty file `.secrets`. This will contain a list of secret configurations and password credentials.
- Create a new file `.env`. This will contain a list of environment variables. Add the following environment variables:

```
AIRFLOW_UID=197609
AIRFLOW_GID=0
```

- Run the following command to create a new Docker container.

  `docker compose up`

**OPTIONAL:** If you want to change the name of volumes created locally, you can update the _volumes_ section in the `docker-compose.yml` file. Moreover, make sure to update the `.gitignore` file to untrack the logs with the new volume name.

- Open the Airflow webserver at:

  `https://localhost:8080`
