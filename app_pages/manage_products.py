"""Manage > Products (S11, S12). Staff and owner. Owner: User 3.

Stories: US-MGT-02 list (U3-01), US-MGT-05 hide/show (U3-02), US-MGT-03 create (U3-03),
US-MGT-04 bulk edit (U3-04), US-MGT-07 image (U3-05), US-MGT-06 delete (U3-06).
Use services.admin_products and services.storage; the add/edit form goes in components/product_form.py.
Staff never see price, gift, Add or Delete controls (02-ui-ux.md §4.10).
"""

from components.states import coming_soon
from utils.guards import require_role

user = require_role("staff", "owner")

coming_soon("US-MGT-02 · U3-01", "every product, including hidden ones, with search and bulk edit")
