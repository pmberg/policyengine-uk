from policyengine_uk.model_api import *


class AFCS(Variable):
    value_type = float
    entity = Person
    label = "Armed Forces Compensation Scheme"
    definition_period = YEAR
    unit = GBP
    uprating = "calibration.uprating.september_cpi"

    def formula(person, period, parameters):
        return person("AFCS_reported", period)


class AFCS_reported(Variable):
    value_type = float
    entity = Person
    label = "Armed Forces Compensation Scheme (reported)"
    definition_period = YEAR
    unit = GBP
