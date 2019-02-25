def stabilize(points):
    """
    因为houghCircle的结果一直变化所以我们需要计算瞳孔位置的平均值来稳定结果

    :return:
    """
    sumX = 0
    sumY = 0
    count = 0
    for i in range(len(points)):
        sumX += points[i][0]
        sumY += points[i][1]
        count += 1
    if count > 0:
        sumX /= count
        sumY /= count

    return (sumX, sumY)