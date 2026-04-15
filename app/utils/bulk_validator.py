def validate_employee_row(row):

    if not row.get("employee_code"):
        return "employee_code missing"

    if not row.get("company_email"):
        return "company_email missing"

    if row.get("role") not in ["admin", "employee"]:
        return "invalid role"

    return None