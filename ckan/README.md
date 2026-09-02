# CKAN Deployment

## 1. `deployment/ansible_script.yml`

- **Purpose**: Provides an **Ansible playbook** to deploy a new instance of CKAN.
- **Features**:
  - Automates installation and configuration of CKAN and its dependencies.
  - Can be used to deploy a CKAN instance on a cloud VM or on-premise server.
  - Highly customizable to match different deployment environments.

## 2. `deployment/ansible_ckan_deployment.md`

- **Purpose**: Provides **documentation** and step-by-step instructions for using the provided Ansible script.
- **Details**:
  - Describes prerequisites (Ansible installation, target machine setup).
  - Explains how to run the playbook and verify the deployed CKAN instance.


community.postgresql

## Custom Template Overrides

CKAN UI customizations live in `ckan/templates/` and follow CKAN's template inheritance structure. The Ansible playbook copies these to `/etc/ckan/default/custom_templates/` on the server and configures `extra_template_paths` in `ckan.ini`.

- **To add a customization**: Create the override file under `ckan/templates/` matching CKAN's directory structure (e.g., `package/search.html`) and use `{% ckan_extends %}` to inherit the base template. Rerun the playbook.
- **To undo a customization**: Delete the override file from `ckan/templates/` and rerun the playbook. CKAN falls back to its default template automatically.

Current overrides:
- `templates/base.html` — Applies CyVerse branding (blue color scheme) via a `{% block styles %}` override. This replaces custom CSS that was previously pasted by hand into the CKAN admin panel. Also empties `{% block meta_generator %}` so the CKAN version is not advertised in page metadata.
- `templates/footer.html` — Removes CKAN footer boilerplate ("Powered by CKAN" and the "CKAN Association" link), replacing it with CyVerse attribution. Also adds the legal/policy content carried over from the old Data Commons: footer links to the User Agreement, Privacy Policy, Acceptable Use, and the full CyVerse policies page, plus a "By using the Data Commons you agree to the terms of our User Agreement" notice. Links point at the canonical `cyverse.org/policies` pages.
- `templates/home/index.html` — Custom homepage: hero shows the Data Commons logo, the welcome line as a subtitle, and the site description; below it, a grid of featured organizations. Replaces CKAN's default "featured section" placeholder.
- `templates/home/about.html` — Replaces CKAN's default "About" page copy with CyVerse Data Commons text.
- `templates/header.html` — Custom main nav (Datasets / Organizations / About). Also points the "Log in" link straight at the Keycloak SSO flow (`oidc_pkce.login`) and drops "Register", since local username/password login and registration are non-functional. Guarded by `h.plugin_loaded('oidc_pkce')` so it falls back to the default links where the OIDC plugin isn't enabled.
- `templates/user/login.html` — Redirects `/user/login` straight to the OIDC login flow (meta-refresh), forwarding `came_from` so users return to their original page after signing in. Falls back to CKAN's default login form when `oidc_pkce` is not loaded (e.g. local dev).
- `templates/package/search.html` — Adds DE date sort options (Date Created in Discovery Environment) to the dataset search dropdown.

## Static Assets & Branding

Branding is fully version-controlled and deployed by the playbook — nothing is set by hand in the CKAN admin panel anymore.

- **Colors / CSS**: Live in the `{% block styles %}` override in `ckan/templates/base.html` (deployed by the template-copy task above).
- **Logo & favicon**: Binary assets live in `ckan/public/` (`cyverse_white.png`, `datacommons_white.png`, `favicon.ico`). The playbook copies them to `/etc/ckan/default/custom_public/` and serves them from the site root via `extra_public_paths` in `ckan.ini`. `cyverse_white.png` is the navbar logo (`ckan.site_logo`); `datacommons_white.png` is the older Data Commons wordmark shown in the homepage hero (referenced directly in `templates/home/index.html`).
- **Site title / description / intro text / logo / favicon**: Set as `ckan.site_title`, `ckan.site_description`, `ckan.site_intro_text` (the homepage hero heading), `ckan.site_logo`, and `ckan.favicon` in the generated `ckan.ini`. Edit the corresponding `ckan_*` vars at the top of `ansible_script.yml`.

> **The playbook regenerates the entire `ckan.ini` on every run.** Any setting hand-added directly to `/etc/ckan/default/ckan.ini` on the server will be **wiped** the next time the playbook runs. All config must live in `ansible_script.yml`. (This is exactly how the homepage hero text was lost once — `ckan.site_intro_text` had been set by hand in the live ini and a deploy overwrote it, so the page fell back to CKAN's default "Welcome to CKAN".)

> **One-time switchover note (DB overrides):** CKAN's admin-panel appearance settings are stored in the database and **override** `ckan.ini`. If `Custom CSS` or `Site Title`/`Description` were previously set via `/ckan-admin/config`, clear those fields once (or run `config_option_update` to reset them) so the code-managed values take effect. Otherwise the stale DB `custom_css` will duplicate the `base.html` styles and the DB values will shadow the ini.

## Custom Solr Schema

The Solr schema lives in `ckan/solr/schema.xml` (based on CKAN 2.11 default). The playbook deploys it to `/var/solr/data/ckan/conf/managed-schema.xml`.

Custom fields added:
- `extras_de_created_date` (type `date`) — enables sorting datasets by DE creation date

After schema changes, datasets need to be reindexed. This happens automatically when the sync re-processes datasets. To force a full reindex without syncing: `sudo -u www-data /usr/lib/ckan/default/bin/ckan -c /etc/ckan/default/ckan.ini search-index rebuild`