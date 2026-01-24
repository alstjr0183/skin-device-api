import os
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle, Wedge
from schemas import SkinScores

def create_radar_chart(scores: SkinScores) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(base_dir, "fonts", "NanumGothic-Bold.ttf")
    
    try:
        font_prop = fm.FontProperties(fname=font_path)
    except Exception:
        font_prop = fm.FontProperties(family='Apple SD Gothic Neo')

    plt.rcParams['axes.unicode_minus'] = False

    labels = [
        f'주름\n({scores.wrinkles})',
        f'모공\n({scores.pores})',
        f'색소\n({scores.pigmentation})',
        f'트러블\n({scores.acne})',
        f'붉은기\n({scores.redness})',
        f'탄력\n({scores.elasticity})',
        f'수분\n({scores.hydration})'
    ]
    values = [
        scores.wrinkles, scores.pores, scores.pigmentation, 
        scores.acne, scores.redness, scores.elasticity,
        scores.hydration
    ]
    
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    
    ax.fill_between(angles, 0, 40, color='#FFDDDD', alpha=0.5)   
    ax.fill_between(angles, 40, 70, color='#FFFEDD', alpha=0.5) 
    ax.fill_between(angles, 70, 100, color='#DDFFDD', alpha=0.5) 
    
    ax.plot(angles, values, color='#FF007F', linewidth=2, linestyle='solid', label='내 피부 점수')
    ax.fill(angles, values, color='#FF007F', alpha=0.2)
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontproperties=font_prop, size=11, weight='bold')
    
    for label in ax.get_xticklabels():
        label.set_color('#333333')
    
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=8)
    plt.ylim(0, 100)
    
    ax.spines['polar'].set_visible(False)
    ax.grid(True, color='grey', linestyle='--', alpha=0.5)

    plt.figtext(0.5, 0.95, "바깥쪽으로 넓을수록 피부 상태가 좋습니다.", ha='center', 
                fontproperties=font_prop, size=13, weight='bold', color='#000000')

    ax.text(0, 0, "Bad", ha='center', va='center', color='red', weight='bold', size=10, alpha=0.7)
    ax.text(np.radians(45), 110, "Good", ha='center', va='center', color='green', weight='bold', size=10)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64
