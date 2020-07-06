# SSD  Test Case
***

## Performance Test

### SSD Single Random IO Performance Test

#### Test Purpose

- 测试SSD单盘随机读写性能

#### Test Steps

1. 除待测盘外，机器不要插入其他无关硬盘以免干扰测试结果
2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交。
3. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32, 64, 128的随机读写，其中混合模式读写比例70/30。
4. 执行测试脚本，后台运行，每个workload组合运行600s
5. 测试结束后收集整理性能测试数据log,格式化log，系统日志log，dmesg log ,测试硬盘SMART log

#### Test Critical

1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件spec中的对应数据的差距不能超过10% 

2. 所有测试结果中，*相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

3. 所有测试结果中，*相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

4. 测试完毕之后，包含`Program Fail Count`，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。



### SSD Single Sequential IO Performance Test
#### Test Purpose

- 测试SSD单盘顺序读写性能

#### Test Steps

1. 除待测盘外，机器不要插入其他无关硬盘干扰
2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
3. 对待测盘依次下发bs为1024k,128k，64k，32k，16k，8k，4k；1jobs,QD为1，2，4，8，16，32的顺序读写，其中混合模式读写比例70/30
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
1. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
2. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32, 64, 128的随机读写，其中混合模式读写比例70/30。
3. 测试过程中注意中断平衡和NUMA打开，内核绑定
4. 执行测试脚本，后台运行每个workload组合运行600s
5. 测试结束后收集性能测试数据，格式化log,系统日志log，dmesg log ,测试硬盘SMART信息



#### Test Critical
1. 当系统设计不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%。

2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%。

3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。


### SSD Multi Sequential IO Performance Test
#### Test Purpose

- 测试SSD的多盘顺序读写性能

#### Test Steps
1. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交。
2. 对待测盘依次下发bs为1024k,128k，64k，32k，16k，8k，4k；1jobs,QD为1，2，4，8，16，32的顺序读写，其中混合模式读写比例70/30
3. 测试过程中注意中断平衡和NUMA打开，内核绑定
4. 执行测试脚本，后台运行每个workload运行600s
5. 测试结束后收集性能测试数据，格式化log,系统日志log，dmesg log ,测试硬盘SMART log



#### Test Critical
1. 当系统不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%。

2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%。

3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。


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
 1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件spec中的对应数据的差距不能超过10% 

2. 所有测试结果中，*相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

3. 所有测试结果中，*相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点*

4. 测试完毕之后，包含`Program Fail Count`，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。

## Stability test
### SSD Single Sequential IO Stability Test
#### Test Purpose

- 测试SSD单盘在长时间负载下的顺序读写稳定性测试

#### Test Steps
1. 除待测硬盘外，机器不要插入其他无关硬盘，以免干扰测试结果 
2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
3. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理2h
3. 对待测硬盘依次下发bs为1024k， 128k，4k；1 jobs ,QD为1, 128的顺序读写，混合读写（70/30）
4. 后台运行测试脚本，每个wordload运行7200s
5. 测试结束后收集测试数据，系统日志，dmesg，测试硬盘SMART，ERROR信息

#### Test Critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印



### SSD Single Random IO Stability Test
#### Test Purpose
- 测试SSD在长时间负载下的单盘随机性能稳定性

#### Test Steps

1. 在制定测试环境下用通用工具NVME cli等工具对待测硬盘格式化处理，确保待测盘从空盘启动，并保存格式化log
2. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理4h；bs为4k，1jobs,QD128随机写8h预处理。
3. 对待测盘下发bs为4k，16k，1024k;1jobs,QD为1，128的随机写，随机读，混合读写（70/30）
4. 后台运行脚本，每个workload组合运行7200s。
5. 测试结束收集性能测试数据，系统日志，dmesg，硬盘SMART，ERROR信息。

#### Test Critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印



### SSD Multi Sequential IO Stability Test
#### Test Purpose
- 测试多盘SSD在负载情况的长时间的顺序读写性能稳定性

#### Test Steps

2. 在指定测试环境下，用NVME cli的format指令对所有待测盘进行格式化处理，已确保测试硬盘从空盘启动，并保存格式化log在结果中提交
3. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理2h
3. 对待测硬盘依次下发bs为1024k， 128k，4k；1 jobs ,QD为1, 128的顺序写，顺序读，混合读写（70/30）
4. 后台运行测试脚本，每个wordload运行7200s；测试过程中注意中断平衡和NUMA打开及绑核处理
5. 测试结束后收集测试数据，系统日志，dmesg，测试硬盘SMART，ERROR信息

#### Test Critical
1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Multi Random IO Stability Test
#### Test Purpose
- 测试多盘SSD在负载情况的长时间的随机读写性能稳定性

#### Test Steps
 
1. 在制定测试环境下用通用工具NVME cli等工具对所有待测硬盘格式化处理，确保待测盘从空盘启动，并保存格式化log
2. 对fio对待测盘进行bs为128k，1jobs，QD128顺序写预处理4h；bs为4k，1jobs,QD128随机写8h预处理。
3. 对待测盘下发bs为4k，16k，1024k;1jobs,QD为1，128的随机写，随机读，混合读写（70/30）
4. 后台运行脚本，每个workload组合运行7200s，测试过程中注意中断平衡和NUMA打开及绑核处理
5. 测试结束收集性能测试数据，系统日志，dmesg，硬盘SMART，ERROR信息。

#### Test Critical
1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count，Erase Fail Count，SATA Downshift Count，End-to-End Error Detection Count，Uncorrectable Error Count，Command Timeouts, Pending Sector Count，Smart Off-line Scan Uncorrectable Error Count，CRC Error Count，media errors，num_err_log_entries critical_warning,Warining_Temperature_Time等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印


### SSD Single OS Drive Wear Leveling Test
#### Test Purpose

- 此测试用例主要验证SSD内部存在频繁被写入的热点数据时，由于FW启动磨损均衡操作，对Host IO处理能力的影响程度。通过长时间观察性能的稳定性波形图，验证启动磨损均衡搬移数据的过程中，Host IO的性能稳定性情况。

#### Test Steps

1. 

#### Test Critical
1. 所有block size的读带宽波形图中，去除测试开始之后和结束之前60秒内的数据，其余所有秒级性能监控数据中，不允许出现低于对应测试项目平均读带宽50%的监控点（对应block size的平均读带宽值在test_data文件内的.csv文件内）。
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，BMC，系统message没有诸如controller reset，io cancel，io error等异常log打印。


### SSD Single OS Drive Read Disturb Test
#### Test Purpose
- 验证SSD在小LBA范围内执行长时间大压力随机读测试的过程中，IO性能是否稳定。目的是验证SSD内部在处理读干扰问题时，FW的处理机制是否合理，是否会引发Host IO的严重性能抖动。

#### test steps

1. 


#### test critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值50%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，BMC，系统message没有诸如controller reset，io cancel，io error等异常log打印。


## Relibility











