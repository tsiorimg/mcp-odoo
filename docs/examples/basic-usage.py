"""Basic end-to-end usage of MCP Odoo (works for 14–19).

- Auto-detects Odoo version and chooses XML-RPC or JSON-2.
- Demonstrates CRUD and fields_get.
"""

import os
from mcp_odoo.core.factory import MCPOdoo


def main():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    database = os.getenv("ODOO_DATABASE", "mcp_test")
    api_key = os.getenv("ODOO_API_KEY", "admin")  # password is accepted for XML-RPC

    mcp = MCPOdoo(url=url, database=database, api_key=api_key)

    # Create
    partner_id = mcp.create(
        "res.partner",
        {"name": "MCP Example", "email": "example@mcp.local", "phone": "+33102030405"},
    )
    print("Created partner:", partner_id)

    # Read
    partner = mcp.read("res.partner", [partner_id], ["name", "email", "phone"])[0]
    print("Read partner:", partner)

    # Update
    mcp.write("res.partner", [partner_id], {"phone": "+33999999999"})
    updated = mcp.read("res.partner", [partner_id], ["phone"])[0]
    print("Updated phone:", updated["phone"])

    # Fields introspection
    fields = mcp.fields_get("res.partner", ["string", "type"])
    print("Field 'email' meta:", fields["email"])

    # Delete
    mcp.unlink("res.partner", [partner_id])
    print("Deleted partner; search returns:", mcp.search("res.partner", [("id", "=", partner_id)]))


if __name__ == "__main__":
    main()
