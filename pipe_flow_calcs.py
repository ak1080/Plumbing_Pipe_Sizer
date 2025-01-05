"""
Uniform Plumbing Code - Appendix A Calculator (Based on 2021 Illustrated Training Manual)

Author: Alex Kalmbach

Description: This Python script calculates cold water and hot water maximum GPM and fixture units
based on user inputs. It performs calculations for various pipe sizes and outputs
the results in a GUI using Tkinter.

Modules:
- fluid_dynamic_equations: Contains functions for solving fluid dynamics equations.
- gpm_and_fixture_units: Contains functions for converting GPM to fixture units and interpolating if necessary

Usage:
Run this script to open the GUI. Enter the required inputs and view the calculated
cold and hot water outputs in the tables.

Version: 1.0 (completed 01/05/2025)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from fluid_dynamic_equations import (
    darcy_weisbach_pressure_drop,
    solve_velocity_given_pressure_drop,
    friction_factor_solver,
    reynolds_num
)
from gpm_and_fixture_units import interpolate_fixture_units

# Constants
COPPER_EPSILON = 5.0e-6  # Roughness for type L copper
WATER_KIN_VISC = 1.2075e-5  # ft^2/s for water at 60°F

# Dictionary of pipe sizes based in type L copper.
copper_pipe_sizes = {
    0.5: 0.545, 0.75: 0.785, 1: 1.025, 1.25: 1.265, 1.5: 1.505, 2: 1.985,
    2.5: 2.465, 3: 2.945, 4: 3.905
}

# Helper function to get valid float input or default to 0.0
def get_float(entry):
    try:
        return float(entry.get())
    except ValueError:
        return 0.0
def show_info():
    info_text = (
        "Uniform Plumbing Code - Appendix A Calculator\n\n"
        "This tool helps engineers calculate the maximum allowable GPM and fixture units "
        "for cold water and hot water systems based on input parameters like "
        "pressure, pipe length, and velocity limits.\n\n"
        "Suggested Maximum Velocities:\n"
        "      Cold Water: 8 ft/s\n"
        "      Hot Water: 5 ft/s\n"
        "Velocity Limit Per Code: 10 ft/s\n\n"
        "Design Parameters Used:\n"
        f"     Type L Copper Roughness: {COPPER_EPSILON} ft\n"
        f"     Water Kinematic Viscosity: {WATER_KIN_VISC} ft^2/s (at 60°F)\n\n"
        "Developed in Python by Alex Kalmbach."
    )
    messagebox.showinfo("About this Tool", info_text)

# Calculation function
def calculate(event=None):
    try:
        # Get inputs
        cw_pressure_psi = get_float(cw_pressure_entry)
        hw_pressure_psi = get_float(hw_pressure_entry)
        developed_length = get_float(length_entry)
        cw_max_velocity = get_float(cw_velocity_entry)
        hw_max_velocity = get_float(hw_velocity_entry)

        # Get the selected fixture type for cold water
        fixture_type = fixture_type_combobox.get()
        cw_fixture_type = "Tank" if fixture_type == "Flush Valve Tanks" else "Valve"
        hw_fixture_type = "Tank"  # Hot Water Fixture Units always tank

        # Check for valid inputs
        if cw_pressure_psi == 0 or hw_pressure_psi == 0 or developed_length == 0 or cw_max_velocity == 0 or hw_max_velocity == 0:
            raise ZeroDivisionError

        # Calculate available friction rates
        cw_friction_rate = (cw_pressure_psi / developed_length) * 2.31 * 100  # ftH2O per 100 ft
        hw_friction_rate = (hw_pressure_psi / developed_length) * 2.31 * 100  # ftH2O per 100 ft

        # Update the friction rate labels
        cw_friction_rate_label.config(text=f"Cold Water Max Friction Rate: {cw_friction_rate:.2f} ft/100ft")
        cw_friction_rate_psi_label.config(text=f"({cw_friction_rate / 2.31:.2f} psi/100ft)", font=("Helvetica", 9))

        hw_friction_rate_label.config(text=f"Hot Water Max Friction Rate: {hw_friction_rate:.2f} ft/100ft")
        hw_friction_rate_psi_label.config(text=f"({hw_friction_rate / 2.31:.2f} psi/100ft)", font=("Helvetica", 9))

        # Clear previous outputs
        for row in table_cw.get_children():
            table_cw.delete(row)
        for row in table_hw.get_children():
            table_hw.delete(row)

        # Loop through all pipe sizes and perform calculations
        for pipe_size, pipe_inner_diam in copper_pipe_sizes.items():
            # CW calculations
            cw_velocity = solve_velocity_given_pressure_drop(cw_friction_rate, pipe_inner_diam, COPPER_EPSILON, WATER_KIN_VISC)

            # Below is a very important line of code. Determines the velocity we'll be using to determine max GPM and therefore max FU's.
            cw_velocity = min(cw_velocity, cw_max_velocity)  # Ensure velocity does not exceed max

            cw_re = reynolds_num(cw_velocity, pipe_inner_diam, WATER_KIN_VISC)
            cw_fric_factor = friction_factor_solver(cw_re, COPPER_EPSILON, pipe_inner_diam)
            cw_pressure_drop = darcy_weisbach_pressure_drop(cw_fric_factor, cw_velocity, pipe_inner_diam)
            cw_gpm = (cw_velocity * pipe_inner_diam ** 2) / 0.4084

            # Interpolate fixture units for CW. The interpolate function is from the gpm_and_fixture_units module.
            cw_fixture_units = interpolate_fixture_units(cw_gpm, cw_fixture_type)

            # HW calculations
            hw_velocity = solve_velocity_given_pressure_drop(hw_friction_rate, pipe_inner_diam, COPPER_EPSILON, WATER_KIN_VISC)
            hw_velocity = min(hw_velocity, hw_max_velocity)  # Ensure velocity does not exceed max

            hw_re = reynolds_num(hw_velocity, pipe_inner_diam, WATER_KIN_VISC)
            hw_fric_factor = friction_factor_solver(hw_re, COPPER_EPSILON, pipe_inner_diam)
            hw_pressure_drop = darcy_weisbach_pressure_drop(hw_fric_factor, hw_velocity, pipe_inner_diam)
            hw_gpm = (hw_velocity * pipe_inner_diam ** 2) / 0.4084

            # Interpolate fixture units for HW
            hw_fixture_units = interpolate_fixture_units(hw_gpm, hw_fixture_type)

            # Populate CW table
            table_cw.insert('', 'end', values=(
                f"{pipe_size} in", f"{cw_velocity:.2f} ft/s", f"{cw_gpm:.1f} GPM", f"{cw_fixture_units}", cw_fixture_type,
                f"{cw_pressure_drop:.2f}  ({cw_pressure_drop / 2.31:.2f})",
                f"{cw_fric_factor:.4f}", f"{cw_re:,.0f}"
            ))

            # Populate HW table
            table_hw.insert('', 'end', values=(
                f"{pipe_size} in", f"{hw_velocity:.2f} ft/s", f"{hw_gpm:.1f} GPM", f"{hw_fixture_units}", hw_fixture_type,
                f"{hw_pressure_drop:.2f}  ({hw_pressure_drop / 2.31:.2f})",
                f"{hw_fric_factor:.4f}", f"{hw_re:,.0f}"
            ))

    except ZeroDivisionError:
        # Clear previous outputs and show "err" if inputs are missing
        for row in table_cw.get_children():
            table_cw.delete(row)
        for row in table_hw.get_children():
            table_hw.delete(row)
        for pipe_size in copper_pipe_sizes:
            table_cw.insert('', 'end', values=(f"{pipe_size} in", "-", "-", "-", "-", "-", "-"))
            table_hw.insert('', 'end', values=(f"{pipe_size} in", "-", "-", "-", "-", "-", "-"))

# GUI Setup
root = tk.Tk()
root.title("Uniform Plumbing Code - Appendix A Calculator")

# Title Label with Info Button
title_frame = ttk.Frame(root)
title_frame.grid(row=0, column=0, columnspan=3, pady=5)

title_label = ttk.Label(title_frame, text="Uniform Plumbing Code - Appendix A Calculator", font=("Helvetica", 12, "bold"))
title_label.pack(side="left")

# Adding the Info Button
info_button = ttk.Button(
    title_frame,
    text="i",
    command=show_info,
    width=2  # Adjust width to make the button smaller
)
info_button.pack(side="left", padx=5, pady=2)

# Center the text in the button
info_button_style = ttk.Style()
info_button_style.configure("TButton", anchor="center", font=("Helvetica", 12, "bold"))


# Input Fields
input_frame = ttk.Frame(root)
input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Dropdown Menu for Fixture Type
ttk.Label(input_frame, text="Fixture Type:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
fixture_type_combobox = ttk.Combobox(input_frame, values=["Flush Valve Tanks", "Flushometer Valves"], state="readonly")
fixture_type_combobox.grid(row=0, column=1, padx=5, pady=2)
fixture_type_combobox.current(0)

# Bind the dropdown to recalculate on selection change
fixture_type_combobox.bind("<<ComboboxSelected>>", calculate)

# Other Input Fields
ttk.Label(input_frame, text="Cold Water Pressure Available for Friction (psi):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
cw_pressure_entry = ttk.Entry(input_frame, width=10)
cw_pressure_entry.grid(row=1, column=1, padx=5, pady=2)

ttk.Label(input_frame, text="Hot Water Pressure Available for Friction (psi):").grid(row=2, column=0, padx=5, pady=2, sticky="e")
hw_pressure_entry = ttk.Entry(input_frame, width=10)
hw_pressure_entry.grid(row=2, column=1, padx=5, pady=2)

ttk.Label(input_frame, text="Total Developed Length (ft):").grid(row=3, column=0, padx=5, pady=2, sticky="e")
length_entry = ttk.Entry(input_frame, width=10)
length_entry.grid(row=3, column=1, padx=5, pady=2)

ttk.Label(input_frame, text="Cold Water Max Velocity (ft/s):").grid(row=4, column=0, padx=5, pady=2, sticky="e")
cw_velocity_entry = ttk.Entry(input_frame, width=10)
cw_velocity_entry.grid(row=4, column=1, padx=5, pady=2)

ttk.Label(input_frame, text="Hot Water Max Velocity (ft/s):").grid(row=5, column=0, padx=5, pady=2, sticky="e")
hw_velocity_entry = ttk.Entry(input_frame, width=10)
hw_velocity_entry.grid(row=5, column=1, padx=5, pady=2)

# Friction Rate Labels
cw_friction_rate_label = ttk.Label(root, text="Cold Water Friction Rate: N/A")
cw_friction_rate_label.grid(row=6, column=0, columnspan=2)

cw_friction_rate_psi_label = ttk.Label(root, text="", font=("Helvetica", 10, "italic"))
cw_friction_rate_psi_label.grid(row=7, column=0, columnspan=2)

hw_friction_rate_label = ttk.Label(root, text="Hot Water Friction Rate: N/A")
hw_friction_rate_label.grid(row=8, column=0, columnspan=2)

hw_friction_rate_psi_label = ttk.Label(root, text="", font=("Helvetica", 10, "italic"))
hw_friction_rate_psi_label.grid(row=9, column=0, columnspan=2)

# Output Tables
columns = ("Copper Pipe Size (in)", "Velocity (ft/s)", "Max GPM", "Max Fixture Units", "Fixture Unit Type", "Pressure Drop ft/100ft (psi/100ft)", "Friction Factor", "Reynolds")

# CW Table
ttk.Label(root, text="Cold Water Outputs", font=("Helvetica", 10, "bold")).grid(row=10, column=0, columnspan=3, pady=2)
cw_frame = ttk.Frame(root)
cw_frame.grid(row=11, column=0, columnspan=3)
table_cw = ttk.Treeview(cw_frame, columns=columns, show='headings', height=9)
table_cw.pack(side="left")

# Scrollbar for CW Table
scroll_cw = ttk.Scrollbar(cw_frame, orient="vertical", command=table_cw.yview)
scroll_cw.pack(side="right", fill="y")
table_cw.configure(yscrollcommand=scroll_cw.set)

# HW Table
ttk.Label(root, text="Hot Water Outputs", font=("Helvetica", 10, "bold")).grid(row=12, column=0, columnspan=3, pady=2)
hw_frame = ttk.Frame(root)
hw_frame.grid(row=13, column=0, columnspan=3)
table_hw = ttk.Treeview(hw_frame, columns=columns, show='headings', height=9)
table_hw.pack(side="left")

# Scrollbar for HW Table
scroll_hw = ttk.Scrollbar(hw_frame, orient="vertical", command=table_hw.yview)
scroll_hw.pack(side="right", fill="y")
table_hw.configure(yscrollcommand=scroll_hw.set)

# Author Credit
author_label = ttk.Label(root, text="Developed by Alex Kalmbach", font=("Helvetica", 8, "italic"))
author_label.grid(row=14, column=2, sticky="e", padx=10, pady=5)

# Configure Table Headings
# Configure Table Headings and Column Widths
column_widths = {
    "Copper Pipe Size (in)": 120,
    "Velocity (ft/s)": 100,
    "Max GPM": 80,
    "Max Fixture Units": 220,
    "Fixture Unit Type": 130,
    "Pressure Drop ft/100ft (psi/100ft)": 180,
    "Friction Factor": 100,
    "Reynolds": 100,
}
for col in columns:
    # Set headings
    table_cw.heading(col, text=col)
    table_hw.heading(col, text=col)

    # Set column widths and alignments
    table_cw.column(col, width=column_widths[col], anchor="center")
    table_hw.column(col, width=column_widths[col], anchor="center")


# Bind input fields to trigger the calculation on key release
for widget in [cw_pressure_entry, hw_pressure_entry, length_entry, cw_velocity_entry, hw_velocity_entry]:
    widget.bind("<KeyRelease>", calculate)

# Run the GUI
root.mainloop()
