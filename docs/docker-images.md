# Automated Docker Images

## Travis deployment

When Travis runs, it builds a Docker image and runs the tests inside it.
If the tests pass, it uploads the image to DockerHub and generate a new test
instance on the [test platform](./odoo-test-platform.md).

## Rancher templates

### Test instances

See [Odoo Test Plaftorm](./odoo-test-platform.md)

### Integration and production instances

The Rancher templates for the integration and production instances are grouped in a project
for the platform:

* https://github.com/camptocamp/odoo-cloud-platform-ch-rancher-templates

## Docker images

Docker images for Odoo are generated and pushed to [Docker Hub](https://hub.docker.com) by Travis when builds are successful.
This push is done in [travis/publish.sh](../travis/publish.sh) which is called by [travis.yml](../.travis.yml) in `after_success` section.

This script will tag docker image with:
 * latest: When the build was triggered by a commit on master
 * `git tag name`: When the build was triggered after a new tag is pushed.
 * a tag generated with the git commit, used by the test instances

So Travis must have access to your project on Docker Hub. If it's not the case, ask someone with access to:
 * Create if needed the [project on Docker Hub](https://hub.docker.com/r/camptocamp/bso_odoo/)
 * Create access for Travis in this new project and put auth informations in Lastpass
  * user: c2cbusinessbso_odootravis
  * password: Generated password
  * email: business-deploy+bso_odoo-travis@camptocamp.com (which is aliased on camptocamp@camptocamp.com)

On Travis, in [settings page](https://travis-ci.com/camptocamp/bso_odoo/settings) , add following environnement variables:
 * DOCKER_USERNAME : c2cbusinessbso_odootravis
 * DOCKER_PASSWORD : The generated password in previous step, so you can find it in Lastpass

**From there, each travis successful build on master or on tags will build a docker image and push it to Docker Hub**
