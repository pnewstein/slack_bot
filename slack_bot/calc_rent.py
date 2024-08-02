from dataclasses import dataclass


def get_rent_to_pay(total_rent: int, rent_fraction) -> int:
    """
    returns the total rent to pay in cents given a rent fraction
    """
    return int(round(total_rent * rent_fraction / 5_00) * 5_00)


class ExludedDoesNotExist(Exception):
    pass


@dataclass(frozen=True)
class ConfigData:
    """
    Represnts all the configuration of rent payment supported by this script
    """

    rent: int
    "A month's rent in cents"
    xfinity: int
    "A month's xfinity bill in cents"
    empty_room_split: list[str]
    "The people who will split an empty room"
    fraction_map: dict[str, float]
    un_map: dict[str, str]
    variable_utility_payer: str
    rent_payer: str
    channel_id: str

    @classmethod
    def fromDict(cls, data: dict) -> "ConfigData":
        """
        instantiates itself from a dict, with some data validation
        """
        rent = data["rent"]
        xfinity = data["xfinity"]
        un_map = data["un_map"]
        channel_id = data["channel_id"]
        empty_room_split = data["empty_room_split"]
        if any((n not in un_map.keys() for n in empty_room_split)):
            raise ValueError("Empty room split included invalid names")
        fraction_map_ints = data["fraction_map"]
        if sum(fraction_map_ints.values()) != 1000:
            print(sum(fraction_map_ints.values()))
            raise ValueError("Fraction map does not add to 1000")
        fraction_map = {k: v / 1000 for k, v in fraction_map_ints.items()}
        names = set(fraction_map.keys())
        names.discard("Empty")
        un_map = data["un_map"]
        rent_payer = data["rent_payer"]
        variable_utility_payer = data["variable_utility_payer"]
        if names != set(un_map):
            raise ValueError("Names dont match")
        return cls(
            rent=rent,
            xfinity=xfinity,
            empty_room_split=empty_room_split,
            fraction_map=fraction_map,
            un_map=un_map,
            variable_utility_payer=variable_utility_payer,
            rent_payer=rent_payer,
            channel_id=channel_id,
        )


def calculate_rent_due(
    config_data: ConfigData,
    utility_excluded: set[str],
    total_variable_utilities: int,
    adjustments: dict[str:int],
) -> tuple[list[str], dict[str, int]]:
    """
    returns a list of formated string explaining the math, and a dict for what each member pays
    all money is in cents

    Raises ExludedDoesNotExist
    """
    assert all(person in config_data.fraction_map for person in adjustments)
    calculation_lines: list[str] = []
    calculation_lines.append(f"We owe ${config_data.rent/100:.2f} in rent")
    total_utilities = total_variable_utilities + config_data.xfinity
    calculation_lines.append(
        f"Utilities are ${total_variable_utilities/100:.2f} above + ${config_data.xfinity/100:.2f} from xfinity"
    )
    # Figure out utilities
    utility_payers = set(config_data.fraction_map.keys())
    utility_payers.discard("Empty")
    for excluded in utility_excluded:
        try:
            utility_payers.remove(excluded)
        except KeyError as err:
            raise ExludedDoesNotExist() from err
    utilities_owed = total_utilities / len(utility_payers)
    calculation_lines.append(
        f"We owe ${total_utilities/100:.2f} in utilities, ${utilities_owed/100:.2f} each"
    )
    # how much do we need to subsidize the empty room
    if "Empty" in config_data.fraction_map:
        empty_room_adjustment = get_rent_to_pay(
            config_data.rent, config_data.fraction_map["Empty"]
        ) / len(config_data.empty_room_split)
    else:
        empty_room_adjustment = 0
    # what each person should pay the rent_payer
    out_dict: dict[str, int] = {}
    for person, rent_fraction in config_data.fraction_map.items():
        if person == "Empty":
            # Empty is not a real person
            continue
        persons_rent = get_rent_to_pay(config_data.rent, rent_fraction)
        if empty_room_adjustment and person in config_data.empty_room_split:
            if person in utility_payers:
                total_owed = persons_rent + empty_room_adjustment + utilities_owed
                calculation_lines.append(
                    f"{person} owes ${persons_rent/100:.2f} (rent) "
                    f"+ ${empty_room_adjustment/100:.2f} (empty room) "
                    f"+ ${utilities_owed/100:.2f} (utilities) = ${total_owed/100:.2f}"
                )
            else:
                total_owed = persons_rent + empty_room_adjustment
                calculation_lines.append(
                    f"{person} owes ${persons_rent/100:.2f} (rent) "
                    f"+ ${empty_room_adjustment/100:.2f} (empty room) "
                    f"= ${total_owed/100:.2f}"
                )
        else:
            if person in utility_payers:
                total_owed = persons_rent + utilities_owed
                calculation_lines.append(
                    f"{person} owes ${persons_rent/100:.2f} (rent) "
                    f"+ ${utilities_owed/100:.2f} (utilities) = ${total_owed/100:.2f}"
                )
            else:
                total_owed = persons_rent
                calculation_lines.append(
                    f"{person} owes ${persons_rent/100:.2f} (rent)"
                )
        if person == config_data.variable_utility_payer:
            if person in adjustments:
                total_payed = total_variable_utilities + adjustments[person]
            else:
                total_payed = total_variable_utilities
            total_owed_utility_payer = total_owed - total_payed
            calculation_lines.append(
                f"But {person} already paid ${total_payed/100:.2f}"
                f", so they owe ${total_owed_utility_payer/100:.2f}"
            )
            out_dict[person] = round(total_owed_utility_payer)
        else:
            if person in adjustments:
                total_owed = total_owed - adjustments[person]
                calculation_lines.append(
                    f"But {person} already paid ${adjustments[person]/100:.2f}"
                    f", so they owe ${total_owed/100:.2f}"
                )
            out_dict[person] = round(total_owed)
    out_strings = ["\n\n".join(calculation_lines)]
    for person, amount_owed in out_dict.items():
        if amount_owed >= 0:
            out_strings.append(
                f"{config_data.un_map[person]} pay "
                f"{config_data.rent_payer} {amount_owed/100:.2f}"
            )
        else:
            out_strings.append(
                f"{config_data.rent_payer} pay "
                f"{config_data.un_map[person]} {-amount_owed/100:.2f}"
            )
    return out_strings, out_dict
