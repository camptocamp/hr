FROM camptocamp/odoo-project:9.0-2.0.0
MAINTAINER Camptocamp

COPY ./requirements.txt ./

# Install additional debian packages
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
        python-dev \
        build-essential \
        libffi-dev \
        libssl-dev \
        # Install additional python packages
        && pip install -r requirements.txt \
        && apt-get remove -y python-dev build-essential libffi-dev libssl-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
  /opt/odoo/src/addons, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/product-variant, \
  /opt/odoo/external-src/web, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/hr-timesheet, \
  /opt/odoo/external-src/partner-contact, \
  /opt/odoo/external-src/hr, \
  /opt/odoo/external-src/connector-jira, \
  /opt/odoo/local-src," \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
