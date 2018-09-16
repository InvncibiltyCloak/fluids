# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, 2017 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from __future__ import division
from math import cos, sin, tan, atan, pi, radians, log10
import numpy as np
from scipy.constants import inch
from scipy.interpolate import splev, bisplev
from fluids.friction import friction_factor
from fluids.core import horner

__all__ = ['contraction_sharp', 'contraction_round',
'contraction_conical', 'contraction_beveled',  'diffuser_sharp',
'diffuser_conical', 'diffuser_conical_staged', 'diffuser_curved',
'diffuser_pipe_reducer',
'entrance_sharp', 'entrance_distance', 'entrance_angled',
'entrance_rounded', 'entrance_beveled', 'entrance_beveled_orifice', 
'exit_normal', 'bend_rounded', 'bend_rounded_Miller', 'bend_miter', 
'bend_miter_Miller', 'helix', 'spiral','Darby3K', 'Hooper2K', 'Kv_to_Cv', 'Cv_to_Kv',
'Kv_to_K', 'K_to_Kv', 'Cv_to_K', 'K_to_Cv', 'change_K_basis', 'Darby', 
'Hooper', 'K_gate_valve_Crane', 'K_angle_valve_Crane', 'K_globe_valve_Crane',
'K_swing_check_valve_Crane', 'K_lift_check_valve_Crane',
'K_tilting_disk_check_valve_Crane', 'K_globe_stop_check_valve_Crane',
'K_angle_stop_check_valve_Crane', 'K_ball_valve_Crane',
'K_diaphragm_valve_Crane', 'K_foot_valve_Crane', 'K_butterfly_valve_Crane',
'K_plug_valve_Crane', 'K_branch_converging_Crane', 'K_run_converging_Crane',
'K_branch_diverging_Crane', 'K_run_diverging_Crane', 'v_lift_valve_Crane']


def change_K_basis(K1, D1, D2):
    r'''Converts a loss coefficient `K1` from the basis of one diameter `D1`
    to another diameter, `D2`. This is necessary when dealing with pipelines
    of changing diameter.
    
    .. math::
        K_2 = K_1\frac{D_2^4}{D_1^4} = K_1 \frac{A_2^2}{A_1^2}

    Parameters
    ----------
    K1 : float
        Loss coefficient with respect to diameter `D`, [-]
    D1 : float
        Diameter of pipe for which `K1` has been calculated, [m]
    D2 : float
        Diameter of pipe for which `K2` will be calculated, [m]

    Returns
    -------
    K2 : float
        Loss coefficient with respect to the second diameter, [-]

    Notes
    -----
    This expression is shown in [1]_ and can easily be derived:
        
    .. math::
        \frac{\rho V_{1}^{2}}{2} \cdot K_{1} = \frac{\rho V_{2}^{2} }{2}
        \cdot K_{2} 
        
    Substitute velocities for flow rate divided by area:
        
    .. math::
        \frac{8 K_{1} Q^{2} \rho}{\pi^{2} D_{1}^{4}} = \frac{8 K_{2} Q^{2} 
        \rho}{\pi^{2} D_{2}^{4}}

    From here, simplification and rearrangement is all that is required.
    
    Examples
    --------
    >>> change_K_basis(K1=32.68875692997804, D1=.01, D2=.02)
    523.0201108796487

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    return K1*(D2/D1)**4


### Entrances

def entrance_sharp():
    r'''Returns loss coefficient for a sharp entrance to a pipe
    as shown in [1]_.

    .. math::
        K = 0.57

    .. figure:: fittings/flush_mounted_sharp_edged_entrance.png
       :scale: 30 %
       :alt: flush mounted sharp edged entrance; after [1]_

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Other values used have been 0.5.

    Examples
    --------
    >>> entrance_sharp()
    0.57

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    return 0.57


def entrance_distance(Di, t):
    r'''Returns loss coefficient for a sharp entrance to a pipe at a distance
    from the wall of a reservoir, as shown in [1]_.

    .. math::
        K = 1.12 - 22\frac{t}{d} + 216\left(\frac{t}{d}\right)^2 +
        80\left(\frac{t}{d}\right)^3

    .. figure:: fittings/sharp_edged_entrace_extended_mount.png
       :scale: 30 %
       :alt: sharp edged entrace, extended mount; after [1]_

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    t : float
        Thickness of pipe wall, [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Recommended for cases where the length of the inlet pipe extending into a 
    tank divided by the inner diameter of the pipe is larger than 0.5.
    If the pipe is 10 cm in diameter, the pipe should extend into the tank 
    at least 5 cm. This type of inlet is also known as a Borda's mouthpiece.
    It is not of practical interest according to [1]_.
    
    If the pipe wall thickness to diameter ratio `t`/`Di` is larger than 0.05,
    it is rounded to 0.05; the effect levels off at that ratio and K=0.57.

    Examples
    --------
    >>> entrance_distance(Di=0.1, t=0.0005)
    1.0154100000000001

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    ratio = t/Di
    if ratio > 0.05:
        ratio = 0.05
    return 1.12 - 22.*ratio + 216.*ratio**2 + 80*ratio**3


def entrance_angled(angle):
    r'''Returns loss coefficient for a sharp, angled entrance to a pipe
    flush with the wall of a reservoir, as shown in [1]_.

    .. math::
        K = 0.57 + 0.30\cos(\theta) + 0.20\cos(\theta)^2

    .. figure:: fittings/entrance_mounted_at_an_angle.png
       :scale: 30 %
       :alt: entrace mounted at an angle; after [1]_

    Parameters
    ----------
    angle : float
        Angle of inclination (90=straight, 0=parallel to pipe wall) [degrees]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Not reliable for angles under 20 degrees.
    Loss coefficient is the same for an upward or downward angled inlet.

    Examples
    --------
    >>> entrance_angled(30)
    0.9798076211353316

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    angle = angle/(180/pi)
    return 0.57 + 0.30*cos(angle) + 0.20*cos(angle)**2


def entrance_rounded(Di, rc):
    r'''Returns loss coefficient for a rounded entrance to a pipe
    flush with the wall of a reservoir, as shown in [1]_.

    .. math::
        K = 0.0696\left(1 - 0.569\frac{r}{d}\right)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622\left(1 - 0.30\sqrt{\frac{r}{d}}
        - 0.70\frac{r}{d}\right)^4
        
    .. figure:: fittings/flush_mounted_rounded_entrance.png
       :scale: 30 %
       :alt: rounded entrace mounted straight and flush; after [1]_

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    rc : float
        Radius of curvature of the entrance, [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    For generously rounded entrance (rc/Di >= 1), the loss coefficient converges
    to 0.03.

    Examples
    --------
    >>> entrance_rounded(Di=0.1, rc=0.0235)
    0.09839534618360923

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    if rc/Di > 1:
        return 0.03
    lbd = 1. + 0.622*(1. - 0.30*(rc/Di)**0.5 - 0.70*(rc/Di))**4
    return 0.0696*(1. - 0.569*rc/Di)*lbd**2 + (lbd - 1.)**2


def entrance_beveled(Di, l, angle):
    r'''Returns loss coefficient for a beveled or chamfered entrance to a pipe
    flush with the wall of a reservoir, as shown in [1]_.

    .. math::
        K = 0.0696\left(1 - C_b\frac{l}{d}\right)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622\left[1-1.5C_b\left(\frac{l}{d}
        \right)^{\frac{1-(l/d)^{1/4}}{2}}\right]

    .. math::
        C_b = \left(1 - \frac{\theta}{90}\right)\left(\frac{\theta}{90}
        \right)^{\frac{1}{1+l/d}}

    .. figure:: fittings/flush_mounted_beveled_entrance.png
       :scale: 30 %
       :alt: Beveled entrace mounted straight; after [1]_

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    l : float
        Length of bevel measured parallel to the pipe length, [m]
    angle : float
        Angle of bevel with respect to the pipe length, [degrees]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    A cheap way of getting a lower pressure drop.
    Little credible data is available.

    Examples
    --------
    >>> entrance_beveled(Di=0.1, l=0.003, angle=45)
    0.45086864221916984

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    Cb = (1-angle/90.)*(angle/90.)**(1./(1 + l/Di ))
    lbd = 1 + 0.622*(1 - 1.5*Cb*(l/Di)**((1 - (l/Di)**0.25)/2.))
    return 0.0696*(1 - Cb*l/Di)*lbd**2 + (lbd - 1.)**2


def entrance_beveled_orifice(Di, do, l, angle):
    r'''Returns loss coefficient for a beveled or chamfered orifice entrance to 
    a pipe flush with the wall of a reservoir, as shown in [1]_.

    .. math::
        K = 0.0696\left(1 - C_b\frac{l}{d_o}\right)\lambda^2 + \left(\lambda
        -\left(\frac{d_o}{D_i}\right)^2\right)^2
        
    .. math::
        \lambda = 1 + 0.622\left[1-C_b\left(\frac{l}{d_o}\right)^{\frac{1-
        (l/d_o)^{0.25}}{2}}\right]
    
    .. math::
        C_b = \left(1 - \frac{\Psi}{90}\right)\left(\frac{\Psi}{90}
        \right)^{\frac{1}{1+l/d_o}}
        
    .. figure:: fittings/flush_mounted_beveled_orifice_entrance.png
       :scale: 30 %
       :alt: Beveled orifice entrace mounted straight; after [1]_

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    do : float
        Inside diameter of orifice, [m]
    l : float
        Length of bevel measured parallel to the pipe length, [m]
    angle : float
        Angle of bevel with respect to the pipe length, [degrees]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Examples
    --------
    >>> entrance_beveled_orifice(Di=0.1, do=.07, l=0.003, angle=45)
    1.2987552913818574

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    Cb = (1-angle/90.)*(angle/90.)**(1./(1 + l/do ))
    lbd = 1 + 0.622*(1 - Cb*(l/do)**((1 - (l/do)**0.25)/2.))
    return 0.0696*(1 - Cb*l/do)*lbd**2 + (lbd - (do/Di)**2)**2


### Exits

def exit_normal():
    r'''Returns loss coefficient for any exit to a pipe
    as shown in [1]_ and in other sources.

    .. math::
        K = 1

    .. figure:: fittings/flush_mounted_exit.png
       :scale: 28 %
       :alt: Exit from a flush mounted wall; after [1]_

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    It has been found on occasion that K = 2.0 for laminar flow, and ranges
    from about 1.04 to 1.10 for turbulent flow.

    Examples
    --------
    >>> exit_normal()
    1.0

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    return 1.0


### Bends


