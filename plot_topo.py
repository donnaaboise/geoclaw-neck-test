#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Plot 2D and 3D topo and save to figs.
"""
import os
import numpy
import matplotlib
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D


def get_Z_and_extent(topofile):
    """Get data from an ESRI ASCII file."""

    f = open(topofile, "r")

    ncols = int(f.readline().split()[1])
    nrows = int(f.readline().split()[1])
    xllcorner = float(f.readline().split()[1])
    yllcorner = float(f.readline().split()[1])
    cellsize = float(f.readline().split()[1])
    nodatavalue = float(f.readline().split()[1])

    data = numpy.zeros((nrows, ncols), dtype=numpy.float64)
    for i in range(nrows):
        data[i, :] = f.readline().strip().split()

    f.close()

    extent = [xllcorner, xllcorner+ncols*cellsize,
              yllcorner, yllcorner+nrows*cellsize]

    return data, extent

def plot_2d_topo(Z, extent):
    """Plot 2D topography."""

    # paths
    repo_path = os.path.dirname(os.path.abspath(__file__))
    figs_path = os.path.join(repo_path, "figs")

    fig = pyplot.figure(figsize=(8, 4), dpi=100)
    main_ax = fig.add_axes([0.1, 0.24, 0.8, 0.66])
    main_ax.imshow(
        Z, cmap=pyplot.get_cmap("terrain"),
        vmin=Z.min(), vmax=Z.max(), extent=extent)
    main_ax.set_xlim(extent[0], extent[1])
    main_ax.set_ylim(extent[2], extent[3])
    main_ax.set_xlabel("x (m)")
    main_ax.set_ylabel("y (m)")
    cbar_ax = fig.add_axes([0.16, 0.11, 0.68, 0.025])
    cbar = matplotlib.colorbar.ColorbarBase(
        cbar_ax, cmap=pyplot.get_cmap("terrain"), orientation="horization",
        norm=matplotlib.colors.Normalize(vmin=Z.min(), vmax=Z.max()),
        ticklocation="bottom")
    cbar.set_label("Elevation (m)")
    fig.suptitle(
        "Topography", x=0.5, y=0.92, fontsize=12,
        horizontalalignment="center", verticalalignment="bottom")
    fig.savefig(
        os.path.join(figs_path, "topo_2d.png"), dpi="figure", bbox_inches="tight")

def plot_3d_topo(Z, extent):
    """Plot 3D topology."""

    # paths
    repo_path = os.path.dirname(os.path.abspath(__file__))
    figs_path = os.path.join(repo_path, "figs")

    nrows, ncols = Z.shape
    dx = (extent[1] - extent[0]) / ncols
    dy = (extent[3] - extent[2]) / nrows

    X, Y = numpy.meshgrid(
        numpy.linspace(extent[0]+dx/2, extent[1]-dx/2, ncols),
        numpy.linspace(extent[2]+dy/2, extent[3]-dy/2, nrows))

    fig = pyplot.figure(figsize=(9, 7), dpi=100)
    main_ax = fig.add_axes([0.05, 0.2, 0.85, 0.7], projection="3d")
    main_ax.contourf3D(
        X, Y, Z, levels=512, cmap=pyplot.get_cmap("terrain"),
        alpha=0.5)
    main_ax.set_xlim(extent[0], extent[1])
    main_ax.set_ylim(extent[2], extent[3])
    main_ax.set_zlim(Z.min(), Z.max())
    main_ax.set_xlabel("x (m)")
    main_ax.set_ylabel("y (m)")
    main_ax.set_zlabel("elevation (m)")
    main_ax.axis('equal')
    main_ax.set_axis_off()
    main_ax.set_frame_on(False)
    main_ax.view_init(30, -134)
    cbar_ax = fig.add_axes([0.16, 0.11, 0.68, 0.025])
    cbar = matplotlib.colorbar.ColorbarBase(
        cbar_ax, cmap=pyplot.get_cmap("terrain"), orientation="horization",
        norm=matplotlib.colors.Normalize(vmin=9, vmax=30),
        ticklocation="bottom")
    cbar.set_label("Elevation (m)")
    fig.suptitle(
        "Topography", x=0.5, y=0.92, fontsize=12,
        horizontalalignment="center", verticalalignment="bottom")
    fig.savefig(
        os.path.join(figs_path, "topo_3d.png"), dpi="figure", bbox_inches="tight")

if __name__ == "__main__":

    # paths
    repo_path = os.path.dirname(os.path.abspath(__file__))
    topofile = os.path.join(repo_path, "topodata", "topo.asc")

    topo, extent = get_Z_and_extent(topofile)
    plot_2d_topo(topo, extent)
    plot_3d_topo(topo, extent)
