# ALeRCE Lightcurve API
## For developers
Run with `poetry run uvicorn api.api:app` or `poetry run dev`
## HTMX endpoint
The htmx returned by this API's htmx endpoint emits the following events:
|       Event      |       Trigger     |      Detail content     |     Level     |
|:----------------:|:-----------------:|:-----------------------:|:-------------:|
| onDetectionClick | Clicked detection | Clicked detection index | document.body |