tck_bend_rounded_Miller = [np.array([0.500967, 0.500967, 0.500967, 0.500967, 0.5572659504420276, 0.6220535279438968, 0.6876695918008857, 
     0.8109956990835443, 0.8966138996017785, 1.0418136796591293, 1.2129808986390955, 1.4328097893561944, 
     2.684491977649823, 3.496050493509287, 4.245254058334557, 10.0581, 10.0581, 10.0581, 10.0581]), 
   np.array([10.0022, 10.0022, 10.0022, 10.0022, 26.661576730080427, 35.71142422728946, 46.22896414495794, 54.476944091380965, 
     67.28681897720492, 79.96560467244989, 88.89484575805731, 104.37345376723293, 113.75217318286595, 121.36638011164008, 
     139.53481668808192, 180.502, 180.502, 180.502, 180.502]), 
   np.array([0.02844925354339322, 0.032368056788003474, 0.06341726367587057, 0.18372991235687228, 0.27828335685928296, 
     0.4184452895626468, 0.5844709012848479, 0.8517327028006999, 1.0883889837806633, 1.003595822015052, 1.2959349743905006,
     1.3631701864169843, 3.2579960738248563, 8.188259745620396, 6.370167194425542, 0.026614405579949103, 0.03578575879432178,
     0.05399131725104529, 0.17357295746658216, 0.2597698136964017, 0.384398460262134, 0.5537955210508835, 0.842964805734998, 
     1.1076060802420074, 1.0500502914944205, 1.2160489773171173, 1.2940140217639442, 2.5150913200614293, 5.987790923112488,
     4.791049223949247, 0.026866783841898684, 0.03061409809632371, 0.054698306220358, 0.14037162784411245, 0.23981090432386729, 
     0.31617091309760137, 0.47435842573782666, 0.7484605121106159, 0.9223888516911868, 1.0345139221619066, 1.0709769967277933, 
     1.1489283659291687, 1.4249255928619116, 2.6908421883082823, 2.3898833324508804, 0.019707980719056793, 0.03350958504709355,
     0.0457699204936841, 0.1180773988295937, 0.18163838540491214, 0.2955424583244998, 0.3178086095370295, 0.54907384767895, 
     0.7497276995283433, 0.8353766950608585, 0.8907203653185313, 0.941376749552297, 0.8755423259796333, 0.8987849646797164, 
     0.9905785504810203, 0.018632197087313764, 0.0275473376021632, 0.046686663726990756, 0.09334625398868963, 
     0.15009471210360348, 0.21438462374865175, 0.310541469358518, 0.27652184608845864, 0.4703245212932829, 
     0.5612926929410017, 0.6344189573543495, 0.6897616299237337, 0.8553230255854581, 0.8050040042565408,
     0.7800498994134173, 0.017040716941189974, 0.027163747207842776, 0.04233976165781228, 0.08546809847236579, 
     0.11872359104267481, 0.1748602349243538, 0.248787221592314, 0.3166892465009758, 0.2894990945943436, 
     0.35635089905047324, 0.3942719381041552, 0.4019846022857163, 0.4910888827789205, 0.4424331343990761, 
     0.5367477778555589, 0.017232689797500957, 0.024595005629126976, 0.04235982677436609, 0.0748705682747817,
     0.11096283696103083, 0.13900984487771062, 0.18773056195495877, 0.2400721832034611, 0.28581377924973544, 
     0.282839816159864, 0.2907117502580411, 0.3035848810896592, 0.31268019467513564, 0.3365050687225188, 0.2836774098946595, 
     0.017462451480157917, 0.02373981127475937, 0.04248526591300313, 0.07305722078054935, 0.09424065630357203, 
     0.13682400355164548, 0.15020534827616405, 0.2100221959547714, 0.23136495625582817, 0.24417894312621574,
     0.2505645472554214, 0.24143469557592281, 0.24722191256497117, 0.2195110087547775, 0.29557609063213136,
     0.017605444779345832, 0.026265210174737128, 0.0445497171166642, 0.07254637551095446, 0.08779690828578819,
     0.11992614224260065, 0.14501268843599757, 0.17386066713179812, 0.21657094190224363, 0.21594544490951023, 0.22661999176624517,
     0.23759356544596819, 0.23887614636323537, 0.25802515101229484, 0.20566480389514516, 0.01928450591486404, 0.03264367752872495, 
     0.05391006363370407, 0.07430728218140033, 0.08818045730326454, 0.09978389535000864, 0.12544634357734885, 0.13365159719049172, 
     0.15802979203343911, 0.17543365869590444, 0.17531453508236272, 0.1706085325985479, 0.15983319357859727, 0.16872558079206196,
     0.19799750352823683, 0.020835891827102552, 0.047105767455498285, 0.05307639179638059, 0.07839236342751181, 0.09519829368423402,
     0.10189528661430994, 0.12852821694010982, 0.13195311029179943, 0.1594822363328695, 0.15660304273110143, 0.15934161651984413,
     0.17702957118830723, 0.1892675345030034, 0.19710951153945122, 0.1897835097361326, 0.031571285288316195, 0.04810266172763896,
     0.05660304311192384, 0.09317293919692342, 0.08967028392412497, 0.12028974875677166, 0.1182836264474129, 0.13845925262729528, 
     0.15739100571169004, 0.17649056196464383, 0.20171423738165223, 0.20947832805305883, 0.22837004534830094, 0.23661874048689152, 
     0.24537433391842686, 0.042992073811512765, 0.045958026954244176, 0.08988351069774198, 0.08320361205549355, 0.1253881915447805, 
     0.12765039447605908, 0.1632907944306065, 0.17922551055575348, 0.20436939408609628, 0.23133806857897737, 0.22837190631962206,
     0.2611718034649056, 0.30462224139228183, 0.3277471634644065, 0.3595577208662931, 0.042671097083349346, 0.06027193387363409,
     0.07182684474072856, 0.12072547771177115, 0.1331787059163636, 0.16137414417679433, 0.1780034002291815, 0.19820571860540606, 
     0.2294059556234193, 0.23221403415772682, 0.2697708431035234, 0.2813760107306456, 0.28992333749905363, 0.3650401400682786, 
     0.8993207970132076, 0.045660964207664585, 0.06299599466264151, 0.09193684371316964, 0.12747145786167088, 0.14606550538249963, 
     0.172664884028299, 0.19152378303841075, 0.2212007207927944, 0.23752800077573005, 0.26289800433018995, 0.2772198641539113,
     0.2995308585350757, 0.3549459028594012, 0.8032461437896778, 3.330618601208751]), 
   3, 3]
bend_rounded_Miller_Kb = lambda rc_D, angle : bisplev(rc_D, angle, tck_bend_rounded_Miller)

tck_bend_rounded_Miller_C_Re = [np.array([4.0, 4.0, 4.0, 4.0, 8.0, 8.0, 8.0, 8.0]), 
                                np.array([1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]), 
                                np.array([2.177340320782947, 2.185952396281732, 2.185952396281732, 2.1775876405173977,
  0.6513348082098823, 0.7944713057222101, 0.7944713057222103, 1.0526247737400114,
  0.6030278030721317, 1.3741240162063968, 1.3741240162063992, 0.7693594604301893, 
  -2.1663631289607883, -1.9474318981548622, -1.9474318981548622, 0.4196741237602154]), 
   3, 3]
                                
bend_rounded_Miller_C_Re = lambda Re, rc_D : bisplev(log10(Re), rc_D, tck_bend_rounded_Miller_C_Re)
bend_rounded_Miller_C_Re_limit_1 = [2428087.757821312, -13637184.203693766, 28450331.830760233, -25496945.91463643, 8471761.477755375]


tck_bend_rounded_Miller_C_o_0_1 = [np.array([9.975803953769495e-06, 9.975803953769495e-06, 9.975803953769495e-06,
        9.975803953769495e-06, 0.5259485989276764, 1.3157845547408782, 3.220104449183945, 6.133677908951886,
        30.260656153593906, 30.260656153593906, 30.260656153593906, 30.260656153593906]),
np.array([0.6179524338907976, 0.6000479624108129, 0.49299050530751654, 0.4820011733402483, 0.5584830305084972,
        0.7496716557444135, 0.8977538553873484, 0.9987218804089956, 0.0, 0.0, 0.0, 0.0]),
3]
tck_bend_rounded_Miller_C_o_0_15 = [np.array([0.0025931401409935687, 0.0025931401409935687, 0.0025931401409935687,
        0.0025931401409935687, 0.26429667728434275, 0.5188174292838083, 1.469212480387932, 4.269571348168375,
        13.268280073552294, 26.28093462852014, 26.28093462852014, 26.28093462852014, 26.28093462852014]),
np.array([0.8691924906711972, 0.8355177386350426, 0.7617588987656675, 0.5853012015918869, 0.5978128647571033,
        0.7366100253604377, 0.8229203841913866, 0.9484887080989913, 1.0003643259424702, 0.0, 0.0, 0.0, 0.0]),
3]
tck_bend_rounded_Miller_C_o_0_2 = [np.array([-0.001273275512351991, -0.001273275512351991, -0.001273275512351991, -
        0.001273275512351991, 0.36379835796750504, 0.7789151587713531, 1.7319487323386349, 3.559883175039053,
        22.10600230228466, 22.10600230228466, 22.10600230228466, 22.10600230228466]),
np.array([1.2055892891232, 1.1810797953131011, 0.8556056552110055, 0.6595884323229468, 0.6669634037761268,
        0.8636791463334055, 0.8855712717206472, 0.9992625616471772, 0.0, 0.0, 0.0, 0.0]),
3]
tck_bend_rounded_Miller_C_o_0_25 = [np.array([0.0025931401409935687, 0.0025931401409935687, 0.0025931401409935687,
        0.0025931401409935687, 0.2765978180291006, 0.5010875816968301, 0.6395222359284018, 0.661563946104784,
        0.6887462820881093, 0.7312909084975013, 0.7605490601821624, 0.8078652661481783, 0.8553090397903271,
        1.024376958429362, 1.4748577103270428, 2.052843716337269, 3.9670225184835175, 6.951737782758053,
        16.770001745987884, 16.770001745987884, 16.770001745987884, 16.770001745987884]),
np.array([2.7181584441006414, 2.6722855229796196, 2.510271857479865, 2.162580617260359, 1.8234805515473758,
        1.5274137403431902, 1.3876379087140025, 1.2712745614209848, 1.1478416325256429, 1.015542018903243,
        0.8445749706812837, 0.7368799268423506, 0.7061205857035833, 0.7381928947255646, 0.7960778489514514,
        0.878729192230999, 0.9281388590439098, 0.9825611959699471, 0.0, 0.0, 0.0, 0.0]),
3]
tck_bend_rounded_Miller_C_o_1_0 = [np.array([0.0025931401409935687, 0.0025931401409935687, 0.0025931401409935687,
        0.0025931401409935687, 0.4940382602529053, 0.7383107558560895, 0.8929948619544391, 0.9910262538499016,
        1.1035407055233972, 1.2685727302009009, 2.190931635360523, 3.718073594472333, 6.026458907878363,
        13.268280073552294, 13.268280073552294, 13.268280073552294, 13.268280073552294]),
np.array([2.713127433391318, 2.6799201583608965, 2.4446034702691906, 2.0505313661892837, 1.7853408404592677,
        1.5802763594858027, 1.395503315683405, 1.0504150726350026, 0.9294800209596744, 0.8937523212160566,
        0.9339124388590752, 0.9769117997985829, 0.9948478073955791, 0.0, 0.0, 0.0, 0.0]),
3]

tck_bend_rounded_Miller_C_os = [tck_bend_rounded_Miller_C_o_0_1, tck_bend_rounded_Miller_C_o_0_15, 
                                tck_bend_rounded_Miller_C_o_0_2, tck_bend_rounded_Miller_C_o_0_25,
                                tck_bend_rounded_Miller_C_o_1_0]
bend_rounded_Miller_C_o_Kbs = [.1, .15, .2, .25, 1]
bend_rounded_Miller_C_o_limits = [30.260656153593906, 26.28093462852014, 22.10600230228466, 16.770001745987884, 13.268280073552294]
bend_rounded_Miller_C_o_limit_0_01 = [0.6169055099514943, 0.8663244713199465, 1.2029584898712695, 2.7143438886138744, 2.7115417734646114]


def Miller_bend_roughness_correction(Re, Di, roughness):
    # Section 9.2.4 - Roughness correction
    # Re limited to under 1E6 in friction factor falculations
    # Use a cached smooth fd value if Re too high
    Re_fd_min = min(1E6, Re)
    if Re_fd_min < 1E6:
        fd_smoth = friction_factor(Re=Re_fd_min, eD=0.0)
    else:
        fd_smoth = 0.011645040997991626
    fd_rough = friction_factor(Re=Re_fd_min, eD=roughness/Di)
    C_roughness = fd_rough/fd_smoth
    return C_roughness


def Miller_bend_unimpeded_correction(Kb, Di, L_unimpeded):
    '''Limitations as follows:
    * Ratio not over 30
    * If ratio under 0.01, tabulated values are used near the limits 
      (discontinuity in graph anyway)
    * If ratio for a tried curve larger than max value, max value is used
      instead of calculating it
    * Kb limited to between 0.1 and 1.0
    * When between two Kb curves, interpolate linearly after evaluating both
      splines appropriately
    '''
    if Kb < 0.1:
        Kb_C_o = 0.1
    elif Kb > 1:
        Kb_C_o = 1.0
    else:
        Kb_C_o = Kb

    L_unimpeded_ratio = L_unimpeded/Di
    if L_unimpeded_ratio > 30:
        L_unimpeded_ratio = 30.0
        
    for i in range(len(bend_rounded_Miller_C_o_Kbs)):        
        Kb_low, Kb_high = bend_rounded_Miller_C_o_Kbs[i], bend_rounded_Miller_C_o_Kbs[i+1]
        if Kb_low <= Kb_C_o <= Kb_high:
            if L_unimpeded_ratio >= bend_rounded_Miller_C_o_limits[i]:
                Co_low = 1.0
            elif L_unimpeded_ratio <= 0.01:
                Co_low = bend_rounded_Miller_C_o_limit_0_01[i]
            else:
                Co_low = splev(L_unimpeded_ratio, tck_bend_rounded_Miller_C_os[i])
            if L_unimpeded_ratio >= bend_rounded_Miller_C_o_limits[i+1]:
                Co_high = 1.0
            elif L_unimpeded_ratio <= 0.01:
                Co_high = bend_rounded_Miller_C_o_limit_0_01[i+1]
            else:
                Co_high = splev(L_unimpeded_ratio, tck_bend_rounded_Miller_C_os[i+1])
#            print(Kb_C_o, [Kb_low, Kb_high], [Co_low, Co_high])
            C_o = Co_low + (Kb_C_o - Kb_low)*(Co_high - Co_low)/(Kb_high - Kb_low)
            return C_o


