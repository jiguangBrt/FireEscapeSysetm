import numpy as np
import heapq
from typing import List, Tuple, Optional

def uniform_cost_search_dynamic(
    grid: List[List[int]],
    smoke_time: List[List[List[float]]],
    start: Tuple[int, int]
) -> Optional[Tuple[float, List[Tuple[int, int, int]]]]:
    """
    Perform UCS on a time-expanded graph for dynamic smoke concentrations,
    where the static `grid` uses:
      0 = free space
      1 = wall/obstacle
      2 = exit
      3 = start

    :param grid: 2D map with codes 0/1/2/3
    :param smoke_time: list of 2D smoke concentration grids (values in [0,1]), one per time step
    :param start: (row, col) of the start position
    :return: (total_smoke_cost, path list of (time, row, col)) or None if no exit reached
    """
    T = len(smoke_time)
    rows, cols = len(grid), len(grid[0])

    # Helper: is this cell an exit (but not the start itself)?
    def is_exit(r: int, c: int) -> bool:
        return grid[r][c] == 2

    # Priority queue of (accumulated_cost, (t, r, c))
    open_list: List[Tuple[float, Tuple[int, int, int]]] = []
    # Initialize with start at time 0
    sr, sc = start
    init_cost = smoke_time[0][sr][sc]
    heapq.heappush(open_list, (init_cost, (0, sr, sc)))

    # Records of best cost to each (t,r,c)
    cost_so_far = {(0, sr, sc): init_cost}
    came_from = {(0, sr, sc): None}

    # 4‐connected moves + wait
    directions = [(-1,0), (1,0), (0,-1), (0,1), (0,0)]

    while open_list:
        current_cost, (t, r, c) = heapq.heappop(open_list)

        # If we've reached an exit, reconstruct path
        if is_exit(r, c):
            path = []
            state = (t, r, c)
            while state is not None:
                path.append(state)
                state = came_from[state]
            path.reverse()
            return current_cost, path

        # If out of time steps, skip expanding
        if t + 1 >= T:
            continue

        # Expand neighbors at next time step
        nt = t + 1
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # must be within bounds and not a wall
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                step_cost = smoke_time[nt][nr][nc]
                new_cost = current_cost + step_cost
                state = (nt, nr, nc)
                if state not in cost_so_far or new_cost < cost_so_far[state]:
                    cost_so_far[state] = new_cost
                    came_from[state] = (t, r, c)
                    heapq.heappush(open_list, (new_cost, state))

    # No exit reached within the time horizon
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
    result = uniform_cost_search_dynamic(grid, smoke_time.tolist(), start)

    if result is None:
        print("在给定时间内未能找到出口！")
    else:
        cost, path = result
        print(f"找到最优路径，总代价 (累积烟雾浓度)：{cost:.3f}")
        print("路径 (time, row, col)：")
        for t, r, c in path:
            cell_type = grid[r][c]
            mark = "出口" if cell_type == 2 else ("起点" if cell_type == 3 else "")
            print(f"  t={t}, pos=({r},{c}) {mark}")

if __name__ == "__main__":
    example()