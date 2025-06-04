import numpy as np
from heapq import heappush, heappop
from typing import List, Tuple, Optional

from heapq import heappush, heappop
from typing import List, Tuple, Optional

def a_star_search_dynamic(
    grid: List[List[int]],
    smoke_time: List[List[List[float]]],
    start: Tuple[int, int],
    w1: float = 0.6,
    w2: float = 0.3,
    w3: float = 0.1,
    danger_threshold: float = 0.4
) -> Optional[Tuple[float, List[Tuple[int, int, int]]]]:
    """
    A* pathfinding on a dynamic smoke-aware time-expanded graph with multiple exits.
    Interface unified with uniform_cost_search_dynamic.
    """

    T = len(smoke_time)
    rows, cols = len(grid), len(grid[0])
    sr, sc = start

    # 提取所有出口坐标
    exits = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2]
    if not exits:
        return None

    def heuristic(r: int, c: int) -> float:
        return min(w2 * (abs(r - er) + abs(c - ec)) for er, ec in exits)

    def is_dangerous(t: int, r: int, c: int) -> bool:
        return smoke_time[t][r][c] >= danger_threshold

    # 初始化起点状态
    g0 = w1 * smoke_time[0][sr][sc] + (w3 if is_dangerous(0, sr, sc) else 0)
    h0 = heuristic(sr, sc)
    f0 = g0 + h0
    open_set = [(f0, g0, (0, sr, sc))]
    came_from = {(0, sr, sc): None}
    cost_so_far = {(0, sr, sc): g0}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]  # 4邻域 + 等待

    while open_set:
        f, g, (t, r, c) = heappop(open_set)

        if grid[r][c] == 2:
            # 到达出口，回溯路径
            path = []
            state = (t, r, c)
            while state is not None:
                path.append(state)
                state = came_from[state]
            path.reverse()
            return g, path

        if t + 1 >= T:
            continue

        nt = t + 1
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                smoke = smoke_time[nt][nr][nc]
                penalty = w3 if is_dangerous(nt, nr, nc) else 0
                step_cost = w1 * smoke + w2 * 1 + penalty
                g_new = g + step_cost
                state = (nt, nr, nc)

                if state not in cost_so_far or g_new < cost_so_far[state]:
                    cost_so_far[state] = g_new
                    came_from[state] = (t, r, c)
                    f_new = g_new + heuristic(nr, nc)
                    heappush(open_set, (f_new, g_new, state))

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

    result = a_star_search_dynamic(grid, smoke_time.tolist(), start)
    if result is None:
        print("在给定时间内未能找到出口！")
    else:
        cost, path = result
        print(f"找到最优路径，总代价 (综合代价)：{cost:.3f}")
        print("路径 (time, row, col)：")
        for t, r, c in path:
            cell_type = grid[r][c]
            mark = "出口" if cell_type == 2 else ("起点" if cell_type == 3 else "")
            print(f"  t={t}, pos=({r},{c}) {mark}")


if __name__ == "__main__":
    example()