def bend_rounded_Miller(Di, angle, Re, rc=None, bend_diameters=None, 
                        roughness=0, L_unimpeded=None):
    r'''Calculates the loss coefficient for a rounded pipe bend according to 
    Miller [1]_. This is a sophisticated model which uses corrections for
    pipe roughness, the length of the pipe downstream before another 
    interruption, and a correction for Reynolds number. It interpolates several
    times using several corrections graphs in [1]_.
    
    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    angle : float
        Angle of bend, [degrees]
    Re : float
        Reynolds number of the pipe (no specification if inlet or outlet
        properties should be used), [m]
    rc : float, optional
        Radius of curvature of the entrance, [m]
    bend_diameters : float, optional
        Number of diameters of pipe making up the bend radius  (used if rc not 
        provided; defaults to 5), [-]
    roughness : float, optional
        Roughness of bend wall, [m]   
    L_unimpeded : float, optional
        The length of unimpeded pipe without any fittings, instrumentation,
        or flow disturbances downstream (assumed 20 diameters if not 
        specified), [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    When inputting bend diameters, note that manufacturers often specify
    this as a multiplier of nominal diameter, which is different than actual
    diameter. Those require that rc be specified.
    
    `rc` is limited to 0.5 or above; which represents a sharp, square, inner 
    edge - and an outer bend radius of 1.0. Losses are at a minimum when this
    value is large.
    
    This was developed for bend angles between 10 and 180 degrees; and r/D
    ratios between 0.5 and 10. Both smooth and rough data was used in its 
    development from several sources.
    
    Note the loss coefficient includes the surface friction of the pipe as if
    it was straight.
   
    Examples
    --------
    >>> bend_rounded_Miller(Di=.6, bend_diameters=2, angle=90,  Re=2e6,
    ... roughness=2E-5, L_unimpeded=30*.6)
    0.152618207051459
    
    References
    ----------
    .. [1] Miller, Donald S. Internal Flow Systems: Design and Performance
       Prediction. Gulf Publishing Company, 1990.
    '''
    if not rc:
        if bend_diameters is None:
            bend_diameters = 5
        rc = Di*bend_diameters
    
    radius_ratio = rc/Di
    
    if L_unimpeded is None:
        # Assumption - smooth outlet
        L_unimpeded = 20*Di
    
    # Graph is defined for angles 10 to 180 degrees, ratios 0.5 to 10
    if radius_ratio < 0.5:
        radius_ratio = 0.5
    if radius_ratio > 10.0:
        radius_ratio = 10.0
    if angle < 10.0:
        angle = 10.0
    
    # Curve fit in terms of degrees
    # Caching could work here - angle, radius ratio does not change often
    Kb = bend_rounded_Miller_Kb(radius_ratio, angle) 
    
    C_roughness = Miller_bend_roughness_correction(Re=Re, Di=Di, 
                                                   roughness=roughness)

    '''Section 9.2.2 - Reynolds Number Correction
    Allow some extrapolation up to 1E8 (1E7 max in graph but the trend looks good)
    '''
    Re_C_Re = min(max(Re, 1E4), 1E8)
    if radius_ratio >= 2.0:
        if Re_C_Re == 1E8:
            C_Re = 0.4196741237602154 # bend_rounded_Miller_C_Re(1e8, 2.0)
        elif Re_C_Re == 1E4:
            C_Re = 2.1775876405173977 # bend_rounded_Miller_C_Re(1e4, 2.0)
        else:
            C_Re = bend_rounded_Miller_C_Re(Re_C_Re, 2.0)
    elif radius_ratio <= 1.0:
        # newton(lambda x: bend_rounded_Miller_C_Re(x, 1.0)-1, 2e5) to get the boundary value
        C_Re_1 = bend_rounded_Miller_C_Re(Re_C_Re, 1.0) if Re_C_Re < 207956.58904584477 else 1.0
        if radius_ratio > 0.7 or Kb < 0.4:
            C_Re = C_Re_1
        else:
            C_Re = Kb/(Kb - 0.2*C_Re_1 + 0.2)
            if C_Re > 2.2 or C_Re < 0:
                C_Re = 2.2
    else:
        # regardless of ratio - 1
        if Re_C_Re > 1048884.4656835075:
            C_Re = 1.0
        elif Re_C_Re > horner(bend_rounded_Miller_C_Re_limit_1, radius_ratio):
            C_Re = 1.0
#            ps = np.linspace(1, 2)
#            qs = [newton(lambda x: bend_rounded_Miller_C_Re(x, i)-1, 2e5) for i in ps]
#            np.polyfit(ps, qs, 4).tolist()
            # Line of C_Re=1 as a function of r_d between 0 and 1
        else:
            C_Re = bend_rounded_Miller_C_Re(Re_C_Re, radius_ratio)
    C_o =  Miller_bend_unimpeded_correction(Kb=Kb, Di=Di, L_unimpeded=L_unimpeded)
    
#    print('Kb=%g, C Re=%g, C rough =%g, Co=%g' %(Kb, C_Re, C_roughness, C_o))
    return Kb*C_Re*C_roughness*C_o


bend_miter_Miller_coeffs = [-12.050299402650126, -4.472433689233185, 50.51478860493546, 18.246302079077196, 
                            -84.61426660754049, -28.9340865412371, 71.07345367553872, 21.354010992349565, 
                            -30.239604839338, -5.855129345095336, 5.465131779316523, -1.0881363712712555, 
                            -0.3635431075401224, 0.5120065303391261, 0.46818214491579246, 0.9789177645343993,
                            0.5080285124448385]

def bend_miter_Miller(Di, angle, Re, roughness=0, L_unimpeded=None):
    r'''Calculates the loss coefficient for a single mitre bend according to 
    Miller [1]_. This is a sophisticated model which uses corrections for
    pipe roughness, the length of the pipe downstream before another 
    interruption, and a correction for Reynolds number. It interpolates several
    times using several corrections graphs in [1]_.
    
    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    angle : float
        Angle of miter bend, [degrees]
    Re : float
        Reynolds number of the pipe (no specification if inlet or outlet
        properties should be used), [m]
    roughness : float, optional
        Roughness of bend wall, [m]   
    L_unimpeded : float, optional
        The length of unimpeded pipe without any fittings, instrumentation,
        or flow disturbances downstream (assumed 20 diameters if not 
        specified), [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----    
    Note the loss coefficient includes the surface friction of the pipe as if
    it was straight.
   
    Examples
    --------
    >>> bend_miter_Miller(Di=.6, angle=90, Re=2e6, roughness=2e-5, 
    ... L_unimpeded=30*.6)
    1.1921574594947668
    
    References
    ----------
    .. [1] Miller, Donald S. Internal Flow Systems: Design and Performance
       Prediction. Gulf Publishing Company, 1990.
    '''
    if L_unimpeded is None:
        L_unimpeded = 20*Di
    if angle > 120:
        angle = 120
    
    Kb = horner(bend_miter_Miller_coeffs, 0.0166666666666666664*(angle-60.000000))
    
    C_o =  Miller_bend_unimpeded_correction(Kb=Kb, Di=Di, L_unimpeded=L_unimpeded)
    C_roughness = Miller_bend_roughness_correction(Re=Re, Di=Di, 
                                                   roughness=roughness)
    Re_C_Re = min(max(Re, 1E4), 1E8)
    C_Re_1 = bend_rounded_Miller_C_Re(Re_C_Re, 1.0) if Re_C_Re < 207956.58904584477 else 1.0
    C_Re = Kb/(Kb - 0.2*C_Re_1 + 0.2)
    if C_Re > 2.2 or C_Re < 0:
        C_Re = 2.2
#    print('Kb=%g, C Re=%g, C rough =%g, Co=%g' %(Kb, C_Re, C_roughness, C_o))
    return Kb*C_Re*C_roughness*C_o


def bend_rounded(Di, angle, fd, rc=None, bend_diameters=5):
    r'''Returns loss coefficient for any rounded bend in a pipe
    as shown in [1]_.

    .. math::
        K = f\alpha\frac{r}{d} + (0.10 + 2.4f)\sin(\alpha/2)
        + \frac{6.6f(\sqrt{\sin(\alpha/2)}+\sin(\alpha/2))}
        {(r/d)^{\frac{4\alpha}{\pi}}}

    .. figure:: fittings/bend_rounded.png
       :scale: 30 %
       :alt: rounded bend; after [1]_

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    angle : float
        Angle of bend, [degrees]
    fd : float
        Darcy friction factor [-]
    rc : float, optional
        Radius of curvature of the entrance, optional [m]
    bend_diameters : float, optional (used if rc not provided)
        Number of diameters of pipe making up the bend radius [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    When inputting bend diameters, note that manufacturers often specify
    this as a multiplier of nominal diameter, which is different than actual
    diameter. Those require that rc be specified.
    
    `rc` is limited to 0.5 or above; which represents a sharp, square, inner 
    edge - and an outer bend radius of 1.0. Losses are at a minimum when this
    value is large.

    First term represents surface friction loss; the second, secondary flows;
    and the third, flow separation.
    Encompasses the entire range of elbow and pipe bend configurations.
    
    This was developed for bend angles between 0 and 180 degrees; and r/D
    ratios above 0.5. Only smooth pipe data was used in its development.
    
    Note the loss coefficient includes the surface friction of the pipe as if
    it was straight.
   
    Examples
    --------
    >>> bend_rounded(Di=4.020, rc=4.0*5, angle=30, fd=0.0163)
    0.10680196344492195

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    angle = angle/(180/pi)
    if not rc:
        rc = Di*bend_diameters
    return (fd*angle*rc/Di + (0.10 + 2.4*fd)*sin(angle/2.)
    + 6.6*fd*(sin(angle/2.)**0.5 + sin(angle/2.))/(rc/Di)**(4.*angle/pi))


def bend_miter(angle):
    r'''Returns loss coefficient for any single-joint miter bend in a pipe
    as shown in [1]_.

    .. math::
        K = 0.42\sin(\alpha/2) + 2.56\sin^3(\alpha/2)

    .. figure:: fittings/bend_mitre.png
       :scale: 25 %
       :alt: Miter bend, one joint only; after [1]_

    Parameters
    ----------
    angle : float
        Angle of bend, [degrees]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Applies for bends from 0 to 150 degrees. One joint only.

    Examples
    --------
    >>> bend_miter(150)
    2.7128147734758103

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    angle = angle/(180/pi)
    return 0.42*sin(angle*0.5) + 2.56*sin(angle*0.5)**3


