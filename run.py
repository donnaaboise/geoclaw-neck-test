#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Run all cases.
"""
import os
import sys
import logging


# logger
logger = logging.getLogger("run.py")
logger.setLevel(logging.DEBUG)

# log message to std io
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# file log
fh = logging.FileHandler("neck_test_run.log", "w", "utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))

# add handlers to the logger
logger.addHandler(ch)
logger.addHandler(fh)


def create_data(casepath):
    """Create *.data files in a case folder."""

    if not os.path.isdir(casepath):
        logger.error("Case folder %s not found.", casepath)
        raise FileNotFoundError("Case folder {} not found.".format(casepath))

    setrunpath = os.path.join(casepath, "setrun.py")
    if not os.path.isfile(setrunpath):
        logger.error("Case folder %s does not have setrun.py.", casepath)
        raise FileNotFoundError("Case folder {} does not have setrun.py.".format(casepath))

    pwd = os.getcwd() # get current working directory
    os.chdir(casepath) # go to case folder


    if casepath != sys.path[0]:
        sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py
    rundata = setrun.setrun() # get ClawRunData object
    rundata.write() # write *.data to the case folder
    del rundata
    del sys.modules["setrun"]
    del sys.path[0]

    os.chdir(pwd) # go back to pwd

def run_case(solver, casepath):
    """Run a single case with specified solver."""
    import shutil
    import glob
    import subprocess

    solver = os.path.abspath(solver)
    casepath = os.path.abspath(casepath)
    out_path = os.path.join(casepath, "_output")

    logger.info("Preparing to run case %s", casepath)
    if os.path.isdir(out_path):

        # if casepath not in sys.path, add it
        if casepath != sys.path[0]:
            print(sys.path[0])
            sys.path.insert(0, casepath) # add case folder to module search path
        print(sys.path[0])

        # get rundata
        import setrun
        rundata = setrun.setrun()
        nframes = rundata.clawdata.num_output_times+1
        del rundata
        del sys.modules["setrun"]
        del sys.path[0]

        nfiles = [
            len(glob.glob(os.path.join(out_path, "fort.t"+"[0-9]"*4))),
            len(glob.glob(os.path.join(out_path, "fort.a"+"[0-9]"*4))),
            len(glob.glob(os.path.join(out_path, "fort.b"+"[0-9]"*4))),
            len(glob.glob(os.path.join(out_path, "fort.q"+"[0-9]"*4)))]

        # check if this case is already completed
        if all([n == nframes for n in nfiles]):
            logger.warning("Case %s seems to be already done. Skip it", casepath)
            return

        logger.warning("Case %s is not complete. Remove outputs and re-run.", casepath)
        shutil.rmtree(out_path)

    # make the output folder
    os.makedirs(out_path)

    # copy data files to output folder
    datafiles = glob.glob(os.path.join(casepath, "*.data"))
    for datafile in datafiles:
        base = os.path.basename(datafile)
        shutil.copyfile(datafile, os.path.join(out_path, base))

    # change directory to output directory
    orig_dir = os.getcwd()
    os.chdir(out_path)

    # run simulation
    logger.info("Runngin case %s", casepath)
    logger.info("STDOUT is redirected to %s", os.path.join(casepath, "stdout.txt"))
    logger.info("STDERR is redirected to %s", os.path.join(casepath, "stderr.txt"))
    stdout = open(os.path.join(casepath, "stdout.txt"), "w")
    stderr = open(os.path.join(casepath, "stderr.txt"), "w")

    job = subprocess.run([solver], stdout=stdout, stderr=stderr)

    stdout.close()
    stderr.close()

    try:
        job.check_returncode()
    except subprocess.CalledProcessError:
        logger.error(job.stderr.decode("UTF-8"))
        logger.error("Simulation case %s failed. Exit.", casepath)
        raise

    logger.info("Finished case %s", casepath)

    # go back to the original directory
    os.chdir(orig_dir)

def run_all():
    """Run all cases."""

    # paths
    repo_path = os.path.dirname(os.path.abspath(__file__))
    claw_path = os.path.join(repo_path, "src", "clawpack-v5.5.0")

    # add environment variables
    os.environ["CLAW"] = claw_path

    # add clawpack python package search path
    if claw_path != sys.path[0]:
        sys.path.insert(0, claw_path)

    # cases and corresponding solvers
    solver_cases = {
        "xgeoclaw.update": ["amr-tests/fix_update"],
        "xgeoclaw.flag2refine2": ["amr-tests/fix_flag2refine2"],
        "xgeoclaw.update_and_flag2refine2": ["amr-tests/fix_update_and_flag2refine2"],
        "xgeoclaw.original": [
            "amr-tests/original",
            "single-mesh-tests/dx=4",
            "single-mesh-tests/dx=2",
            "single-mesh-tests/dx=1",
            "single-mesh-tests/dx=0.5",
            "single-mesh-tests/dx=0.25",
            "single-mesh-tests/dx=0.125"]}

    for solver, cases in solver_cases.items():
        for case in cases:
            solver = os.path.join(repo_path, "bin", solver)
            case = os.path.join(repo_path, case)

            # create *.data files
            create_data(case)

            # run simulation
            run_case(solver, case)

if __name__ == "__main__":
    run_all()
