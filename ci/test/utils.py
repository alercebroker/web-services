from test.tests_stage_steps import healthcheck_test_step

staging_url = "https://api.staging.alerce.online/v2"
prod_url = "https://api.alerce.online/v2"

_tests_selection = {
    "lightcurve": [
        {
            "step": healthcheck_test_step,
            "args": {
                "staging": [f"{staging_url}/lightcurve/healthcheck"],
                "production": [f"{prod_url}/lightcurve/healthcheck"],
            },
        },
    ],
    "astroobject": [
        {
            "step": healthcheck_test_step,
            "args": {
                "staging": [f"{staging_url}/astroobject/healthcheck"],
                "production": [f"{prod_url}/astroobject/healthcheck"],
            },
        },
    ],
    "xmatch-service": [
        {
            "step": healthcheck_test_step,
            "args": {
                "staging": [f"{staging_url}/xmatch-service"],
                "production": [f"{prod_url}/xmatch-service"],
            },
        },
    ]
}