def helix(Di, rs, pitch, N, fd):
    r'''Returns loss coefficient for any size constant-pitch helix
    as shown in [1]_. Has applications in immersed coils in tanks.

    .. math::
        K = N \left[f\frac{\sqrt{(2\pi r)^2 + p^2}}{d} + 0.20 + 4.8 f\right]

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    rs : float
        Radius of spiral, [m]
    pitch : float
        Distance between two subsequent coil centers, [m]
    N : float
        Number of coils in the helix [-]
    fd : float
        Darcy friction factor [-]


    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Formulation based on peak secondary flow as in two 180 degree bends per
    coil. Flow separation ignored. No f, Re, geometry limitations.
    Source not compared against others.

    Examples
    --------
    >>> helix(Di=0.01, rs=0.1, pitch=.03, N=10, fd=.0185)
    14.525134924495514

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    return N*(fd*((2*pi*rs)**2 + pitch**2)**0.5/Di + 0.20 + 4.8*fd)


def spiral(Di, rmax, rmin, pitch, fd):
    r'''Returns loss coefficient for any size constant-pitch spiral
    as shown in [1]_. Has applications in immersed coils in tanks.

    .. math::
        K = \frac{r_{max} - r_{min}}{p} \left[ f\pi\left(\frac{r_{max}
        +r_{min}}{d}\right) + 0.20 + 4.8f\right]
        + \frac{13.2f}{(r_{min}/d)^2}

    Parameters
    ----------
    Di : float
        Inside diameter of pipe, [m]
    rmax : float
        Radius of spiral at extremity, [m]
    rmin : float
        Radius of spiral at end near center, [m]
    pitch : float
        Distance between two subsequent coil centers, [m]
    fd : float
        Darcy friction factor [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Source not compared against others.

    Examples
    --------
    >>> spiral(Di=0.01, rmax=.1, rmin=.02, pitch=.01, fd=0.0185)
    7.950918552775473

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    return (rmax-rmin)/pitch*(fd*pi*(rmax+rmin)/Di + 0.20 + 4.8*fd) + 13.2*fd/(rmin/Di)**2

### Contractions

def contraction_sharp(Di1, Di2):
    r'''Returns loss coefficient for any sharp edged pipe contraction
    as shown in [1]_.

    .. math::
        K = 0.0696(1-\beta^5)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622(1-0.215\beta^2 -  0.785\beta^5) 

    .. math::
        \beta = d_2/d_1

    .. figure:: fittings/contraction_sharp.png
       :scale: 40 %
       :alt: Sharp contraction; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe, [m]
    Di2 : float
        Inside diameter of following pipe, [m]

    Returns
    -------
    K : float
        Loss coefficient in terms of the following pipe [-]

    Notes
    -----
    A value of 0.506 or simply 0.5 is often used.

    Examples
    --------
    >>> contraction_sharp(Di1=1, Di2=0.4)
    0.5301269161591805

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di2/Di1
    lbd = 1 + 0.622*(1-0.215*beta**2 - 0.785*beta**5)
    return 0.0696*(1-beta**5)*lbd**2 + (lbd-1)**2


def contraction_round(Di1, Di2, rc):
    r'''Returns loss coefficient for any round edged pipe contraction
    as shown in [1]_.

    .. math::
        K = 0.0696\left(1 - 0.569\frac{r}{d_2}\right)\left(1-\sqrt{\frac{r}
        {d_2}}\beta\right)(1-\beta^5)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622\left(1 - 0.30\sqrt{\frac{r}{d_2}}
        - 0.70\frac{r}{d_2}\right)^4 (1-0.215\beta^2-0.785\beta^5)

    .. math::
        \beta = d_2/d_1

    .. figure:: fittings/contraction_round.png
       :scale: 30 %
       :alt: Cirucular round contraction; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe, [m]
    Di2 : float
        Inside diameter of following pipe, [m]
    rc : float
        Radius of curvature of the contraction, [m]

    Returns
    -------
    K : float
        Loss coefficient in terms of the following pipe [-]

    Notes
    -----
    Rounding radius larger than 0.14Di2 prevents flow separation from the wall.
    Further increase in rounding radius continues to reduce loss coefficient.

    Examples
    --------
    >>> contraction_round(Di1=1, Di2=0.4, rc=0.04)
    0.1783332490866574

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di2/Di1
    lbd = 1 + 0.622*(1 - 0.30*(rc/Di2)**0.5 - 0.70*rc/Di2)**4*(1-0.215*beta**2 - 0.785*beta**5)
    return 0.0696*(1-0.569*rc/Di2)*(1-(rc/Di2)**0.5*beta)*(1-beta**5)*lbd**2 + (lbd-1)**2


def contraction_conical(Di1, Di2, fd, l=None, angle=None):
    r'''Returns loss coefficient for any conical pipe contraction
    as shown in [1]_.

    .. math::
        K = 0.0696[1+C_B(\sin(\alpha/2)-1)](1-\beta^5)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622(\alpha/180)^{0.8}(1-0.215\beta^2-0.785\beta^5)

    .. math::
        \beta = d_2/d_1

    .. figure:: fittings/contraction_conical.png
       :scale: 30 %
       :alt: contraction conical; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe, [m]
    Di2 : float
        Inside diameter of following pipe, [m]
    fd : float
        Darcy friction factor [-]
    l : float
        Length of the contraction, optional [m]
    angle : float
        Angle of contraction, optional [degrees]

    Returns
    -------
    K : float
        Loss coefficient in terms of the following pipe [-]

    Notes
    -----
    Cheap and has substantial impact on pressure drop.

    Examples
    --------
    >>> contraction_conical(Di1=0.1, Di2=0.04, l=0.04, fd=0.0185)
    0.15779041548350314

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di2/Di1
    if angle:
        angle = angle/(180/pi)
        l = (Di1 - Di2)/(2*tan(angle/2))
    elif l:
        angle = 2*atan((Di1-Di2)/2/l)
    else:
        raise Exception('Either l or angle is required')

    lbd = 1 + 0.622*(angle/pi)**0.8*(1-0.215*beta**2 - 0.785*beta**5)
    return fd*(1-beta**4)/(8*sin(angle/2)) + 0.0696*sin(angle/2)*(1-beta**5)*lbd**2 + (lbd-1)**2


def contraction_beveled(Di1, Di2, l=None, angle=None):
    r'''Returns loss coefficient for any sharp beveled pipe contraction
    as shown in [1]_.

    .. math::
        K = 0.0696[1+C_B(\sin(\alpha/2)-1)](1-\beta^5)\lambda^2 + (\lambda-1)^2

    .. math::
        \lambda = 1 + 0.622\left[1+C_B\left(\left(\frac{\alpha}{180}
        \right)^{0.8}-1\right)\right](1-0.215\beta^2-0.785\beta^5)

    .. math::
        C_B = \frac{l}{d_2}\frac{2\beta\tan(\alpha/2)}{1-\beta}

    .. math::
        \beta = d_2/d_1

    .. figure:: fittings/contraction_beveled.png
       :scale: 30 %
       :alt: contraction beveled; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe, [m]
    Di2 : float
        Inside diameter of following pipe, [m]
    l : float
        Length of the bevel along the pipe axis ,[m]
    angle : float
        Angle of bevel, [degrees]

    Returns
    -------
    K : float
        Loss coefficient in terms of the following pipe [-]

    Notes
    -----

    Examples
    --------
    >>> contraction_beveled(Di1=0.5, Di2=0.1, l=.7*.1, angle=120)
    0.40946469413070485

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    angle = angle/(180/pi)
    beta = Di2/Di1
    CB = l/Di2*2*beta*tan(angle/2)/(1-beta)
    lbd  = 1 + 0.622*(1 + CB*((angle/pi)**0.8-1))*(1-0.215*beta**2-0.785*beta**5)
    return 0.0696*(1 + CB*(sin(angle/2)-1))*(1-beta**5)*lbd**2 + (lbd-1)**2

### Expansions (diffusers)

def diffuser_sharp(Di1, Di2):
    r'''Returns loss coefficient for any sudden pipe diameter expansion
    as shown in [1]_ and in other sources.

    .. math::
        K_1 = (1-\beta^2)^2

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe (smaller), [m]
    Di2 : float
        Inside diameter of following pipe (larger), [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Highly accurate.

    Examples
    --------
    >>> diffuser_sharp(Di1=.5, Di2=1)
    0.5625

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di1/Di2
    return (1. - beta*beta)**2


def diffuser_conical(Di1, Di2, l=None, angle=None, fd=None):
    r'''Returns loss coefficient for any conical pipe expansion
    as shown in [1]_. Five different formulas are used, depending on
    the angle and the ratio of diameters.

    For 0 to 20 degrees, all aspect ratios:

    .. math::
        K_1 = 8.30[\tan(\alpha/2)]^{1.75}(1-\beta^2)^2 + \frac{f(1-\beta^4)}{8\sin(\alpha/2)}

    For 20 to 60 degrees, beta < 0.5:

    .. math::
        K_1 = \left\{1.366\sin\left[\frac{2\pi(\alpha-15^\circ)}{180}\right]^{0.5}
        - 0.170 - 3.28(0.0625-\beta^4)\sqrt{\frac{\alpha-20^\circ}{40^\circ}}\right\}
        (1-\beta^2)^2 + \frac{f(1-\beta^4)}{8\sin(\alpha/2)}

    For 20 to 60 degrees, beta >= 0.5:

    .. math::
        K_1 = \left\{1.366\sin\left[\frac{2\pi(\alpha-15^\circ)}{180}\right]^{0.5}
        - 0.170 \right\}(1-\beta^2)^2 + \frac{f(1-\beta^4)}{8\sin(\alpha/2)}

    For 60 to 180 degrees, beta < 0.5:

    .. math::
        K_1 = \left[1.205 - 3.28(0.0625-\beta^4)-12.8\beta^6\sqrt{\frac
        {\alpha-60^\circ}{120^\circ}}\right](1-\beta^2)^2

    For 60 to 180 degrees, beta >= 0.5:

    .. math::
        K_1 = \left[1.205 - 0.20\sqrt{\frac{\alpha-60^\circ}{120^\circ}}
        \right](1-\beta^2)^2

    .. figure:: fittings/diffuser_conical.png
       :scale: 60 %
       :alt: diffuser conical; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe (smaller), [m]
    Di2 : float
        Inside diameter of following pipe (larger), [m]
    l : float
        Length of the contraction along the pipe axis, optional[m]
    angle : float
        Angle of contraction, [degrees]
    fd : float
        Darcy friction factor [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    For angles above 60 degrees, friction factor is not used.

    Examples
    --------
    >>> diffuser_conical(Di1=1/3., Di2=1, angle=50, fd=0.03)
    0.8081340270019336

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di1/Di2

    if angle is not None:
        angle_rad = angle/(180/pi)
        l = (Di2 - Di1)/(2*tan(angle_rad/2))
    elif l is not None:
        angle_rad = 2*atan((Di2-Di1)/2/l)
        angle = angle_rad*(180/pi)
    else:
        raise Exception('Either `l` or `angle` must be specified')

    if 0 < angle <= 20:
        K = 8.30*tan(angle_rad/2)**1.75*(1-beta**2)**2 + fd*(1-beta**4)/8./sin(angle_rad/2)
    elif 20 < angle <= 60 and 0 <= beta < 0.5:
        K = (1.366*sin(2*pi*(angle-15)/180.)**0.5-0.170
        - 3.28*(0.0625-beta**4)*((angle-20)/40.)**0.5)*(1-beta**2)**2 + fd*(1-beta**4)/8./sin(angle_rad/2)
    elif 20 < angle <= 60 and beta >= 0.5:
        K = (1.366*sin(2*pi*(angle-15)/180.)**0.5-0.170)*(1-beta**2)**2 + fd*(1-beta**4)/8./sin(angle_rad/2)
    elif 60 < angle <= 180 and 0 <= beta < 0.5:
        K = (1.205 - 3.28*(0.0625-beta**4) - 12.8*beta**6*((angle-60)/120.)**0.5)*(1-beta**2)**2
    elif 60 < angle <= 180 and beta >= 0.5:
        K = (1.205 - 0.20*((angle-60)/120.)**0.5)*(1-beta**2)**2
    else:
        raise Exception('Conical diffuser inputs incorrect')
    return K


def diffuser_conical_staged(Di1, Di2, DEs, ls, fd=None):
    r'''Returns loss coefficient for any series of staged conical pipe expansions
    as shown in [1]_. Five different formulas are used, depending on
    the angle and the ratio of diameters. This function calls diffuser_conical.

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe (smaller), [m]
    Di2 : float
        Inside diameter of following pipe (larger), [m]
    DEs : array
        Diameters of intermediate sections, [m]
    ls : array
        Lengths of the various sections, [m]
    fd : float
        Darcy friction factor [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Only lengths of sections currently allowed. This could be changed
    to understand angles also.

    Formula doesn't make much sense, as observed by the example comparing
    a series of conical sections. Use only for small numbers of segments of
    highly differing angles.

    Examples
    --------
    >>> diffuser_conical(Di1=1., Di2=10.,l=9, fd=0.01)
    0.973137914861591

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    K = 0
    DEs.insert(0, Di1)
    DEs.append(Di2)
    for i in range(len(ls)):
        K += diffuser_conical(Di1=float(DEs[i]), Di2=float(DEs[i+1]), l=float(ls[i]), fd=fd)
    return K


def diffuser_curved(Di1, Di2, l):
    r'''Returns loss coefficient for any curved wall pipe expansion
    as shown in [1]_.

    .. math::
        K_1 = \phi(1.43-1.3\beta^2)(1-\beta^2)^2

    .. math::
        \phi = 1.01 - 0.624\frac{l}{d_1} + 0.30\left(\frac{l}{d_1}\right)^2
        - 0.074\left(\frac{l}{d_1}\right)^3 + 0.0070\left(\frac{l}{d_1}\right)^4

    .. figure:: fittings/curved_wall_diffuser.png
       :scale: 25 %
       :alt: diffuser curved; after [1]_

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe (smaller), [m]
    Di2 : float
        Inside diameter of following pipe (larger), [m]
    l : float
        Length of the curve along the pipe axis, [m]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Beta^2 should be between 0.1 and 0.9.
    A small mismatch between tabulated values of this function in table 11.3
    is observed with the equation presented.

    Examples
    --------
    >>> diffuser_curved(Di1=.25**0.5, Di2=1., l=2.)
    0.2299781250000002

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    beta = Di1/Di2
    phi = 1.01 - 0.624*l/Di1 + 0.30*(l/Di1)**2 - 0.074*(l/Di1)**3 + 0.0070*(l/Di1)**4
    return phi*(1.43 - 1.3*beta**2)*(1 - beta**2)**2


def diffuser_pipe_reducer(Di1, Di2, l, fd1, fd2=None):
    r'''Returns loss coefficient for any pipe reducer pipe expansion
    as shown in [1]. This is an approximate formula.

    .. math::
        K_f = f_1\frac{0.20l}{d_1} + \frac{f_1(1-\beta)}{8\sin(\alpha/2)}
        + f_2\frac{0.20l}{d_2}\beta^4

    .. math::
        \alpha = 2\tan^{-1}\left(\frac{d_1-d_2}{1.20l}\right)

    Parameters
    ----------
    Di1 : float
        Inside diameter of original pipe (smaller), [m]
    Di2 : float
        Inside diameter of following pipe (larger), [m]
    l : float
        Length of the pipe reducer along the pipe axis, [m]
    fd1 : float
        Darcy friction factor at inlet diameter [-]
    fd2 : float
        Darcy friction factor at outlet diameter, optional [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Industry lack of standardization prevents better formulas from being
    developed. Add 15% if the reducer is eccentric.
    Friction factor at outlet will be assumed the same as at inlet if not specified.

    Doubt about the validity of this equation is raised.

    Examples
    --------
    >>> diffuser_pipe_reducer(Di1=.5, Di2=.75, l=1.5, fd1=0.07)
    0.06873244301714816

    References
    ----------
    .. [1] Rennels, Donald C., and Hobart M. Hudson. Pipe Flow: A Practical
       and Comprehensive Guide. 1st edition. Hoboken, N.J: Wiley, 2012.
    '''
    if fd2 is None:
        fd2 = fd1
    beta = Di1/Di2
    angle = -2*atan((Di1-Di2)/1.20/l)
    K = fd1*0.20*l/Di1 + fd1*(1-beta)/8./sin(angle/2) + fd2*0.20*l/Di2*beta**4
    return K

### TODO: Tees

###  3 Darby 3K Method (with valves)
Darby = {}
Darby['Elbow, 90°, threaded, standard, (r/D = 1)'] = {'K1': 800, 'Ki': 0.14, 'Kd': 4}
Darby['Elbow, 90°, threaded, long radius, (r/D = 1.5)'] = {'K1': 800, 'Ki': 0.071, 'Kd': 4.2}
Darby['Elbow, 90°, flanged, welded, bends, (r/D = 1)'] = {'K1': 800, 'Ki': 0.091, 'Kd': 4}
Darby['Elbow, 90°, (r/D = 2)'] = {'K1': 800, 'Ki': 0.056, 'Kd': 3.9}
Darby['Elbow, 90°, (r/D = 4)'] = {'K1': 800, 'Ki': 0.066, 'Kd': 3.9}
Darby['Elbow, 90°, (r/D = 6)'] = {'K1': 800, 'Ki': 0.075, 'Kd': 4.2}
Darby['Elbow, 90°, mitered, 1 weld, (90°)'] = {'K1': 1000, 'Ki': 0.27, 'Kd': 4}
Darby['Elbow, 90°, 2 welds, (45°)'] = {'K1': 800, 'Ki': 0.068, 'Kd': 4.1}
Darby['Elbow, 90°, 3 welds, (30°)'] = {'K1': 800, 'Ki': 0.035, 'Kd': 4.2}
Darby['Elbow, 45°, threaded standard, (r/D = 1)'] = {'K1': 500, 'Ki': 0.071, 'Kd': 4.2}
Darby['Elbow, 45°, long radius, (r/D = 1.5)'] = {'K1': 500, 'Ki': 0.052, 'Kd': 4}
Darby['Elbow, 45°, mitered, 1 weld, (45°)'] = {'K1': 500, 'Ki': 0.086, 'Kd': 4}
Darby['Elbow, 45°, mitered, 2 welds, (22.5°)'] = {'K1': 500, 'Ki': 0.052, 'Kd': 4}
Darby['Elbow, 180°, threaded, close-return bend, (r/D = 1)'] = {'K1': 1000, 'Ki': 0.23, 'Kd': 4}
Darby['Elbow, 180°, flanged, (r/D = 1)'] = {'K1': 1000, 'Ki': 0.12, 'Kd': 4}
Darby['Elbow, 180°, all, (r/D = 1.5)'] = {'K1': 1000, 'Ki': 0.1, 'Kd': 4}
Darby['Tee, Through-branch, (as elbow), threaded, (r/D = 1)'] = {'K1': 500, 'Ki': 0.274, 'Kd': 4}
Darby['Tee, Through-branch,(as elbow), (r/D = 1.5)'] = {'K1': 800, 'Ki': 0.14, 'Kd': 4}
Darby['Tee, Through-branch, (as elbow), flanged, (r/D = 1)'] = {'K1': 800, 'Ki': 0.28, 'Kd': 4}
Darby['Tee, Through-branch, (as elbow), stub-in branch'] = {'K1': 1000, 'Ki': 0.34, 'Kd': 4}
Darby['Tee, Run-through, threaded, (r/D = 1)'] = {'K1': 200, 'Ki': 0.091, 'Kd': 4}
Darby['Tee, Run-through, flanged, (r/D = 1)'] = {'K1': 150, 'Ki': 0.05, 'Kd': 4}
Darby['Tee, Run-through, stub-in branch'] = {'K1': 100, 'Ki': 0, 'Kd': 0}
Darby['Valve, Angle valve, 45°, full line size, β = 1'] = {'K1': 950, 'Ki': 0.25, 'Kd': 4}
Darby['Valve, Angle valve, 90°, full line size, β = 1'] = {'K1': 1000, 'Ki': 0.69, 'Kd': 4}
Darby['Valve, Globe valve, standard, β = 1'] = {'K1': 1500, 'Ki': 1.7, 'Kd': 3.6}
Darby['Valve, Plug valve, branch flow'] = {'K1': 500, 'Ki': 0.41, 'Kd': 4}
Darby['Valve, Plug valve, straight through'] = {'K1': 300, 'Ki': 0.084, 'Kd': 3.9}
Darby['Valve, Plug valve, three-way (flow through)'] = {'K1': 300, 'Ki': 0.14, 'Kd': 4}
Darby['Valve, Gate valve, standard, β = 1'] = {'K1': 300, 'Ki': 0.037, 'Kd': 3.9}
Darby['Valve, Ball valve, standard, β = 1'] = {'K1': 300, 'Ki': 0.017, 'Kd': 3.5}
Darby['Valve, Diaphragm, dam type'] = {'K1': 1000, 'Ki': 0.69, 'Kd': 4.9}
Darby['Valve, Swing check'] = {'K1': 1500, 'Ki': 0.46, 'Kd': 4}
Darby['Valve, Lift check'] = {'K1': 2000, 'Ki': 2.85, 'Kd': 3.8}


def Darby3K(NPS=None, Re=None, name=None, K1=None, Ki=None, Kd=None):
    r'''Returns loss coefficient for any various fittings, depending
    on the name input. Alternatively, the Darby constants K1, Ki and Kd
    may be provided and used instead. Source of data is [1]_.
    Reviews of this model are favorable.

    .. math::
        K_f = \frac{K_1}{Re} + K_i\left(1 + \frac{K_d}{D_{\text{NPS}}^{0.3}}
        \right)

    Note this model uses nominal pipe diameter in inches.
    
    Parameters
    ----------
    NPS : float
        Nominal diameter of the pipe, [in]
    Re : float
        Reynolds number, [-]
    name : str
        String from Darby dict representing a fitting
    K1 : float
        K1 parameter of Darby model, optional [-]
    Ki : float
        Ki parameter of Darby model, optional [-]
    Kd : float
        Kd parameter of Darby model, optional [in]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Also described in Albright's Handbook and Ludwig's Applied Process Design.
    Relatively uncommon to see it used.

    The possibility of combining these methods with those above are attractive.

    Examples
    --------
    >>> Darby3K(NPS=2., Re=10000., name='Valve, Angle valve, 45°, full line size, β = 1')
    1.1572523963562353
    >>> Darby3K(NPS=12., Re=10000., K1=950,  Ki=0.25,  Kd=4)
    0.819510280626355

    References
    ----------
    .. [1] Silverberg, Peter, and Ron Darby. "Correlate Pressure Drops through
       Fittings: Three Constants Accurately Calculate Flow through Elbows,
       Valves and Tees." Chemical Engineering 106, no. 7 (July 1999): 101.
    .. [2] Silverberg, Peter. "Correlate Pressure Drops Through Fittings."
       Chemical Engineering 108, no. 4 (April 2001): 127,129-130.
    '''
    if name:
        if name in Darby:
            d = Darby[name]
            K1, Ki, Kd = d['K1'], d['Ki'], d['Kd']
        else:
            raise Exception('Name of fitting not in list')
    elif K1 and Ki and Kd:
        pass
    else:
        raise Exception('Name of fitting or constants are required')
    return K1/Re + Ki*(1. + Kd/NPS**0.3)


### 2K Hooper Method

Hooper = {}
Hooper['Elbow, 90°, Standard (R/D = 1), Screwed'] = {'K1': 800, 'Kinfty': 0.4}
Hooper['Elbow, 90°, Standard (R/D = 1), Flanged/welded'] = {'K1': 800, 'Kinfty': 0.25}
Hooper['Elbow, 90°, Long-radius (R/D = 1.5), All types'] = {'K1': 800, 'Kinfty': 0.2}
Hooper['Elbow, 90°, Mitered (R/D = 1.5), 1 weld (90° angle)'] = {'K1': 1000, 'Kinfty': 1.15}
Hooper['Elbow, 90°, Mitered (R/D = 1.5), 2 weld (45° angle)'] = {'K1': 800, 'Kinfty': 0.35}
Hooper['Elbow, 90°, Mitered (R/D = 1.5), 3 weld (30° angle)'] = {'K1': 800, 'Kinfty': 0.3}
Hooper['Elbow, 90°, Mitered (R/D = 1.5), 4 weld (22.5° angle)'] = {'K1': 800, 'Kinfty': 0.27}
Hooper['Elbow, 90°, Mitered (R/D = 1.5), 5 weld (18° angle)'] = {'K1': 800, 'Kinfty': 0.25}
Hooper['Elbow, 45°, Standard (R/D = 1), All types'] = {'K1': 500, 'Kinfty': 0.2}
Hooper['Elbow, 45°, Long-radius (R/D 1.5), All types'] = {'K1': 500, 'Kinfty': 0.15}
Hooper['Elbow, 45°, Mitered (R/D=1.5), 1 weld (45° angle)'] = {'K1': 500, 'Kinfty': 0.25}
Hooper['Elbow, 45°, Mitered (R/D=1.5), 2 weld (22.5° angle)'] = {'K1': 500, 'Kinfty': 0.15}
Hooper['Elbow, 45°, Standard (R/D = 1), Screwed'] = {'K1': 1000, 'Kinfty': 0.7}
Hooper['Elbow, 180°, Standard (R/D = 1), Flanged/welded'] = {'K1': 1000, 'Kinfty': 0.35}
Hooper['Elbow, 180°, Long-radius (R/D = 1.5), All types'] = {'K1': 1000, 'Kinfty': 0.3}
Hooper['Elbow, Used as, Standard, Screwed'] = {'K1': 500, 'Kinfty': 0.7}
Hooper['Elbow, Elbow, Long-radius, Screwed'] = {'K1': 800, 'Kinfty': 0.4}
Hooper['Elbow, Elbow, Standard, Flanged/welded'] = {'K1': 800, 'Kinfty': 0.8}
Hooper['Elbow, Elbow, Stub-in type branch'] = {'K1': 1000, 'Kinfty': 1}
Hooper['Tee, Run, Screwed'] = {'K1': 200, 'Kinfty': 0.1}
Hooper['Tee, Through, Flanged or welded'] = {'K1': 150, 'Kinfty': 0.05}
Hooper['Tee, Tee, Stub-in type branch'] = {'K1': 100, 'Kinfty': 0}
Hooper['Valve, Gate, Full line size, Beta = 1'] = {'K1': 300, 'Kinfty': 0.1}
Hooper['Valve, Ball, Reduced trim, Beta = 0.9'] = {'K1': 500, 'Kinfty': 0.15}
Hooper['Valve, Plug, Reduced trim, Beta = 0.8'] = {'K1': 1000, 'Kinfty': 0.25}
Hooper['Valve, Globe, Standard'] = {'K1': 1500, 'Kinfty': 4}
Hooper['Valve, Globe, Angle or Y-type'] = {'K1': 1000, 'Kinfty': 2}
Hooper['Valve, Diaphragm, Dam type'] = {'K1': 1000, 'Kinfty': 2}
Hooper['Valve, Butterfly,'] = {'K1': 800, 'Kinfty': 0.25}
Hooper['Valve, Check, Lift'] = {'K1': 2000, 'Kinfty': 10}
Hooper['Valve, Check, Swing'] = {'K1': 1500, 'Kinfty': 1.5}
Hooper['Valve, Check, Tilting-disc'] = {'K1': 1000, 'Kinfty': 0.5}


def Hooper2K(Di, Re, name=None, K1=None, Kinfty=None):
    r'''Returns loss coefficient for any various fittings, depending
    on the name input. Alternatively, the Hooper constants K1, Kinfty
    may be provided and used instead. Source of data is [1]_.
    Reviews of this model are favorable less favorable than the Darby method
    but superior to the constant-K method.

    .. math::
        K = \frac{K_1}{Re} + K_\infty\left(1 + \frac{1\text{ inch}}{D_{in}}\right)

    Note this model uses actual inside pipe diameter in inches.

    Parameters
    ----------
    Di : float
        Actual inside diameter of the pipe, [in]
    Re : float
        Reynolds number, [-]
    name : str, optional
        String from Hooper dict representing a fitting
    K1 : float, optional
        K1 parameter of Hooper model, optional [-]
    Kinfty : float, optional
        Kinfty parameter of Hooper model, optional [-]

    Returns
    -------
    K : float
        Loss coefficient [-]

    Notes
    -----
    Also described in Ludwig's Applied Process Design.
    Relatively uncommon to see it used.
    No actual example found.

    Examples
    --------
    >>> Hooper2K(Di=2., Re=10000., name='Valve, Globe, Standard')
    6.15
    >>> Hooper2K(Di=2., Re=10000., K1=900, Kinfty=4)
    6.09

    References
    ----------
    .. [1] Hooper, W. B., "The 2-K Method Predicts Head Losses in Pipe
       Fittings," Chem. Eng., p. 97, Aug. 24 (1981).
    .. [2] Hooper, William B. "Calculate Head Loss Caused by Change in Pipe
       Size." Chemical Engineering 95, no. 16 (November 7, 1988): 89.
    .. [3] Kayode Coker. Ludwig's Applied Process Design for Chemical and
       Petrochemical Plants. 4E. Amsterdam ; Boston: Gulf Professional
       Publishing, 2007.
    '''
    if name:
        if name in Hooper:
            d = Hooper[name]
            K1, Kinfty = d['K1'], d['Kinfty']
        else:
            raise Exception('Name of fitting not in list')
    elif K1 and Kinfty:
        pass
    else:
        raise Exception('Name of fitting or constants are required')
    return K1/Re + Kinfty*(1. + 1./Di)


### Valves



def Kv_to_Cv(Kv):
    r'''Convert valve flow coefficient from imperial to common metric units.

    .. math::
        C_v = 1.156 K_v

    Parameters
    ----------
    Kv : float
        Metric Kv valve flow coefficient (flow rate of water at a pressure drop  
        of 1 bar) [m^3/hr]

    Returns
    -------
    Cv : float
        Imperial Cv valve flow coefficient (flow rate of water at a pressure   
        drop of 1 psi) [gallons/minute]

    Notes
    -----
    Kv = 0.865 Cv is in the IEC standard 60534-2-1.
    It has also been said that Cv = 1.17Kv; this is wrong by current standards.
    
    The conversion factor does not depend on the density of the fluid or the
    diameter of the valve. It is calculated with the definition of a US gallon
    as 231 cubic inches, and a psi as a pound-force per square inch.

    The exact conversion coefficient between Kv to Cv is 1.1560992283536566;
    it is rounded in the formula above.

    Examples
    --------
    >>> Kv_to_Cv(2)
    2.3121984567073133

    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return 1.1560992283536566*Kv


def Cv_to_Kv(Cv):
    r'''Convert valve flow coefficient from imperial to common metric units.

    .. math::
        K_v = C_v/1.156

    Parameters
    ----------
    Cv : float
        Imperial Cv valve flow coefficient (flow rate of water at a pressure   
        drop of 1 psi) [gallons/minute]

    Returns
    -------
    Kv : float
        Metric Kv valve flow coefficient (flow rate of water at a pressure drop  
        of 1 bar) [m^3/hr]

    Notes
    -----
    Kv = 0.865 Cv is in the IEC standard 60534-2-1.
    It has also been said that Cv = 1.17Kv; this is wrong by current standards.

    The conversion factor does not depend on the density of the fluid or the
    diameter of the valve. It is calculated with the definition of a US gallon
    as 231 cubic inches, and a psi as a pound-force per square inch.

    The exact conversion coefficient between Kv to Cv is 1.1560992283536566;
    it is rounded in the formula above.

    Examples
    --------
    >>> Cv_to_Kv(2.312)
    1.9998283393826013

    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return Cv/1.1560992283536566


def Kv_to_K(Kv, D):
    r'''Convert valve flow coefficient from common metric units to regular
    loss coefficients.

    .. math::
        K = 1.6\times 10^9 \frac{D^4}{K_v^2}
        
    Parameters
    ----------
    Kv : float
        Metric Kv valve flow coefficient (flow rate of water at a pressure drop  
        of 1 bar) [m^3/hr]
    D : float
        Inside diameter of the valve [m]

    Returns
    -------
    K : float
        Loss coefficient, [-]

    Notes
    -----
    Crane TP 410 M (2009) gives the coefficient of 0.04 (with diameter in mm).
    
    It also suggests the density of water should be found between 5-40°C. 
    Older versions specify the density should be found at 60 °F, which is
    used here, and the pessure for the appropriate density is back calculated.

    .. math::
        \Delta P = 1 \text{ bar} = \frac{1}{2}\rho V^2\cdot K
        
        V = \frac{\frac{K_v\cdot \text{ hour}}{3600 \text{ second}}}{\frac{\pi}{4}D^2}
        
        \rho = 999.29744568 \;\; kg/m^3  \text{ at } T=60° F, P = 703572 Pa

    The value of density is calculated with IAPWS-95; it is chosen as it makes
    the coefficient a very convenient round number. Others constants that have
    been used are 1.604E9, and 1.60045E9.

    Examples
    --------
    >>> Kv_to_K(2.312, .015)
    15.153374600399898

    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return 1.6E9*D**4*Kv**-2


def K_to_Kv(K, D):
    r'''Convert regular loss coefficient to valve flow coefficient.

    .. math::
        K_v = 4\times 10^4 \sqrt{ \frac{D^4}{K}}

    Parameters
    ----------
    K : float
        Loss coefficient, [-]
    D : float
        Inside diameter of the valve [m]

    Returns
    -------
    Kv : float
        Metric Kv valve flow coefficient (flow rate of water at a pressure drop  
        of 1 bar) [m^3/hr]

    Notes
    -----
    Crane TP 410 M (2009) gives the coefficient of 0.04 (with diameter in mm).
    
    It also suggests the density of water should be found between 5-40°C. 
    Older versions specify the density should be found at 60 °F, which is
    used here, and the pessure for the appropriate density is back calculated.

    .. math::
        \Delta P = 1 \text{ bar} = \frac{1}{2}\rho V^2\cdot K
        
        V = \frac{\frac{K_v\cdot \text{ hour}}{3600 \text{ second}}}{\frac{\pi}{4}D^2}
        
        \rho = 999.29744568 \;\; kg/m^3 \text{ at } T=60° F, P = 703572 Pa

    The value of density is calculated with IAPWS-95; it is chosen as it makes
    the coefficient a very convenient round number. Others constants that have
    been used are 1.604E9, and 1.60045E9.

    Examples
    --------
    >>> K_to_Kv(15.15337460039990, .015)
    2.312

    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return D*D*(1.6E9/K)**0.5


def K_to_Cv(K, D):
    r'''Convert regular loss coefficient to imperial valve flow coefficient.

    .. math::
        K_v = 1.156 \cdot 4\times 10^4 \sqrt{ \frac{D^4}{K}}
        
    Parameters
    ----------
    K : float
        Loss coefficient, [-]
    D : float
        Inside diameter of the valve [m]

    Returns
    -------
    Cv : float
        Imperial Cv valve flow coefficient (flow rate of water at a pressure   
        drop of 1 psi) [gallons/minute]

    Notes
    -----
    The conversion factor does not depend on the density of the fluid or the
    diameter of the valve. It is calculated with the definition of a US gallon
    as 231 cubic inches, and a psi as a pound-force per square inch.

    The exact conversion coefficient between Kv to Cv is 1.1560992283536566;
    it is rounded in the formula above.

    Examples
    --------
    >>> K_to_Cv(16, .015)
    2.601223263795727
    
    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return 1.1560992283536566*D*D*(1.6E9/K)**0.5


def Cv_to_K(Cv, D):
    r'''Convert imperial valve flow coefficient from imperial units to regular
    loss coefficients.

    .. math::
        K = 1.6\times 10^9 \frac{D^4}{\left(\frac{C_v}{1.56}\right)^2}
        
    Parameters
    ----------
    Cv : float
        Imperial Cv valve flow coefficient (flow rate of water at a pressure   
        drop of 1 psi) [gallons/minute]
    D : float
        Inside diameter of the valve [m]

    Returns
    -------
    K : float
        Loss coefficient, [-]

    Notes
    -----
    The exact conversion coefficient between Kv to Cv is 1.1560992283536566;
    it is rounded in the formula above.

    Examples
    --------
    >>> Cv_to_K(2.712, .015)
    14.719595348352552

    References
    ----------
    .. [1] ISA-75.01.01-2007 (60534-2-1 Mod) Draft
    '''
    return 1.6E9*D**4*(Cv/1.1560992283536566)**-2


def K_gate_valve_Crane(D1, D2, angle, fd):
    r'''Returns loss coefficient for a gate valve of types wedge disc, double
    disc, or plug type, as shown in [1]_.

    If β = 1 and θ = 0:
        
    .. math::
        K = K_1 = K_2 = 8f_d
        
    If β < 1 and θ <= 45°:
        
    .. math::
        K_2 = \frac{K + \sin \frac{\theta}{2} \left[0.8(1-\beta^2) 
        + 2.6(1-\beta^2)^2\right]}{\beta^4}
            
    If β < 1 and θ > 45°:
        
    .. math::
        K_2 = \frac{K + 0.5\sqrt{\sin\frac{\theta}{2}}(1-\beta^2) 
        + (1-\beta^2)^2}{\beta^4}
        
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    angle : float
        Angle formed by the reducer in the valve, [degrees]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]

    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions [2]_.
    
    Examples
    --------
    Example 7-4 in [1]_; a 150 by 100 mm glass 600 steel gate valve, conically
    tapered ports, length 550 mm, back of sear ring ~150 mm. The valve is 
    connected to 146 mm schedule 80 pipe. The angle can be calculated to be 
    13 degrees. The valve is specified to be operating in turbulent conditions.
    
    >>> K_gate_valve_Crane(D1=.1, D2=.146, angle=13.115, fd=0.015)
    1.145830368873396
    
    The calculated result is lower than their value of 1.22; the difference is
    due to intermediate rounding.
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    .. [2] Harvey Wilson. "Pressure Drop in Pipe Fittings and Valves | 
       Equivalent Length and Resistance Coefficient." Katmar Software. Accessed
       July 28, 2017. http://www.katmarsoftware.com/articles/pipe-fitting-pressure-drop.htm.
    '''
    angle = radians(angle)
    beta = D1/D2
    K1 = 8*fd # This does not refer to upstream loss per se
    if beta == 1 or angle == 0:
        return K1 # upstream and down
    else:
        if angle <= pi/4:
            K = (K1 + sin(angle/2)*(0.8*(1-beta**2) + 2.6*(1-beta**2)**2))/beta**4
        else:
            K = (K1 + 0.5*(sin(angle/2))**0.5 * (1 - beta**2) + (1-beta**2)**2)/beta**4
    return K


def K_globe_valve_Crane(D1, D2, fd):
    r'''Returns the loss coefficient for all types of globe valve, (reduced 
    seat or throttled) as shown in [1]_.

    If β = 1:
        
    .. math::
        K = K_1 = K_2 = 340 f_d
        
    Otherwise:
    
    .. math::
        K_2 = \frac{K + \left[0.5(1-\beta^2) + (1-\beta^2)^2\right]}{\beta^4}
        
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]

    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_globe_valve_Crane(.01, .02, fd=.015)
    87.1
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = D1/D2
    K1 = 340*fd 
    if beta == 1:
        return K1 # upstream and down
    else:
        return (K1 + beta*(0.5*(1-beta)**2 + (1-beta**2)**2))/beta**4


