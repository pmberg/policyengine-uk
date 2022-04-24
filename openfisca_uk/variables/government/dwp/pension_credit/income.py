from openfisca_uk.model_api import *

class pension_credit_income(Variable):
    label = "Income for Pension Credit"
    entity = BenUnit
    definition_period = YEAR
    value_type = float
    unit = "currency-GBP"
    reference = "https://www.legislation.gov.uk/ukpga/2002/16/section/15"

    formula = sum_of_variables("dwp.pension_credit.income.sources")

