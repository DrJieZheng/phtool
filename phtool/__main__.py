# -*- coding: utf-8 -*-
"""
    v0 20250607, Dr/AssoProf Jie Zheng & Dr/Prof Linqiao Jiang
    publish v0.1 20250717
    v0.2 0.26.425
    Photometry Tools
"""


# from ast import parse
import sys
import argparse
import os
import glob
import logging
from .util import filename_split, ext_check
version = "0.26.428"

import warnings
warnings.filterwarnings('ignore')


def _short_match_(s):
    """用短名字匹配命令"""
    tasks = [
        "cutimage",
        "biascombine",
        "flatcombine",
        "imcorrect",
        "offset",
        "find",
        "align",
        "phot",
        "xyget",
        "display",
        "pick",
        "diffcali",
    ]
    tt = [t for t in tasks if t.startswith(s)]
    if len(tt) == 1:
        return tt[0]
    elif len(tt) > 1:
        raise ValueError(f"Ambiguous task: {s}")
    else:
        raise ValueError(f"Unknown task: {s}")


def _out_dir_file_(filename, defaultname, *ext):
    """
    处理输出目录和文件名
    """
    if not filename:
        filename = defaultname
    filename = os.path.expanduser(filename)
    if not ext_check(filename, ext):
        filename += ext[0]
    return filename


def str_or_int(value):
    """test str or int, for argparse"""
    try:
        return int(value)
    except ValueError:
        return value


def pos_xy(coord_str):
    """converts a string 'x,y' to a float tuple (x, y)"""
    try:
        x, y = coord_str.split(',')
        return float(x.strip()), float(y.strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"Cannot convert '{coord_str}' to a x,y position.")


def set_logger(log_level="INFO"):
    """
    设置日志记录器
    :param log_level: 日志级别
    :return: 无
    """
    logger = logging.getLogger("phtool_main")
    # 新建一个控制台 Handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level) 
    # 可选：设置格式
    # fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(fmt)
    # 把 Handler 挂到 Logger 上
    logger.addHandler(ch)
    logger.setLevel(log_level)



