# -*- coding: utf-8 -*-


"""
实现图像的平移对齐
"""


def align(
    filelist, 
    alignfile,
    baseix=0,
    whenexist="autonum",
):
    """
    图像对齐
    :param filelist: 待对齐的文件列表
    :param alignfile: 偏移文件
    :param baseix: 基准图像索引
    :param whenexist: 当输出文件存在时怎么处理
    :return: 无
    """

    from .util import filename_split, change_suffix, pkl_dump, pkl_load
    import numpy as np
    import logging
    import astropy.io.fits as fits
    import os
    import astroalign as aa
    import qmatch
    from astropy.stats import sigma_clipped_stats

    logger = logging.getLogger("phtool_main")
    # 选多少星进行处理
    ngood = 100
    # load base image
    b_fn, b_star_file = change_suffix(filelist[baseix], "_stars", ".pkl")
    if not os.path.exists(b_star_file):
        logger.error(f"Base catalog {b_star_file} not found.")
        return
    logger.debug(f"Loading base cstalog: {b_star_file}")
    b_cat, _, _ = pkl_load(b_star_file)
    b_ix = np.argsort(b_cat["mag"])
    b_xy = np.c_[b_cat["xcentroid"], b_cat["ycentroid"]][b_ix[:ngood], :]
    b_mag = b_cat["mag"][b_ix[:ngood]]
    # 文件数
    nf = len(filelist)

    # xy offset array
    trans = [None] * nf
    bjd = np.empty(nf)
    mag_diff_med = np.empty(nf)
    mag_diff_std = np.empty(nf)
    
    # 文件名的最大宽度，仅用于确保输出整齐
    maxn = max(len(filename_split(f)[1]) for f in filelist)

    logger.debug(f"{'i':>3s}/{'N':<3s} {'Filename':>{maxn}s}: {'BJD-2450000':>13s} "
                   f"{'Rot':>5s} {'Scale':>5s}({'Trans-X/Y':^15s}) "
                   f"{'MagDiff':10s}")

    # load images and process
    for k, fc in enumerate(filelist):
        # process data
        bf, k_star_file = change_suffix(fc, "_stars", ".pkl")
        if not os.path.exists(k_star_file):
            logger.error(f"Catalog {k_star_file} not found.")
            continue
        k_cat, _, _ = pkl_load(k_star_file)
        k_ix = np.argsort(k_cat["mag"])
        k_xy = np.c_[k_cat["xcentroid"], k_cat["ycentroid"]][k_ix[:ngood], :]
        k_mag = k_cat["mag"][k_ix[:ngood]]
        # mjd of obs
        bjd[k] = fits.getval(fc, "BJD")
        try:
            tr, (k_xym, b_xym) = aa.find_transform(k_xy, b_xy)
            # 找出匹配到的源是原始源的哪一些
            k_ix, k_ixm = qmatch.match2d(k_xy[:, 0], k_xy[:, 1], k_xym[:, 0], k_xym[:, 1], 0.1)
            b_ix, b_ixm = qmatch.match2d(b_xy[:, 0], b_xy[:, 1], b_xym[:, 0], b_xym[:, 1], 0.1)
            # 做下标转换，找到对应原始源的下标
            k0 = np.zeros(len(k_ix), int)
            b0 = np.zeros(len(b_ix), int)
            k0[k_ixm] = b_ix
            b0[b_ixm] = k_ix
            # 计算零点差    
            mag_diff = b_mag[b0] - k_mag[k0]
            mag_diff_med[k], _, mag_diff_std[k] = sigma_clipped_stats(mag_diff)
        except:
            logger.error(f"{k+1:03d}/{nf:03d}: Failed to align {bf}")
            tr = None
            bjd[k] = np.nan
            mag_diff_med[k] = np.nan
            mag_diff_std[k] = np.nan
            continue
        trans[k] = tr

        logger.debug(f"{k+1:03d}/{nf:03d} {bf:{maxn}s}: {bjd[k]-2450000:13.7f} "
                   f"{tr.rotation:+5.1f} {tr.scale:4.2f} ({tr.translation[0]:+7.1f} {tr.translation[1]:+7.1f}) "
                   f"{mag_diff_med[k]:+6.2f}+-{mag_diff_std[k]:5.3f}")

    # 保存align数据
    pkl_dump(alignfile, bjd, trans, filelist, b_fn, mag_diff_med, mag_diff_std)
    logger.debug(f"Writing {alignfile}")
