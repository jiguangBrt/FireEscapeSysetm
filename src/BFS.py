import numpy as np
from collections import deque
from typing import List, Tuple, Optional

def bfs_search_dynamic(
    grid: List[List[int]],
    smoke_time: List[List[List[float]]],
    start: Tuple[int, int]
) -> Optional[Tuple[float, List[Tuple[int, int, int]]]]:
    """
    BFS to find the time-optimal (fewest steps) path to any exit,
    returning total smoke cost and the path [(t, r, c), ...].

    :param grid: static grid (0=free, 1=wall, 2=exit, 3=start)
    :param smoke_time: smoke concentrations over time [T][R][C]
    :param start: (row, col)
    :return: (total smoke cost, path) or None if no exit reachable
    """
    T = len(smoke_time)
    rows, cols = len(grid), len(grid[0])
    sr, sc = start

    exits = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2]
    if not exits:
        return None

    queue = deque()
    queue.append(((0, sr, sc), smoke_time[0][sr][sc], [(0, sr, sc)]))
    visited = set()
    visited.add((0, sr, sc))

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]  # 4方向 + 等待

    while queue:
        (t, r, c), current_cost, path = queue.popleft()

        if (r, c) in exits:
            return current_cost, path

        if t + 1 >= T:
            continue

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            nt = t + 1
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                state = (nt, nr, nc)
                if state not in visited:
                    visited.add(state)
                    step_cost = smoke_time[nt][nr][nc]
                    new_path = path + [state]
                    queue.append((state, current_cost + step_cost, new_path))

    return None

def example():
    # 定义地图：
    # 0 = 可通行，1 = 墙壁，2 = 出口，3 = 起点
    grid = [
        [2, 0, 0, 0],
        [1, 1, 0, 1],
        [3, 0, 0, 2],
        [1, 0, 1, 1],
    ]
    # 在 grid 中自动寻找起点坐标
    start = next(
        (r, c)
        for r in range(len(grid))
        for c in range(len(grid[0]))
        if grid[r][c] == 3
    )

    # 模拟 6 秒内的烟雾浓度时序 (shape = [T, H, W])
    T = 6
    H, W = len(grid), len(grid[0])
    smoke_time = np.random.rand(T, H, W)  # 值域在 [0,1)

    # 调用 UCS 动态搜索
    result = bfs_search_dynamic(grid, smoke_time.tolist(), start)

    if result is None:
        print("在给定时间内未能找到出口！")
    else:
        cost, path = result
        print(f"找到最短路径，总代价 (累积烟雾浓度)：{cost:.3f}")
        print("路径 (time, row, col)：")
        for t, r, c in path:
            cell_type = grid[r][c]
            mark = "出口" if cell_type == 2 else ("起点" if cell_type == 3 else "")
            print(f"  t={t}, pos=({r},{c}) {mark}")

if __name__ == "__main__":
    example()