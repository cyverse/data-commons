#!/bin/bash
echo "[entrypoint.d] Patching ckan.ini with Docker service connection settings..."
ckan config-tool $CKAN_INI \
  "sqlalchemy.url = $CKAN_SQLALCHEMY_URL" \
  "solr_url = $CKAN_SOLR_URL" \
  "ckan.redis.url = $CKAN_REDIS_URL" \
  "ckan.site_url = $CKAN_SITE_URL"
echo "[entrypoint.d] Config patched."
