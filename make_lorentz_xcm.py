#! /usr/bin/env python3

import sys
from argparse import ArgumentParser

linelist = {
"FeKa":[
[6404.148,1.613,0.278],
[6391.19,2.487,0.207],
[6403.295,1.965,0.182],
[6389.106,4.433,0.066],#modified from [6389.106,2.339,0.066],
[6400.653,4.833,0.106],
[6390.275,2.339,0.065],#modified from [6390.275,4.433,0.065],
[6402.077,2.803,0.094]
],
"FeKb":[
[7046.9,14.17,0.301],
[7057.21,3.12,0.279],
[7058.36,1.97,0.241],
[7054.75,6.38,0.179]
],
"NiKa":[
[7478.281,2.013,0.487],
[7461.131,2.674,0.25],
[7476.529,4.711,0.171],
[7459.874,3.039,0.064],
[7458.029,4.476,0.028]
],
#Holzer
#"MnKa":[
#[5898.853,1.715,0.353],
#[5887.743,2.361,0.229],
#[5897.867,2.043,0.141],
#[5886.495,4.216,0.11],
#[5894.829,4.499,0.079],
#[5896.532,2.663,0.066],
#[5899.417,0.969,0.005]
#],
#$CALDB/data/gen/bcf/ah_gen_linefit_20140101v003
"MnKa":[
[5898.882,1.7145,0.3523],
[5897.898,2.0442,0.1409],
[5894.864,4.4985,0.07892],
[5896.566,2.6616,0.06624],
[5899.444,0.97669,0.01818],
[5902.712,1.5528,0.004475],
[5887.772,2.3604,0.2283],
[5886.528,4.216,0.1106]
],
"CrKa":[
[5414.874,1.457,0.378],
[5405.551,2.224,0.271],
[5414.099,1.76,0.132],
[5403.986,4.74,0.054],
[5412.745,3.138,0.084],
[5410.583,5.149,0.073],
[5418.304,1.988,0.009]
],
"CoKa":[
[6930.425,1.795,0.378],
[6915.713,2.406,0.197],
[6929.388,2.695,0.144],
[6914.659,2.773,0.095],
[6927.676,4.555,0.127],
[6913.078,4.463,0.05],
[6930.941,0.808,0.088]
],
"CuKa":[
[8047.837,2.285,0.579],
[8027.993,2.666,0.236],
[8045.367,3.358,0.08],
[8026.504,3.571,0.105]
],
"CrKb":[
[5947,1.7,0.307],
[5935.31,15.98,0.236],
[5946.24,1.9,0.172],
[5942.04,6.69,0.148],
[5944.93,3.37,0.137]
],
"MnKb":[
[6490.89,1.83,0.254],
[6486.31,9.4,0.234],
[6477.73,13.22,0.234],
[6490.06,1.81,0.164],
[6488.83,2.81,0.114]
],
"CoKb":[
[7649.6,3.05,0.449],
[7647.83,3.58,0.189],
[7639.87,9.78,0.153],
[7645.49,4.89,0.103],
[7636.21,13.59,0.082],
[7654.13,3.79,0.025]
],
"NiKb":[
[8265.01,3.76,0.45],
[8263.01,4.34,0.258],
[8256.67,13.7,0.203],
[8268.7,5.18,0.089]
],
"CuKb":[
[8905.532,3.52,0.485],
[8903.109,3.52,0.248],
[8908.462,3.55,0.11],
[8897.387,8.08,0.1],
[8911.393,5.31,0.055]
]
}

xcm = """#PyXspec: Output generated from Xset.save().  DO NOT MODIFY.

statistic cstat

method leven 10 0.01
abund angr
xsect vern
cosmo 70 0 0.73
xset delta 0.01
systematic 0
model  powerlaw + zashift(zashift(gsmooth(lorentz)*constant))
            2.0          1        1.0        1.0        3.0        3.0
           0.01       0.01          0          0      1e+20      1e+24
              0      -0.01       -1.0       -1.0         10         10
              0       0.01       -1.0       -1.0         10         10
          0.001       0.05          0          0         10         20
              0      -0.01         -1         -1          1          1
          0.001       0.01          0          0      1e+10      1e+10
bayes off
"""

def get_argument():
    argparser = ArgumentParser(description='This program makes the line profile XCM file.')
    argparser.add_argument('-l', '--line', default='FeKa', help='Line name: FeKa, NiKa, MnKa, CrKa, CoKa, CuKa, or Kb lines')
    return argparser.parse_args()

def modify_lorentz(line):
    lines = linelist[line]
    num_lorentz = len(lines)
    file_content = xcm
    lorentz_list = " + ".join(["lorentz"] * num_lorentz)

    new_content = file_content.replace("lorentz)", f"{lorentz_list})")
    new_contents = new_content.split("\n")
    for i in range(num_lorentz):
        energy, width, norm = lines[i]
        new_contents.insert(-3,
        '{0:>12}e-3      -0.05          0          0      1e+06      1e+06'.format(energy)
         )
        new_contents.insert(-3,
        '{0:>12}e-3      -0.05          0          0         10         20'.format(width)
        )
        new_contents.insert(-3,
        '{0:>15}      -0.01          0          0      1e+20      1e+24'.format(norm)
        )
    new_content = "\n".join(new_contents)
    output_file = "fit_lorentz_" + line + ".xcm"
    with open(output_file, mode='w') as f:
        f.write(new_content)

if __name__ == "__main__":
    args = get_argument()

    line = args.line

    modify_lorentz(line)
