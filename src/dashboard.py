from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio



# 1. PATHS


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "dashboard_market_data.csv"
OUTPUT_DIR = BASE_DIR / "docs"
OUTPUT_PATH = OUTPUT_DIR / "index.html"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# 2. LOAD DATA


if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Run market_analysis.ipynb first."
    )

df = pd.read_csv(DATA_PATH)

required_columns = [
    "year",
    "category",
    "volume_mln_l",
    "avg_price_rub_l",
    "market_value_bln_rub",
    "cagr_pct",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

if df[required_columns].isna().any().any():
    raise ValueError(
        "Dashboard dataset contains missing values."
    )

df["year"] = df["year"].astype(int)



# 3. BASIC DATASETS


df_2025 = df[df["year"] == 2025].copy()
df_2030 = df[df["year"] == 2030].copy()

total_volume_2025 = df_2025["volume_mln_l"].sum()
total_volume_2030 = df_2030["volume_mln_l"].sum()

total_value_2025 = df_2025["market_value_bln_rub"].sum()
total_value_2030 = df_2030["market_value_bln_rub"].sum()

total_market_cagr = (
    (total_volume_2030 / total_volume_2025) ** (1 / 5) - 1
) * 100

largest_category_2025 = (
    df_2025
    .sort_values("market_value_bln_rub", ascending=False)
    .iloc[0]
)

fastest_category = (
    df_2025
    .sort_values("cagr_pct", ascending=False)
    .iloc[0]
)



# 4. COMMON CHART SETTINGS


FONT_COLOR = "#243B64"
GRID_COLOR = "#E7ECF4"
BACKGROUND = "#FFFFFF"

category_order = [
    "Газированные",
    "Негазированные",
    "Энергетики",
    "Пиво",
    "Пивные напитки",
]

# Corporate-style palette.
# Keeping the same category color across all charts makes
# the dashboard easier to read.
category_colors = {
    "Газированные": "#3B82F6",
    "Негазированные": "#EF4444",
    "Энергетики": "#F59E0B",
    "Пиво": "#8B5CF6",
    "Пивные напитки": "#10B981",
}


def style_figure(fig):
    """Apply common visual styling to Plotly figures."""

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font=dict(
            family="Inter, Arial, sans-serif",
            color=FONT_COLOR,
            size=13,
        ),
        title=dict(
            font=dict(
                size=20,
                color=FONT_COLOR,
            ),
            x=0.02,
            xanchor="left",
        ),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(
            l=60,
            r=30,
            t=100,
            b=60,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zeroline=False,
    )

    return fig



# 5. NATURAL MARKET VOLUME


fig_volume = px.line(
    df,
    x="year",
    y="volume_mln_l",
    color="category",
    markers=True,
    category_orders={
        "category": category_order,
    },
    color_discrete_map=category_colors,
    labels={
        "year": "Год",
        "volume_mln_l": "Объём, млн л",
        "category": "Категория",
    },
    title="Динамика рынка в натуральном выражении",
)

fig_volume.update_traces(
    line=dict(width=3),
    marker=dict(size=7),
)

fig_volume.update_layout(
    hovermode="x unified",
)

fig_volume.update_xaxes(
    dtick=1,
)

style_figure(fig_volume)



# 6. MARKET VALUE


fig_value = px.line(
    df,
    x="year",
    y="market_value_bln_rub",
    color="category",
    markers=True,
    category_orders={
        "category": category_order,
    },
    color_discrete_map=category_colors,
    labels={
        "year": "Год",
        "market_value_bln_rub": "Объём рынка, млрд ₽",
        "category": "Категория",
    },
    title="Динамика рынка в стоимостном выражении",
)

fig_value.update_traces(
    line=dict(width=3),
    marker=dict(size=7),
)

fig_value.update_layout(
    hovermode="x unified",
)

fig_value.update_xaxes(
    dtick=1,
)

style_figure(fig_value)



# 7. MARKET STRUCTURE 2025


structure_2025 = (
    df_2025
    .groupby(
        "category",
        as_index=False,
    )["market_value_bln_rub"]
    .sum()
)

fig_structure = px.pie(
    structure_2025,
    names="category",
    values="market_value_bln_rub",
    hole=0.55,
    category_orders={
        "category": category_order,
    },
    color="category",
    color_discrete_map=category_colors,
    title="Структура рынка по стоимости, 2025",
)

fig_structure.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "%{value:.1f} млрд ₽<br>"
        "%{percent}"
        "<extra></extra>"
    ),
)