def K_angle_valve_Crane(D1, D2, fd, style=0):
    r'''Returns the loss coefficient for all types of angle valve, (reduced 
    seat or throttled) as shown in [1]_.

    If β = 1:
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    Otherwise:
    
    .. math::
        K_2 = \frac{K + \left[0.5(1-\beta^2) + (1-\beta^2)^2\right]}{\beta^4}
        
    For style 0 and 2, N = 55; for style 1, N=150.
    
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        One of 0, 1, or 2; refers to three different types of angle valves
        as shown in [1]_ [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_angle_valve_Crane(.01, .02, fd=.016)
    19.58
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = D1/D2
    if style not in [0, 1, 2]:
        raise Exception('Valve style should be 0, 1, or 2')
    if style == 0 or style == 2:
        K1 = 55*fd
    else:
        K1 = 150*fd
    if beta == 1:
        return K1 # upstream and down
    else:
        return (K1 + beta*(0.5*(1-beta)**2 + (1-beta**2)**2))/beta**4


def K_swing_check_valve_Crane(fd, angled=True):
    r'''Returns the loss coefficient for a swing check valve as shown in [1]_.
        
    .. math::
        K_2 = N\cdot f_d
        
    For angled swing check valves N = 100; for straight valves, N = 50.
    
    Parameters
    ----------
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    angled : bool, optional
        If True, returns a value 2x the unangled value; the style of the valve
        [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_swing_check_valve_Crane(fd=.016)
    1.6
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    if angled:
        return 100.*fd
    return 50.*fd


def K_lift_check_valve_Crane(D1, D2, fd, angled=True):
    r'''Returns the loss coefficient for a lift check valve as shown in [1]_.
        
    If β = 1:
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    Otherwise:
    
    .. math::
        K_2 = \frac{K + \left[0.5(1-\beta^2) + (1-\beta^2)^2\right]}{\beta^4}
        
        
    For angled lift check valves N = 55; for straight valves, N = 600.
    
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    angled : bool, optional
        If True, returns a value 2x the unangled value; the style of the valve
        [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_lift_check_valve_Crane(.01, .02, fd=.016)
    21.58
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = D1/D2
    if angled:
        K1 = 55*fd
        if beta == 1:
            return K1
        else:
            return (K1 + beta*(0.5*(1 - beta**2) + (1 - beta**2)**2))/beta**4
    else:
        K1 = 600.*fd
        if beta == 1:
            return K1
        else:
            return (K1 + beta*(0.5*(1 - beta**2) + (1 - beta**2)**2))/beta**4
            
        
def K_tilting_disk_check_valve_Crane(D, angle, fd):
    r'''Returns the loss coefficient for a tilting disk check valve as shown in
    [1]_. Results are specified in [1]_ to be for the disk's resting position
    to be at 5 or 25 degrees to the flow direction.  The model is implemented
    here so as to switch to the higher loss 15 degree coefficients at 10 
    degrees, and use the lesser coefficients for any angle under 10 degrees.
        
    .. math::
        K = N\cdot f_d
        
    N is obtained from the following table:

    +--------+-------------+-------------+
    |        | angle = 5 ° | angle = 15° |
    +========+=============+=============+
    | 2-8"   | 40          | 120         |
    +--------+-------------+-------------+
    | 10-14" | 30          | 90          |
    +--------+-------------+-------------+
    | 16-48" | 20          | 60          |
    +--------+-------------+-------------+
    
    The actual change of coefficients happen at <= 9" and <= 15".
            
    Parameters
    ----------
    D : float
        Diameter of the pipe section the valve in mounted in; the
        same as the line size [m]
    angle : float
        Angle of the tilting disk to the flow direction; nominally 5 or 15
        degrees [degrees]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_tilting_disk_check_valve_Crane(.01, 5, fd=.016)
    0.64
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    if angle < 10:
        # 5 degree case
        if D <= 0.2286:
            # 2-8 inches, split at 9 inch
            return 40*fd
        elif D <= 0.381:
            # 10-14 inches, split at 15 inch
            return 30*fd
        else:
            # 16-18 inches
            return 20*fd
    else:
        # 15 degree case
        if D < 0.2286:
            # 2-8 inches
            return 120*fd
        elif D < 0.381:
            # 10-14 inches
            return 90*fd
        else:
            # 16-18 inches
            return 60*fd


def K_globe_stop_check_valve_Crane(D1, D2, fd, style=0):
    r'''Returns the loss coefficient for a globe stop check valve as shown in 
    [1]_.
        
    If β = 1:
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    Otherwise:
    
    .. math::
        K_2 = \frac{K + \left[0.5(1-\beta^2) + (1-\beta^2)^2\right]}{\beta^4}
        
    Style 0 is the standard form; style 1 is angled, with a restrition to force
    the flow up through the valve; style 2 is also angled but with a smaller
    restriction forcing the flow up. N is 400, 300, and 55 for those cases
    respectively.
    
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        One of 0, 1, or 2; refers to three different types of angle valves
        as shown in [1]_ [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_globe_stop_check_valve_Crane(.1, .02, .0165, style=1)
    4.51992
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: 400, 1: 300, 2: 55}
    try:
        K = coeffs[style]*fd
    except KeyError:
        raise KeyError('Accepted valve styles are 0, 1, and 2 only')
    beta = D1/D2
    if beta == 1:
        return K
    else:
        return (K + beta*(0.5*(1 - beta**2) + (1 - beta**2)**2))/beta**4


def K_angle_stop_check_valve_Crane(D1, D2, fd, style=0):
    r'''Returns the loss coefficient for a angle stop check valve as shown in 
    [1]_.
        
    If β = 1:
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    Otherwise:
    
    .. math::
        K_2 = \frac{K + \left[0.5(1-\beta^2) + (1-\beta^2)^2\right]}{\beta^4}
        
    Style 0 is the standard form; style 1 has a restrition to force
    the flow up through the valve; style 2 is has the clearest flow area with
    no guides for the angle valve. N is 200, 350, and 55 for those cases
    respectively.
    
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be smaller or equal to `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        One of 0, 1, or 2; refers to three different types of angle valves
        as shown in [1]_ [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_angle_stop_check_valve_Crane(.1, .02, .0165, style=1)
    4.52124
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: 200, 1: 350, 2: 55}
    try:
        K = coeffs[style]*fd
    except KeyError:
        raise KeyError('Accepted valve styles are 0, 1, and 2 only')

    beta = D1/D2
    if beta == 1:
        return K
    else:
        return (K + beta*(0.5*(1 - beta**2) + (1 - beta**2)**2))/beta**4


def K_ball_valve_Crane(D1, D2, angle, fd):
    r'''Returns the loss coefficient for a ball valve as shown in [1]_.

    If β = 1:
        
    .. math::
        K = K_1 = K_2 = 3f_d
        
    If β < 1 and θ <= 45°:
        
    .. math::
        K_2 = \frac{K + \sin \frac{\theta}{2} \left[0.8(1-\beta^2) 
        + 2.6(1-\beta^2)^2\right]} {\beta^4}
            
    If β < 1 and θ > 45°:
        
    .. math::
        K_2 = \frac{K + 0.5\sqrt{\sin\frac{\theta}{2}}(1-\beta^2) 
        + (1-\beta^2)^2}{\beta^4}
        
    Parameters
    ----------
    D1 : float
        Diameter of the valve seat bore (must be equal to or smaller than 
        `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    angle : float
        Angle formed by the reducer in the valve, [degrees]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]

    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_ball_valve_Crane(.01, .02, 50, .025)
    14.100545785228675
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = D1/D2
    K1 = 3*fd
    angle = radians(angle)
    if beta == 1:
        return K1
    else:
        if angle <= pi/4:
            return (K1 + sin(angle/2)*(0.8*(1-beta**2) + 2.6*(1-beta**2)**2))/beta**4
        else:
            return (K1 + 0.5*(sin(angle/2))**0.5 * (1 - beta**2) + (1-beta**2)**2)/beta**4


