import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import matplotlib
import csv
from conf.test_conf import test_conf, tc_logger

def csv_charting(csv, png, title=None, xlabel=None, ylabel=None, xvalue=None, yvalue=None, legend=None, axis=[None, None, None, None]):
  data = pd.read_csv(csv)
  data = data[yvalue]
  plt.plot(data)
  if (legend is not None):
    plt.legend(legend)
  if (title is not None):
    plt.title(title)
  if (xlabel is not None):
    plt.xlabel(xlabel)
  if (ylabel is not None):
    plt.ylabel(ylabel)
  if (axis[0] is not None):
    plt.xlim(xmin=axis[0])
  if (axis[1] is not None):
    plt.xlim(xmax=axis[1])
  if (axis[2] is not None):
    plt.ylim(ymin=axis[2])
  if (axis[3] is not None):
    plt.ylim(ymax=axis[3])
    
  plt.savefig(png)
  plt.close()

def bar_charting(png, title=None, xlabel=None, ylabel=None, xvalue=None, yvalue=None, legend=None):
  if (len(yvalue) > 4):
    raise Exception("bar_charting doesn't support more than 4 y series")
  width = 0.84/len(yvalue)
  x = np.arange(len(xvalue))
  
  for i in range (0, len(yvalue)):
    plt.bar(x+width*i, yvalue[i], width, label=legend[i])
  if (title is not None):
    plt.title(title)
  if (xlabel is not None):
    plt.xlabel(xlabel)
  if (ylabel is not None):
    plt.ylabel(ylabel)
  plt.xticks(x+width*(len(yvalue)-1)/2, xvalue)
  plt.legend()
  plt.savefig(png)
  plt.close()


def csv_statistics(source_csv, columns=None, percentiles=[0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99], target_csv=None):
  data = pd.read_csv(source_csv)
  if len(data) == 4:
    data = data[1:]
  if (columns is not None):
    data = data[columns]
  result = data.describe(percentiles=percentiles)
  if (target_csv is not None):
    result.to_csv(target_csv, na_rep='NaN')
  return result


def csv_statistics_get_rw(testcase, source_csv, columns=None, percentiles=[0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99],
                          target_csv=None):
  data = pd.read_csv(source_csv)
  if (columns is not None):
    data = data[columns]
    if testcase == 'fio':
      columns_write = [columns[2]]
      columns_read = [columns[0]]
    else:
      columns_write = [columns[0]]
      columns_read = [columns[2]]
    data_write = data[columns_write]
    data_read = data[columns_read]
    result_write = data_write.values[-1]
    result_read = data_read.values[-1]
  result = data.describe(percentiles=percentiles)
  if (target_csv is not None):
    result.to_csv(target_csv, na_rep='NaN')
  return result_write, result_read


if __name__ == "__main__":
  # csv_charting(csv="/home/ssd/AB.csv", png="/home/ssd/AB.png", title="Seq RW Throughput", xlabel="loop", ylabel="MB/S", yvalue=["Sequential Read(MB/s)","Sequential Write(MB/s)"], legend=["Sequential Read","Sequential Write"])
  data = pd.read_csv("/home/ssd/git_project/android-test-program/result/ts_debug/tc_debug/std_perf_summary.csv")
  xvalue = data.loc[data["TestName"] == "AB"]["Loop"]
  yvalue_AB = data.loc[data["TestName"] == "AB"]["Sequential Read(MB/s)"]
  yvalue_FIO1G = data.loc[data["TestName"] == "FIO - 1G"]["Sequential Read(MB/s)"]
  yvalue_TEST = data.loc[data["TestName"] == "FIO - 1G"]["Sequential Read(MB/s)"]
  yvalue = [yvalue_AB, yvalue_FIO1G, yvalue_TEST]
  xlabel = "Loop"
  ylabel = "MB/s"
  legend = ["AB", "FIO1G", "TEST"]
  bar_charting("/home/ssd/git_project/android-test-program/result/ts_debug/tc_debug/std_perf_summary.png", title="Title", xlabel=xlabel, ylabel=ylabel, xvalue=xvalue, yvalue=yvalue, legend=legend)


