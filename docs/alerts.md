## Linking Daily Spray Effectiveness with a RapidPro flow.

- Create a flow on RapidPro that will process the Spray Effectiveness data for each spray area, and get the flow UUID. The flow SHOULD start with a "Split By Expression" block. The Spray Effectiveness payload to the RapidPro flow will include `@extra.spray_effictiveness`, `@extra.district` and `@extra.spray_area` fields.
- The flow UUID MUST be configured into the dashboard using the `RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_ID` in settings.
- Create another flow, a trigger flow, on RapidPro. This flow will need to call a webhook, set the webhook to do a `GET` request to "https://[dashboard domain]/api/alerts/daily-spray-effectiveness".
- Create a RapidPro Trigger, "Start a flow in the future or on a schedule.", set the above trigger flow and select the date and schedule when the trigger flow should be run.

When the endpoint `/api/alerts/daily-spray-effectiveness` is accessed by RapidPro, it will send the spray effectiveness results for every spray area that has been visited on the current date.