def K_diaphragm_valve_Crane(fd, style=0):
    r'''Returns the loss coefficient for a diaphragm valve of either weir
    (`style` = 0) or straight-through (`style` = 1) as shown in [1]_.
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    For style 0 (weir), N = 149; for style 1 (straight through), N = 39.
    
    Parameters
    ----------
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        Either 0 (weir type valve) or 1 (straight through weir valve) [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_diaphragm_valve_Crane(0.015, style=0)
    2.235
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: 149, 1: 39}
    try:
        K = coeffs[style]*fd
    except KeyError:
        raise KeyError('Accepted valve styles are 0 (weir) or 1 (straight through) only')
    return K


def K_foot_valve_Crane(fd, style=0):
    r'''Returns the loss coefficient for a foot valve of either poppet disc
    (`style` = 0) or hinged-disk (`style` = 1) as shown in [1]_. Both valves
    are specified include the loss of the attached strainer.
        
    .. math::
        K = K_1 = K_2 = N\cdot f_d
        
    For style 0 (poppet disk), N = 420; for style 1 (hinged disk), N = 75.
    
    Parameters
    ----------
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        Either 0 (poppet disk foot valve) or 1 (hinged disk foot valve) [-]
        
    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_foot_valve_Crane(0.015, style=0)
    6.3
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: 420, 1: 75}
    try:
        K = coeffs[style]*fd
    except KeyError:
        raise KeyError('Accepted valve styles are 0 (poppet disk) or 1 (hinged disk) only')
    return K


