FROM camptocamp/odoo-project:10.0-2.0.0
MAINTAINER Camptocamp

# Install additional debian packages if needed
# RUN set -x; \
#         apt-get update \
#         && apt-get install -y --no-install-recommends \
#         python-shapely \
#         && apt-get clean \
#         && rm -rf /var/lib/apt/lists/*

# Install additional python packages if needed
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
  /opt/odoo/src/addons, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/external-src/hr, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/hr-timesheet, \
  /opt/odoo/external-src/intrastat, \
  /opt/odoo/local-src," \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