fig_structure.update_layout(
    template="plotly_white",
    paper_bgcolor=BACKGROUND,
    font=dict(
        family="Inter, Arial, sans-serif",
        color=FONT_COLOR,
    ),
    title=dict(
        font=dict(size=20),
        x=0.02,
    ),
    legend=dict(
        title=None,
        orientation="v",
    ),
    margin=dict(
        l=30,
        r=30,
        t=80,
        b=30,
    ),
)



# 8. CAGR


cagr_data = (
    df[
        [
            "category",
            "cagr_pct",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "cagr_pct",
        ascending=True,
    )
)

fig_cagr = px.bar(
    cagr_data,
    x="cagr_pct",
    y="category",
    orientation="h",
    color="category",
    color_discrete_map=category_colors,
    text="cagr_pct",
    labels={
        "cagr_pct": "CAGR, %",
        "category": "",
    },
    title="Среднегодовой темп роста натурального рынка, 2025–2030",
)

fig_cagr.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate=(
        "<b>%{y}</b><br>"
        "CAGR: %{x:.1f}%"
        "<extra></extra>"
    ),
)

fig_cagr.update_layout(
    showlegend=False,
)

style_figure(fig_cagr)



# 9. 2025 VS 2030


comparison = (
    df[
        df["year"].isin([2025, 2030])
    ][
        [
            "year",
            "category",
            "market_value_bln_rub",
        ]
    ]
    .copy()
)

comparison["year"] = comparison["year"].astype(str)

fig_comparison = px.bar(
    comparison,
    x="category",
    y="market_value_bln_rub",
    color="year",
    barmode="group",
    labels={
        "category": "",
        "market_value_bln_rub": "млрд ₽",
        "year": "Год",
    },
    title="Стоимость рынка: 2025 vs 2030",
)

fig_comparison.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{y:.1f} млрд ₽"
        "<extra></extra>"
    )
)

style_figure(fig_comparison)



# 10. SUMMARY TABLE


summary_2025 = df_2025[
    [
        "category",
        "volume_mln_l",
        "avg_price_rub_l",
        "market_value_bln_rub",
        "cagr_pct",
    ]
].copy()

summary_2030 = df_2030[
    [
        "category",
        "volume_mln_l",
        "market_value_bln_rub",
    ]
].copy()

summary = summary_2025.merge(
    summary_2030,
    on="category",
    suffixes=("_2025", "_2030"),
)

summary = summary.sort_values(
    "market_value_bln_rub_2025",
    ascending=False,
)

table_rows = ""

for _, row in summary.iterrows():
    cagr = row["cagr_pct"]

    if cagr > 0:
        cagr_class = "positive"
        cagr_text = f"+{cagr:.1f}%"
    elif cagr < 0:
        cagr_class = "negative"
        cagr_text = f"{cagr:.1f}%"
    else:
        cagr_class = "neutral"
        cagr_text = "0.0%"

    table_rows += f"""
        <tr>
            <td class="category-cell">{row['category']}</td>
            <td>{row['volume_mln_l_2025']:,.0f}</td>
            <td>{row['volume_mln_l_2030']:,.0f}</td>
            <td>{row['avg_price_rub_l']:,.1f}</td>
            <td>{row['market_value_bln_rub_2025']:,.1f}</td>
            <td>{row['market_value_bln_rub_2030']:,.1f}</td>
            <td class="{cagr_class}">{cagr_text}</td>
        </tr>
    """

# 11. CONVERT PLOTS TO HTML

volume_html = pio.to_html(
    fig_volume,
    full_html=False,
    include_plotlyjs=True,
    config={
        "displaylogo": False,
        "responsive": True,
    },
)

value_html = pio.to_html(
    fig_value,
    full_html=False,
    include_plotlyjs=False,
    config={
        "displaylogo": False,
        "responsive": True,
    },
)

structure_html = pio.to_html(
    fig_structure,
    full_html=False,
    include_plotlyjs=False,
    config={
        "displaylogo": False,
        "responsive": True,
    },
)

cagr_html = pio.to_html(
    fig_cagr,
    full_html=False,
    include_plotlyjs=False,
    config={
        "displaylogo": False,
        "responsive": True,
    },
)

