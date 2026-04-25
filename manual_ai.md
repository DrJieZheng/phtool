          
# phtool 使用手册

## 1. 项目简介

phtool 是一个用于天文测光数据处理的工具，由 Dr/Prof Jie Zheng 和 Dr/Prof LinQiao Jiang 开发。该工具提供了完整的较差测光数据处理流程，包括本底合并、平场合并、图像改正、图像对齐、找源、测光、选星和较差分析等功能。

## 2. 安装说明

### 2.1 从源码安装

```bash
cd /Users/lzj/coding/25L_phtool
pip install -e .
```

### 2.2 从pypi安装

```bash
pip install phtool
```

## 3. 使用流程

典型的测光数据处理流程如下：

1. **本底合并** (`biascombine`) - 合并多幅本底文件
2. **平场合并** (`flatcombine`) - 合并多幅平场文件并归一化
3. **图像改正** (`imcorr`) - 对科学图像进行本底和平场改正
4. **找源** (`find`) - 检测图像中的恒星
5. **图像对齐** (`align`) - 计算各图像之间的平移和旋转
6. **测光** (`phot`) - 对检测到的恒星进行测光
7. **选星** (`xyget`/`pick`) - 选择目标星和参考星
8. **较差分析** (`diffcali`) - 进行较差测光分析

### 3.1 python命令行调用

```bash
python -m phtool [命令] [参数]
```

### 3.2 shell命令行调用

```bash
phtool [命令] [参数]
```

### 3.3 作为Python包被调用

```python
import phtool
phtool.xxxx(xxxx)
```

## 4. 各模块详细使用说明

### 4.1 biascombine - 本底合并

#### 功能描述
合并多幅本底文件为一个主本底文件。

#### 终端调用模式
```bash
python -m phtool biascombine [本底文件列表] --bias [输出本底文件] --combine [合并方法]
```

**参数说明**：
- `本底文件列表`：需要合并的本底文件
- `--bias`：输出的主本底文件名，默认生成 `BIAS.fits`
- `--combine`：合并方法，可选值：`clip`（默认）、`median`、`mean`、`avg`、`average`

**示例**：
```bash
python -m phtool biascombine bias1.fits bias2.fits bias3.fits --bias master_bias.fits --combine median
```

#### 函数调用模式
```python
from phtool.biascomb import biascomb

# 参数说明：
# filelist: 本底文件列表
# biasfile: 合并后的文件
# combine_method: 合并方法，默认为"clip"
biascomb(["bias1.fits", "bias2.fits", "bias3.fits"], "master_bias.fits", "median")
```

### 4.2 flatcombine - 平场合并

#### 功能描述
合并多幅平场文件并归一化，生成主平场文件。

#### 终端调用模式
```bash
python -m phtool flatcombine [平场文件列表] --bias [本底文件] --flat [输出平场文件] --combine [合并方法] --norm [归一化方法]
```

**参数说明**：
- `平场文件列表`：需要合并的平场文件
- `--bias`：本底文件，默认使用 `BIAS.fits`
- `--flat`：输出的主平场文件名，默认生成 `FLAT.fits`
- `--combine`：合并方法，可选值：`clip`（默认）、`median`、`mean`、`avg`、`average`
- `--norm`：归一化方法，可选值：`clip`（默认）、`median`、`mean`、`avg`、`average`

**示例**：
```bash
python -m phtool flatcombine flat1.fits flat2.fits flat3.fits --bias master_bias.fits --flat master_flat.fits --combine median --norm mean
```

#### 函数调用模式
```python
from phtool.flatcomb import flatcomb

# 参数说明：
# filelist: 平场文件列表
# biasfile: 本底文件
# flatfile: 合并后的平场文件
# combine_method: 合并方法，默认为"clip"
# norm_method: 归一化方法，默认为"clip"
flatcomb(["flat1.fits", "flat2.fits", "flat3.fits"], "master_bias.fits", "master_flat.fits", "median", "mean")
```

### 4.3 imcorr - 图像改正

#### 功能描述
对科学图像进行本底和平场改正，并计算观测时间相关的时间戳（JD/MJD/BJD）。

#### 终端调用模式
```bash
python -m phtool imcorrect [科学图像列表] --bias [本底文件] --flat [平场文件] --outdir [输出目录] --radec [目标坐标] --keyradec [坐标关键字] --sitename [观测站点] --sitecoord [站点坐标]
```

