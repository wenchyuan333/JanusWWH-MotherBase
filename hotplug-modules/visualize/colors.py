"""
ABCD 四元群 · 狀態色彩系統
A=原點 B=顯現 C=邊界 D=流轉
"""

STATE_COLORS = {
    'A': {'name': 'Origin', 'hex': '#12121F', 'rgb': (18, 18, 31), 'desc': '核心本體'},
    'B': {'name': 'Manifest', 'hex': '#6EE7B7', 'rgb': (110, 231, 183), 'desc': '內容顯現'},
    'C': {'name': 'Boundary', 'hex': '#3B82F6', 'rgb': (59, 130, 246), 'desc': '邊界約束'},
    'D': {'name': 'Flow', 'hex': '#F59E0B', 'rgb': (245, 158, 11), 'desc': '時間流轉'},
    'HASH': {'name': 'Block', 'hex': '#FFFFFF', 'rgb': (255, 255, 255), 'desc': '哈希節點'}
}

def get_color(state):
    return STATE_COLORS.get(state.upper(), {}).get('hex', '#888888')

def gradient(start_state, end_state, steps=10):
    """生成狀態間漸層色譜"""
    import colorsys
    s = STATE_COLORS[start_state.upper()]['rgb']
    e = STATE_COLORS[end_state.upper()]['rgb']
    grad = []
    for t in range(steps+1):
        f = t / steps
        r = int(s[0] + (e[0]-s[0])*f)
        g = int(s[1] + (e[1]-s[1])*f)
        b = int(s[2] + (e[2]-s[2])*f)
        grad.append(f'#{r:02X}{g:02X}{b:02X}')
    return grad

if __name__ == "__main__":
    print("=== ABCD 狀態色彩 ===")
    for k,v in STATE_COLORS.items():
        print(f"  {k} {v['hex']} — {v['name']}: {v['desc']}")
    print("\n環流漸層:")
    for c in gradient('A','B',4) + gradient('B','C',4)[1:] + gradient('C','D',4)[1:] + gradient('D','A',4)[1:]:
        print(f"  {c} ███████")
