import os
import pytest


def available_odoo_urls():
    return {
        name: url for name, url in {
            "odoo_14": os.getenv("ODOO14_URL"),
            "odoo_17": os.getenv("ODOO17_URL"),
            "odoo_19": os.getenv("ODOO19_URL"),
        }.items() if url
    }


@pytest.fixture(scope="session")
def odoo_urls():
    urls = available_odoo_urls()
    if not urls:
        pytest.skip("Aucune instance Odoo disponible (set ODOO14_URL/17_URL/19_URL)")
    return urls
