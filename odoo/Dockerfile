FROM camptocamp/odoo-project:10.0-2.2.0
MAINTAINER Camptocamp

COPY ./requirements.txt /opt/odoo

# Install additional debian packages
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
        python-dev \
        build-essential \
        libffi-dev \
        libssl-dev \
        && cd /opt/odoo && pip install -r requirements.txt \
        # Install additional python packages
        && apt-get remove -y python-dev build-essential libffi-dev libssl-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*


ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
  /opt/odoo/src/addons, \
  /opt/odoo/external-src/account-financial-tools, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/connector-jira, \
  /opt/odoo/external-src/hr, \
  /opt/odoo/external-src/hr-timesheet, \
  /opt/odoo/external-src/margin-analysis, \
  /opt/odoo/external-src/partner-contact, \
  /opt/odoo/external-src/product-variant, \
  /opt/odoo/external-src/purchase-workflow, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/queue, \
  /opt/odoo/external-src/project, \
  /opt/odoo/external-src/web, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/local-src," \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
