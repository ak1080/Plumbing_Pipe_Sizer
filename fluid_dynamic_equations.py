import numpy as np
from scipy.optimize import fsolve

GRAVITY = 32.174  # ft/s^2

def reynolds_num(velocity, diam_inch, kin_visc):
    """
    Calculate Reynolds number using velocity (ft/s),
    pipe diameter in inches, and kinematic viscosity in ft^2/s.

    Re = (v * D_ft) / nu = (v * (diam_inch/12)) / kin_visc
    """
    return (velocity * (diam_inch / 12.0)) / kin_visc


def friction_factor_solver(re, epsilon, diam_inch, initial_guess=0.02):
    """
    Solves the Colebrook-White equation for the Darcy-Weisbach friction factor
    using fsolve.

    re        : Reynolds number
    epsilon   : absolute roughness (ft)
    diam_inch : pipe diameter in inches
    """
    # Convert diam_inch to ft
    D_ft = diam_inch / 12.0

    # Define the Colebrook–White equation function (set = 0):
    def colebrook_white(f):
        # 1/sqrt(f) = -2 log10( (epsilon/(3.7D)) + (2.51/(Re sqrt(f))) )
        return (1.0 / np.sqrt(f) +
                2.0 * np.log10((epsilon / (3.7 * D_ft)) +
                               (2.51 / (re * np.sqrt(f)))))
    # Laminar flow condition. Refer to Moody chart.
    if re < 2000:
        friction_factor = 64/re
    else:
        # fsolve will numerically solve for the root "f". Needs an initial guess. Think back to numerical analysis class.
        friction_factor = fsolve(colebrook_white, initial_guess)[0]
    return friction_factor


def darcy_weisbach_pressure_drop(f, velocity, diam_inch):
    """
    Calculates the pressure loss (in ft of head per 100 ft of pipe) using the Darcy–Weisbach equation:
    h_f = (f * L * v^2) / (D_ft * 2*g)

    Here, L=100 ft =>
    h_f (ft per 100 ft) = [f * 100 * v^2] / [(D_inch/12) * 2*g]
    """
    D_ft = diam_inch / 12.0
    # Darcy–Weisbach head loss for 100 ft of pipe:
    h_f = (f * 100.0 * velocity ** 2) / (D_ft * 2.0 * GRAVITY)
    return h_f


def solve_velocity_given_pressure_drop(friction_rate_target, diam_inch, epsilon, kin_visc, velocity_guess=5.0):
    """
    Solve for velocity (ft/s) given a target friction rate in ft H2O per 100 ft pipe.

    friction_rate_target : target head loss (ft / 100 ft)
    diam_inch            : pipe diameter (inches)
    epsilon              : absolute roughness (ft)
    kin_visc             : kinematic viscosity (ft^2/s)
    velocity_guess       : initial guess for velocity (ft/s)
    """

    # Define the function whose root we'll find via fsolve
    def friction_rate_residual(velocity):
        # 1) Compute Reynolds number
        re = reynolds_num(velocity, diam_inch, kin_visc)
        # 2) Solve for friction factor using Colebrook–White
        f = friction_factor_solver(re, epsilon, diam_inch)
        # 3) Compute the Darcy–Weisbach friction head loss (ft H2O per 100 ft)
        h_f = darcy_weisbach_pressure_drop(f, velocity, diam_inch)
        # Return difference from target
        return h_f - friction_rate_target

    # Use fsolve to drive friction_rate_residual(...) to zero
    solution = fsolve(friction_rate_residual, velocity_guess)
    return float(solution[0])


# ------------------------------------------------------------------------
# DEMO / TEST
# ------------------------------------------------------------------------
if __name__ == "__main__":

    diam_inch = 1.025
    epsilon_ft = 0.00006
    nu_ft2_s = 1.2075e-5
    friction_rate = 25  # ft / 100 ft
    v_guess = 5.0  # ft/s

    v_solution = solve_velocity_given_pressure_drop(
        friction_rate, diam_inch, epsilon_ft, nu_ft2_s, v_guess
    )
    gpm = (v_solution * diam_inch ** 2) / 0.4084  # Using velocity in ft/s. Pipe diam in inches.


    # Print results
    print("=== Solve Velocity for Target Friction Rate ===")
    print(f"Pipe ID:             {diam_inch} inches")
    print(f"Epsilon:             {epsilon_ft} ft")
    print(f"Kinematic Viscosity: {nu_ft2_s} ft^2/s")
    print(f"Friction Rate:       {friction_rate} ftH2O/100ft or {friction_rate/2.31:.2f} psi/100ft")
    print(f"Solution velocity:   {v_solution:.2f} ft/s")
    print(f"Solution GPM:        {gpm:.1f} GPM")