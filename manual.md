          
# phtool 使用手册

## 1. 项目简介

phtool 是一个用于天文测光数据处理的工具，由郑捷和江林巧开发。该工具提供了完整的较差测光数据处理流程，包括本底合并、平场合并、图像改正、图像对齐、找源、测光、选星和较差分析等功能。

目前主要支持测光数据处理，未来考虑支持光谱等处理。待新增功能包括天测处理等。运行环境支持终端Python命令行调用、终端命令调用、Python包调用等形式。

## 2. 安装说明

从pypi安装

```bash
pip install phtool
```

## 3. 使用

本软件支持的测光数据处理步骤如下：

1. **图像裁剪** (`cutimage`) - 裁剪图像为指定区域
2. **本底合并** (`biascombine`) - 合并多幅本底文件
3. **平场合并** (`flatcombine`) - 合并多幅平场文件并归一化
4. **图像改正** (`imcorr`) - 对科学图像进行本底和平场改正
5. **找源** (`find`) - 检测图像中的恒星
6. **图像对齐** (`offset`/`align`) - 计算各图像之间的平移、旋转、缩放
7. **测光** (`phot`) - 对检测到的恒星进行孔径测光
8. **选星** (`xyget`/`disp`/`pick`) - 选择目标星和参考星
9. **较差分析** (`diffcali`) - 进行较差测光分析

### 3.1 python命令行调用

```bash
python -m phtool task filelist parameters
```

*根据Python环境不同，命令可能是python3或python。*

### 3.2 shell命令行调用

```bash
phtool task filelist parameters
```

### 3.3 作为Python包被调用

```python
import phtool
phtool.set_logger("DEBUG")  # 可选
phtool.task(filelist, parameters)
```

### 3.4 调用说明

- 以下调用方式示例一律采用python命令行形式。
- 任务名在不冲突的情况下可以只写前缀。
- 文件列表在任务名后，参数在文件列表后。文件可以使用原始图像文件，也可以使用平场本底改正后的文件，会自动识别。
- 文件列表可以直接列出文件（包括使用通配符），也可以使用`-l xx`或`--list xx`指定文件列表。函数调用方式只接受文件名列表/数组。
- 作为Python命令行调用或shell命令行调用时，非当前任务的参数可以提供，不会报错，会被忽略。但是作为函数方式调用时，提供额外参数会导致报错。
- 作为函数方式调用时，参数名基本上和终端一致，但是`xx-xx`将被替换为下划线`xx_xx`。
- `whenexist`：当输出文件已存在时如何处理，目前暂未实现，执行直接覆盖。
- `log`、`whenexist`，这两个参数对所有任务均可用，以下示例中不展示。

## 4. 各模块详细使用说明

### 4.1 cutimage - 图像裁剪

#### 功能描述
裁剪图像的指定区域。

#### 终端调用模式
```bash
python -m phtool cutimage [输入文件列表] --out-dir [输出路径] --cut-x [裁剪x坐标] --cut-y [裁剪y坐标] --cut-w [裁剪宽度] --cut-h [裁剪高度]
```

**参数说明**：
- `输入文件列表`：需要裁剪的输入文件
- `--out-dir`：输出的路径，默认当前目录
- `--cut-x`：裁剪的x坐标，默认为None，即不裁剪
- `--cut-y`：裁剪的y坐标，默认为None，即不裁剪
- `--cut-w`：裁剪的宽度，默认输入图像宽度
- `--cut-h`：裁剪的高度，默认输入图像高度

`cut-x/y`可以有以下提供方式：
- `100`，提供大于1的数值，表示像素数，从左侧/顶部算起
- `0.1`，提供0-1的小数，表示坐标比例，从左侧/顶部算起
- `-100`、`-0.1`，同上，但是为负数，表示从右侧/底部算起
- 提供单个数值的时候，表示左右/上下裁剪相同的距离
- 提供多个数值的时候，只有前两个有效，表示左右/上下裁剪的距离

`cut-w/h`可以有以下提供方式：
- 只允许提供一个正整数，表示像素数，裁剪区域的宽度/高度
- 当不提供时，根据`cut-x/y`自动计算裁剪区域的宽度/高度
- 当提供时，`cut-x/y`的第二个参数被忽略

**示例**：
```bash
python -m phtool cutimage image*.fits --out-dir cutted --cut-x 100 --cut-y 100 0.9 --cut-w 1000
```

#### 函数调用模式
```python
import phtool
import glob
filelist = glob.glob("image*.fits")
phtool.cutimage(filelist, "cutted", cut_x=100, cut_y=[100, 0.9], cut_w=1000)
```

*后面不再展示函数调用模式。*

### 4.2 biascombine - 本底合并

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

### 4.3 flatcombine - 平场合并

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

### 4.4 imcorr - 图像改正

#### 功能描述
对科学图像进行本底和平场改正，并计算观测时间相关的时间戳（JD/MJD/BJD）。

输出文件名为原始文件名后加上`_corr.`后缀，文件扩展名保持不变。

#### 终端调用模式
```bash
python -m phtool imcorr [科学图像列表] --bias [本底文件] --flat [平场文件] --outdir [输出目录] --radec [目标坐标] --keyradec [坐标关键字] --sitename [观测站点] --sitecoord [站点坐标]
```

