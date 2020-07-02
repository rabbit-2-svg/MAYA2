# SSD  Test Case
***

## Performance Test

### SSD Single Random IO Performance Test

#### test purpose

- 测试SSD单盘随机读写性能

#### test steps

1. 除待测盘外，机器不要插入其他无关硬盘干扰
2. 对待测硬盘进行格式化，确保待测盘从空盘启动
3. 对待测盘依次下发bs为4k,8k，16k，32k，64k，128k，1024k；1jobs,QD为1，2，4，8，16，32的随机读写
4. 后台运行测试脚本，每个worload运行600s
5. 测试结束收集测试数据log，dmesg log，待测盘SMART log

#### test critical

1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件厂家spec中的对应数据的差距不能超过10% 

2. 所有测试结果中，相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点；

3. 所有测试结果中，相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点；

4. 测试完毕之后，包含`Program Fail Count (ID 171)`，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。



### SSD Single Sequential IO Performance Test
#### test purpose

- 测试SSD单盘顺序读写性能

#### test steps

1. 除待测盘外，机器不要插入其他无关硬盘干扰
2. 对待测硬盘进行格式化，确保待测盘从空盘启动
3. 对待测盘依次下发bs为1024k,128k，64k，32k，16k，8k，4k；1jobs,QD为1，2，4，8，16，32的随机读写
4. 后台运行测试脚本，每个worload运行600s
5. 测试结束收集测试数据log，dmesg log，待测盘SMART log



#### test critical
1. 在相同软硬件配置下，和相同的测试压力下（block size，queue depth），包括**`带宽，IOPS，延迟及Qos`**在内的测试结果与部件厂家spec中的对应数据的差距不能超过10%
2. 所有测试结果中，相同queue depth，随着Block Size增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点；
3. 所有测试结果中，相同Block size，随着queue depth增加，性能线性增加，直至饱和，中间无超过10%的跌落拐点；
4. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。




### SSD Multi Random IO Performance Test
#### test purpose
- 测试SSD的多盘随机读写性能

#### test steps
1. 


#### test critical
1. 当系统设计不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%。

2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%。

3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。


### SSD Multi Sequential IO Performance Test
#### test purpose
- 测试SSD的多盘顺序读写性能

#### test steps

1. 



#### test critical
1. 当系统不存在性能瓶颈时，所有槽位的待测试SSD的性能数据与对应项目的单盘测试结果的误差不能大于10%。
2. 相同存储链路不同槽位SSD所有测试项目的性能差异不能超过10%。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。




## Stability test
### SSD Single Sequential IO Stability Test
#### test purpose

- SSD_Single Sequential IO Stability Test

#### test steps

1. 

#### test critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。



### SSD Single Random IO Stability Test
#### test purpose
- 测试SSD长时间的单盘随机性能稳定性

#### test steps

1. 

#### test critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 测试完毕之后，包含`Program Fail Count (ID 171)`，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。



### SSD Multi Sequential IO Stability Test
#### test purpose
- 测试系统多盘SSD在负载情况，长时间的性能稳定性表现

#### test steps

1. 

#### test critical
1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印



### SSD Multi Random IO Stability Test
#### test purpose
- 测试系统中所有待测试SSD在负载情况，长时间的性能稳定性表现

#### test steps

1. 

#### test critical
1. 所有槽位的待测试SSD，在不同测试项目中的平均值与多盘性能测试对应槽位相同负载下的数据差异必须在10%以内。
2. 所有槽位的待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值80%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。


### SSD Single OS Drive Wear Leveling Test
#### test purpose

- 此测试用例主要验证SSD内部存在频繁被写入的热点数据时，由于FW启动磨损均衡操作，对Host IO处理能力的影响程度。通过长时间观察性能的稳定性波形图，验证启动磨损均衡搬移数据的过程中，Host IO的性能稳定性情况。

#### test steps

1. 

#### test critical
1. 所有block size的读带宽波形图中，去除测试开始之后和结束之前60秒内的数据，其余所有秒级性能监控数据中，不允许出现低于对应测试项目平均读带宽50%的监控点（对应block size的平均读带宽值在test_data文件内的.csv文件内）。
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。


### SSD Single OS Drive Read Disturb Test
#### test purpose
- 验证SSD在小LBA范围内执行长时间大压力随机读测试的过程中，IO性能是否稳定。目的是验证SSD内部在处理读干扰问题时，FW的处理机制是否合理，是否会引发Host IO的严重性能抖动。

#### test steps

1. 


#### test critical
1. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，低于对应测试项目带宽或者IOPS平均值50%的监控点数量不能超过总数量的千分之一（平均值从.csv文件中获取）。
2. 待测试SSD，去除测试开始之后和结束之前60秒内的数据，不同测试项目的秒级性能监控数据中，不允许出现跌落至0的点。
3. 测试完毕之后，包含Program Fail Count (ID 171)，Erase Fail Count (ID 172)，SATA Downshift Count (ID 183)，End-to-End Error Detection Count (ID 184)，Uncorrectable Error Count (ID 187)，Command Timeouts ( ID 188), Pending Sector Count (ID 197)，Smart Off-line Scan Uncorrectable Error Count (ID 198)，CRC Error Count (ID 199)等信息在内的SSD SMART信息无新增计数，FIO输出无报错，系统message没有诸如controller reset，io cancel，io error等异常log打印。















