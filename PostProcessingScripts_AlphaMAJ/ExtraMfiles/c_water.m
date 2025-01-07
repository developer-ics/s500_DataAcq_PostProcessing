function [c_mps] = c_water(T_degrees_C,P_kPa,S_ppt)
% c_water calculates sound speed (in m/s) of seawater given T (°C), P (kPa)
% adapted from from UNESCO (1983): Algorithms for computation of fundamental 
% properties of seawater. UNESCO technical papers in marine science 44:1-55.
% Employs CHEN AND MILLERO 1977, JASA, 62, 1129-1135
% Originally FORTRAN code, adapted by Chad Greene 01JUNE2009
% Credit also to Jan Schulz
%
% OUTPUT: sound speed in m/s
%
% INPUTS: 
% This function allows any or all inputs to be scalar or vectors.  However,
% dimensions of all vector inputs must agree.  
%
% T_degrees_C is temperature in [°C]
% P_kPa is absolute pressure [kPa] 
% S_ppt is salinity in ppt; most often close enough to psu for practical purposes. 
% For freshwater use S_ppt = 0 or leave blank
%
% If you have data from a CTD cast, you might have values for temperature,
% pressure, and salinity in the following format.  (These example values are
% entirely hypothetical):
% T_profile = [22 22 21 19 18];
% P_profile = [101 150 199 240 300];
% S_profile = [35.5 35 34.5 34 34.5]; 
% 
% Or you might have constant values for one or all of the input parameters:
% T_const = 22;
% P_const = 110; 
% S_const = 33;
%
% ANY OF THE INPUTS FOLLOWING WILL WORK: 
% c_water(T_const,P_const,S_const)
% c_water(T_const,P_const)
% c_water(T_const)
% c_water()
% c_water
% c_water(T_profile) 
% c_water(T_profile,P_profile)
% c_water(T_profile,P_profile,S_profile)
% c_water(T_profile,P_profile,S_const)
% c_water(T_profile,P_const,S_profile)
% c_water(T_profile,P_const,S_const)
% c_water(T_const,P_profile,S_profile)
% c_water(T_const,P_const,S_profile)
% c_water(T_const,P_profile,S_const)
% c_water(T_const,P_profile) 
% c_water(T_profile,P_const)
% 
% GRAPHICAL EXAMPLE
% d = 0:5000; % for depth of 0 to 5 kilometers
% p = 101.325+1025*9.81*d/1000; % pressure equivalent in kPa
% t = [20:-10/500:10 10*ones(1,4500)]; % a very simplified thermocline model
% c = c_water(t,p,32);
% plot(c,-d)
% ylabel('depth (m)')
% xlabel('sound speed (m/s)')

if exist('T_degrees_C')==0
    T = 20; % assumes 20 degrees C if undefined
else
    T = T_degrees_C;
end

if exist('P_kPa')==0
    P = 1.01325; % assumes atmospheric pressure if undefined
else
    P = P_kPa/100; % converts kPa to bar
end

if exist('S_ppt')==0
    S = 0; % assumes fresh water if salinity is undefined
else
    S = S_ppt;
end

SR = sqrt (abs(S));
  % S^2 TERM
  D = 1.727E-3 - 7.9836E-6 * P;
  % S^3/2 TERM
  B1 =  7.3637E-5 + 1.7945E-7 * T;
  B0 = -1.922E-2  - 4.42E-5   * T;
  B  = B0 + B1 .* P;
  % S^1 TERM
  A3 = (-3.389E-13    .* T + 6.649E-12)  .* T + 1.100E-10;
  A2 = ((7.988E-12    .* T - 1.6002E-10) .* T + 9.1041E-9) .* T - 3.9064E-7;
  A1 = (((-2.0122E-10 .* T + 1.0507E-8)  .* T - 6.4885E-8) .* T - 1.2580E-5) .* T + 9.4742E-5;
  A0 = (((-3.21E-8    .* T + 2.006E-6)   .* T + 7.164E-5)  .* T - 1.262E-2)  .* T + 1.389;
  A  = ((A3.* P + A2) .*P + A1) .* P + A0;
  % S^0 TERM
  C3 = (-2.3643E-12   .* T + 3.8504E-10) .* T - 9.7729E-9;
  C2 = (((1.0405E-12  .* T - 2.5335E-10) .* T + 2.5974E-8) .* T - 1.7107E-6)  .* T + 3.1260E-5;
  C1 = (((-6.1185E-10 .* T + 1.3621E-7)  .* T - 8.1788E-6) .* T + 6.8982E-4)  .* T + 0.153563;
  C0 = ((((3.1464E-9  .* T - 1.47800E-6) .* T + 3.3420E-4) .* T - 5.80852E-2) .* T + 5.03711) .* T + 1402.388;
  C  = ((C3 .* P + C2) .* P + C1) .* P + C0;
% SOUND SPEED RETURN
  c_mps = C + (A + B .* SR + D .* S) .* S;
end

