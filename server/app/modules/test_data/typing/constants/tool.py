from app.shared.permissions import Capability

SET_TEST_DATA_CAPABILITY = Capability.TEST_DATA_EDIT
SET_TEST_DATA_DESCRIPTION = (
    "Save a non-secret test data value (kind variable or endpoint) for the whole project, or for one environment "
    "by name, where it overrides the project value. An existing key in that scope is updated. kind secret is "
    "refused: secrets are added on the Test data page. Save only a value the person confirmed."
)
