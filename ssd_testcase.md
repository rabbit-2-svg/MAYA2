# SSD  Test Case

***

## Basic Function

### SSD SN/PN info verify test
#### Test Purpose

- 测试SSD硬盘主要信息在系统及BIOS下显示是否正确

#### Test Steps
1. 在系统下用指令抓取Identify,SMART,SN,MN,capcity等硬盘主要信息，保存log

```
$ nvme id-ctrl /dev/nvmeXn1
$ nvme smart-log /dev/nvmeXn1
$ nvme list
$ fdisk -l /dev/nvmeXn1
$ smartctl -a /dev/sdX
$ smartctl -I /dev/sdX
```

2. 在BIOS Setup界面检查硬盘厂家信息及SN，拍照

#### Test Critical

1. 系统和BIOS界面显示硬盘信息与Spec对比正确


### SSD LED status verify test
#### Test Purpose

- 验证SSD系统各种工作状态下灯号显示

#### Test Steps

1. 在系统下检查硬盘非工作状态下LED状态
2. 在active状态下检查LED状态，用dd对硬盘进行读写

#### Test Critical

1. 在不同工作状态下硬盘LED状态灯显示正确


### SSD speed negotiate verify test

#### Test Purpose 


#### Test Steps


#### Test Critial


### SSD Partition 

















## Performance Test

### SSD Single Random IO Performance Test

#### Test Purpose

- 测试SSD单盘随机读写性能

#### Test Steps

1. 除待测盘外，机器不要插入其他无关硬盘以免干扰测试结果
2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交。
3. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32, 64, 128的随机读写，其中混合模式读写比例70/30。
4. 执行测试脚本，后台运行，每个workload组合运行600s
5. 测试结束后收集整理性能测试数据log,格式化log，系统日志，dmesg ,测试硬盘SMART log

#### Test Critical

1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件spec中的对应数据的差距不能超过10% 

2. 所有测试结果中，*相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

3. 所有测试结果中，*相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

4. 测试完毕之后，包含`Program Fail Count`，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，`media errors`，`num_err_log_entries critical_warning`,`Warining_Temperature_Time`等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。



### SSD Single Sequential IO Performance Test
#### Test Purpose

- 测试SSD单盘顺序读写性能

#### Test Steps

1. 除待测盘外，机器不要插入其他无关硬盘干扰
2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
3. 对待测盘依次下发bs为1024k,128k，64k，32k，16k，8k，4k；1jobs,QD为1，2，4，8，16，32，64，128的顺序读写，其中混合模式读写比例70/30
4. 执行测试脚本，后台运行，每个workload组合运行600s
5. 测试结束后收集整理性能测试数据，格式化log,系统日志log，dmesg log ,测试硬盘SMART




#### Test Critical
1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件spec中的对应数据的差距不能超过10%
2. 所有测试结果中，*相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*
3. 所有测试结果中，*相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*
4. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。




### SSD Multi Random IO Performance Test
#### Test Purpose
- 测试SSD的多盘随机读写性能

#### Test Steps
1. 在指定测试环境下，用NVME cli的format指令或其他指定格式化工具对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
2. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32, 64, 128的随机读写，其中混合模式读写比例70/30。
3. 测试过程中注意中断平衡和NUMA打开，内核绑定
4. 执行测试脚本，后台运行每个workload组合运行600s
5. 测试结束后收集性能测试数据，格式化log,系统日志log，dmesg log ,测试硬盘SMART信息


#### Test Critical
1. 当系统设计不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%

2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%

3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Multi Sequential IO Performance Test
#### Test Purpose

- 测试SSD的多盘顺序读写性能

#### Test Steps
1. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交。
2. 对待测盘依次下发bs为1024k,128k，64k，32k，16k，8k，4k；1jobs,QD为1，2，4，8，16，32，64，128的顺序读写，其中混合模式读写比例70/30
3. 测试过程中注意中断平衡和NUMA打开，内核绑定
4. 执行测试脚本，后台运行每个workload运行600s
5. 测试结束后收集性能测试数据，格式化log,系统日志log，dmesg log ,测试硬盘SMART log


#### Test Critical
1. 当系统不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%