**参数说明**：
- `科学图像列表`：需要改正的科学图像
- `--bias`：本底文件，默认使用 `BIAS.fits`
- `--flat`：平场文件，默认使用 `FLAT.fits`
- `--outdir`：输出目录，默认为当前目录
- `--radec`：目标坐标，格式为 "RA,DEC"，例如 "12:34:56.78,-12:34:56.78" 或 "12.3456,+23.4567"，用于fits头中缺失赤经赤纬或者有错时
- `--keyradec`：坐标关键字，格式为 "RA_KEY,DEC_KEY"，例如 "RA,DEC"，用于fits头中用其他关键字表示赤经赤纬时
- `--sitename`：观测站点名称，默认为 "xinglong"
- `--sitecoord`：站点坐标，格式为 "经度,纬度"，例如 "117.55,40.40"

**示例**：
```bash
python -m phtool imcorr sci1.fits sci2.fits --bias master_bias.fits --flat master_flat.fits --outdir corrected --radec "12:34:56.78,-12:34:56.78" --sitename "xinglong" --sitecoord "117.55,40.40"
```

### 4.5 offset - 计算图像偏移

#### 功能描述
计算各图像之间的平移量。

**注意：**该功能不需要先找星，且稳定性较好。但是要求图像之间只能有平移，不能有旋转、缩放。适合同一台赤道式望远镜观测的图像，如果是地平时望远镜则必须图像旋转角保持一致。

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


### 4.6 find - 找源

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

### 4.7 align - 图像对齐

#### 功能描述
图像对齐，相比offset，需要先找星，但是可以计算出旋转角等。适用于任何类型。还有一个情况是可能处理失败。

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


### 4.8 phot - 测光

#### 功能描述
调用 photutils 进行测光，可选测光模式以及孔径。

#### 终端调用模式
```bash
python -m phtool phot [图像列表] --apers [测光孔径]
```

**参数说明**：
- `图像列表`：需要测光的图像
- `--apers`：测光孔径，默认为[-2.5]，负数表示相对于FWHM的倍数，正数表示具体孔径。可以是多个值

**示例**：
```bash
python -m phtool phot corrected/*fits --apers -2.5 -3.5
```


### 4.9 display - 图像选星

#### 功能描述
显示图像以及找到的星，供用户人工选星。

注意：该方法仅用于本地执行，或者在notebook执行。基于ssh连接上的无图形界面终端不支持。

#### 终端调用模式
```bash
python -m phtool display [图像文件] --show-x [x坐标范围] --show-y [y坐标范围] --show-n [显示数量]
```

**参数说明**：
- `图像文件`：需要选星的图像
- `--show-x`：x坐标范围，默认为None
- `--show-y`：y坐标范围，默认为None
- `--show-n`：显示数量，默认为25
- `show-x/y`表示坐标范围时，描述方法与`cut-x/y`相同

**示例**：
```bash
python -m phtool display corrected/*fits --show-x 0 1 --show-y 0 1 --show-n 100
```

### 4.10 xyget - 可视化选星

#### 功能描述
可视化模式下选择目标星。

注意，该方法仅限于本地执行，在ssh连接的终端，以及notebook无法执行。

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

### 4.10 pick - 从测光结果中选星

#### 功能描述
根据实现的选星结果，从phot结果中挑出想要的星。

如果调用时未指定`--xyfile`，那么将自动调用`xyget`进行选星。

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

## 5. 输出文件说明

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

## 6. 参数与任务的对应关系

| PARA |`cutim`|`bias`|`flat`|`imcorr`|`find`|`phot`|`offset`|`align`|`xyget`|`disp`|`pick`|`diffcali`|
|------|:-----:|:----:|:----:|:------:|:----:|:----:|:------:|:-----:|:-----:|:----:|:----:|:--------:|
| `out-dir` |i |      |      |    i   |      |      |        |       |       |      |      |          |
| `cut-x/y` |i |      |      |        |      |      |        |       |       |      |      |          |
| `cut-h/w` |i |      |      |        |      |      |        |       |       |      |      |          |
| `bias` |     |  o   |  i   |    i   |      |      |        |       |       |      |      |          |
| `flat` |     |      |  o   |    i   |      |      |        |       |       |      |      |          |
| `combine` |  |  i   |  i   |        |      |      |        |       |       |      |      |          |
| `norm` |     |      |  i   |        |      |      |        |       |       |      |      |          |
| `radec` |    |      |      |    i   |      |      |        |       |       |      |      |          |
| `radeckey` | |      |      |    i   |      |      |        |       |       |      |      |          |
| `sitecoord`| |      |      |    i   |      |      |        |       |       |      |      |          |
| `sitename` | |      |      |    i   |      |      |        |       |       |      |      |          |
| `apers`  |   |      |      |        |      |  i   |        |       |       |      |      |          |
| `offset` |   |      |      |        |      |      |   o    |       |       |      |      |          |
| `maxoffset`| |      |      |        |      |      |   i    |       |       |      |      |          |
| `baseix` |   |      |      |        |      |      |   i    |   i   |       |      |  i   |          |
| `align` |    |      |      |        |      |      |        |   o   |   i   |      |  i   |          |
| `show-x/y` | |      |      |        |      |      |        |       |       |  i   |      |          |
| `show-n` |   |      |      |        |      |      |        |       |       |  i   |      |          |
| `pickbox` |  |      |      |        |      |      |        |       |   i   |      |  i   |          |
| `xyfile` |   |      |      |        |      |      |        |       |   o   |      |  i   |          |
| `pickfile` | |      |      |        |      |      |        |       |       |      |  o   |    i     |
| `califile` | |      |      |        |      |      |        |       |       |      |      |    o     |
| `tgtidx` |   |      |      |        |      |      |        |       |       |      |      |    i     |
| `refidx` |   |      |      |        |      |      |        |       |       |      |      |    i     |
| `chkidx` |   |      |      |        |      |      |        |       |       |      |      |    i     |

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

