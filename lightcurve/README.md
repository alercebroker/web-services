# ALeRCE Lightcurve API
## For developers
Set up environment variables. Look at [example](.env.example) 
Run with `poetry run uvicorn api.api:app` or `poetry run dev`

### Connecting to remote databases without public IPs
If you want to test against a remote database that doesn't have public IP enabled, you can connect using an SSH tunnel via a proxy server. Check the EC2 console for the IP of the proxy server or ask on slack.

There are additional environment variables that you need to set up this tunnel: 

- `MONGO_IP`: the private ip of the mongo instance to connect to
- `PROXY_IP`: the public ip of the proxy instance that has access to `MONGO_IP`
- `SSH_PKEY`: path to the public key used to connect to the `PROXY_IP`

Then run `poetry run tunnel` (make sure to have run `poetry install` first)

## HTMX endpoint
The htmx returned by this API's htmx endpoint emits the following events:

|       Event      |       Trigger     |      Detail content     |     Level     |
|:----------------:|:-----------------:|:-----------------------:|:-------------:|
| onDetectionClick | Clicked detection | Clicked detection index | document.body |

## .env file for services configuration
The environment variables for each container are defined from an .env file.
.env example.

```
ENV=dev
API_URL=http://localhost:8000
SECRET_KEY=some_secret
MONGO_USER=mongo
MONGO_PASSWORD=mongo
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=database
MONGO_AUTH_SOURCE=admin
PSQL_USER=postgres
PSQL_PASSWORD=postgres
PSQL_DATABASE=postgres
PSQL_HOST=localhost
PSQL_PORT=5432
```