2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%

3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Single performance in EXT4 test
#### Test Purpose

-  测试待测硬盘在EXT4文件系统下性能测试

### Test Steps
1. 在指定待测环境下，用通用NVME cli工具或其他指定工具对待测硬盘进行格式化处理.保存格式化log
2. 用mkfs.ext4命令将待测盘格式化EXT4的文件系统并挂载。
3. 用FIO对待测盘下发bs为128k，1jobs QD128，loops=2的顺序写预处理
4. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32, 64, 128的随机读写，其中混合模式读写比例70/30。
5. 后台运行测试脚本，每个workload运行600s
6. 测试完成后收集性能数据，系统日志，dmesg，硬盘SMART ERROR log

### Test Critical
 1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`IOPS，延迟及Qos`**在内的测试结果与部件spec中的对应数据的差距不能超过10% 

2. 所有测试结果中，*相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

3. 所有测试结果中，*相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

4. 测试完毕之后，包含`Program Fail Count`，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印

## Stability test
### SSD Sequential IO Stability Test
#### Test Purpose

- 测试SSD单盘在长时间负载下的顺序读写稳定性测试

#### Test Steps
1. 除待测硬盘外，机器不要插入其他无关硬盘，以免干扰测试结果 
2. 在指定测试环境下，用NVME cli的format指令或其他指定工具对待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
3. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理2h
3. 对待测硬盘依次下发bs为1024k， 128k，4k；1 jobs ,QD为1, 128的顺序读写，混合读写（70/30）
4. 后台运行测试脚本，每个wordload运行7200s
5. 测试结束后收集测试数据，系统日志，dmesg，测试硬盘SMART，ERROR信息

#### Test Critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一(平均值从.csv文件中获取)
2. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印



### SSD Random IO Stability Test
#### Test Purpose

- 测试SSD在长时间负载下的单盘随机性能稳定性

#### Test Steps

1. 在指定测试环境下用通用工具NVME cli等工具对待测硬盘格式化处理，确保待测盘从空盘启动，并保存格式化log
2. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理4h；bs为4k，1jobs,QD128随机写8h预处理
3. 对待测盘下发bs为4k，16k，1024k;1jobs,QD为1，128的随机写，随机读，混合读写（70/30）
4. 后台运行脚本，每个workload组合运行7200s
5. 测试结束收集性能测试数据，系统日志，dmesg，硬盘SMART，ERROR信息。

#### Test Critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印



### SSD Multi Sequential IO Stability Test
#### Test Purpose

- 测试多盘SSD在长时间负载情况下的顺序读写性能稳定性

#### Test Steps

1. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
2. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理2h
3. 对待测硬盘依次下发bs为1024k， 128k，4k；1 jobs ,QD为1, 128的顺序写，顺序读，混合读写（70/30）
4. 后台运行测试脚本，每个wordload运行7200s；测试过程中注意中断平衡和NUMA打开及绑核处理
5. 测试结束后收集测试数据，系统日志，dmesg，测试硬盘SMART，ERROR信息

#### Test Critical

1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Multi Random IO Stability Test
#### Test Purpose

- 测试多盘SSD在长时间负载情况下的随机读写性能稳定性

#### Test Steps

1. 在指定测试环境下用通用工具NVME cli等工具对所有待测硬盘格式化处理，确保待测盘从空盘启动，并保存格式化log
2. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理4h；bs为4k，1jobs,QD128随机写8h预处理。
3. 对待测盘下发bs为4k，16k，1024k;1jobs,QD为1，128的随机写，随机读，混合读写（70/30）
4. 后台运行脚本，每个workload组合运行7200s，测试过程中注意中断平衡和NUMA打开及绑核处理
5. 测试结束收集性能测试数据，系统日志，dmesg，硬盘SMART，ERROR信息。

#### Test Critical
1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Wear Leveling Test
#### Test Purpose

- 测试SSD内部在启动磨损均衡搬移数据的过程中，IO性能稳定性情况。

