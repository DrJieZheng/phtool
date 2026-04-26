# -*- coding: utf-8 -*-


"""
显示图像，并根据需要截取部分区域，进行人工选星
add: 2026-04-08
"""


def _size_range_(p, size):
    """
    计算显示范围的索引
    :param p: 输入的显示范围，None/单值/双值
    :param size: 图像大小
    :return: 显示范围
    """
    # 先把p规范化，确保是两个元素的列表，对于单元素，右侧按负值处理
    if p is None:
        r = [0, 1]
    elif isinstance(p, (list, tuple)):
        r = p[:2] if len(p) >= 2 else ([p[0], -p[0]] if len(p) == 1 else [0, 1])
    else:
        r = [p, -p]
    # 对上限为0的，当做1处理
    r[1] = 1 if r[1] == 0 else r[1]
    # 对r进行处理，-1到1之间的当做是比例
    r = [v * size if -1 <= v <= 1 else v for v in r]
    # 对负数，当做是从右数起，转为正
    r = [size + v if v < 0 else v for v in r]

    return r


def disp(
    filelist,
    show_x=None,
    show_y=None,
    show_n=25,
    whenexist="autonum",
):
    """
    找源
    :param filelist: 待显示的文件列表（实际上只显示第一张）
    :param show_x: 显示图像的x范围（默认None）
    :param show_y: 显示图像的y范围（默认None）
    :param show_n: 显示图像中源的数量（默认25）
    :param whenexist: 当输出文件存在时怎么处理，这个模块实际上用不上，只是保留一致而已
    :return: None
    """

    from .util import filename_split, pkl_dump, pkl_load
    import numpy as np
    import logging
    import astropy.io.fits as fits
    import matplotlib.pyplot as plt
    import os

    logger = logging.getLogger("phtool_main")
    # 确定具体文件名
    basefile = filelist[0]
    p, bf, suff, e = filename_split(basefile)
    # 加载图像，确认图像背景显示范围
    data = fits.getdata(basefile)
    ny, nx = data.shape
    vmin, vmax = np.percentile(data, [0.5, 99.5])

    # 确认显示范围
    xlim = _size_range_(show_x, nx)
    ylim = _size_range_(show_y, ny)
    # 确认图的合适大小
    xs, ys = xlim[1] - xlim[0], ylim[1] - ylim[0]
    # 确认图的合适大小
    ms = max(xs, ys) / 8
    xs, ys = xs / ms, ys / ms

    # 加载找源结果
    star_pkl_file = os.path.join(p, bf + "_stars.pkl")
    sources, _, _ = pkl_load(star_pkl_file)
    x, y, m = sources["xcentroid"], sources["ycentroid"], sources["mag"]
    # 筛选显示范围内的源
    goodix = np.where((xlim[0] < x) & (x < xlim[1]) & (ylim[0] < y) & (y < ylim[1]))
    x, y, m = x[goodix], y[goodix], m[goodix]
    # 筛选最亮的源
    goodix = np.argsort(m)[:show_n]
    x, y, m = x[goodix], y[goodix], m[goodix]
    # 画星图
    fig = plt.figure(figsize=(xs, ys))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    img = ax.imshow(data, vmin=vmin, vmax=vmax, origin="lower", cmap="gray")
    # 标注源
    cir_star = ax.scatter(x, y,
        s=20, #transform=ax.transData,
        facecolors="none", edgecolors="r",
    )
    print(f"{'No':^2s} | {'x':^7s} {'y':^7s} | {'mag':^5s}")
    for i, (ix, iy) in enumerate(zip(x, y)):
        ax.text(ix, iy, f"{i+1:2d}", ha="left", va="bottom", color="r", fontsize=12, fontweight="bold")
        print(f"{i+1:2d} | {ix:7.2f} {iy:7.2f} | {m[i]+25:5.2f}")
    # 调整显示范围
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_title(f"{bf}")
    plt.show()

    return
