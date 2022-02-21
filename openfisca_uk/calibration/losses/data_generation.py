import pandas as pd
import warnings
import yaml
from openfisca_uk.system import CountryTaxBenefitSystem

warnings.filterwarnings("ignore")

START_YEAR = 2019  # The year to down-rate inputs to.
parameters = CountryTaxBenefitSystem().parameters

def construct_age_decades_per_region(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()
    cols = ["Name"]
    df.Name = df.Name.apply(lambda x: str(x).replace(" ", "_")).apply(
        lambda x: {
            "YORKSHIRE_AND_THE_HUMBER": "YORKSHIRE",
            "EAST": "EAST_OF_ENGLAND",
        }.get(x, x)
    )

    def safe_number(x):
        return float(str(x).replace(",", ""))

    for i in range(10, 90, 10):
        name = f"BETWEEN_{i-10}_{i}"
        cols += [name]
        df[name] = sum(
            [df[str(j)].apply(safe_number) for j in range(i - 10, i)]
        )
    cols += ["OVER_80"]
    df["OVER_80"] = sum(
        [df[str(i)].apply(safe_number) for j in range(80, 90)]
    ) + df["90+"].apply(safe_number)
    df = df[cols]
    return df


def write_parameter(
    male: pd.DataFrame, female: pd.DataFrame, year: int
) -> str:
    parameter = {"MALE": {}, "FEMALE": {}}
    for df, label in zip([male, female], ["MALE", "FEMALE"]):
        df = df.set_index("Name")
        param = parameter[label]
        for region in df.index:
            param[region] = {
                "metadata": {
                    "propagate_metadata_to_children": True,
                    "uprating": {
                        "parameter": f"calibration.regional_populations.{region}",
                    }
                }
            }
            uprater = getattr(parameters.calibration.regional_populations, region)
            downrating_multiplier = (
                uprater(f"{START_YEAR}-01-01") / uprater(f"{year}-01-01")
            )
            for col in df.columns:
                param[region][col] = {
                    "values": {f"{START_YEAR}-01-01": f"{df[col].loc[region] * downrating_multiplier:_.0f}"}
                }
    return yaml.dump(parameter).replace("'", "")


# Sources:
# Male, mid-2020: https://docs.google.com/spreadsheets/d/1SQn3BzQcqvTliwjoN5tnHTG2EIIoqv3n2zA-yEXJ7v8/edit?usp=sharing
# Female, mid-2020: https://docs.google.com/spreadsheets/d/1lI9nx_XUFzCqH99a8fQ_qNp7WbOu0u9LdFPFxfAwc44/edit#gid=0


male = pd.read_csv("~/Downloads/Male ONS populations.csv")
female = pd.read_csv("~/Downloads/Female ONS populations.csv")

male = construct_age_decades_per_region(male)
female = construct_age_decades_per_region(female)

print(write_parameter(male, female, 2020))