#### Test Steps
1. 在指定测试环境下，用NVME cli工具或其他指定的格式化工具对SSD全盘格式化处理，保存格式化log
2. 用FIO对待测盘下发bs为128k，1jobs，QD128的顺序写预处理，运行时间约2h
3. 用FIO对待测盘测试bs为128k，4k，1jobs，QD为1，32的顺序读。
4. 后台运行测试脚本，每个workload组合运行约7200s
5. 测试结束后收集性能测试数据，系统dmesg日志，硬盘SMART等信息

#### Test Critical
1. 所有block size的读带宽波形图中，去除测试开始之后和结束之前60秒内的数据，其余所有秒级性能监控数据中，不允许出现低于对应测试项目平均读带宽50%的监控点（对应block size的平均读带宽值在test_data文件内的.csv文件内）。
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点。
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Read Disturb Test
#### Test Purpose

- 测试SSD在进行长时间大压力随机读测试，IO性能是否稳定，是否有严重性能抖动。

#### Test Steps
1. 在指定环境下，用NVME cli工具或其他指定格式化工具对硬盘进行格式化处理，保存格式化log 
2. 用FIO对待测硬盘下发bs为16k，32k，64k，128k，1024k，2048k；1 jobs；QD为1，128随机读测试
3. 后台运行测试脚本，每个workload组合运行2h。
4. 测试结束后收集读带宽和IOPS等性能测试数据，系统日志，dmesg及硬盘SMART error等信息


#### Test Critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值50%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Collect info during IO test
#### Test Purpose

- 测试在硬盘读写过程中收集SSD相关log是否引起性能抖动

#### Test Steps
1. 用FIO对待测硬盘进行bs为4k ，1jobs，QD128的随机混合读写，后台运行

2. FIO运行约10min用nvme cli或其他工具收集identify ，smart，error等log

```
   $ nvme id-ctrl /dev/nvmeXn1
   $ nvme smart-log /dev/nvmeXn1
   $ nvme error-log /dev/nvmeXn1
   $ nvme list
```
3. log收集次数不少于10次，结束后kill fio进程
4. 将性能数据整理成二维散点图，检查性能抖动情况

#### Test Critical

1. FIO运行无报错，SMART信息值每次轮询检查无异常
2. 收集log过程中FIO性能无波动


## Reliability

### SSD OSReboot with IO test
#### Test Purpose

- 测试SSD硬盘在机器长时间热重启过程中是否正常识别，读写是否正常，数据是否有丢失等

#### Test Steps
1. 对所有待测硬盘进行分区，每个分区约占50%
2. 对分区1格式化挂载并且写入1G文件，对文件进行MD5加密
3. 用FIO对分区2下发bs为4k随机混合读写，每次进系统后FIO运行至少1分钟，轮循次数不少于1000cycle
4. 测试结束后收集系统日志，iostat log 硬盘SMART error等关键值信息


#### Test Critical
1. 所有待测硬盘在每次重启后能正常识别，无掉盘及盘符漂移
2. 外部PCIe链路无CRC error，无降速和掉位宽
3. 每次重启进系统后FIO运行无报错，系统dmesg无IO error打印
4. 硬盘SMART ERROR信息无异常报警
5. 寄存器UESta CESta状态正常，MAD5数据校检无丢失
6. BMC 检测硬盘sensor状态正常


### SSD DCcycle with IO test
#### Test Purpose

-  测试SSD硬盘在机器长时间冷重启过程中是否掉盘，读写是否正常，数据是否丢失等

#### Test Steps
1. 对所有待测硬盘进行分区，每个分区50%
2. 对分区1格式化挂载并且写入1G文件，对文件进行MD5加密，生成MD5值
3. 用FIO对分区2下发bs为4k随机混合读写，每次进系统后FIO运行至少1分钟，轮循次数不少于1000cycle
4. 测试结束后收集系统日志，iostat log 硬盘SMART error等关键信息

#### Test Critical
1. 所有待测硬盘在每次重启后能正常识别，无掉盘及盘符漂移
2. 外部PCIe链路无CRC error，无降速和掉位宽
3. 每次重启进系统后FIO运行无报错，系统dmesg无IO error打印
4. 硬盘SMART ERROR信息无异常报警
5. 寄存器UESta CESta状态正常，MAD5数据校检无丢失
6. BMC 检测硬盘sensor状态正常


