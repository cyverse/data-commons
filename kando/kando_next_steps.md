# Next Steps: Data Commons

## Data Publishing Pipeline — Kando vs. Structured Workflow

A key decision involves determining the optimal mechanism for initiatives to publish data to the Data Commons. Two approaches merit consideration:

- **Kando-based publishing:** Initiatives publish directly through Kando, allowing broad flexibility in what is submitted to the Data Environment.
- **Structured staging pipeline:** A more controlled workflow in which a cron job monitors designated directories for newly staged data and triggers a publishing process upon detection.

An additional option worth exploring is integrating publishing functionality into the portal(s) currently being developed by Tyson. This could include a dedicated "Publish to Data Commons" action that simultaneously updates all relevant AVUs, streamlining the workflow for end users.

## Organizational Structure — Shared vs. Dedicated CKAN Instances

Two architectural models should be evaluated for how organizations are represented within the Data Commons:

- **Single shared CKAN instance:** A unified Data Commons with multiple organizations, where CyVerse hosts its own data under the CyVerse organization, and partners such as NCEMS and ESIIL maintain their own organizational spaces with the ability to publish independently via the portal.
- **Dedicated CKAN instances:** A separate CKAN deployment for each organization, providing greater isolation and customization at the cost of increased infrastructure overhead.

Each model presents distinct trade-offs in terms of maintenance complexity, data governance, and scalability. The preferred approach should be weighed against the operational capacity of each participating organization.
