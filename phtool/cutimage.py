# -*- coding: utf-8 -*-


"""
根据给定的区域，截取图像并保存
这里复用disp的show_x/y参数
add: 2026-04-24
"""


def cutimage(
    filelist,
    out_dir="./",
    cut_x=None,
    cut_y=None,
    cut_w=None,
    cut_h=None,
):
    """
    找源
    :param filelist: 待显示的文件列表（实际上只显示第一张）
    :param out_dir: 输出目录（默认当前目录）
    :param cut_x: 截取图像的x范围（默认None）
    :param cut_y: 截取图像的y范围（默认None）
    :param cut_w: 截取图像的宽度（默认None）
    :param cut_h: 截取图像的高度（默认None）
    :return: None
    """

    from .util import filename_split, pkl_dump, pkl_load
    import numpy as np
    import logging
    import astropy.io.fits as fits
    import os
    import glob
    # 复用disp的_size_range_函数
    from .disp import _size_range_

    logger = logging.getLogger("phtool_main")
    # 逐个进行平场改正
    os.makedirs(out_dir, exist_ok=True)
    maxn = max(len(fn) for fn in filelist)
    for f in filelist:
        # 读取文件
        with fits.open(f, verify="ignore") as hdul:
            hdul[0].verify("fix")
            dat = hdul[0].data
            hdr = hdul[0].header
        
        # 裁剪范围
        ny, nx = dat.shape
        x0, x1 = _size_range_(cut_x, nx)
        y0, y1 = _size_range_(cut_y, ny)
        x0, x1, y0, y1 = round(x0), round(x1), round(y0), round(y1)
        # 如果开始点是0，那么应该是1，表示从头开始截取
        x0 = 1 if x0 == 0 else x0
        y0 = 1 if y0 == 0 else y0
        # 如果单独提供了宽度、高度，那么上面算出的右/上边界忽略，只取指定宽度、高度
        x1 = min(x0+cut_w, nx+1) if cut_w else x1
        y1 = min(y0+cut_h, ny+1) if cut_h else y1
        # 如果边界颠倒，那么交换边界
        x0, x1 = (x0, x1) if x0 < x1 else (x1, x0)
        y0, y1 = (y0, y1) if y0 < y1 else (y1, y0)

        # 裁剪图像，这里坐标从1开始，需要调整成从0开始的
        dat_cut = dat[y0-1:y1-1, x0-1:x1-1]

        # 新文件名
        p, fn, suff, e = filename_split(f)
        f_cut = os.path.join(out_dir, fn+""+e)
        fits.writeto(f_cut, dat_cut, hdr, overwrite=True)
        logger.info(f"Cut {fn:{maxn}s} [{nx},{ny}] -> [{x0:4d}~{x1:4d}] [{y0:4d}~{y1:4d}]")

    return
