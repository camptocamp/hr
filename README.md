[![Build Status](https://travis-ci.com/camptocamp/bso_odoo.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://travis-ci.com/camptocamp/bso_odoo)

# BSO Network Solutions Odoo

**Our internal id for this project is: 1882.**

**Project is installed On-Permises and will not be updated via the
standard procedure on cloud platform**
Once you have a new image built on hub.docker.com, you can send an email
to BSO in order to let them download it and install it.

This project uses Docker.
Travis builds a new image for each change on the branches and for each new tag.

The images built on the master branch are built as `camptocamp/bso_odoo:latest`.
The images built on other branches are built as `camptocamp/bso_odoo:<branch-name>`.
The ones built from tags are built as `camptocamp/bso_odoo:<tag-name>`.

Images are pushed on the registry only when Travis has a green build.

The database is automatically created and the migration scripts
automatically run.

You'll find a [Docker guide for the development](./docs/docker-dev.md) and on for the [testers](./docs/docker-test.md).

## Guides

* [Docker pre-requisite](./docs/prerequisites.md)
* [Docker developer guide](./docs/docker-dev.md)
* [Docker tester guide](./docs/docker-test.md)
* [Structure](./docs/structure.md)
* [Releases and versioning](./docs/releases.md)
* [Pull Requests](./docs/pull-requests.md)
* [Upgrade scripts](./docs/upgrade-scripts.md)
* [Docker Images](./docs/docker-images.md)
* [Using automated tasks with Invoke](./docs/invoke.md)
* [Odoo Cloud Platform](./docs/odoo-cloud-platform.md)
* [Odoo Test Cloud Platform](./docs/odoo-test-cloud-platform.md)

## How-to

* [How to add a new addons repository](./docs/how-to-add-repo.md)
* [How to add a Python or Debian dependency](./docs/how-to-add-dependency.md)
* [How to integrate an open pull request of an external repository](./docs/how-to-integrate-pull-request.md)
* [How to connect to psql in Docker](./docs/how-to-connect-to-docker-psql.md)
* [How to change Odoo configuration values](./docs/how-to-set-odoo-configuration-values.md)
* [How to backup and restore volumes](./docs/how-to-backup-and-restore-volumes.md)

The changelog is in [HISTORY.rst](HISTORY.rst).
