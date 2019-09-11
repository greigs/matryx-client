def iterate_2d(rows, cols, rows_start=0, cols_start=0):
    for x in range(rows):
        for y in range(cols):
            yield (x, y)
