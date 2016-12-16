# Odoo Platform

Odoo platform is the new platform for deploying Camptocamp Odoo projects.
This platform is managed on [Rancher](https://caas.camptocamp.net/)

So your project should be dockerized and use:
 * [Camptocamp Docker base image for Odoo project](https://github.com/camptocamp/docker-odoo-project)
 * [Odoo cloud platform addons](https://github.com/camptocamp/odoo-cloud-platform)

If you are creating a new project from scratch, you can use the [Camptocamp docker template project for Odoo](https://github.com/camptocamp/odoo-template)

## Platform structure

On [Rancher](https://caas.camptocamp.net/), you can find the [odoo-platform environment](https://caas.camptocamp.net/env/1a19171/apps/stacks).

Currently, this environment is hosted on 4 servers (and a 5th for sysadmin monitoring stacks):

* 2 applications servers on which we will deploy our containers
* 2 database servers which host a postgres cluster with:
 * A primary postgres instance on the first server
 * A read only replicated postgres instance on the second server which is in another datacenter.

These servers are tagged with Rancher labels (e.g.: application=true), we will see how to use this label in order to deploy our containers on the right place.

**Warning: All databases put on postgres cluster must not contain the name of the client in their name** because some client have access to their database, so they can see databases list.

## Instances

For a standard Camptocamp Odoo project, we will have 3 Odoo instances:

### Test

This instance is for Camptocamp developer and project manager. The goal is to quickly test a merged pull request on master.

This instance will be **automatically recreated from scratch** after every commit on master in your github project.
For this reason:
* We will not put the test database on the postgres cluster but in a docker container in your composition.
* This instance should be populated with a little set of data in order to be quickly created.
* Assumed this Odoo **can be deleted at every moment** with all the data you have created or modified.

### Integration

This instance can be used by the client as well as Camptocamp.
The goal is to test new release, either during project developement or upgrade release when project is in production.

This instance should be populated with all the client data, in order to test full creation process and server performance.

The database should be created on the Postgres cluster with a randomly generated name.

### Prod

The client production instance, the database is of course also on the Postgres cluster (with a generated name too).


## Rancher stacks

For all those instances, we should create many stacks on Rancher.

**Odoo stacks**:

* **roctool-odoo-test**
 * odoo: Your odoo image with latest tag, build from the last commit in master
 * nginx: [Nginx proxy for odoo](https://github.com/camptocamp/docker-odoo-nginx)
 * db: [Postgres database container](https://github.com/camptocamp/docker-postgresql)
 * letsencrypt: [Container managing the certificate for the test domain name](https://github.com/janeczku/rancher-letsencrypt)
* **roctool-odoo-integration**
 * odoo: Your odoo image with a fixed version (e.g.: 9.1.0) build from a github tag
 * nginx: [Nginx proxy for odoo](https://github.com/camptocamp/docker-odoo-nginx)
 * letsencrypt: [Container managing the certificate for the integraton domain name](https://github.com/janeczku/rancher-letsencrypt)
* **roctool-odoo-prod**
 * odoo: Your odoo image with a fixed production version (e.g.: 9.1.0) build from a github tag
 * nginx: [Nginx proxy for odoo](https://github.com/camptocamp/docker-odoo-nginx)
 * letsencrypt: [Container managing the certificate for the production domain name](https://github.com/janeczku/rancher-letsencrypt)

**Common stacks**:

Some stacks are used by all the projects

* **lb**
 * lb: Rancher load balancer container (HAProxy), entry point of Odoo platform.
 ```
 TODO put a link to lb configuration explanation.
 ```
 * redirect: A [simple nginx container](https://github.com/camptocamp/docker-https-redirect) which redirect all HTTP query to HTTPS.

* **redis**
 * redis: [A redis server](https://hub.docker.com/_/redis/) for storing session for all Odoo hosted on this platform.

## Let's start

### Odoo cloud platforms addons installation

[Odoo cloud platform addons](https://github.com/camptocamp/odoo-cloud-platform) is a set of Odoo addons which allowed, inter alia,
to have Odoo containers without any files stored locally. Filestore is saved on cloud (with S3 compatible API, currently on Exoscale), sessions are saved in Redis.

Thanks to this, Odoo container can be scaled (have multiple container for one instance) or moved easily from a server to another.

First of all, read the [project Readme](https://github.com/camptocamp/odoo-cloud-platform)

#### Installation in Camptocamp Odoo project:

* Add odoo-cloud-platform as a submodule:

```bash
git submodule add git@github.com:camptocamp/odoo-cloud-platform.git odoo/external-src/odoo-cloud-platform
```
* Add /opt/odoo/external-src/odoo-cloud-platform in ADDONS_PATH in [odoo/Dockerfile](../odoo/Dockerfile)
```
[...]
# This is just an example
ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
 /opt/odoo/local-src, \
 /opt/odoo/external-src/odoo-cloud-platform"
[...]
```

* In odoo/migration.yml, you have to:
 * Add or modify the --load in install_args option.
 * Add the cloud_platform module installation.
 * Call cloud_platform songs to setup exoscale.

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
            #camptocamp/cloud-platform
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

Each rancher instance has a specific docker-compose.yml file in rancher directory which describes the stack composition.
There is another file, rancher.env.gpg, which is encrypted and contains environment values to pass to docker like password, mode, etc..

See [rancher.md](rancher.md#rancher-environment-setup) for more details and encrypt / decrypt command.

#### Test stack configuration

For test stack, the composition file is [rancher/latest/docker-compose.yml](../rancher/latest/docker-compose.yml)

If you used [Odoo template](https://github.com/camptocamp/odoo-template) to create your project you should already have it.
Otherwise, you can download it and replace all cookiecutter values.

Then create a rancher.env file containing:

 ```
 export RANCHER_URL=https://caas.camptocamp.net/
 export RANCHER_ACCESS_KEY=
 export RANCHER_SECRET_KEY=

 export DOMAIN_NAME=test.roctool.odoo.camptocamp.ch
 export LETSENCRYPT_AWS_ACCESS_KEY=
 export LETSENCRYPT_AWS_SECRET_KEY=

 export DB_USER=roctool_test
 export DB_NAME=roctool_test_db
 export DB_PASSWORD=
 export DB_PORT=5432
 export ADMIN_PASSWD=
 export RUNNING_ENV=test
 # set to WORKERS=2 and MAX_CRON_THREADS=1 when
 # once the production is up
 export WORKERS=2
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
 export MARABUNTA_MODE=demo

 export ODOO_SESSION_REDIS=1
 export ODOO_SESSION_REDIS_HOST=redis
 export ODOO_SESSION_REDIS_PREFIX=roctool-odoo-test
 export ODOO_SESSION_REDIS_EXPIRATION=86400

 export ODOO_LOGGING_JSON=1

 # when activated, platform checks are not performed, use for debug
 export ODOO_CLOUD_PLATFORM_UNSAFE=0
 ```

You have to fill:
* RANCHER_ACCESS_KEY and RANCHER_SECRET_KEY, you can find this value in rancher.env.gpg of other project hosted on odoo-platform.
  This access keys is per rancher environment.
* LETSENCRYPT_AWS_ACCESS_KEY and LETSENCRYPT_AWS_SECRET_KEY, you can find this value in rancher.env.gpg of other project hosted on odoo-platform.
* DB_PASSWORD and ADMIN_PASSWD by generated passwords. To generate passwords, you can use this command in your terminal `pwgen -s 20`

Then encrypt this file (see [rancher.md](rancher.md#rancher-environment-setup) to know how to encrypt the file).

#### Integration stack

The composition file is [rancher/integration/docker-compose.yml](../integration/latest/docker-compose.yml)

If you used [Odoo template](https://github.com/camptocamp/odoo-template) to create your project you should already have it.
Otherwise, you can download it and replace all cookiecutter values.

Let's talk about the difference with test stack:
 * Odoo docker image version is a fixed version (e.g: 10.0.0 for the first one) instead of latest
 * No db container but an external links to the postgres cluster. But the hostname of the database server for Odoo is still "db".
 * Filestore is stored on S3
 * Scaling: Rancher will spawn as much odoo container as application servers (so 2 at the moment)
  ```
  TODO put a link to an explanation of odoo scaling/lb/etc...
  ```

Create the rancher.env file containing:

 ```
 export RANCHER_URL=https://caas.camptocamp.net/
 export RANCHER_ACCESS_KEY=
 export RANCHER_SECRET_KEY=

 export DOMAIN_NAME=integration.roctool.odoo.camptocamp.ch
 export LETSENCRYPT_AWS_ACCESS_KEY=
 export LETSENCRYPT_AWS_SECRET_KEY=

 export DB_USER=
 export DB_NAME=
 export DB_PASSWORD=
 export DB_PORT=5432
 export ADMIN_PASSWD=
 export RUNNING_ENV=integration
 # set to WORKERS=2 and MAX_CRON_THREADS=1 when
 # once the production is up
 export WORKERS=8
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

 export AWS_HOST=
 export AWS_ACCESS_KEY_ID=
 export AWS_SECRET_ACCESS_KEY=
 export AWS_BUCKETNAME=roctool-odoo-integration

 export ODOO_SESSION_REDIS=1
 export ODOO_SESSION_REDIS_HOST=redis
 export ODOO_SESSION_REDIS_PREFIX=roctool-odoo-integration

 export ODOO_LOGGING_JSON=1

 # when activated, platform checks are not performed, use for debug
 export ODOO_CLOUD_PLATFORM_UNSAFE=0
 ```

You have to fill:
* RANCHER_ACCESS_KEY and RANCHER_SECRET_KEY: Same value than the test stack.
* LETSENCRYPT_AWS_ACCESS_KEY and LETSENCRYPT_AWS_SECRET_KEY: Same value than the test stack.
* DB_USER and DB_NAME: You have to generate a random database name (and use the same name for the user),
                       because database on cluster postgres must not contain the name of the client.
                       You can use http://kevinmlawson.com/herokuname/ and replace '-'  by '_'.
* DB_PASSWORD and ADMIN_PASSWD by generated passwords. To generate passwords, you can use this command in your terminal `pwgen -s 20`
* AWS_HOST, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: you can find these values in rancher.env.gpg of other project hosted on odoo-platform.

Then encrypt this file (see [rancher.md](rancher.md#rancher-environment-setup) to know how to encrypt the file).

### Docker images

Docker images for Odoo are generated and pushed to [Docker Hub](https://hub.docker.com) by Travis when builds are successfull.
This push is done in [travis/publish.sh](../travis/publish.sh) which is called by [travis.yml](../.travis.yml) in after_succes section.

You can see that this script will tag docker image with:
 * latest: When the build was triggered by a commit on master
 * `git tag name`: When the build was triggered after a new tag is pushed.

So Travis should have access to your project on Docker Hub. If it's not the case, ask someone with access to:
 * Create if needed the [project on Docker Hub](https://hub.docker.com/r/camptocamp/roctool_odoo/)
 * Create access for Travis in this new project and put auth informations in Lastpass
  * user: c2cbusinessroctooltravis
  * password: Generated password
  * email: business-deploy+roctool-travis@camptocamp.com (which should aliased on camptocamp@camptocamp.com)

On Travis, in [settings page](https://travis-ci.com/camptocamp/roctool_odoo/settings) , add following environnement variables:
 * DOCKER_USERNAME : c2cbusinessroctooltravis
 * DOCKER_PASSWORD : The generated password in previous step, so you can find it in Lastpass
 * DOCKER_EMAIL : business-deploy+roctool-travis@camptocamp.com (which should aliased on camptocamp@camptocamp.com)


**From there, each travis successfull build on master or on tags will build a docker image and push it to Docker Hub**

**And even better, if you followed all the previous steps, the next successfull build on master will automatically create the test stack (roctool-odoo-test) on Rancher**

**See next part to understand how.**

### Stack Deployment

#### Rancher Compose

To deploy stacks on rancher, we use the Rancher client [rancher-compose](https://github.com/rancher/rancher-compose).

rancher-compose is a Docker compose compatible client that deploys to Rancher.

rancher-compose need a -p parameter which indicates the name of the stack to work on.

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

#### Test deployment

In [travis/publish.sh](../travis/publish.sh), you can see that the deploy function is called when the latest image is generated
(so after a successfull travis build on master)

This deploy function do the following steps:
 * Download a rancher-compose client
 * Decrypt latest/rancher.env.gpg and source it to read all needed configurations for accessing rancher and configuring the stack.
 * Remove, if exists, the test stack db container on rancher.
 * Create or upgrade the full stack (with the new builded odoo docker image)
 * This upgrade will recreate a database and container and run the installation process.

But Travis need the gpg password in order to decrypt rancher.env.gpg file.

Look at [rancher.md in travis section](rancher.md#travis) to know how to configure travis for that.

#### Integration deployment

The integration stack is manually deployed but the process is quite similar with test

* If neeeded, download [rancher-compose](http://releases.rancher.com/compose/beta/v0.7.2/rancher-compose-linux-amd64-v0.7.2.tar.gz) and untar the executable.
* Go to rancher/integration directory
* Decrypt rancher.env.gpg (password is in Lastpass, see [rancher.md](rancher.md#rancher-environment-setup) for the decrypt command)
* `source rancher.env` to set all needed configuration variables in your environment.
* `rancher-compose -p roctool-odoo-integration up -d` to create the stack and start containers


### Upgrade stack

#### Test

As test stack is automatically rebuilt from scratch, there is no need to upgrade


#### Integration / Production

**Warning**: The example below is for integration, replace all `integration` reference (rancher directory, stack name) by `prod` for the production.

To upgrade your stack, first of all you need to prepare your release on the project.
Take a look at [releases.md](releases.md) for more details but here is a quick steps list:
 * Merge all wanted PRs in master and check HISTORY.rst is correctly filled and clear empty sections.
 * Wait for a successfull Travis build
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
 * Travis will run a build on this tag and, if succcessfull, push a docker image (tagged as X.X.X) on Docker Hub.
 * Once the new image is pushed on Docker Hub, upgrade the stack on Rancher:

 ```bash
 cd rancher/integration/
 source <(gpg2 -d rancher.env.gpg) # Password is in Lastpass
 rancher-compose -p roctool-odoo-integration up --pull --recreate --confirm-upgrade -d
 ```

As the docker-compose.yml in rancher/integration directory reference the new image version (changed by invoke),
rancher will download the image and recreate an odoo container with it.

At start, it will automatically execute the upgrade defined in [odoo/migration.yml](../odoo/migration.yml) for this new version.

#### Specific case for integration database

For the integration stack, during development, we use to recreate from scratch the database (if client agrees).

This allows to test correctly the initial setup with full csv files (as this setup will be applied on production).

If it's your case, you have to drop the database and recreate an empty one before execute the last step in previous part (`rancher-compose -p [...]`)

A ssh container with access to the cluster is available. Accessible with connection link as `odoo-platform-db`.

As there are metrics container which keeps open connections to the database you will need to terminate them
and immediately drop the database on the same line, otherwise a connection for the metrics will be reopened before you can even run the drop command.

Here is how to drop and recreate the database:
```
odoo-platform-db

# docker exec -it r-postgres-cluster_postgres_2 bash

root@0e612fdba185:/# psql -U postgres

postgres=# select pg_terminate_backend(pid) from pg_stat_activity where datname = 'mighty_pinguin_l337'; drop database mighty_pinguin_1337;
postgres=# create database mighty_pinguin_1337 owner mighty_pinguin_1337;

```
