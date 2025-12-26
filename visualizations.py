import plotly.graph_objects as go
import pandas as pd

def create_risk_matrix(risks_detected):
    """
    Creates a Risk Matrix Heatmap (Frequency vs. Gravity) with a Professional Cyber Style.
    
    Background: Tiled Heatmap (z = x*y).
    Colors: Deep Teal (Low), Muted Amber (Major), Deep Red (Critical).
    Markers: White with Red Border (Target effect).

    Args:
        risks_detected (list): List of dicts with 'pillar', 'frequency', 'gravity'.

    Returns:
        plotly.graph_objects.Figure: The risk matrix figure.
    """
    # 1. Generate Heatmap Data (5x5 Grid)
    x_axis = [1, 2, 3, 4, 5]
    y_axis = [1, 2, 3, 4, 5]
    
    z_data = []
    
    for y in y_axis:
        row = []
        for x in x_axis:
            row.append(x * y) # z = Score
        z_data.append(row)

    fig = go.Figure()

    # 2. Add Heatmap Layer (The Board)
    # Custom Colorscale based on Score (1-25)
    # Subtle/Mature Palette
    # 1-5: #143d3d (Deep Muted Teal) -> Normalized: 0.0 to ~0.17
    # 6-10: #4d3a1a (Deep Muted Amber/Bronze) -> Normalized: ~0.21 to ~0.38
    # 12-25: #4d1a1a (Deep Muted Burgundy) -> Normalized: ~0.46 to 1.0
    
    # Thresholds:
    # Green/Orange boundary: 5.5 (Norm: 0.1875) -> Use 0.18
    # Orange/Red boundary: 11 (Norm: 0.4166) -> Use 0.41
    
    cyber_colorscale = [
        [0.0, '#143d3d'],  # Low Start
        [0.18, '#143d3d'], # Low End (Covers 5)
        [0.18, '#4d3a1a'], # Major Start (Covers 6)
        [0.41, '#4d3a1a'], # Major End (Covers 10)
        [0.41, '#4d1a1a'], # Critical Start (Covers 12)
        [1.0, '#4d1a1a']   # Critical End
    ]

    fig.add_trace(go.Heatmap(
        x=x_axis,
        y=y_axis,
        z=z_data,
        colorscale=cyber_colorscale,
        showscale=False, # Hide Legend
        xgap=3, # Tile effect
        ygap=3,
        hovertemplate='<b>Score : %{z}</b><extra></extra>'
    ))

    # 3. Add Scatter Plot Layer (The Risks)
    if risks_detected:
        df = pd.DataFrame(risks_detected)
        
        # Ensure we have the right columns
        if {'frequency', 'gravity', 'pillar'}.issubset(df.columns):
            # Calculate score for tooltip if not present
            if 'risk_score' not in df.columns:
                df['risk_score'] = df['frequency'] * df['gravity']

            fig.add_trace(go.Scatter(
                x=df['frequency'],
                y=df['gravity'],
                mode='markers',
                text=df['pillar'],
                customdata=df['risk_score'],
                marker=dict(
                    size=18,
                    color='rgba(255, 255, 255, 0.9)', # White, slight opacity
                    line=dict(width=2, color='#FF0000'), # Red Border (Target)
                    symbol='circle'
                ),
                hoverinfo='text',
                hovertemplate='<b>Pilier :</b> %{text}<br><b>Score :</b> %{customdata}<extra></extra>'
            ))

    # 4. Professional Layout
    fig.update_layout(
        title=dict(
            text="MATRICE DES RISQUES",
            font=dict(size=18, color='#58a6ff', family="Courier New, monospace"),
            x=0.0,
            y=0.95
        ),
        xaxis=dict(
            title=dict(text="FRÉQUENCE", font=dict(color='#8b949e', size=12)),
            range=[0.5, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            showgrid=True,
            gridcolor='#333',
            zeroline=False,
            tickfont=dict(color='#8b949e')
        ),
        yaxis=dict(
            title=dict(text="GRAVITÉ", font=dict(color='#8b949e', size=12)),
            range=[0.5, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            showgrid=True,
            gridcolor='#333',
            zeroline=False,
            tickfont=dict(color='#8b949e')
        ),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=50, b=40),
        width=700,
        height=600,
        showlegend=False
    )

    return fig
