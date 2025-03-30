# -*- coding: utf-8 -*-
"""
Two-State Thermodynamic Calculator

This program provides a graphical user interface (GUI) for calculating the thermodynamic properties
of steam at two different states. Each state is defined by specifying any two independent properties
(e.g., pressure and temperature, specific volume and quality, etc). Once the user clicks "Calculate",
the application computes all thermodynamic properties for each state and the changes between them.

Features:
- Input of any two independent thermodynamic properties for two states.
- Output of p, T, u, h, s, v, and x for each state.
- Computation of property changes between states.
- Support for SI and English units with automatic value conversion.

This GUI is built with PyQt5 and uses the pyXSteam module for steam property calculations.

Assignment Requirements Satisfied:
1. Group boxes for specifying State 1 and State 2 properties.
2. Horizontal display of State 1, State 2, and ΔState values.
3. Full unit toggle support with numerical conversions.
"""

#Used ChatGPT to help formulate and organize the code "
 #as well as point out any errors in my code "

# region imports
import sys
from PyQt5 import QtWidgets
from ThermoStatesCalc_TwoStates import Ui__frm_StateCalculator
from ThermoStateCalc_app import thermoState, UC
from pyXSteam.XSteam import XSteam
# endregion


# region class definitions
class main_window(QtWidgets.QWidget, Ui__frm_StateCalculator):
    """
    Main GUI class that handles user interaction, input parsing,
    thermodynamic computation, and display updates.
    """

    def __init__(self):
        """
        Initializes the application window, UI layout, default settings,
        and connects signals to corresponding slots.
        """
        super().__init__()
        self.setupUi(self)
        self.SetupSlotsAndSignals()
        self.steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
        self.currentUnits = 'SI'
        self.setUnits()
        self.show()

    def SetupSlotsAndSignals(self):
        """
        Connects UI widgets (buttons, dropdowns, radio buttons)
        to appropriate handler methods.
        """
        self._rdo_English.clicked.connect(self.setUnits)
        self._rdo_SI.clicked.connect(self.setUnits)
        self._cmb_State1_Property1.currentIndexChanged.connect(self.setUnits)
        self._cmb_State1_Property2.currentIndexChanged.connect(self.setUnits)
        self._cmb_State2_Property1.currentIndexChanged.connect(self.setUnits)
        self._cmb_State2_Property2.currentIndexChanged.connect(self.setUnits)
        self._pb_Calculate.clicked.connect(self.calculateProperties)

    def setUnits(self):
        """
        Sets or converts units between SI and English based on user selection.
        Updates the units labels and optionally converts numeric values.
        """
        SI = self._rdo_SI.isChecked()
        newUnits = 'SI' if SI else 'EN'
        UnitChange = self.currentUnits != newUnits
        self.currentUnits = newUnits

        if SI:
            self.steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
            self.p_Units = "bar"
            self.t_Units = "C"
            self.u_Units = "kJ/kg"
            self.h_Units = "kJ/kg"
            self.s_Units = "kJ/kg*C"
            self.v_Units = "m^3/kg"
        else:
            self.steamTable = XSteam(XSteam.UNIT_SYSTEM_FLS)
            self.p_Units = "psi"
            self.t_Units = "F"
            self.u_Units = "btu/lb"
            self.h_Units = "btu/lb"
            self.s_Units = "btu/lb*F"
            self.v_Units = "ft^3/lb"

        # Update inputs and units for both states
        self.updatePropertyUnits(self._cmb_State1_Property1, self._le_State1_Property1, self._lbl_State1_Property1_Units, UnitChange, SI)
        self.updatePropertyUnits(self._cmb_State1_Property2, self._le_State1_Property2, self._lbl_State1_Property2_Units, UnitChange, SI)
        self.updatePropertyUnits(self._cmb_State2_Property1, self._le_State2_Property1, self._lbl_State2_Property1_Units, UnitChange, SI)
        self.updatePropertyUnits(self._cmb_State2_Property2, self._le_State2_Property2, self._lbl_State2_Property2_Units, UnitChange, SI)

    def updatePropertyUnits(self, combo, lineEdit, label, UnitChange, SI):
        """
        Updates the unit label and optionally converts the value in the input field.

        Parameters:
        combo (QComboBox): The property selector combo box.
        lineEdit (QLineEdit): The field where the property value is entered.
        label (QLabel): The label showing the units.
        UnitChange (bool): Whether the unit system is being changed.
        SI (bool): Whether SI is the selected system.
        """
        prop = combo.currentText()
        try:
            val = float(lineEdit.text())
        except:
            val = 0.0

        if 'Pressure' in prop:
            label.setText(self.p_Units)
            if UnitChange:
                val = val * UC.psi_to_bar if SI else val * UC.bar_to_psi
        elif 'Temperature' in prop:
            label.setText(self.t_Units)
            if UnitChange:
                val = UC.F_to_C(val) if SI else UC.C_to_F(val)
        elif 'Energy' in prop:
            label.setText(self.u_Units)
            if UnitChange:
                val = val * UC.btuperlb_to_kJperkg if SI else val * UC.kJperkg_to_btuperlb
        elif 'Enthalpy' in prop:
            label.setText(self.h_Units)
            if UnitChange:
                val = val * UC.btuperlb_to_kJperkg if SI else val * UC.kJperkg_to_btuperlb
        elif 'Entropy' in prop:
            label.setText(self.s_Units)
            if UnitChange:
                val = val * UC.btuperlbF_to_kJperkgC if SI else val * UC.kJperkgc_to_btuperlbF
        elif 'Volume' in prop:
            label.setText(self.v_Units)
            if UnitChange:
                val = val * UC.ft3perlb_to_m3perkg if SI else val * UC.m3perkg_to_ft3perlb
        elif 'Quality' in prop:
            label.setText("")  # Quality is unitless

        lineEdit.setText("{:0.3f}".format(val))

    def calculateProperties(self):
        """
        Reads the two specified properties for each state, computes all other thermodynamic
        properties using pyXSteam, and updates the display with results and property changes.
        """
        try:
            # State 1 inputs
            SP1 = [self._cmb_State1_Property1.currentText()[-2:-1].lower(),
                   self._cmb_State1_Property2.currentText()[-2:-1].lower()]

            if SP1[0] == SP1[1]:
                self._lbl_Warning.setText("Warning: You cannot specify the same property twice for State 1.")
                return

            f1 = [float(self._le_State1_Property1.text()), float(self._le_State1_Property2.text())]

            # State 2 inputs
            SP2 = [self._cmb_State2_Property1.currentText()[-2:-1].lower(),
                   self._cmb_State2_Property2.currentText()[-2:-1].lower()]

            if SP2[0] == SP2[1]:
                self._lbl_Warning.setText("Warning: You cannot specify the same property twice for State 2.")
                return

            f2 = [float(self._le_State2_Property1.text()), float(self._le_State2_Property2.text())]
            SI = self._rdo_SI.isChecked()

            # Set states
            self.state1 = thermoState()
            self.state1.setState(SP1[0], SP1[1], f1[0], f1[1], SI)

            self.state2 = thermoState()
            self.state2.setState(SP2[0], SP2[1], f2[0], f2[1], SI)

            # Display results
            self._lbl_State1_Properties.setText(self.makeLabel(self.state1))
            self._lbl_State2_Properties.setText(self.makeLabel(self.state2))
            self._lbl_StateChange_Properties.setText(self.makeDeltaLabel(self.state1, self.state2))
            self._lbl_Warning.setText("")

        except ValueError:
            self._lbl_Warning.setText("Error: Please enter valid numerical values.")
        except Exception as e:
            self._lbl_Warning.setText(f"Unexpected error: {str(e)}")

    def makeLabel(self, state):
        """
        Formats a state's thermodynamic properties for display.

        Parameters:
        state (thermoState): The state object containing thermodynamic properties.

        Returns:
        str: HTML-formatted string for display.
        """
        region_colors = {
            "two-phase": "blue",
            "super-heated vapor": "green",
            "sub-cooled liquid": "red",
            "saturated": "black"
        }
        color = region_colors.get(state.region, "black")

        stProps = f"<span style='color:{color};'><b>Region = {state.region}</b></span>"
        stProps += f"<br>Pressure = {state.p:.3f} {self.p_Units}"
        stProps += f"<br>Temperature = {state.t:.3f} {self.t_Units}"
        stProps += f"<br>Internal Energy = {state.u:.3f} {self.u_Units}"
        stProps += f"<br>Enthalpy = {state.h:.3f} {self.h_Units}"
        stProps += f"<br>Entropy = {state.s:.3f} {self.s_Units}"
        stProps += f"<br>Specific Volume = {state.v:.3f} {self.v_Units}"
        stProps += f"<br>Quality = {state.x:.3f}"
        return stProps

    def makeDeltaLabel(self, state1, state2):
        """
        Computes and formats the property changes between two states.

        Parameters:
        state1 (thermoState): Initial state.
        state2 (thermoState): Final state.

        Returns:
        str: Formatted multi-line string showing Δ values.
        """
        stDelta = "Property change:"
        stDelta += "\nP2-P1 = {:0.3f} {:}".format(state2.p - state1.p, self.p_Units)
        stDelta += "\nT2-T1 = {:0.3f} {:}".format(state2.t - state1.t, self.t_Units)
        stDelta += "\nu2-u1 = {:0.3f} {:}".format(state2.u - state1.u, self.u_Units)
        stDelta += "\nh2-h1 = {:0.3f} {:}".format(state2.h - state1.h, self.h_Units)
        stDelta += "\ns2-s1 = {:0.3f} {:}".format(state2.s - state1.s, self.s_Units)
        stDelta += "\nv2-v1 = {:0.3f} {:}".format(state2.v - state1.v, self.v_Units)
        stDelta += "\nx2-x1 = {:0.3f}".format(state2.x - state1.x)
        return stDelta


# endregion

# region function definitions
def main():
    """
    Launches the application if run as the main module.
    Ensures a QApplication exists and instantiates the main window.
    """
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()
    sys.exit(app.exec_())
# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion
