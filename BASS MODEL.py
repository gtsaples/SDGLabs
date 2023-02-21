"""
Python model 'BASS MODEL.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.9.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 10,
    "time_step": lambda: 0.0625,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="aadopters leaving the service completely",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"adopters_a": 1, "leaving_serviceproduct_rate": 1},
)
def aadopters_leaving_the_service_completely():
    return adopters_a() * leaving_serviceproduct_rate()


@component.add(
    name='"becoming potential adopters after product/service update"',
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"cost_variable_to_update_productservice": 1},
)
def becoming_potential_adopters_after_productservice_update():
    return np.interp(
        cost_variable_to_update_productservice(),
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        [0.4, 0.45, 0.5, 0.65, 0.7, 0.65, 0.6, 0.5, 0.3, 0.1],
    )


@component.add(
    name="becoming potential adopters for new service",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "switch": 1,
        "adopters_a": 1,
        "becoming_potential_adopters_after_productservice_update": 1,
    },
)
def becoming_potential_adopters_for_new_service():
    return (
        switch()
        * adopters_a()
        * becoming_potential_adopters_after_productservice_update()
    )


@component.add(
    name="cost spent on advertising", comp_type="Constant", comp_subtype="Normal"
)
def cost_spent_on_advertising():
    return 0.0


@component.add(
    name='"cost variable to update product/service"',
    comp_type="Constant",
    comp_subtype="Normal",
)
def cost_variable_to_update_productservice():
    return 0.0


@component.add(
    name='"leaving service/product rate"', comp_type="Constant", comp_subtype="Normal"
)
def leaving_serviceproduct_rate():
    return 0.1


@component.add(name="switch", comp_type="Constant", comp_subtype="Normal")
def switch():
    return 1


@component.add(
    name="Adopters A",
    units="Units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_adopters_a": 1},
    other_deps={
        "_integ_adopters_a": {
            "initial": {},
            "step": {
                "adoption_rate_ar": 1,
                "aadopters_leaving_the_service_completely": 1,
                "becoming_potential_adopters_for_new_service": 1,
            },
        }
    },
)
def adopters_a():
    """
    The number of active adopters in the system.
    """
    return _integ_adopters_a()


_integ_adopters_a = Integ(
    lambda: adoption_rate_ar()
    - aadopters_leaving_the_service_completely()
    - becoming_potential_adopters_for_new_service(),
    lambda: 0,
    "_integ_adopters_a",
)


@component.add(
    name="Advertising Effectiveness a",
    units="1/Year",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"cost_spent_on_advertising": 1},
)
def advertising_effectiveness_a():
    """
    Advertising results in adoption according the effectiveness of the advertising.
    """
    return np.interp(
        cost_spent_on_advertising(),
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        [0.011, 0.012, 0.013, 0.014, 0.015, 0.015, 0.018, 0.018, 0.016, 0.014],
    )


@component.add(
    name="Potential Adopters P",
    units="Units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_potential_adopters_p": 1},
    other_deps={
        "_integ_potential_adopters_p": {
            "initial": {},
            "step": {
                "becoming_potential_adopters_for_new_service": 1,
                "adoption_rate_ar": 1,
            },
        }
    },
)
def potential_adopters_p():
    """
    The number of potential adopters is determined by the total population size and the current number of active adopters.
    """
    return _integ_potential_adopters_p()


_integ_potential_adopters_p = Integ(
    lambda: becoming_potential_adopters_for_new_service() - adoption_rate_ar(),
    lambda: 1000000.0,
    "_integ_potential_adopters_p",
)


@component.add(
    name="Adoption Rate AR",
    units="Units/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"adoption_from_advertising": 1, "adoption_from_word_of_mouth": 1},
)
def adoption_rate_ar():
    """
    The rate at which a potential adopter becomes an active adopter. This is driven by advertising efforts and the word of mouth effect.
    """
    return adoption_from_advertising() + adoption_from_word_of_mouth()


@component.add(
    name="Adoption from Advertising",
    units="Units/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"advertising_effectiveness_a": 1, "potential_adopters_p": 1},
)
def adoption_from_advertising():
    """
    Adoption can result from advertising according to the effectiveness of the advertising effort with the pool of potential adopters.
    """
    return advertising_effectiveness_a() * potential_adopters_p()


@component.add(
    name="Total Population N",
    units="Units",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_population_n():
    """
    The size of the total population.
    """
    return 1000000.0


@component.add(
    name="Adoption from Word of Mouth",
    units="Units/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "contact_rate_c": 1,
        "adoption_fraction_i": 1,
        "potential_adopters_p": 1,
        "adopters_a": 1,
        "total_population_n": 1,
    },
)
def adoption_from_word_of_mouth():
    """
    Adoption by word of mouth is driven by the contact rate between potential adopters and active adopters and the fraction of times these interactions will result in adoption. The word of mouth effect is small if the number of active adopters relative to the total population size is small.
    """
    return (
        contact_rate_c()
        * adoption_fraction_i()
        * potential_adopters_p()
        * adopters_a()
        / total_population_n()
    )


@component.add(
    name="Contact Rate c", units="1/Year", comp_type="Constant", comp_subtype="Normal"
)
def contact_rate_c():
    """
    The rate at which active adopters come into contact with potential adopters.
    """
    return 100


@component.add(
    name="Adoption Fraction i",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def adoption_fraction_i():
    """
    The fraction of times a contact between an active adopter and a potential adopter results in adoption.
    """
    return 0.015