### SSD ACcycle with IO test
#### Test Purpose

- 测试硬盘在机器频繁异常断电重启后是否能识别，有无降速及掉位宽，读写是否正常等

#### Test Steps
1. 用FIO对所有待测SSD下发bs为4K的随机混合读写（50/50），运行约1min对机器执行AC断电操作
2. 重启进系统后检查硬盘状态，SMART,系统日志,SEL信息等
3. AC断电次数不少于1000cycle

#### Test Critical
1. 所有待测硬盘在每次重启后能正常识别，无掉盘及盘符漂移
2. 外部PCIe链路无CRC error，无降速和掉位宽
3. 每次重启进系统后FIO运行无报错，系统dmesg无IO error打印
4. 硬盘SMART ERROR信息无异常报警
5. BMC 检测硬盘sensor状态正常


### FW upgrade and downgrade with IO test
#### Test Purpose

- 测试硬盘在读写过程中升降级至指定FW版本,且无数据丢失

#### Test Steps
1. 在指定测试环境下，对待测硬盘进行分区。每个分区比例约50%
2. 对分区1格式化挂载，用dd写入1G文件，且用MD5对文件加密
3. 用FIO对分区下发bs为4k ，1jobs，QD128随机混合读写（50/50），后台运行
4. 在FIO运行过程中执行FW升降级，升降级轮循次数不少于100cycle
5. 升降级结束后用md5 checksum 对分区1进行数据校检
6. 收集系统日志，FW升降级log，iostat log，硬盘SMART EEROR log等其他关键信息

#### Test Critical
1. FW升降级过程中，待测硬盘能升降级到指定的目标版本
2. FIO运行过程中无报错，无IO error，且在升降级过程中IO中断时间少于2s
3. MD5校检无数据丢失
4. 系统日志，BMC无其他异常打印，硬盘SMART关键信息如media error, critical_warning, num_error_entries等值测试前后无增加


### SSD Hotplug test
#### Test Purpose

- 测试硬盘在执行通知式热插拔过程中,盘符是否正常识别,数据是否丢失等

#### Test Steps
1. 对机器所有待测硬盘分区，每个分区约占50%
2. 对分区1格式化挂载，dd指令写入100G的文件，用MD5对文件进行加密
3. umount分区1，对所有硬盘按顺序（按硬盘加载顺序从低位到高位）进行通知式热插拔操作
4. 同一个slot槽位每次热插拔时间间隔60s,热插拔次数不少于50cycle
5. 热插拔结束后，对分区1文件，进行MD5 checksum校检
6. 对分区2用FIO下发bs为4k, 1jobs, QD128随机混合读写（50/50）
6. 测试结束收集系统日志，dmesg，硬盘SMART ERROR等信息

#### Test Critical
1. 每次热插拔前后硬盘能正常识别，无掉盘及盘符漂移
2. 每次热插拔前后硬盘LED灯闪烁正常
2. 热插拔前后PCIe链路lnkSta无降速及掉位宽
3. 热插拔结束后硬盘数据无丢失，读写无异常
4. 寄存器UESta，CESta状态位无置+
5. 系统日志无IO相关异常error黑名单, SMART关键值信息如media error, critical_warning, num_error_entries等值无增加


### SSD OP adjust test
#### Test Purpose

- 测试SSD在调整成不同用户容量下，硬盘读写正常，SMART关键值信息无异常增加

#### Test Steps
1. 在指定测试环境，用给定的SSD tool对硬盘进行OP调整
1. 对待测硬盘做OP调整，调整比例依次为用户可用容量占90%， 80%， 70%， 60%， 50%。
2. 每次调整完OP后，对盘做bs为4k，1jobs，QD128的随机混合读写（50/50），FIO运行3min
3. 重新恢复实际容量100%，收集调整前后硬盘SMART信息，对比关键值如media error等有无增加

#### Test Critical
1. 用指定工具按规定比例调整用户容量，无错误
2. 每次调整过的用户空间系统下显示正确，FIO运行无报错，性能无跌落
3. 调整前后硬盘SMART值无增加
4. 系统日志，dmesg， BMC无IO相关错误打印






















   ```

   ```

```

```