def main():
    """
    A cli tool to run the pipeline.
    """
    if len(sys.argv) == 1:
        print(f"""Photometry Tools (phtool) v{version}
Usage:
    python -m phtool command arguments
    phtool command arguments
    import phtool; phtool.xxx(xxxx)
Commands:  `phtool -h`  for detail help
""")
    else:
        # cmd = _short_match_(sys.argv[1])
        # parse arguments
        parser = argparse.ArgumentParser(
            prog="Photometry Tools (phtool)",
            description="Photometry Tools (phtool)",
        )
        parser.add_argument("-v", "--version", action='version', version=f"%(prog)s v{version}")
        parser.add_argument("task", type=str, nargs=1,
            help="Task to run")
        parser.add_argument("--whenexist", type=str.lower, nargs="?", default="autonum",
            choices=["overwrite", "skip", "append", "autonum", "error"],
            help="What to do when output file exists")
        parser.add_argument("--log", type=str.upper, nargs="?", default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level")
        parser.add_argument("files", type=str, nargs="*",
            help="Raw data files")
        parser.add_argument("-l", "--list", type=str, nargs="?", default=None,
            help="Raw data list")
        parser.add_argument("-o", "--out-dir", type=str, nargs="?", default="./",
            help="Output directory")
        parser.add_argument("--bias", type=str, nargs="?", default=None,
            help="Master bias filename")
        parser.add_argument("--flat", type=str, nargs="?", default=None,
            help="Master flat filename")
        parser.add_argument("--combine", type=str.lower, nargs="?", default="clip",
            choices=["clip", "median", "mean", "avg", "average"],
            help="Bias & flat combine method")
        parser.add_argument("--norm", type=str.lower, nargs="?", default="clip",
            choices=["clip", "median", "mean", "avg", "average"],
            help="Flat normalizing method")
        parser.add_argument("--cut-x", type=float, nargs="*", default=None,
            help="X range for cutting image")
        parser.add_argument("--cut-y", type=float, nargs="*", default=None,
            help="Y range for cutting image")
        parser.add_argument("--cut-w", type=int, nargs="?", default=None,
            help="Width for cutting image")
        parser.add_argument("--cut-h", type=int, nargs="?", default=None,
            help="Height for cutting image")
        parser.add_argument("--radec", type=str, nargs="?", default=None,
            help="RA and Dec of the target, e.g. '12:34:56.78,-12:34:56.78' or '12.3456,+23.4567'")
        parser.add_argument("--keyradec", type=str, nargs="?", default=None,
            help="Header key of RA and Dec of the target, e.g. 'RA,DEC'")
        parser.add_argument("--sitename", type=str.lower, nargs="?", default="xinglong",
            help="Site name, e.g. 'xinglong'")
        parser.add_argument("--sitecoord", type=str, nargs="?", default="117.55,40.40",
            help="Site coordinate, e.g. '117.55,40.40' or '117:33:01,40:28:23'")
        parser.add_argument("--offsetfile", type=str, nargs="?", default=None,
            help="Offset file")
        parser.add_argument("--baseix", type=int, nargs="?", default=0,
            help="Base image index for offset")
        parser.add_argument("--maxoffset", type=int, nargs="?", default=500,
            help="Max offset for offset")
        parser.add_argument("--alignfile", type=str, nargs="?", default=None,
            help="Align file")
        parser.add_argument("--apers", type=float, nargs="*", default=[-2.5],
            help="Aperture(s) for photometry")
        parser.add_argument("--show-x", type=float, nargs="*", default=None,
            help="X range for display image")
        parser.add_argument("--show-y", type=float, nargs="*", default=None,
            help="Y range for display image")
        parser.add_argument("--show-n", type=int, nargs="?", default=25,
            help="No of stars to display in the image")
        parser.add_argument("--xyfile", type=str, nargs="?", default=None,
            help="XY file of selected sources")
        parser.add_argument("--pickbox", type=float, nargs="?", default=20,
            help="Pick box size for selecting sources")
        parser.add_argument("--pickfile", type=str, nargs="?", default=None,
            help="Pick file of selected sources")
        parser.add_argument("--califile", type=str, nargs="?", default=None,
            help="Calibration file of selected sources")
        parser.add_argument("--tgtidx", type=int, nargs="*", default=None,
            help="Target star index")
        parser.add_argument("--refidx", type=int, nargs="*", default=None,
            help="Reference star index")
        parser.add_argument("--chkidx", type=int, nargs="*", default=None,
            help="Check star index")
        
        args = parser.parse_args()

        # 配置日志
        set_logger(args.log)

        # logging.debug(f"{args}")
        # 解析命令
        task = _short_match_(args.task[0])
        # 输出文件存在处理模式
        whenexist = args.whenexist
        # 处理列表
        files = args.files
        if args.list and os.path.exists(args.list):
            with open(args.list, "r") as f:
                files.extend([line.strip() for line in f.readlines()])
        efiles = []
        for f in files:
            efiles.extend(glob.glob(os.path.expanduser(f)))
        efiles.sort()

        # 根据提供的任务逐个选择调用对应的函数
        if task == "cutimage":
            # 截取图像
            from .cutimage import cutimage
            cutimage(efiles, out_dir=args.out_dir, 
                cut_x=args.cut_x, cut_y=args.cut_y, cut_w=args.cut_w, cut_h=args.cut_h, 
                whenexist=args.whenexist)
        elif task == "biascombine":
            # 合并本底
            # 处理合并后的文件名
            biasfile = _out_dir_file_(args.bias, "BIAS", ".fits")
            from .biascomb import biascomb
            biascomb(efiles, biasfile=biasfile, combine_method=args.combine, 
                whenexist=args.whenexist)
        elif task == "flatcombine":
            # 处理合并后的文件名
            biasfile = _out_dir_file_(args.bias, "BIAS", ".fits")
            flatfile = _out_dir_file_(args.flat, "FLAT", ".fits")
            from .flatcomb import flatcomb
            flatcomb(efiles, biasfile=biasfile, flatfile=flatfile, 
                combine_method=args.combine, norm_method=args.norm, 
                whenexist=args.whenexist)
        elif task == "imcorrect":
            # 处理合并后的文件名
            biasfile = _out_dir_file_(args.bias, "BIAS", ".fits")
            flatfile = _out_dir_file_(args.flat, "FLAT", ".fits")
            keyradec = args.keyradec
            radec = args.radec
            sitename = args.sitename
            sitecoord = args.sitecoord
            from .imcorr import imcorr
            imcorr(efiles, biasfile=biasfile, flatfile=flatfile, 
                out_dir=args.out_dir, 
                keyradec=keyradec, radec=radec, 
                sitename=sitename, sitecoord=sitecoord,
                whenexist=args.whenexist)
        elif task == "offset":
            # 处理偏移文件
            baseix = args.baseix
            maxoffset = args.maxoffset
            offsetfile = _out_dir_file_(args.offsetfile, "offset", ".txt")
            from .offset import offset
            offset(efiles, offsetfile=offsetfile,
                baseix=baseix, maxoffset=maxoffset, 
                whenexist=args.whenexist)
        elif task == "find":
            # 找源，暂无其他参数
            from .find import find
            find(efiles, whenexist=args.whenexist)
        elif task == "align":
            # 图像对齐
            baseix = args.baseix
            alignfile = _out_dir_file_(args.alignfile, "align", ".pkl")
            from .align import align
            align(efiles, alignfile=alignfile, baseix=baseix, 
                whenexist=args.whenexist)
        elif task == "phot":
            # 找源，暂无其他参数
            from .phot import phot
            phot(efiles, apers=args.apers,
                whenexist=args.whenexist)
        elif task == "xyget":
            # 选择目标星
            baseix = args.baseix
            pickbox = args.pickbox
            xyfile = args.xyfile
            from .xyget import xyget
            xyget(efiles, baseix=baseix, pickbox=pickbox, xyfile=xyfile, display=True, 
                whenexist=args.whenexist)
        elif task == "display":
            # 显示图像，并根据需要截取部分区域，进行人工选星
            from .disp import disp
            disp(efiles, show_x=args.show_x, show_y=args.show_y, show_n=args.show_n,
                whenexist=args.whenexist)
        elif task == "pick":
            # 选择目标星
            baseix = args.baseix
            pickfile = _out_dir_file_(args.pickfile, "pick", ".pkl")
            alignfile = _out_dir_file_(args.alignfile, "align", ".pkl")
            xyfile = args.xyfile
            pickbox = args.pickbox
            from .pick import pick
            pick(efiles, baseix=baseix, pickfile=pickfile, alignfile=alignfile, xyfile=xyfile, 
                pickbox=pickbox, whenexist=args.whenexist)
        elif task == "diffcali":
            # 差校
            pickfile = _out_dir_file_(args.pickfile, "pick", ".pkl")
            califile = _out_dir_file_(args.califile, "cali", ".pkl")
            tgtidx = args.tgtidx
            refidx = args.refidx
            chkidx = args.chkidx
            from .diffcali import diffcali
            diffcali(pickfile=pickfile, califile=califile, 
                tgt_idx=tgtidx, ref_idx=refidx, chk_idx=chkidx,
                whenexist=args.whenexist)
            

if __name__ == "__main__":
    main()