**参数说明**：
- `科学图像列表`：需要改正的科学图像
- `--bias`：本底文件，默认使用 `BIAS.fits`
- `--flat`：平场文件，默认使用 `FLAT.fits`
- `--outdir`：输出目录，默认为当前目录
- `--radec`：目标坐标，格式为 "RA,DEC"，例如 "12:34:56.78,-12:34:56.78" 或 "12.3456,+23.4567"
- `--keyradec`：坐标关键字，格式为 "RA_KEY,DEC_KEY"，例如 "RA,DEC"
- `--sitename`：观测站点名称，默认为 "xinglong"
- `--sitecoord`：站点坐标，格式为 "经度,纬度"，例如 "117.55,40.40"

**示例**：
```bash
python -m phtool imcorrect sci1.fits sci2.fits --bias master_bias.fits --flat master_flat.fits --outdir corrected --radec "12:34:56.78,-12:34:56.78" --sitename "xinglong"
```

#### 函数调用模式
```python
from phtool.imcorr import imcorr

# 参数说明：
# filelist: 待改正的文件列表
# biasfile: 本底文件
# flatfile: 平场文件
# outdir: 输出目录
# keyradec: 坐标关键字，默认为None
# radec: 坐标，默认为None
# sitename: 观测站点，默认为"xinglong"
# sitecoord: 站点坐标，默认为"117.55,40.40"
imcorr(["sci1.fits", "sci2.fits"], "master_bias.fits", "master_flat.fits", "corrected", 
       keyradec="RA,DEC", radec="12:34:56.78,-12:34:56.78", 
       sitename="xinglong", sitecoord="117.55,40.40")
```

### 4.4 offset - 计算图像偏移

#### 功能描述
计算各图像之间的平移量。

#### 终端调用模式
```bash
python -m phtool offset [图像列表] --offset [偏移文件] --baseix [基准图像索引] --maxoffset [最大偏移]
```

**参数说明**：
- `图像列表`：需要计算偏移的图像
- `--offset`：偏移文件，默认生成 `offset.txt`
- `--baseix`：基准图像索引，默认为0
- `--maxoffset`：最大偏移，默认为500

**示例**：
```bash
python -m phtool offset corrected/*fits --offset offset.txt --baseix 0 --maxoffset 500
```

#### 函数调用模式
```python
from phtool.offset import offset

# 参数说明：
# filelist: 待对齐的文件列表
# offsetfile: 偏移文件
# baseix: 基准图像索引，默认为0
# maxoffset: 最大偏移，默认为500
offset(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"], "offset.txt", 0, 500)
```

### 4.5 find - 找源

#### 功能描述
调用 photutils 进行找源以及FWHM计算，输出星表，按照亮度排序，给出综合的FWHM预估值。

#### 终端调用模式
```bash
python -m phtool find [图像列表]
```

**参数说明**：
- `图像列表`：需要找源的图像

**示例**：
```bash
python -m phtool find corrected/*fits
```

#### 函数调用模式
```python
from phtool.find import find

# 参数说明：
# filelist: 待找源的文件列表
find(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"])
```

### 4.6 align - 图像对齐

#### 功能描述
图像对齐，相比offset，需要先找星，但是可以计算出旋转角等。

#### 终端调用模式
```bash
python -m phtool align [图像列表] --align [对齐文件] --baseix [基准图像索引]
```

**参数说明**：
- `图像列表`：需要对齐的图像
- `--align`：对齐文件，默认生成 `align.pkl`
- `--baseix`：基准图像索引，默认为0

**示例**：
```bash
python -m phtool align corrected/*fits --align align.pkl --baseix 0
```

#### 函数调用模式
```python
from phtool.align import align

# 参数说明：
# filelist: 待对齐的文件列表
# alignfile: 对齐文件
# baseix: 基准图像索引，默认为0
align(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"], "align.pkl", 0)
```

### 4.7 phot - 测光

#### 功能描述
调用 photutils 进行测光，可选测光模式以及孔径。

#### 终端调用模式
```bash
python -m phtool phot [图像列表] --apers [测光孔径]
```

**参数说明**：
- `图像列表`：需要测光的图像
- `--apers`：测光孔径，默认为[-2.5]，负数表示相对于FWHM的倍数

**示例**：
```bash
python -m phtool phot corrected/*fits --apers -2.5 -3.5
```

#### 函数调用模式
```python
from phtool.phot import phot

# 参数说明：
# filelist: 待测光的文件列表
# apers: 测光孔径，默认为[-2.5]
phot(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"], apers=[-2.5, -3.5])
```

### 4.8 display - 图像选星

#### 功能描述
显示图像以及找到的星，供用户人工选星。

#### 终端调用模式
```bash
python -m phtool display [图像文件] --disp-x [x坐标范围] --disp-y [y坐标范围] --disp-n [显示数量]
```

**参数说明**：
- `图像文件`：需要选星的图像
- `--disp-x`：x坐标范围，默认为None
- `--disp-y`：y坐标范围，默认为None
- `--disp-n`：显示数量，默认为25

**示例**：
```bash
python -m phtool display corrected/*fits --disp-x 0 1 --disp-y 0 1 --disp-n 100
```

#### 函数调用模式
```python
from phtool.display import display

# 参数说明：
# filelist: 待显示的文件列表，只会显示第一个文件
# show_x: x坐标范围，默认为None
# show_y: y坐标范围，默认为None
# show_n: 显示数量，默认为25
display(["corrected/sci1_corr.fits"], show_x=[0, 1], show_y=[0, 1], show_n=100)
```

`disp-x`、`disp-y` 分别表示x坐标范围、y坐标范围，允许以下描述方式：
- `None`：全画面
- `0.3`，或者`[0.3]`：单个值，表示从左（下）0.3*图像宽度（高度）到右（上）0.3*图像宽度（高度）
- `[100, 200]`：两个值，从100到200的范围。如果超过两个值，前两个有效

取值范围：
- `0.3`：0～1（包括1）之间的正小数，表示宽度（高度）的倍数
- `100`：大于1的数，表示具体位置，可以是浮点数
- `-0.1`：-1～0之间的负小数，表示宽度（高度）的倍数，从右边数起，相当于`(1-0.1)`
- `-100`：小于-1的数，表示具体位置，从右边数起，相当于`(nsize-100)`

### 4.9 xyget - 可视化选星

#### 功能描述
可视化模式下选择目标星。

#### 终端调用模式
```bash
python -m phtool xyget [图像列表] --baseix [基准图像索引] --pickbox [选星范围] --xyfile [选星结果文件]
```

**参数说明**：
- `图像列表`：需要选星的图像
- `--baseix`：基准图像索引，默认为0
- `--pickbox`：选星范围，默认为20
- `--xyfile`：选星结果文件，默认为None

**示例**：
```bash
python -m phtool xyget corrected/*fits --baseix 0 --pickbox 20 --xyfile selected_stars.txt
```

#### 函数调用模式
```python
from phtool.xyget import xyget

# 参数说明：
# filelist: 待测光的文件列表
# baseix: 基准图像索引，默认为0
# pickbox: 选源范围，默认为20
# xyfile: 选源结果文件，默认为None
# display: 是否最后在屏幕显示结果，适用于从终端调用的情况，默认为False
bf, x, y = xyget(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"], baseix=0, pickbox=20, xyfile="selected_stars.txt", display=True)
```

### 4.10 pick - 从测光结果中选星

#### 功能描述
根据实现的选星结果，从phot结果中挑出想要的星。

#### 终端调用模式
```bash
python -m phtool pick [图像列表] --align [对齐文件] --pickfile [选星结果文件] --baseix [基准图像索引] --pickbox [选星范围] --xyfile [选星坐标文件]
```

**参数说明**：
- `图像列表`：需要处理的图像
- `--align`：对齐文件，默认使用 `align.pkl`
- `--pickfile`：选星结果文件，默认生成 `pick.pkl`
- `--baseix`：基准图像索引，默认为0
- `--pickbox`：选星范围，默认为20
- `--xyfile`：选星坐标文件，默认为None

**示例**：
```bash
python -m phtool pick corrected/*fits --align align.pkl --pickfile pick.pkl --baseix 0 --pickbox 20 --xyfile selected_stars.txt
```

#### 函数调用模式
```python
from phtool.pick import pick

# 参数说明：
# filelist: 待处理文件列表
# alignfile: 对齐文件
# pickfile: 星等文件
# baseix: 基准图像索引，默认为0
# pickbox: 选源范围，默认为20
# xyfile: 源位置文件，默认为None
pick(["corrected/sci1_corr.fits", "corrected/sci2_corr.fits"], "align.pkl", "pick.pkl", baseix=0, pickbox=20, xyfile="selected_stars.txt")
```

