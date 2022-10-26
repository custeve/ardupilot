#!/usr/bin/env python

import sys, random, os, time, multiprocessing, subprocess
from pymavlink import mavutil
from MAVProxy.modules.lib import grapher
import common

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)

parser.add_argument("--newer", action='store_true')
parser.add_argument("--parallel", default=6, type=int)
parser.add_argument("--mission", type=int, default=0)
parser.add_argument("files", type=str, nargs='+', help="input files")
args = parser.parse_args()

files = list(dict.fromkeys(args.files))
nfiles = len(files)

if args.mission >= 6:
    kmz = "missions/high.kmz"
    fence = "missions/high.fence"
else:
    kmz = "missions/low.kmz"
    fence = "missions/low.fence"

graphed = set()

graphs = [
    ('TECS Speed', 'SL2.KEAS<KEAS> knots(TECS.spdem)/CTUN.E2T<KEAS_Target> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Attitude Control', 'ATT.Roll ATT.Pitch ATT.DesRoll ATT.DesPitch feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Speeds', 'SL2.KEAS<KEAS> SL2.KTAS<KTAS> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Surfaces Deg', 'SL2.Elev<Elevator(deg)> SL2.Ail<Aileron(deg)> SL2.Rud<Rudder(deg)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Surfaces PWM', 'RCOU.C3<Elevator(PWM)> RCOU.C4<Rudder(PWM)> RCOU.C2<AileronLeft(PWM)> RCOU.C5<AileronRight(PWM)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Angle of Attack', 'SL2.AoA<AoA(deg)> SL2.SSA<SSA(deg)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('G-Force', 'IMU.AccZ<AccelZ(m/s/s)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Distance To Home', 'distance_lat_lon(GPS.Lat,GPS.Lng,34.905429,-117.883702)/1852.0<DistToHome(nm)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Air Density', 'SLD.AD<AirDensity(kg/m^3)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Dynamic Pressure', 'SLD.q<DynamicPressure(Pa)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Lift/Drag', 'SLD.LD<Lift/Drag> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('RollRates', 'PIDR.Act<RollRate(deg/s)> PIDR.Tar<RollRateTarget(deg/s)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('PitchRates', 'PIDP.Act<PitchRate(deg/s)> PIDP.Tar<PitchRateTarget(deg/s)> feet(GPS.Alt):2<AltAMSL(Ft)>'),
    ('Attitude (pullup)', 'ATT.Roll{CMD.CNum<7}<Roll(deg)> ATT.Pitch{CMD.CNum<7}<Pitch(deg)> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
    ('Speeds (pullup)', 'SL2.KEAS{CMD.CNum<7}<KEAS> SL2.KTAS{CMD.CNum<7}<KTAS> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
    ('Surfaces Deg (pullup)', 'SL2.Elev{CMD.CNum<7}<Elevator(deg)> SL2.Ail{CMD.CNum<7}<Aileron(deg)> SL2.Rud{CMD.CNum<7}<Rudder(deg)> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
    ('Surfaces PWM (pullup)', 'RCOU.C3{CMD.CNum<7}<Elevator(PWM)> RCOU.C4{CMD.CNum<7}<Rudder(PWM)> RCOU.C2{CMD.CNum<7}<AileronLeft(PWM)> RCOU.C5{CMD.CNum<7}<AileronRight(PWM)> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
    ('Angle of Attack (pullup)', 'SL2.AoA{CMD.CNum<7}<AOA(deg)> SL2.SSA{CMD.CNum<7}<SSA(deg)> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
    ('G-Force (pullup)', 'IMU.AccZ{CMD.CNum<7}<AccelZ(m/s/s)> feet(GPS.Alt){CMD.CNum<7}:2<AltAMSL(Ft)>'),
]

def graph_one(mlog, title, expression, filename):
    '''create one graph'''
    print("Graphing %s to %s" % (title, filename))
    mg = grapher.MavGraph()
    mg.add_mav(mlog)
    for e in expression.split():
        mg.add_field(e)
    mg.set_title(title)
    mg.process([],[],0)
    mg.set_grid(True)
    mg.show(1, output=filename)

def script_path():
    '''path of this script'''
    import inspect
    return os.path.abspath(inspect.getfile(inspect.currentframe()))

def process_one(fname):
    '''process one file'''
    html = fname + ".html"
    print("Graphing %s %u/%u" % (fname, len(graphed), len(files)))

    tmp = html+".tmp"+str(random.randint(0,100000))
    tmpg = tmp+".png"
    try:
        os.unlink(tmp)
    except Exception:
        pass
    try:
        os.unlink(tmpg)
    except Exception:
        pass

    bname = os.path.basename(fname)
    bname2 = bname[:8]
    dname = os.path.dirname(fname)
    f = open(tmp, "w")
    f.write("<html><head><title>Graphs of %s</title><body>\n" % bname)
    f.write("<h1>Graphs of log %s</h1>\n" % bname)
    f.write('Logfile: <a href="%s" target="_blank">%s</a><br>\n' % (bname, bname))
    f.write("<pre>")
    proc = subprocess.Popen("mavflighttime.py %s | egrep '^Flig|^Total.dist'" % fname, shell=True, stdout=subprocess.PIPE)
    f.write(str(proc.stdout.read()))
    f.write("</pre><p>")

    map_log = "%s/%s.bin" % (dname, bname2)
    map_img = "%s-map.png" % bname
    map_img2 = "%s-map2.png" % bname

    os.system("mavflightview.py --imagefile=%s/%s --fence %s %s" % (dname, map_img, fence, map_log))
    os.system("mavflightview.py --imagefile=%s/%s --fence %s --fencebounds %s" % (dname, map_img2, fence, map_log))
    f.write('<hr><p><table><tr><td><img src="%s"></td><td><img src="%s"></td></tr></table><p>\n' % (map_img, map_img2))

    mlog = mavutil.mavlink_connection(fname)
    idx = 0
    for (title, expression) in graphs:
        idx += 1
        if os.path.exists(tmpg):
            os.unlink(tmpg)
        p = multiprocessing.Process(target=graph_one, args=(mlog, title, expression, tmpg))
        p.start()
        p.join()
        if os.path.exists(tmpg):
            os.rename(tmpg, "%s/%s-g%u.png" % (dname, bname, idx))
            png_name = "%s-g%u.png" % (bname, idx)
            f.write('<a href="%s"><img src="%s" width=1035 height=527></a><p>\n' % (png_name, png_name))
    f.write("</body>\n")
    f.close()
    if os.path.exists(tmp):
        try:
            os.unlink(html)
        except Exception:
            pass
        os.rename(tmp, html)

def is_done(fname):
    '''check if already done'''
    return False

files2 = []
for f in files:
    if os.path.getsize(f) == 0:
        continue
    if not is_done(f + ".html"):
        files2.append(f)
files = files2
nfiles = len(files2)

procs = []

while len(graphed) < nfiles:
    r = random.randint(0, nfiles-1)
    fname = files[r]
    if fname in graphed:
        continue
    graphed.add(fname)
    html = fname + ".html"
    if is_done(html):
        continue
    p = multiprocessing.Process(target=process_one, args=(fname,))
    p.start()
    procs.append(p)
    while len(procs) >= args.parallel:
        for p in procs:
            if p.exitcode is not None:
                p.join()
                procs.remove(p)
        time.sleep(0.1)
