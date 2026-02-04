"""
charts.py
Visualization module using Matplotlib for generating charts.
Dark-native theme that matches the glassmorphism UI in main.py.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')  # Non-interactive backend for Streamlit

# ═══════════════════════════════════════════════════════════
#  DESIGN TOKENS  — mirrors the CSS variables in main.py
# ═══════════════════════════════════════════════════════════
BG_ROOT     = '#0f0d1a'          # --clr-bg-0
BG_SURFACE  = '#16142a'          # --clr-bg-1
ACCENT      = '#635bff'
INCOME_CLR  = '#10d48a'
EXPENSE_CLR = '#ff5c6b'
BALANCE_CLR = '#60a5fa'
WARNING_CLR = '#f59e0b'

TEXT_PRIMARY   = '#ffffff'
TEXT_SECONDARY = (1, 1, 1, 0.55)
TEXT_MUTED     = (1, 1, 1, 0.30)
GRID_CLR       = (1, 1, 1, 0.07)
SPINE_CLR      = (1, 1, 1, 0.10)

# Categorical palette — ordered by visual weight
CATEGORY_PALETTE = [
    '#635bff',  # accent violet
    '#10d48a',  # income green
    '#ff5c6b',  # expense red
    '#60a5fa',  # balance blue
    '#f59e0b',  # amber
    '#a78bfa',  # soft purple
    '#34d399',  # teal
    '#fb923c',  # orange
    '#67e8f9',  # cyan
    '#f472b6',  # pink
]

# ═══════════════════════════════════════════════════════════
#  GLOBAL THEME  — applied once at import time
# ═══════════════════════════════════════════════════════════
mpl.rcParams.update({
    'figure.facecolor':      BG_ROOT,
    'axes.facecolor':        BG_SURFACE,
    'axes.edgecolor':        SPINE_CLR,
    'axes.labelcolor':       TEXT_PRIMARY,
    'axes.labelweight':      'bold',
    'axes.labelsize':        11,
    'axes.titlecolor':       TEXT_PRIMARY,
    'axes.titlesize':        14,
    'axes.titleweight':      'bold',
    'axes.titlepad':         16,
    'axes.grid':             True,
    'axes.spines.top':       False,
    'axes.spines.right':     False,
    'grid.color':            GRID_CLR,
    'grid.linestyle':        '--',
    'grid.linewidth':        0.8,
    'text.color':            TEXT_SECONDARY,
    'xtick.color':           TEXT_MUTED,
    'xtick.labelsize':       9,
    'ytick.color':           TEXT_MUTED,
    'ytick.labelsize':       9,
    'legend.facecolor':      BG_SURFACE,
    'legend.edgecolor':      SPINE_CLR,
    'legend.labelcolor':     TEXT_SECONDARY,
    'legend.frameon':        True,
    'legend.fontsize':       9,
})


# ─────────────────────────────────────────────────────────
# HELPER  — shared figure setup so every chart starts clean
# ─────────────────────────────────────────────────────────
def _new_fig(w=10, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG_ROOT)
    ax.set_facecolor(BG_SURFACE)
    return fig, ax


# ═══════════════════════════════════════════════════════════
#  EXPENSE PIE  →  rendered as a DONUT chart
# ═══════════════════════════════════════════════════════════
def create_expense_pie_chart(expense_data):
    """
    Donut chart showing expense breakdown by category.

    Args:
        expense_data (dict): {category: amount}

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = _new_fig(10, 7)

    if not expense_data or sum(expense_data.values()) == 0:
        ax.text(0.5, 0.5, 'No expense data available',
                ha='center', va='center', fontsize=14, color=TEXT_SECONDARY,
                transform=ax.transAxes)
        ax.axis('off')
        plt.tight_layout()
        return fig

    categories = list(expense_data.keys())
    amounts    = list(expense_data.values())
    colors     = CATEGORY_PALETTE[:len(categories)]
    total      = sum(amounts)

    # ── Donut wedges ──
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=None,                       # labels handled by legend
        autopct=lambda pct: f'{pct:.1f}%' if pct > 4 else '',
        pctdistance=0.78,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.42, edgecolor=BG_ROOT, linewidth=2.5),
        explode=[0.02] * len(categories),  # tiny gap for breathing room
    )

    # Style percentage labels
    for t in autotexts:
        t.set_color('#fff')
        t.set_fontweight('bold')
        t.set_fontsize(9)

    # ── Centre text: total spend ──
    ax.text(0, 0, f'₹{total:,.0f}\ntotal',
            ha='center', va='center',
            fontsize=17, fontweight='800', color=TEXT_PRIMARY,
            linespacing=1.3)

    # ── Legend (right side) ──
    legend_labels = [f'{cat}  ₹{amt:,.0f}' for cat, amt in zip(categories, amounts)]
    ax.legend(wedges, legend_labels,
              loc='center left', bbox_to_anchor=(1.02, 0.5),
              frameon=True, title='Categories',
              title_fontsize=9)
    ax.get_legend().get_title().set_color(TEXT_MUTED)

    ax.set_title('Expense Breakdown', pad=20)
    ax.axis('equal')
    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════
