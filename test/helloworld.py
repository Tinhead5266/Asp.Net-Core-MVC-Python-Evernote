# -*- coding: utf-8 -*-
def hello():
    print  ("Hello World!")
    pass

def yhsj():
    sum=10
    print(' '*sum+"1")
    # 上一排数字
    lastNums=[1]
    for i in range(1,sum):
        Nums = [n for n in range(i)]
        # 修改第一个数
        Nums[0] = Nums[-1] =  1
        # 修改最后一个数

        maxLenNums=len(Nums)
        if  maxLenNums>=3:
            for nIndex in range(maxLenNums):
                # 修改当前数组不是第一和最后的元素
                if nIndex>1 and nIndex <maxLenNums:
                    # 当前数=【上一个数组】当前位置加上【上一个数组】当前位置-1的值  注：nIndex=1需要从0开始
                    Nums[nIndex-1] = lastNums[nIndex-1-1]+lastNums[nIndex-1]
        # 修改第一个数
        Nums[0] = Nums[-1] =  1
        # 修改最后一个数
        print Nums
        lastNums=Nums
    pass


if __name__ == "__main__":
    yhsj()
def triangles():
    line = [1]  # 第一行就一个元素1

    while True:
        yield line

        # 生成下一行，表达式为 : [1] + 上一行的两个元素之和 + [1]

        line = [1] + [line[i] + line[i + 1] for i in range(len(line) - 1)] + [1]

n = 0
results = []
for t in triangles():
    results.append(t)
    n = n + 1
    if n == 10:
        break

for t in results:
    print(t)