comparison_html = pio.to_html(
    fig_comparison,
    full_html=False,
    include_plotlyjs=False,
    config={
        "displaylogo": False,
        "responsive": True,
    },
)


# 12. HTML TEMPLATE

html = f"""
<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
Рынок напитков России — аналитический dashboard
</title>

<style>

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: #F5F7FB;
        font-family:
            Inter,
            Arial,
            sans-serif;
        color: #243B64;
    }}

    .container {{
        max-width: 1500px;
        margin: 0 auto;
        padding: 40px;
    }}

    .header {{
        margin-bottom: 32px;
    }}

    .header h1 {{
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        color: #1E355D;
    }}

    .header p {{
        margin-top: 10px;
        color: #66758F;
        font-size: 15px;
        line-height: 1.6;
    }}

    .badge {{
        display: inline-block;
        margin-top: 12px;
        padding: 7px 12px;
        background: #EAF0FA;
        color: #365986;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns:
            repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 24px;
    }}

    .kpi-card {{
        background: white;
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #E6EBF3;
        box-shadow:
            0 3px 12px
            rgba(26, 52, 93, 0.04);
    }}

    .kpi-title {{
        font-size: 13px;
        color: #7B879D;
        margin-bottom: 12px;
        font-weight: 600;
    }}

    .kpi-value {{
        font-size: 29px;
        font-weight: 700;
        color: #213A63;
    }}

    .kpi-subtitle {{
        margin-top: 8px;
        color: #8793A7;
        font-size: 12px;
    }}

    .section-title {{
        margin-top: 38px;
        margin-bottom: 18px;
    }}

    .section-title h2 {{
        margin: 0;
        font-size: 22px;
        color: #213A63;
    }}

    .section-title p {{
        color: #7A879B;
        margin-top: 6px;
        font-size: 14px;
    }}

    .chart-card {{
        background: white;
        border-radius: 14px;
        border: 1px solid #E6EBF3;
        padding: 12px;
        margin-bottom: 20px;
        box-shadow:
            0 3px 12px
            rgba(26, 52, 93, 0.04);
    }}

    .two-column {{
        display: grid;
        grid-template-columns:
            1fr 1fr;
        gap: 20px;
    }}

    .table-card {{
        background: white;
        border-radius: 14px;
        border: 1px solid #E6EBF3;
        padding: 24px;
        overflow-x: auto;
        box-shadow:
            0 3px 12px
            rgba(26, 52, 93, 0.04);
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}

    th {{
        text-align: right;
        padding: 14px 12px;
        background: #F7F9FC;
        color: #69778E;
        font-weight: 600;
        border-bottom: 1px solid #E7EBF2;
    }}

    th:first-child {{
        text-align: left;
    }}

    td {{
        padding: 15px 12px;
        text-align: right;
        border-bottom: 1px solid #EDF0F5;
        color: #394B68;
    }}

    td:first-child {{
        text-align: left;
    }}

    .category-cell {{
        font-weight: 600;
        color: #243B64;
    }}

    .positive {{
        color: #16875B;
        font-weight: 700;
    }}

    .negative {{
        color: #C44A4A;
        font-weight: 700;
    }}

    .neutral {{
        color: #69778E;
        font-weight: 700;
    }}

    .methodology {{
        margin-top: 22px;
        padding: 22px 26px;
        background: #EEF3FA;
        border-radius: 12px;
        color: #5B6E89;
        font-size: 13px;
        line-height: 1.7;
    }}

    .methodology strong {{
        color: #2C476E;
    }}

    .footer {{
        margin-top: 35px;
        color: #909BAD;
        font-size: 12px;
        text-align: center;
    }}

    @media (max-width: 1000px) {{

        .container {{
            padding: 20px;
        }}

        .kpi-grid {{
            grid-template-columns:
                repeat(2, 1fr);
        }}

        .two-column {{
            grid-template-columns:
                1fr;
        }}

    }}

    @media (max-width: 600px) {{

        .kpi-grid {{
            grid-template-columns:
                1fr;
        }}

    }}

</style>

</head>


<body>

<div class="container">

    <div class="header">

        <h1>
            Рынок напитков России
        </h1>

        <p>
            Аналитическая модель рынка безалкогольных
            и слабоалкогольных напитков, 2025–2030.
            Натуральный и стоимостный прогноз.
        </p>

        <div class="badge">
            Base scenario · 2025–2030
        </div>

    </div>


    <!-- KPI CARDS -->

    <div class="kpi-grid">

        <div class="kpi-card">

            <div class="kpi-title">
                Рынок 2025
            </div>

            <div class="kpi-value">
                {total_value_2025:,.0f} млрд ₽
            </div>

            <div class="kpi-subtitle">
                суммарный стоимостный объём
            </div>

        </div>


        <div class="kpi-card">

            <div class="kpi-title">
                Прогноз 2030
            </div>

            <div class="kpi-value">
                {total_value_2030:,.0f} млрд ₽
            </div>

            <div class="kpi-subtitle">
                базовый сценарий
            </div>

        </div>


        <div class="kpi-card">

            <div class="kpi-title">
                CAGR натурального рынка
            </div>

            <div class="kpi-value">
                {total_market_cagr:+.1f}%
            </div>

            <div class="kpi-subtitle">
                2025–2030
            </div>

        </div>


        <div class="kpi-card">

            <div class="kpi-title">
                Наиболее быстрорастущий сегмент
            </div>

            <div class="kpi-value"
                 style="font-size:22px;">
                {fastest_category['category']}
            </div>

            <div class="kpi-subtitle">
                CAGR {fastest_category['cagr_pct']:+.1f}%
            </div>

        </div>

    </div>


    <!-- MARKET DYNAMICS -->

    <div class="section-title">

        <h2>
            Динамика рынка
        </h2>

        <p>
            Историческая оценка 2025 года
            и базовый сценарий прогноза до 2030 года.
        </p>

    </div>


    <div class="chart-card">
        {volume_html}
    </div>


    <div class="chart-card">
        {value_html}
    </div>


    <!-- STRUCTURE -->

    <div class="section-title">

        <h2>
            Структура и динамика сегментов
        </h2>

        <p>
            Сравнение категорий по размеру рынка
            и ожидаемым темпам роста.
        </p>

    </div>


    <div class="two-column">

        <div class="chart-card">
            {structure_html}
        </div>

        <div class="chart-card">
            {cagr_html}
        </div>

    </div>


    <div class="chart-card">
        {comparison_html}
    </div>


    <!-- TABLE -->

    <div class="section-title">

        <h2>
            Ключевые показатели
        </h2>

        <p>
            Сводная таблица основных показателей
            модели по категориям.
        </p>

    </div>


    <div class="table-card">

        <table>

            <thead>

                <tr>

                    <th>
                        Категория
                    </th>

                    <th>
                        Объём 2025,<br>
                        млн л
                    </th>

                    <th>
                        Объём 2030,<br>
                        млн л
                    </th>

                    <th>
                        Цена 2025,<br>
                        ₽/л
                    </th>

                    <th>
                        Рынок 2025,<br>
                        млрд ₽
                    </th>

                    <th>
                        Рынок 2030,<br>
                        млрд ₽
                    </th>

                    <th>
                        CAGR
                    </th>

                </tr>

            </thead>


            <tbody>

                {table_rows}

            </tbody>

        </table>

    </div>


    <!-- METHODOLOGY -->

    <div class="methodology">

        <strong>Методология.</strong>

        Модель объединяет публичные рыночные данные
        и аналитические оценки. Значения, для которых
        отсутствуют полностью сопоставимые публичные
        показатели, используются как model assumptions.

        Прогноз 2026–2030 построен сценарным методом.
        На dashboard представлен базовый сценарий.

        Стоимостный прогноз рассчитан как произведение
        натурального объёма рынка и средней цены.
        В базовом сценарии предполагается ежегодная
        индексация средней цены на 5%.

        CAGR — Compound Annual Growth Rate,
        среднегодовой темп роста натурального объёма
        рынка в 2025–2030 гг.

    </div>


    <div class="footer">

        Аналитический dashboard ·
        рынок напитков России ·
        2025–2030

    </div>

</div>

</body>

</html>
"""



# 13. SAVE DASHBOARD


OUTPUT_PATH.write_text(
    html,
    encoding="utf-8",
)

print("=" * 60)
print("Dashboard successfully generated")
print("=" * 60)

print(f"\nInput:")
print(DATA_PATH)

print(f"\nOutput:")
print(OUTPUT_PATH)

print(
    f"\nRows: {len(df):,}"
)

print(
    f"Categories: {df['category'].nunique()}"
)

print(
    f"Years: {df['year'].min()}–{df['year'].max()}"
)