### 4.11 diffcali - 较差分析

#### 功能描述
根据phot结果，进行不同指定的较差计算和绘图，可以指定目标。采用指定比较星的方式。

#### 终端调用模式
```bash
python -m phtool diffcali --pickfile [选星结果文件] --califile [差校结果文件] --tgtidx [目标星索引] --refidx [参考星索引] --chkidx [检查星索引]
```

**参数说明**：
- `--pickfile`：选星结果文件，默认使用 `pick.pkl`
- `--califile`：差校结果文件，默认生成 `cali.pkl`
- `--tgtidx`：目标星索引，多个索引用空格分隔
- `--refidx`：参考星索引，多个索引用空格分隔
- `--chkidx`：检查星索引，多个索引用空格分隔

**示例**：
```bash
python -m phtool diffcali --pickfile pick.pkl --califile cali.pkl --tgtidx 0 --refidx 1 2 --chkidx 3 4
```

#### 函数调用模式
```python
from phtool.diffcali import diffcali

# 参数说明：
# pickfile: 星等文件
# califile: 差校文件
# tgt_idx: 目标星索引
# ref_idx: 参考星索引
# chk_idx: 检查星索引
diffcali(pickfile="pick.pkl", califile="cali.pkl", tgt_idx=[0], ref_idx=[1, 2], chk_idx=[3, 4])
```

## 5. 示例工作流

以下是一个完整的测光数据处理工作流示例：

### 步骤1：本底合并
```bash
python -m phtool biascombine bias/*.fits --bias master_bias.fits --combine median
```

### 步骤2：平场合并
```bash
python -m phtool flatcombine flat/*.fits --bias master_bias.fits --flat master_flat.fits --combine median --norm mean
```

### 步骤3：图像改正
```bash
python -m phtool imcorrect sci/*.fits --bias master_bias.fits --flat master_flat.fits --outdir corrected --radec "12:34:56.78,-12:34:56.78" --sitename "xinglong"
```

### 步骤4：找源
```bash
python -m phtool find corrected/*.fits
```

### 步骤5：图像对齐
```bash
python -m phtool align corrected/*.fits --align align.pkl --baseix 0
```

### 步骤6：测光
```bash
python -m phtool phot corrected/*.fits --apers -2.5 -3.5
```

### 步骤7：选星
```bash
python -m phtool xyget corrected/*.fits --baseix 0 --pickbox 20 --xyfile selected_stars.txt
```

### 步骤8：从测光结果中选星
```bash
python -m phtool pick corrected/*.fits --align align.pkl --pickfile pick.pkl --baseix 0 --pickbox 20 --xyfile selected_stars.txt
```

### 步骤9：较差分析
```bash
python -m phtool diffcali --pickfile pick.pkl --califile cali.pkl --tgtidx 0 --refidx 1 2 --chkidx 3 4
```

## 6. 输出文件说明

| 模块 | 输出文件 | 说明 |
|------|---------|------|
| biascombine | `*.fits` | 主本底文件 |
| flatcombine | `*.fits` | 主平场文件 |
| imcorr | `*_corr.fits` | 改正后的科学图像 |
| offset | `offset.txt`, `offset.pkl`, `offset.png` | 偏移数据文件、偏移图像 |
| find | `*_stars.pkl`, `*_stars.png` | 星表数据、星图 |
| align | `align.pkl` | 对齐数据 |
| phot | `*_phot.pkl` | 测光结果 |
| xyget | `*.txt` | 选星坐标文件 |
| pick | `pick.pkl`, `pick_*.txt` | 选星结果、星等数据文件 |
| diffcali | `cali.pkl`, `cali_*.png` | 差校结果、光变曲线图像 |

## 7. 常见问题与解决方案

1. **问题**：运行 `xyget` 时无法显示图像
   **解决方案**：确保安装了 matplotlib 并且配置了正确的显示后端

2. **问题**：测光结果中星等为 NaN
   **解决方案**：检查图像质量，确保恒星被正确检测

3. **问题**：对齐失败
   **解决方案**：确保图像中有足够的恒星用于匹配，调整 `find` 模块的参数

4. **问题**：较差分析结果噪声很大
   **解决方案**：选择更多的参考星，确保参考星的稳定性

## 8. 依赖项

- Python 3.8+
- NumPy
- Matplotlib
- Astropy
- Photutils
- qmatch
- astroalign