def K_butterfly_valve_Crane(D, fd, style=0):
    r'''Returns the loss coefficient for a butterfly valve as shown in
    [1]_. Three different types are supported; Centric (`style` = 0),
    double offset (`style` = 1), and triple offset (`style` = 2).
        
    .. math::
        K = N\cdot f_d
        
    N is obtained from the following table:
        
    +------------+---------+---------------+---------------+
    | Size range | Centric | Double offset | Triple offset |
    +============+=========+===============+===============+
    | 2" - 8"    | 45      | 74            | 218           |
    +------------+---------+---------------+---------------+
    | 10" - 14"  | 35      | 52            | 96            |
    +------------+---------+---------------+---------------+
    | 16" - 24"  | 25      | 43            | 55            |
    +------------+---------+---------------+---------------+
        
    The actual change of coefficients happen at <= 9" and <= 15".
            
    Parameters
    ----------
    D : float
        Diameter of the pipe section the valve in mounted in; the
        same as the line size [m]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        Either 0 (centric), 1 (double offset), or 2 (triple offset) [-]

    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_butterfly_valve_Crane(.01, .016, style=2)
    3.488
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: (45, 35, 25), 1: (74, 52, 43), 2: (218, 96, 55)}
    try:
        c1, c2, c3 = coeffs[style]
    except KeyError:
        raise KeyError('Accepted valve styles are 0 (centric), 1 (double offset), or 2 (triple offset) only.')
    if D <= 0.2286:
        # 2-8 inches, split at 9 inch
        return c1*fd
    elif D <= 0.381:
        # 10-14 inches, split at 15 inch
        return c2*fd
    else:
        # 16-18 inches
        return c3*fd
    
    
def K_plug_valve_Crane(D1, D2, angle, fd, style=0):
    r'''Returns the loss coefficient for a plug valve or cock valve as shown in
    [1]_.

    If β = 1:
        
    .. math::
        K = K_1 = K_2 = Nf_d
        
    Otherwise:
        
    .. math::
        K_2 = \frac{K + 0.5\sqrt{\sin\frac{\theta}{2}}(1-\beta^2) 
        + (1-\beta^2)^2}{\beta^4}
        
    Three types of plug valves are supported. For straight-through plug valves
    (`style` = 0), N = 18. For 3-way, flow straight through (`style` = 1) 
    plug valves, N = 30. For 3-way, flow 90° valves (`style` = 2) N = 90.
        
    Parameters
    ----------
    D1 : float
        Diameter of the valve plug bore (must be equal to or smaller than 
        `D2`), [m]
    D2 : float
        Diameter of the pipe attached to the valve, [m]
    angle : float
        Angle formed by the reducer in the valve, [degrees]
    fd : float
        Darcy friction factor calculated for the actual pipe flow in clean 
        steel (roughness = 0.0018 inch) in the fully developed turbulent 
        region [-]
    style : int, optional
        Either 0 (straight-through), 1 (3-way, flow straight-through), or 2 
        (3-way, flow 90°) [-]

    Returns
    -------
    K : float
        Loss coefficient with respect to the pipe inside diameter [-]

    Notes
    -----    
    This method is not valid in the laminar regime and the pressure drop will
    be underestimated in those conditions.

    Examples
    --------
    >>> K_plug_valve_Crane(.01, .02, 50, .025)
    20.100545785228675
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    coeffs = {0: 18, 1: 30, 2: 90}
    beta = D1/D2
    try:
        K = coeffs[style]*fd
    except KeyError:
        raise KeyError('Accepted valve styles are 0 (straight-through), 1 (3-way, flow straight-through), or 2 (3-way, flow 90°)')
    angle = radians(angle)
    if beta == 1:
        return K
    else:
        return (K + 0.5*(sin(angle/2))**0.5 * (1 - beta**2) + (1-beta**2)**2)/beta**4


