import math, time, os

STRANDS = 3              # 3=三兔；改 2 就是 DNA 雙股
WIDTH, ROWS, TURN = 41, 22, 0.5
chars = ["#", "O", "*"]
cols  = ["\033[91m", "\033[94m", "\033[92m"]   # 紅 藍 綠
RESET = "\033[0m"; mid = WIDTH // 2

try:
    t = 0.0
    while True:
        os.system("clear")
        print("旋轉 + 前進 = 螺旋　每一橫列都是正弦取樣　三股差120°=三兔　(Ctrl-C 停)\n")
        for r in range(ROWS):
            line = [" "] * WIDTH
            for k in range(STRANDS):
                ph = 2 * math.pi * k / STRANDS
                x = math.sin(r * TURN + t + ph)        # 這一股在這列的水平位置
                col = max(0, min(WIDTH - 1, int(mid + x * (mid - 1))))
                line[col] = cols[k] + chars[k] + RESET
            print("".join(line))
        t += 0.22
        time.sleep(0.07)
except KeyboardInterrupt:
    print("\n停。")
