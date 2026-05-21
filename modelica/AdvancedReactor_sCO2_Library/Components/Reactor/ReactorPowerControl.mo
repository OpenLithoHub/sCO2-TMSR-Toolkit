within AdvancedReactor_sCO2_Library.Components.Reactor;
model ReactorPowerControl
  "PI controller commanding reactor power fraction to track outlet T setpoint"

  parameter Real K_p     = 0.5     "Proportional gain";
  parameter Real T_i     = 30      "Integral time (s)";
  parameter Real out_max = 1.0     "Power fraction upper limit";
  parameter Real out_min = 0.05    "Power fraction lower limit";

  Modelica.Blocks.Interfaces.RealInput  T_setpoint;
  Modelica.Blocks.Interfaces.RealInput  T_measured;
  Modelica.Blocks.Interfaces.RealOutput power_fraction;

  Modelica.Blocks.Continuous.LimPID pid(
    controllerType = Modelica.Blocks.Types.SimpleController.PI,
    k = K_p,
    Ti = T_i,
    yMax = out_max,
    yMin = out_min);
equation
  connect(T_setpoint,  pid.u_s);
  connect(T_measured,  pid.u_m);
  connect(pid.y,       power_fraction);
end ReactorPowerControl;
