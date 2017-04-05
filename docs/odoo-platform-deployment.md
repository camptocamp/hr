# Odoo Cloud Platform

Odoo Cloud Platform is the new platform for deploying Camptocamp Odoo projects.

This platform is managed on [Rancher](https://caas.camptocamp.com/).
There is also a test platform on [Rancher-dev](https://caas-dev.camptocamp.com/), see this [document](./odoo-test-cloud-platform.md).

Your project should be dockerized and use:
 * [Camptocamp Docker base image for Odoo project](https://github.com/camptocamp/docker-odoo-project)
 * [Odoo cloud platform addons](https://github.com/camptocamp/odoo-cloud-platform)

If you are creating a new project from scratch, you can use the [Camptocamp docker template project for Odoo](https://github.com/camptocamp/odoo-template)

## Platform structure

On [Rancher](https://caas.camptocamp.com/), you can find the [odoo-platform environment](https://caas.camptocamp.com/env/1a233618/apps/stacks).

Currently, this environment is hosted on 6 servers (and a 7th for sysadmin monitoring stacks):

* 2 applications servers on which we will deploy our production containers
* 2 database servers which host a postgres cluster with:
 * A primary postgres instance on the first server
 * A read only replicated postgres instance on the second server which is in another datacenter.
* 1 application server for the integration stacks
* 1 database server for the integration stacks with a standalone postgres

These servers are tagged with Rancher labels (e.g.: application=true), we will see how to use this label in order to deploy our containers on the right place.

**Warning: All databases put on postgres cluster must not contain the name of the client in their name** because some client have access to their database, so they can see databases list.

## Instances

For a standard Camptocamp Odoo project, we will have 3 Odoo environments:

### Test

See the dedicated [document](./odoo-test-cloud-platform.md).

### Integration

This instance can be used by the client as well as Camptocamp.
The goal is to test new release, either during project development or upgrade release when project is in production.

This instance should be populated with all the client data, in order to test full creation process and server performance.

The database should be created on Postgres integration with the production randomly generated name suffixed by `_integration`.

### Prod

The client production instance, the database is on the Postgres cluster (with randomly generated name).


## Rancher stacks

Different stacks are required for our project to run on the platform.
All the stacks templates are on the [odoo-cloud-platform-ch-rancher-templates GitHub project](https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates).

**Odoo stacks**:

* **bso-odoo-integration**
 * odoo: Your odoo image with a fixed version (e.g.: 9.1.0) build from a github tag
 * nginx: it's a sidekick of the odoo container [Nginx proxy for odoo](https://github.com/camptocamp/docker-odoo-nginx)
 * letsencrypt: [Container managing the certificate for the integraton domain name](https://github.com/janeczku/rancher-letsencrypt)
* **bso-odoo-prod**
 * odoo: Your odoo image with a fixed production version (e.g.: 9.1.0) build from a github tag
 * nginx: it's a sidekick of the odoo container [Nginx proxy for odoo](https://github.com/camptocamp/docker-odoo-nginx)
 * letsencrypt: [Container managing the certificate for the production domain name](https://github.com/janeczku/rancher-letsencrypt)

**Common stacks**:

Some stacks are used by all the projects, they already exist

* **lb**
 * lb: Rancher load balancer container (HAProxy), entry point of Odoo platform.
 ```
 TODO put a link to lb configuration explanation.
 ```
 * redirect: A [simple nginx container](https://github.com/camptocamp/docker-https-redirect) which redirect all HTTP query to HTTPS.

* **redis**
 * redis: [A redis server](https://hub.docker.com/_/redis/) for storing session
   of the Odoo production instances hosted on this platform.

* **redis-integration**
 * redis: [A redis server](https://hub.docker.com/_/redis/) for storing session
   of the Odoo integration instances hosted on this platform.

* **postgres-cluster**
 * The production Postgresql cluster

* **postgres-integration**
 * The integration Postgresql server


## Let's start

### Odoo cloud platforms addons installation

[Odoo cloud platform addons](https://github.com/camptocamp/odoo-cloud-platform) is a set of Odoo addons which allowed, inter alia,
to have Odoo containers without any files stored locally. Filestore is saved on
a cloud Object Storage (with S3 compatible API, currently on Exoscale),
sessions are saved in Redis.

Thanks to this, Odoo container can be scaled (have multiple container for one instance) or moved easily from a server to another.

First of all, read the [project Readme](https://github.com/camptocamp/odoo-cloud-platform)

#### Installation in Camptocamp Odoo project:

* Add odoo-cloud-platform as a submodule:

```bash
git submodule add git@github.com:camptocamp/odoo-cloud-platform.git odoo/external-src/odoo-cloud-platform
```
* Add `/opt/odoo/external-src/odoo-cloud-platform` in `ADDONS_PATH` in [odoo/Dockerfile](../odoo/Dockerfile)
```
[...]
# This is just an example
ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
 /opt/odoo/local-src, \
 /opt/odoo/external-src/odoo-cloud-platform"
[...]
```

* In `odoo/migration.yml`, you have to:
 * Add or modify the --load in `install_args` option.
 * Change the `command` to `command: odoo --load=web,web_kanban,attachment_s3,session_redis,logging_json` in
   `docker-compose.yml`
 * Add the `cloud_platform` module installation.
 * Call the `cloud_platform` song to setup exoscale.

 ```
 migration:
   options:
     install_args: --load=web,web_kanban,session_redis,attachment_s3,logging_json
     [...]
    versions:
      - version: X.X.X
        operations:
          post:
            - anthem openerp.addons.cloud_platform.songs::install_exoscale
        [..]
        addons:
          upgrade:
            [...]
            # camptocamp/cloud-platform
            - cloud_platform
            [...]

 ```

* Add new requirements in `odoo/requirements.txt`

 ```
 boto==2.42.0
 redis==2.10.5
 python-json-logger==0.1.5
 statsd==3.2.1
 ```

* Configuration will be set in rancher configurations section

### Rancher stacks configurations

Each rancher instance has a specific `docker-compose.yml file in rancher directory which describes the stack composition.
There is another file, rancher.env.gpg, which is encrypted and contains environment values to pass to docker like password, mode, etc..

See [rancher.md](rancher.md#rancher-environment-setup) for more details and encrypt / decrypt command.

#### Integration and production stacks

The files for the integration and production stacks are stored in a project
dedicated to the platform:
https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates

Let's talk about the difference with test stack:
 * Odoo docker image version is a fixed version (e.g: 10.0.0 for the first one) instead of latest
 * No db container but an external links to the postgres stacks. But the hostname of the database server for Odoo is still "db".
 * Filestore is stored on S3
 * Scaling: for Production, Rancher will spawn as much odoo container as application servers (so 2 at the moment)

  ```
  TODO put a link to an explanation of odoo scaling/lb/etc...
  ```

##### Integration files

* `docker-compose.yml`

 ```
 odoo:
  image: camptocamp/bso_odoo:10.0.0
   command: odoo --load=web,web_kanban,attachment_s3,session_redis,logging_json
   external_links:
     - postgres-integration/postgres:db
     - redis-integration/redis:redis
   environment:
     - DB_USER=${DB_USER}
     - DB_PASSWORD=${DB_PASSWORD}
     - DB_NAME=${DB_NAME}
     - DB_PORT=${DB_PORT}
     - ADMIN_PASSWD=${ADMIN_PASSWD}
     - RUNNING_ENV=${RUNNING_ENV}
     - DEMO=${DEMO}
     - WORKERS=${WORKERS}
     - MAX_CRON_THREADS=${MAX_CRON_THREADS}
     - LOG_LEVEL=${LOG_LEVEL}
     - LOG_HANDLER=${LOG_HANDLER}
     - DB_MAXCONN=${DB_MAXCONN}
     - LIMIT_MEMORY_SOFT=${LIMIT_MEMORY_SOFT}
     - LIMIT_MEMORY_HARD=${LIMIT_MEMORY_HARD}
     - LIMIT_REQUEST=${LIMIT_REQUEST}
     - LIMIT_TIME_CPU=${LIMIT_TIME_CPU}
     - LIMIT_TIME_REAL=${LIMIT_TIME_REAL}
     - ODOO_BASE_URL=${ODOO_BASE_URL}
     - MARABUNTA_ALLOW_SERIE=False
     - MARABUNTA_MODE=${MARABUNTA_MODE}
     - AWS_HOST=${AWS_HOST}
     - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
     - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
     - AWS_BUCKETNAME=${AWS_BUCKETNAME}
     - ODOO_SESSION_REDIS=${ODOO_SESSION_REDIS}
     - ODOO_SESSION_REDIS_HOST=${ODOO_SESSION_REDIS_HOST}
     - ODOO_SESSION_REDIS_PREFIX=${ODOO_SESSION_REDIS_PREFIX}
     - ODOO_LOGGING_JSON=${ODOO_LOGGING_JSON}
     - ODOO_CLOUD_PLATFORM_UNSAFE=${ODOO_CLOUD_PLATFORM_UNSAFE}
     - ODOO_STATSD=${ODOO_STATSD}
     - STATSD_CUSTOMER=bso_odoo
     - STATSD_ENVIRONMENT=${STATSD_ENVIRONMENT}
     - STATSD_HOST=${STATSD_HOST}
     - STATSD_PORT=${STATSD_PORT}
   labels:
     io.rancher.scheduler.affinity:host_label: application=true,integration=true
     io.rancher.sidekicks: nginx
 
 nginx:
   image: camptocamp/odoo-nginx:9.0-1.1.0
   net: "container:odoo"
   environment:
     - NGX_ODOO_HOST=127.0.0.1
   links:
     - odoo:odoo
 
 letsencrypt:
   environment:
     API_VERSION: Production
     AWS_ACCESS_KEY: ${LETSENCRYPT_AWS_ACCESS_KEY}
     AWS_SECRET_KEY: ${LETSENCRYPT_AWS_SECRET_KEY}
     CERT_NAME: ${DOMAIN_NAME}
     CLOUDFLARE_EMAIL: ''
     CLOUDFLARE_KEY: ''
     DNSIMPLE_EMAIL: ''
     DNSIMPLE_KEY: ''
     DOMAINS: ${DOMAIN_NAME}
     DO_ACCESS_TOKEN: ''
     DYN_CUSTOMER_NAME: ''
     DYN_PASSWORD: ''
     DYN_USER_NAME: ''
     EMAIL: letsencrypt@camptocamp.com
     EULA: 'Yes'
     PROVIDER: Route53
     PUBLIC_KEY_TYPE: RSA-2048
     RENEWAL_TIME: '12'
   labels:
     io.rancher.scheduler.affinity:host_label: application=true,integration=true
     io.rancher.container.create_agent: 'true'
     io.rancher.container.agent.role: environment
   image: janeczku/rancher-letsencrypt:v0.3.0
   volumes:
     - troisepis-integration-certs:/etc/letsencrypt/production/certs
 ```

* `rancher.public.env`

 ```
 export DOMAIN_NAME=integration.bso_odoo.odoo.camptocamp.ch
 export ODOO_BASE_URL="https://${DOMAIN_NAME}"
 
 export DB_USER=
 export DB_NAME=
 export DB_PORT=5432
 export RUNNING_ENV=integration
 # number of workers to configure according to the plan of the customer
 export WORKERS=4
 export MAX_CRON_THREADS=1
 export LOG_LEVEL=info
 export LOG_HANDLER=":INFO"
 export DB_MAXCONN=5
 export LIMIT_MEMORY_SOFT=325058560
 export LIMIT_MEMORY_HARD=1572864000
 export LIMIT_TIME_CPU=86400
 export LIMIT_TIME_REAL=86400
 export LIMIT_REQUEST=8192
 export DEMO=False
 export MARABUNTA_MODE=full
 
 export AWS_BUCKETNAME=bso-odoo-integration
 
 export ODOO_SESSION_REDIS=1
 export ODOO_SESSION_REDIS_HOST=redis
 export ODOO_SESSION_REDIS_PREFIX=bso-odoo-integration
 
 export ODOO_LOGGING_JSON=1
 
 export ODOO_STATSD=0
 export STATSD_ENVIRONMENT=integration
 export STATSD_HOST=10.42.24.101
 export STATSD_PORT=8125

 # when activated, platform checks are not performed, use for debug
 export ODOO_CLOUD_PLATFORM_UNSAFE=0
 ```

* `rancher.env.gpg` (encrypted file)

 ```
 export DB_PASSWORD=
 export ADMIN_PASSWD=
 ```

##### Production files

* `docker-compose.yml`

 ```
 odoo:
  image: camptocamp/bso_odoo:10.0.0
   command: odoo --load=web,web_kanban,attachment_s3,session_redis,logging_json
   external_links:
     - postgres-cluster/lb:db
     - redis/redis:redis
   environment:
     - DB_USER=${DB_USER}
     - DB_PASSWORD=${DB_PASSWORD}
     - DB_NAME=${DB_NAME}
     - DB_PORT=${DB_PORT}
     - ADMIN_PASSWD=${ADMIN_PASSWD}
     - RUNNING_ENV=${RUNNING_ENV}
     - DEMO=${DEMO}
     - WORKERS=${WORKERS}
     - MAX_CRON_THREADS=${MAX_CRON_THREADS}
     - LOG_LEVEL=${LOG_LEVEL}
     - LOG_HANDLER=${LOG_HANDLER}
     - DB_MAXCONN=${DB_MAXCONN}
     - LIMIT_MEMORY_SOFT=${LIMIT_MEMORY_SOFT}
     - LIMIT_MEMORY_HARD=${LIMIT_MEMORY_HARD}
     - LIMIT_REQUEST=${LIMIT_REQUEST}
     - LIMIT_TIME_CPU=${LIMIT_TIME_CPU}
     - LIMIT_TIME_REAL=${LIMIT_TIME_REAL}
     - ODOO_BASE_URL=${ODOO_BASE_URL}
     - MARABUNTA_ALLOW_SERIE=False
     - MARABUNTA_MODE=${MARABUNTA_MODE}
     - AWS_HOST=${AWS_HOST}
     - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
     - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
     - AWS_BUCKETNAME=${AWS_BUCKETNAME}
     - ODOO_SESSION_REDIS=${ODOO_SESSION_REDIS}
     - ODOO_SESSION_REDIS_HOST=${ODOO_SESSION_REDIS_HOST}
     - ODOO_SESSION_REDIS_PREFIX=${ODOO_SESSION_REDIS_PREFIX}
     - ODOO_LOGGING_JSON=${ODOO_LOGGING_JSON}
     - ODOO_CLOUD_PLATFORM_UNSAFE=${ODOO_CLOUD_PLATFORM_UNSAFE}
     - ODOO_STATSD=${ODOO_STATSD}
     - STATSD_CUSTOMER=bso_odoo
     - STATSD_ENVIRONMENT=${STATSD_ENVIRONMENT}
     - STATSD_HOST=${STATSD_HOST}
     - STATSD_PORT=${STATSD_PORT}
   labels:
     io.rancher.scheduler.affinity:host_label: application=true,production=true
     io.rancher.scheduler.global: 'true'
     io.rancher.sidekicks: nginx
 
 nginx:
   image: camptocamp/odoo-nginx:9.0-1.1.0
   net: "container:odoo"
   environment:
     - NGX_ODOO_HOST=127.0.0.1
   links:
     - odoo:odoo
 
 letsencrypt:
   environment:
     API_VERSION: Production
     AWS_ACCESS_KEY: ${LETSENCRYPT_AWS_ACCESS_KEY}
     AWS_SECRET_KEY: ${LETSENCRYPT_AWS_SECRET_KEY}
     CERT_NAME: ${DOMAIN_NAME}
     CLOUDFLARE_EMAIL: ''
     CLOUDFLARE_KEY: ''
     DNSIMPLE_EMAIL: ''
     DNSIMPLE_KEY: ''
     DOMAINS: ${DOMAIN_NAME}
     DO_ACCESS_TOKEN: ''
     DYN_CUSTOMER_NAME: ''
     DYN_PASSWORD: ''
     DYN_USER_NAME: ''
     EMAIL: letsencrypt@camptocamp.com
     EULA: 'Yes'
     PROVIDER: Route53
     PUBLIC_KEY_TYPE: RSA-2048
     RENEWAL_TIME: '12'
   labels:
     io.rancher.scheduler.affinity:host_label: application=true,production=true
     io.rancher.container.create_agent: 'true'
     io.rancher.container.agent.role: environment
   image: janeczku/rancher-letsencrypt:v0.3.0
   volumes:
     - bso_odoo-prod-certs:/etc/letsencrypt/production/certs
 ```

* `rancher.public.env`

 ```
 export DOMAIN_NAME=integration.bso_odoo.odoo.camptocamp.ch
 export ODOO_BASE_URL="https://${DOMAIN_NAME}"
 
 export DB_USER=
 export DB_NAME=
 export DB_PORT=5432
 export RUNNING_ENV=prod
 # number of workers to configure according to the plan of the customer
 export WORKERS=4
 export MAX_CRON_THREADS=1
 export LOG_LEVEL=info
 export LOG_HANDLER=":INFO"
 export DB_MAXCONN=5
 export LIMIT_MEMORY_SOFT=325058560
 export LIMIT_MEMORY_HARD=1572864000
 export LIMIT_TIME_CPU=86400
 export LIMIT_TIME_REAL=86400
 export LIMIT_REQUEST=8192
 export DEMO=False
 export MARABUNTA_MODE=full
 
 export AWS_BUCKETNAME=bso-odoo-prod
 
 export ODOO_SESSION_REDIS=1
 export ODOO_SESSION_REDIS_HOST=redis
 export ODOO_SESSION_REDIS_PREFIX=bso-odoo-prod
 
 export ODOO_LOGGING_JSON=1
 
 export ODOO_STATSD=1
 export STATSD_ENVIRONMENT=prod
 export STATSD_HOST=10.42.24.101
 export STATSD_PORT=8125

 # when activated, platform checks are not performed, use for debug
 export ODOO_CLOUD_PLATFORM_UNSAFE=0
 ```

* `rancher.env.gpg` (encrypted file)

 ```
 export DB_PASSWORD=
 export ADMIN_PASSWD=
 ```

#### Preparing the integration and production stacks

* In `rancher.public.env` for production, fill `DB_USER` and `DB_NAME` with a
  randomly generated name (http://kevinmlawson.com/herokuname/ and replace '-'
  by '_').  The `DB_USER` is the same name than `DB_NAME`. For integration, the
  same name is used suffixed by `_integration`.
* In `rancher.env`, set different `DB_PASSWORD` and `ADMIN_PASSWD`.
  You can use `pwgen -s 20`. Please add them in Lastpass.
* Encrypt `rancher.env` to `rancher.env.gpg` ([rancher.md](rancher.md#rancher-environment-setup))
* Configure the number of workers according to the plan of the customer
  (detailed on the [platform
  project](https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates#cloud-plans).

Finally once all is configured, you have to start the `letsencrypt` container
of the stack. This is necessary to ensure that the SSL certificate is created
as soon as possible, considering Let's Encrypt has rate limits, it would be a
pity to be unable to create the certificate the day of the golive. In the platform project:

```
./rancher bso-odoo-integration up -d letsencrypt
./rancher bso-odoo-prod up -d letsencrypt
```

### Stack Deployment

#### Rancher Compose

To deploy stacks on rancher, we use the Rancher client [rancher-compose](https://github.com/rancher/rancher-compose).

`rancher-compose` is a Docker compose compatible client that deploys to Rancher.

`rancher-compose` need a -p parameter which indicates the name of the stack to work on.

The access keys and rancher url can be passed with rancher-compose options or with environment variables ($RANCHER_URL, $RANCHER_ACCESS_KEY, $RANCHER_SECRET_KEY)

Example (we assumed environments variables are correctly set):

```bash
# Like docker-compose up, create if needed the stack and start all the containers.
rancher-compose -p stack_name up -d
```

```bash
# Check the output logs of odoo container
rancher-compose -p stack_name logs --follow odoo
```


#### Integration deployment

The integration stack is deployed manually after a release.

* If needed, download [rancher-compose](http://releases.rancher.com/compose/beta/v0.7.2/rancher-compose-linux-amd64-v0.7.2.tar.gz) and untar the executable in a `$PATH`.
* Go to your locally cloned platform project (https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates)
* Use the local `./rancher` script, example to start the containers:
  
  ```
  ./rancher bso-odoo-integration up -d
  ```

### Upgrade stack

#### Integration / Production

**Warning**: The example below is for integration, replace all `integration` reference (rancher directory, stack name) by `prod` for the production.

To upgrade your stack, first of all you need to prepare your release on the project.
Take a look at [releases.md](releases.md) for more details but here is a quick steps list:
 * Merge all wanted PRs in master and check HISTORY.rst is correctly filled and clear empty sections.
 * Wait for a successful Travis build
 * You can check on the newly re-created test server if everything is ok.
 * On master:

 ```bash
 invoke release.bump --feature
 # (or --patch for a bugfix release)
 ```
 * Check that your [odoo/migration.yml](../odoo/migration.yml) upgrade section for this version is ok. (if needed)
 * Check and commit updated files:

 ```bash
 git add odoo/VERSION HISTORY.rst rancher/integration/docker-compose.yml
 git commit -m "Release X.X.X"
 ```
 * Create a tag for the release and push it.

 ```bash
 git tag -a X.X.X
 # Use git tag -s if you have a GPG key to sign your tag
 # You can put the corresponding HISTORY.rst section as tag message

 git push --tags
 # Don't forget to push master too but note that it will drop/recreate the test stack.
 git push
 ```
 * Travis will run a build on this tag and, if successful, push a docker image (tagged as X.X.X) on Docker Hub.

* Go to your locally cloned platform project (https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates)
* Update the version of the image in the `docker-compose.yml` file of the stack, commit and push
* Use the local `./rancher` script, example to upgrade the containers:
  
  ```
  ./rancher bso-odoo-integration up --pull --recreate --confirm-upgrade -d
  ```

At start, the new container will automatically execute the upgrade defined in
[odoo/migration.yml](../odoo/migration.yml) for this new version.

#### Specific case for integration database

For the integration stack, during development, we use to recreate from scratch the database (if client agrees).

This allows to test correctly the initial setup with full csv files (as this setup will be applied on production).

If it's your case, you have to drop the database and recreate an empty one before execute the last step in previous part (`rancher-compose -p [...]`)

A ssh container with access to the cluster is available. Accessible with connection link as `odoo-platform-int-db`.

Here is how to drop and recreate the database:
```
odoo-platform-int-db

# docker exec -it r-postgres-cluster_postgres_2 bash

# sudo docker exec -it r-postgres-integration_postgres_1 psql -U postgres -c "DROP DATABASE mighty_pinguin_l337_integration"
# sudo docker exec -it r-postgres-integration_postgres_1 psql -U postgres -c "CREATE DATABASE mighty_pinguin_l337_integration OWNER mighty_pinguin_l337_integration"

```