def v_lift_valve_Crane(rho, D1=None, D2=None, style='swing check angled'):
    r'''Calculates the approximate minimum velocity required to lift the disk 
    or other controlling element of a check valve to a fully open, stable,
    position according to the Crane method [1]_.
    
    .. math::        
        v_{min} = N\cdot \text{m/s} \cdot \sqrt{\frac{\text{kg/m}^3}{\rho}}
    
    .. math::
        v_{min} = N\beta^2 \cdot \text{m/s} \cdot \sqrt{\frac{\text{kg/m}^3}{\rho}}
        
    See the notes for the definition of values of N and which check valves use 
    which formulas.

    Parameters
    ----------
    rho : float
        Density of the fluid [kg/m^3]
    D1 : float, optional
        Diameter of the valve bore (must be equal to or smaller than 
        `D2`), [m]
    D2 : float, optional
        Diameter of the pipe attached to the valve, [m]
    style : str
        The type of valve; one of ['swing check angled', 'swing check straight',
        'swing check UL', 'lift check straight', 'lift check angled', 
        'tilting check 5°', 'tilting check 15°', 'stop check globe 1', 
        'stop check angle 1', 'stop check globe 2',  'stop check angle 2', 
        'stop check globe 3', 'stop check angle 3', 'foot valve poppet disc', 
        'foot valve hinged disc'], [-]

    Returns
    -------
    v_min : float
        Approximate minimum velocity required to keep the disc fully lifted,
        preventing chattering and wear [m/s]

    Notes
    -----
    This equation is not dimensionless.

    +--------------------------+-----+------+
    | Name/string              | N   | Full |
    +==========================+=====+======+
    | 'swing check angled'     | 45  | No   |
    +--------------------------+-----+------+
    | 'swing check straight'   | 75  | No   |
    +--------------------------+-----+------+
    | 'swing check UL'         | 120 | No   |
    +--------------------------+-----+------+
    | 'lift check straight'    | 50  | Yes  |
    +--------------------------+-----+------+
    | 'lift check angled'      | 170 | Yes  |
    +--------------------------+-----+------+
    | 'tilting check 5°'       | 100 | No   |
    +--------------------------+-----+------+
    | 'tilting check 15°'      | 40  | No   |
    +--------------------------+-----+------+
    | 'stop check globe 1'     | 70  | Yes  |
    +--------------------------+-----+------+
    | 'stop check angle 1'     | 95  | Yes  |
    +--------------------------+-----+------+
    | 'stop check globe 2'     | 75  | Yes  |
    +--------------------------+-----+------+
    | 'stop check angle 2'     | 75  | Yes  |
    +--------------------------+-----+------+
    | 'stop check globe 3'     | 170 | Yes  |
    +--------------------------+-----+------+
    | 'stop check angle 3'     | 170 | Yes  |
    +--------------------------+-----+------+
    | 'foot valve poppet disc' | 20  | No   |
    +--------------------------+-----+------+
    | 'foot valve hinged disc' | 45  | No   |
    +--------------------------+-----+------+

    Examples
    --------
    >>> v_lift_valve_Crane(rho=998.2, D1=0.0627, D2=0.0779, style='lift check straight')
    1.0252301935349286
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    specific_volume = 1./rho
    if D1 is not None and D2 is not None:
        beta = D1/D2
        beta2 = beta*beta
    if style == 'swing check angled':
        return 45*specific_volume**0.5
    elif style == 'swing check straight':
        return 75*specific_volume**0.5
    elif style == 'swing check UL':
        return 120*specific_volume**0.5
    elif style == 'lift check straight':
        return 50.*beta2*specific_volume**0.5
    elif style == 'lift check angled':
        return 170.*beta2*specific_volume**0.5
    elif style == 'tilting check 5°':
        return 100*specific_volume**0.5
    elif style == 'tilting check 15°':
        return 40*specific_volume**0.5
    elif style == 'stop check globe 1':
        return 70*beta2*specific_volume**0.5
    elif style == 'stop check angle 1':
        return 95*beta2*specific_volume**0.5
    elif style in ['stop check globe 2', 'stop check angle 2']:
        return 75*beta2*specific_volume**0.5
    elif style in ['stop check globe 3', 'stop check angle 3']:
        return 170*beta2*specific_volume**0.5
    elif style == 'foot valve poppet disc':
        return 20*specific_volume**0.5
    elif style == 'foot valve hinged disc':
        return 45*specific_volume**0.5


branch_converging_Crane_Fs = np.array([1.74, 1.41, 1, 0])
branch_converging_Crane_angles = np.array([30, 45, 60, 90])


def K_branch_converging_Crane(D_run, D_branch, Q_run, Q_branch, angle=90):
    r'''Returns the loss coefficient for the branch of a converging tee or wye
    according to the Crane method [1]_.
    
    .. math::
        K_{branch} = C\left[1 + D\left(\frac{Q_{branch}}{Q_{comb}\cdot 
        \beta_{branch}^2}\right)^2 - E\left(1 - \frac{Q_{branch}}{Q_{comb}}
        \right)^2 - \frac{F}{\beta_{branch}^2} \left(\frac{Q_{branch}}
        {Q_{comb}}\right)^2\right]
            
    .. math::
        \beta_{branch} = \frac{D_{branch}}{D_{comb}}
    
    In the above equation, D = 1, E = 2. See the notes for definitions of F and
    C.

    Parameters
    ----------
    D_run : float
        Diameter of the straight-through inlet portion of the tee or wye [m]
    D_branch : float
        Diameter of the pipe attached at an angle to the straight-through, [m]
    Q_run : float
        Volumetric flow rate in the straight-through inlet of the tee or wye,
        [m^3/s]
    Q_branch : float
        Volumetric flow rate in the pipe attached at an angle to the straight-
        through, [m^3/s]
    angle : float, optional
        Angle the branch makes with the straight-through (tee=90, wye<90)
        [degrees]

    Returns
    -------
    K : float
        Loss coefficient of branch with respect to the velocity and inside 
        diameter of the combined flow outlet [-]

    Notes
    -----
    F is linearly interpolated from the table of angles below. There is no 
    cutoff to prevent angles from being larger or smaller than 30 or 90
    degrees. 

    +-----------+------+
    | Angle [°] |      |
    +===========+======+
    | 30        | 1.74 |
    +-----------+------+
    | 45        | 1.41 |
    +-----------+------+
    | 60        | 1    |
    +-----------+------+
    | 90        | 0    |
    +-----------+------+
    
    If :math:`\beta_{branch}^2 \le 0.35`, C = 1

    If :math:`\beta_{branch}^2 > 0.35` and :math:`Q_{branch}/Q_{comb} > 0.4`,
    C = 0.55.

    If neither of the above conditions are met:
        
    .. math::
        C = 0.9\left(1 - \frac{Q_{branch}}{Q_{comb}}\right)

    Note that there is an error in the text of [1]_; the errata can be obtained 
    here: http://www.flowoffluids.com/publications/tp-410-errata.aspx

    Examples
    --------
    Example 7-35 of [1]_. A DN100 schedule 40 tee has 1135 liters/minute of
    water passing through the straight leg, and 380 liters/minute of water
    converging with it through a 90° branch. Calculate the loss coefficient in
    the branch. The calculated value there is -0.04026.
    
    >>> K_branch_converging_Crane(0.1023, 0.1023, 0.018917, 0.00633)
    -0.04044108513625682
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = (D_branch/D_run)
    beta2 = beta*beta
    Q_comb = Q_run + Q_branch
    Q_ratio = Q_branch/Q_comb
    if beta2 <= 0.35:
        C = 1.
    elif Q_ratio <= 0.4:
        C = 0.9*(1 - Q_ratio)
    else:
        C = 0.55
    D, E = 1., 2.
    F = np.interp(angle, branch_converging_Crane_angles, branch_converging_Crane_Fs)
    K = C*(1. + D*(Q_ratio/beta2)**2 - E*(1. - Q_ratio)**2 - F/beta2*Q_ratio**2)
    return K


run_converging_Crane_Fs = np.array([1.74, 1.41, 1])
run_converging_Crane_angles = np.array([30, 45, 60])

def K_run_converging_Crane(D_run, D_branch, Q_run, Q_branch, angle=90):
    r'''Returns the loss coefficient for the run of a converging tee or wye
    according to the Crane method [1]_.
    
    .. math::
        K_{branch} = C\left[1 + D\left(\frac{Q_{branch}}{Q_{comb}\cdot 
        \beta_{branch}^2}\right)^2 - E\left(1 - \frac{Q_{branch}}{Q_{comb}}
        \right)^2 - \frac{F}{\beta_{branch}^2} \left(\frac{Q_{branch}}
        {Q_{comb}}\right)^2\right]
            
    .. math::
        \beta_{branch} = \frac{D_{branch}}{D_{comb}}
    
    In the above equation, C=1, D=0, E=1. See the notes for definitions of F 
    and also the special case of 90°.

    Parameters
    ----------
    D_run : float
        Diameter of the straight-through inlet portion of the tee or wye
        [m]
    D_branch : float
        Diameter of the pipe attached at an angle to the straight-through, [m]
    Q_run : float
        Volumetric flow rate in the straight-through inlet of the tee or wye,
        [m^3/s]
    Q_branch : float
        Volumetric flow rate in the pipe attached at an angle to the straight-
        through, [m^3/s]
    angle : float, optional
        Angle the branch makes with the straight-through (tee=90, wye<90)
        [degrees]

    Returns
    -------
    K : float
        Loss coefficient of run with respect to the velocity and inside 
        diameter of the combined flow outlet [-]

    Notes
    -----
    F is linearly interpolated from the table of angles below. There is no 
    cutoff to prevent angles from being larger or smaller than 30 or 60
    degrees. The switch to the special 90° happens at 75°.

    +-----------+------+
    | Angle [°] |      |
    +===========+======+
    | 30        | 1.74 |
    +-----------+------+
    | 45        | 1.41 |
    +-----------+------+
    | 60        | 1    |
    +-----------+------+
    
    For the special case of 90°, the formula used is as follows. 
        
    .. math::
        K_{run} = 1.55\left(\frac{Q_{branch}}{Q_{comb}} \right)
        - \left(\frac{Q_{branch}}{Q_{comb}}\right)^2
    
    Examples
    --------
    Example 7-35 of [1]_. A DN100 schedule 40 tee has 1135 liters/minute of
    water passing through the straight leg, and 380 liters/minute of water
    converging with it through a 90° branch. Calculate the loss coefficient in
    the run. The calculated value there is 0.03258.
    
    >>> K_run_converging_Crane(0.1023, 0.1023, 0.018917, 0.00633)
    0.32575847854551254
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = (D_branch/D_run)
    beta2 = beta*beta
    Q_comb = Q_run + Q_branch
    Q_ratio = Q_branch/Q_comb
    if angle < 75.:
        C = 1
    else:
        return 1.55*(Q_ratio) - Q_ratio*Q_ratio

    D, E = 0, 1
    F = np.interp(angle, run_converging_Crane_angles, run_converging_Crane_Fs)
    K = C*(1. + D*(Q_ratio/beta2)**2 - E*(1. - Q_ratio)**2 - F/beta2*Q_ratio**2)
    return K


def K_branch_diverging_Crane(D_run, D_branch, Q_run, Q_branch, angle=90):
    r'''Returns the loss coefficient for the branch of a diverging tee or wye
    according to the Crane method [1]_.
    
    .. math::
        K_{branch} = G\left[1 + H\left(\frac{Q_{branch}}{Q_{comb}
        \beta_{branch}^2}\right)^2 - J\left(\frac{Q_{branch}}{Q_{comb}
        \beta_{branch}^2}\right)\cos\theta\right]
            
    .. math::
        \beta_{branch} = \frac{D_{branch}}{D_{comb}}
    
    See the notes for definitions of H, J, and G.

    Parameters
    ----------
    D_run : float
        Diameter of the straight-through inlet portion of the tee or wye [m]
    D_branch : float
        Diameter of the pipe attached at an angle to the straight-through, [m]
    Q_run : float
        Volumetric flow rate in the straight-through outlet of the tee or wye,
        [m^3/s]
    Q_branch : float
        Volumetric flow rate in the pipe attached at an angle to the straight-
        through, [m^3/s]
    angle : float, optional
        Angle the branch makes with the straight-through (tee=90, wye<90)
        [degrees]

    Returns
    -------
    K : float
        Loss coefficient of branch with respect to the velocity and inside 
        diameter of the combined flow inlet [-]

    Notes
    -----
    If :math:`\beta_{branch} = 1, \theta = 90^\circ`, H = 0.3 and J = 0. 
    Otherwise H = 1 and J = 2.
    
    G is determined according to the following pseudocode:
        
    .. code-block:: python
    
        if angle < 75:
            if beta2 <= 0.35:
                if Q_ratio <= 0.4:
                    G = 1.1 - 0.7*Q_ratio
                else:
                    G = 0.85
            else:
                if Q_ratio <= 0.6:
                    G = 1.0 - 0.6*Q_ratio
                else:
                    G = 0.6
        else:
            if beta2 <= 2/3.:
                G = 1
            else:
                G = 1 + 0.3*Q_ratio*Q_ratio

    Note that there are several errors in the text of [1]_; the errata can be  
    obtained here: http://www.flowoffluids.com/publications/tp-410-errata.aspx

    Examples
    --------
    Example 7-36 of [1]_. A DN150 schedule 80 wye has 1515 liters/minute of
    water exiting the straight leg, and 950 liters/minute of water
    exiting it through a 45° branch. Calculate the loss coefficient in
    the branch. The calculated value there is 0.4640.
    
    >>> K_branch_diverging_Crane(0.146, 0.146, 0.02525, 0.01583, angle=45)
    0.4639895627496694
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = (D_branch/D_run)
    beta2 = beta*beta
    Q_comb = Q_run + Q_branch
    Q_ratio = Q_branch/Q_comb

    if angle < 60 or beta <= 2/3.:
        H, J = 1., 2.
    else:
        H, J = 0.3, 0
    if angle < 75:
        if beta2 <= 0.35:
            if Q_ratio <= 0.4:
                G = 1.1 - 0.7*Q_ratio
            else:
                G = 0.85
        else:
            if Q_ratio <= 0.6:
                G = 1.0 - 0.6*Q_ratio
            else:
                G = 0.6
    else:
        if beta2 <= 2/3.:
            G = 1
        else:
            G = 1 + 0.3*Q_ratio*Q_ratio
    angle_rad = radians(angle)
    K_branch = G*(1 + H*(Q_ratio/beta2)**2 - J*(Q_ratio/beta2)*cos(angle_rad))
    return K_branch


def K_run_diverging_Crane(D_run, D_branch, Q_run, Q_branch, angle=90):
    r'''Returns the loss coefficient for the run of a converging tee or wye
    according to the Crane method [1]_.
    
    .. math::
        K_{run} = M \left(\frac{Q_{branch}}{Q_{comb}}\right)^2
            
    .. math::
        \beta_{branch} = \frac{D_{branch}}{D_{comb}}
    
    See the notes for the definition of M.

    Parameters
    ----------
    D_run : float
        Diameter of the straight-through inlet portion of the tee or wye [m]
    D_branch : float
        Diameter of the pipe attached at an angle to the straight-through, [m]
    Q_run : float
        Volumetric flow rate in the straight-through outlet of the tee or wye,
        [m^3/s]
    Q_branch : float
        Volumetric flow rate in the pipe attached at an angle to the straight-
        through, [m^3/s]
    angle : float, optional
        Angle the branch makes with the straight-through (tee=90, wye<90)
        [degrees]

    Returns
    -------
    K : float
        Loss coefficient of run with respect to the velocity and inside 
        diameter of the combined flow inlet [-]

    Notes
    -----
    M is calculated according to the following pseudocode:
        
    .. code-block:: python

        if beta*beta <= 0.4:
            M = 0.4
        elif Q_branch/Q_comb <= 0.5:
            M = 2*(2*Q_branch/Q_comb - 1)
        else:
            M = 0.3*(2*Q_branch/Q_comb - 1)

    Examples
    --------
    Example 7-36 of [1]_. A DN150 schedule 80 wye has 1515 liters/minute of
    water exiting the straight leg, and 950 liters/minute of water
    exiting it through a 45° branch. Calculate the loss coefficient in
    the branch. The calculated value there is -0.06809.
    
    >>> K_run_diverging_Crane(0.146, 0.146, 0.02525, 0.01583, angle=45)
    -0.06810067607153049
    
    References
    ----------
    .. [1] Crane Co. Flow of Fluids Through Valves, Fittings, and Pipe. Crane,
       2009.
    '''
    beta = (D_branch/D_run)
    beta2 = beta*beta
    Q_comb = Q_run + Q_branch
    Q_ratio = Q_branch/Q_comb
    if beta2 <= 0.4:
        M = 0.4
    elif Q_ratio <= 0.5:
        M = 2.*(2.*Q_ratio - 1.)
    else:
        M = 0.3*(2.*Q_ratio - 1.)
    return M*Q_ratio*Q_ratio


