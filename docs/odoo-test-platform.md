# Odoo Test Platform

## Introduction

This platform builds test instances for our projects.  The tests instances are
mainly intended to be used by Camptocamp developers and project managers, but
occasionally they may be useful for showing a feature to a customer.  New
features can be tested on these instances before deploying to integration.

The test instances are automatically created on every successful commit on the
branches of a project.  Only 3 instances per branch can exist at the same time,
hence any further build will drop the oldest one.

For this reason:
* This instance should be populated with a small set of data in order to be
  quickly created.
* Assume this instance **will be deleted** with all the data you
  have created or modified.
* We will not put the test database on the postgres cluster but in a standalone
  container in the test stack.

The platform is on
[https://caas-dev.camptocamp.com/env/1a100359/apps/stacks](https://caas-dev.camptocamp.com/env/1a100359/apps/stacks).

**Minions overview**:
https://bso_odoo.odoo-test.camptocamp.ch

Minion test instances are created in the `*.odoo-test.camptocamp.ch`
subdomain, such as bso_odoo-1.odoo-test.camptocamp.ch.

## Setup 

### Overview

The test infrastructure for a project is composed of two parts:

* A Rancher Minion server, started on the test Rancher platform. It waits for
  orders to spawn new test instances and provides a dashboard showing all the
  test instances.
* A small Rancher Minion client in the project repository which asks creation
  of new test server on successful commits (called at the end of the Travis
  build).

### Run a Rancher Minion server

The Rancher compositions for the Rancher Minion servers are stored in
https://github.com/camptocamp/odoo-cloud-platform-test-rancher-templates.

1. Follow this documentation to generate the stack:
   https://github.com/camptocamp/odoo-cloud-platform-test-rancher-templates#generate-a-new-rancher-minion-stack

2. When the stack is generated, it generates token and passwords for you. If it
   could not create them automatically on Lastpass, please add them manually.

3. Commit the new files

4. The server will use the domain "project.odoo-test.camptocamp.ch", so if a
   test server was already using this domain, it should be stopped and removed.

5. Start the stack on Rancher (`./rancher project-rancher-minion up -d`)

#### Server passwords

The passwords generated on Lastpass are:

* `[odoo-test] bso_odoo auth token for creating stacks on rancher-minion server`:
  is the token used by the client in the project repository to be able to generate new Minions on Travis builds
* `[odoo-test] bso_odoo rancher-minion for test servers`:
  is the Basic Auth to access the Rancher Minion server and see the instances
* `[odoo-test] bso_odoo default Test DB password`:
  is the PostgreSQL password of the generated test databases
* `[odoo-test] bso_odoo default Test database manager password`:
  is the Odoo's Database Manager password for the test instances

### Setup the Rancher Minion client

This part happens in the project's repository.

If you are working on a new project, the base files should have been copied from the odoo-template project.
If you are migrating an existing project to the Rancher Minion infrastructure,
you will need to copy files from
https://github.com/camptocamp/odoo-template/tree/master/%7B%7Bcookiecutter.repo_name%7D%7D,
namely:

* update `.travis.yml`, environment variables have changed, including the secure key which now contains the Rancher Minion Server
* Replace the `travis` directory
* The `rancher` directory should no longer be required

Both for new or existing projects, you will have to complete the files:

#### Setup Environment variables in Travis configuration

Configure in the `.travis.yml` file the global variables:

* `GENERATED_IMAGE=${COMPOSE_PROJECT_NAME}_odoo`
* `DOCKER_HUB_REPO=camptocamp/bso_odoo_odoo`
* `RANCHER_MINION_SERVER=https://bso_odoo.odoo-test.camptocamp.ch`

Then, set the Rancher Minion server token in a secured variable.  It has been
generated previously and must be set in a secure variable named
`minion_server_token` in `.travis.yml`:

* Install, if needed, the travis command line client

 ```bash
 sudo gem install travis
 ```

* Authenticate yourself on travis server with your github account.

 ```bash
 travis login
 ```

* Then ask Travis to encrypt the token (should have been added to Lastpass when the Rancher Minion server was created)

 ```bash
 travis encrypt -r camptocamp/<repository_name> minion_server_token=xxxxxxx
 ```

The output of this command (should be like `secure=encrypted key`) should be
added in the `global` section in `env` of `.travis.yml`.


#### Check composition files

Edit the files in `travis/minion-files` and ensure that they match with your project's needs (name of the image and so on).