#  INCOME vs EXPENSE BAR
# ═══════════════════════════════════════════════════════════
def create_income_expense_bar_chart(total_income, total_expense):
    """
    Vertical bar chart comparing income and expense totals.

    Args:
        total_income  (float)
        total_expense (float)

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = _new_fig(8, 5.5)

    labels  = ['Income', 'Expense']
    amounts = [total_income, total_expense]
    colors  = [INCOME_CLR, EXPENSE_CLR]

    bars = ax.bar(labels, amounts,
                  color=colors,
                  width=0.42,
                  edgecolor='none',
                  zorder=3)

    # Value labels above each bar
    max_val = max(amounts) if max(amounts) > 0 else 100
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max_val * 0.015,
                f'₹{h:,.0f}',
                ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=TEXT_PRIMARY)

    # Axis formatting
    ax.set_ylabel('Amount (₹)')
    ax.set_title('Income vs Expense')
    ax.set_ylim(0, max_val * 1.18)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))

    # Left spine only
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color(SPINE_CLR)
    ax.tick_params(axis='x', length=0)   # hide x tick marks
    ax.grid(axis='y', zorder=0)

    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════
#  FINANCIAL SUMMARY  (horizontal bar)
# ═══════════════════════════════════════════════════════════
def create_summary_chart(summary_data):
    """
    Horizontal bar chart: Income, Expense, Balance.

    Args:
        summary_data (dict): keys total_income, total_expense, balance

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = _new_fig(10, 5)

    labels  = ['Total Income', 'Total Expense', 'Balance']
    amounts = [
        summary_data['total_income'],
        summary_data['total_expense'],
        summary_data['balance'],
    ]
    colors  = [INCOME_CLR, EXPENSE_CLR,
               BALANCE_CLR if amounts[2] >= 0 else WARNING_CLR]

    bars = ax.barh(labels, amounts,
                   color=colors,
                   height=0.42,
                   edgecolor='none',
                   zorder=3)

    # Value labels to the right of each bar
    max_val = max(abs(v) for v in amounts) if any(amounts) else 100
    for bar, amt in zip(bars, amounts):
        x_pos = max(amt, 0) + max_val * 0.018
        ax.text(x_pos,
                bar.get_y() + bar.get_height() / 2,
                f'₹{amt:,.0f}',
                ha='left', va='center',
                fontsize=11, fontweight='bold', color=TEXT_PRIMARY)

    # Axis formatting
    ax.set_xlabel('Amount (₹)')
    ax.set_title('Financial Summary')
    ax.set_xlim(0, max_val * 1.22)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))

    # Bottom spine only
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color(SPINE_CLR)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.grid(axis='x', zorder=0)

    plt.tight_layout()
    return fig